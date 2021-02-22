# Desarrollado para LaSociedadPost - Nonstop
# Author: Leandro Inocencio aka Cesio (cesio.arg@gmail.com)
# Collaboration & Maintenance. Updates, new Features: Gaston Sbodio (gastonsbodio@gmail.com)

from lasp.tactic.utils import autofix_path, SaveVersion_Publish, lenSequence, existsSequence
from lasp.tactic.extractor import get_info_from_media
from lasp.tactic.Xmlparser import get_data_from_xml
from subprocess import Popen, PIPE, STDOUT
from lasp.nuke.Submitter import SubmitCmd
from lasp.packages.pyseq import *
from functools import partial
from itertools import chain
from datetime import date
from time import sleep

import os
import sys
import re
import ctypes
import json
import importlib
import threading
import lasp.tactic.Xmlparser as xmlparser
import lasp.tactic.media as media
import lasp.tactic.extractor as extractor
import glob

reload(xmlparser)
reload(extractor)
reload(media)

global recentFootage

recentFootage = media.root + '/'


userpref = os.environ['USERPROFILE'] + '\\nuke_pref.json'

project_name = "los_lunnis"

try:
    import nuke
except:
    print "No Nuke loaded."
    nuke = None


class LoadPath(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__( self )
        self.path = path

    def run(self):
        nuke.pluginAppendPath(self.path)


def fullListdir(path):
    files = []
    for item in os.listdir(path):
        files.append(os.path.join(path, item))
    return files


def load_python_modules():
    modules = {}
    nuke_modules_path = os.path.join(os.environ.get('TOOLS_PATH'), 'dev/lasp/nuke/python')
    for file in os.listdir(nuke_modules_path):
        module, ext = os.path.splitext(file)
        if not module.startswith('_') and ext == '.py':
            try:
                ret = importlib.import_module('lasp.nuke.python.%s' % module)
                print 'Module %s imported.' % module
                modules[module] = ret
            except ImportError, e:
                print "No se pudo importar el modulo: %s" % module

    return modules


def ensure_module(module):
    from lasp.packages import modules
    try:
        ret = importlib.import_module(module)

    except ImportError, e:
        package = e.message.split(' ')[-1]
        print "Module %s in not present, try install..." % (package)
        try:
            import pip
        except:
            from lasp.get_pip import main
            import pip

        pip.main(['install', modules.get(module)])
        ret = importlib.import_module(module)

    return {ret.__name__: ret}


def getUniqueName(name):
    regex_name = re.compile('(?P<name>.*?)(?P<number>[0-9]+)$')
    while nuke.exists(name):
        info = [match.groupdict() for match in regex_name.finditer(name)]
        if info:
            info = info[0]
            name = info['name'] + str(int(info['number']) + 1)
    return name


def evaluateNodesFileKnob():
    for node in chain(nuke.allNodes('Read'), nuke.allNodes('Write')):
        expr = node.knob('file').getValue()
        node.knob('file').setValue(expr)
        try:
            value = eval(expr[expr.index('python ') + 7:expr.rindex(']')])
            node.knob('file').setValue(value)
        except Exception, e:
            pass


def clean_and_show():
    selected = nuke.selectedNode()
    for node in nuke.allNodes():
        if not node.name() == selected.name():
            node.hideControlPanel()

    selected.showControlPanel()


userpref = os.environ['USERPROFILE'] + '\\nuke_pref.json'

project_name = "los_lunnis"
project_name2 = "el_potro"

def fullresPath():
    try:
        # path = "Z:/disney/once_02/episodios/EP08/secuencias/E7A/shots/GFX_ONCE_Y02_EP08_E7A_020/Compo Final/NO_PARENT_a_Compo Final_v003.nk" # script de prueba
        info_path = media.Path(nuke.root().name(), app='nuke')
        if info_path.project == project_name:
            return info_path.fullresPathExr
        if info_path.project == project_name2:
            return info_path.fullresPathExr
        else:
            return info_path.fullresPath
        # return media.Path(nuke.root().name(), app='nuke').fullresPath # script original
    except:
        return ''


def fullresStereoPath():
    return '%s/%%v_%s' % os.path.split(fullresPath())


def lowresPath():
    try:
        return media.Path(nuke.root().name(), app='nuke').lowresPath
    except:
        return ''


def lowresStereoPath():
    return '%s/%%v_%s' % os.path.split(lowresPath())


def lowresMOVPath():
    try:
        return media.Path(nuke.root().name(), app='nuke').lowresMOVPath
    except:
        return ''


def MOVPath():
    return media.Path(nuke.root().name(), app='nuke').MOVPath

    
def mediaPath():
    try:
        print (media.Path(nuke.root().name()).mediaPath)
        return media.Path(nuke.root().name()).mediaPath
    except:
        return media.root


def prerenderPath():
    try:
        return media.Path(nuke.root().name(), app='nuke', node_name=nuke.thisNode().name()).PreRenderPath
    except:
        return ''

def proxyprerenderPath():
    try:
        return media.Path(nuke.root().name(), app='nuke', node_name=nuke.thisNode().name()).ProxyPreRenderPath
    except:
        return 

def isMedia(sequence):
    return sequence.tail() in media.formats


def rename_group(nodes, name):
    for node in nuke.allNodes():  # HACK por que no me deja renombrar los nodos se crashea
        if node.name() in nodes:
            node.setSelected(True)
        else:
            node.setSelected(False)

    for node in nuke.selectedNodes():
        node.setName(name)


def build_sequence(xml_parser, digicuts, client, escena):
    old_dir = ''
    #codec = "9"
    codec = 5

    """Codecs:  Animacion       = 0
                BMP             = 1
                Cinepak         = 2
                DV - PAL        = 3
                DV/DVCPRO - NTSC= 4
                DVCPRO - PAL    = 5
                Graficos        = 6
                H.261           = 7
                H.263           = 8
                H.264           = 9
                ...
    """
    sequence_mov = None

    script = 'import nuke\n'
    script += 'import threading\n'
    script += 'from lasp.nuke.Submitter import SubmitJob\n'
    script += 'mov_read = None\n'

    handler_in = 5

    width = xml_parser.video_format.width 
    height = xml_parser.video_format.height
    mov = digicuts[0]

    if(xml_parser.escenas):
        escena_info = xml_parser.escenas[escena]

    try:
        if len(xml_parser.escenas) > 1:
            start_escena = escena_info['in_label'].start
            end_escena = escena_info['out_label'].end
        else:
            start_escena = None
            end_escena = None
    except:
        start_escena = 0
        end_escena = None
        print "No contine labels de IN/OUT."
        return

    for shot in shots_with_spaces(xml_parser, escena):
        if start_escena is None:
            start_escena = int(shot.get('start_frame'))

        duration = shot['end_frame'] - shot['start_frame'] - 1

        rate = mov.get('fps')
        audiofile = mov.get('filepath')
        seq_ok = False
        handler = 0

        for app in ['nuke', 'ae']:
            p = media.Path.from_shot(shot, app=app, client=client)

            try:
                path = p.appOutputPath + '/lowres'

                if not sequence_mov and p.client and p.project:
                    today = date.today()
                    today = '%d%02d%d' % (today.day, today.month, today.year - 2000)
                    sequence_mov = '/'.join([p.sequencePath, 'Armados', '%s_%s_%s.mov' % (p.episodio, p.secuencia, today)])

            except media.NoAttributes:
                continue

            if shot.get('has_gfx') and os.path.exists(path):
                versions = [dir_ for dir_ in os.listdir(path) if os.path.isdir(path + '/' + dir_) and dir_.lower().startswith('v') and os.listdir(path + '/' + dir_)]
                old_dir = os.path.join(path, max(versions))
                #Empieza a agarrar cada frame del lowres que esta en old_dir
                for seq in pyseq.get_sequences(old_dir):
                    if seq.tail() == '.jpg':
                        mpath = seq.format('%D/%h%p%t').replace('\\', '/')
                        handler = int(round((seq.end() - seq.start() - duration) / 2))

                        if handler > seq.start():
                            start = handler
                        else:
                            start = seq.start()
                            handler = 0

                        end = start + duration

                        script += "nuke.createNode('Read', 'file \"%s\" first %d last %d before 3 after 3 on_error 1')\n" % (mpath, start, end)
                        script += "nuke.createNode('Reformat', 'resize 4 black_outside 1')\n"
                        script += "nuke.createNode('TimeOffset', 'time_offset %d')\n" % (shot['start_frame'] - start_escena - start + 1)
                        seq_ok = True
                        break
                break
            shotOK = shot
        else:
            input = mov.get('filepath').replace('\\', '/')
            audiofile = mov.get('filepath')
            script += "mov_read = nuke.createNode('Read', 'file \"%s\" first %d last %d before 3 after 3 on_error 1')\n" % (input, shot['start_frame'] + 1, shot['end_frame'])
            script += "nuke.createNode('Reformat', 'resize 4 black_outside 1')\n"
            script += "nuke.createNode('TimeOffset', 'time_offset %d')\n" % (start_escena * -1)

        if seq_ok:
            vfx = 'VFX'
        else:
            vfx = ''

        print '%s - Start: %d, End: %d, Handler: %s, %s ' % (shot.get('name'), shot.get('start_frame'), shot.get('end_frame'), handler, vfx)

    if not end_escena:
        end_escena = shot.get('end_frame')

    total_duration = end_escena - start_escena

    script += '''nuke.root()['fps'].setValue(%s)
format = nuke.root()['format'].value()
format.setWidth(%d)
format.setHeight(%d)
nuke.root()['format'].setValue('HD_1080') # format
nuke.nodes.Constant(format='HD_1080')    # format
nuke.root()['first_frame'].setValue(1)
nuke.root()['last_frame'].setValue(%s)

def TimeOffsetNodes():
    for index, node in enumerate(nuke.allNodes('Constant') + nuke.allNodes('TimeOffset')):
        if index == 2:
            yield None
        yield node

merge = nuke.nodes.Merge2(inputs=list(TimeOffsetNodes()))\n''' % (rate, width, height, total_duration)
    if not sequence_mov:
        sequence_mov = 'Z:/INTERNO/MEDIA/'

    #script += "write = nuke.nodes.Write(file='%s', writeTimeCode=1, file_type=7, codec=%s, inputs=[merge], on_error=1, audiofile='%s', beforeRender='createWriteDir()')\n" % (sequence_mov, codec, audiofile)
    script += "write = nuke.nodes.Write(file='%s', writeTimeCode=1, file_type='mov',meta_codec=%s, inputs=[merge], on_error=1, audiofile='%s', beforeRender='createWriteDir()')\n" % (sequence_mov, codec, audiofile)
    script += "write.knob('units').setValue(1)\n"
    script += "write.knob('audio_offset').setValue(%d)\n" % (start_escena * -1)
    dirname, basename = os.path.split(sequence_mov)
    filename, ext = os.path.splitext(basename)
    python_script = '/'.join((os.environ.get('RAMON_TEMP'), 'armados','%s_builder_sequence.py')) % filename
    nuke_script = os.path.splitext(python_script)[0] + '.nk'
    script += "nuke.scriptSaveAs('%s', True)\n" % nuke_script
    script += "FrameList = '-'.join([str(int(nuke.root()['first_frame'].value())), str(int(nuke.root()['last_frame'].value()))])\n"
    script += "ChunkSize = 10000000\n"
    script += "SubmitJob(nuke.root(), write, '%s', ChunkSize, FrameList, '%s' ,1)\n" % (filename, sequence_mov)
    script += 'nuke.scriptExit(True)\n'

    #Para que funcione tiene que estar cereada la ruta: Z:\INTERNO\TOOLS2\tmp\armados\
    with open(python_script, 'w') as f:
        f.write(script)

    #cmd = '"C:\Program Files\Nuke8.0v5\Nuke8.0.exe" -safe -t "%s"' % python_script
    #cmd = '"C:\Program Files\Nuke11.1v3\Nuke11.1.exe" -safe -t --nukex "%s"' % python_script
    cmd = '"C:\Program Files\Nuke11.1v3\Nuke11.1.exe" -safe -t "%s"' % python_script
    startupDir = os.path.dirname(python_script)
    job = threading.Thread(None, SubmitCmd, args=(cmd, filename + '_cmd', 'Creando .nk desde python.', 'Pipeline', 0, startupDir))
    job.start()

def shots_with_spaces(parsed, escena):
    escena_info = parsed.escenas.get(escena)
    try:
        _in = escena_info.get('in_label')
        duration = escena_info.get('out_label').end
    except:
        duration = parsed.duration

    try:
        first_shot = {'start_frame':_in.start ,'end_frame':_in.end, 'has_gfx':False, 'name': escena + '_in'}
    except:
        first_shot = {'start_frame':0 ,'end_frame':0, 'has_gfx':False, 'name': escena + '_in'}

    prev_shot = first_shot

    for shot in parsed.shots:
        if shot.get('sequence') == escena:
            if first_shot and first_shot.get('start_frame') <= shot.get('start_frame') and first_shot.get('end_frame') > 0:
                first_shot['end_frame'] = shot.get('start_frame')
                yield first_shot
                first_shot = None

            if prev_shot and prev_shot.get('end_frame') == shot.get('start_frame'):
                yield shot

            elif prev_shot:
                newshot = shot.copy()
                newshot['start_frame'] = prev_shot.get('end_frame')
                newshot['end_frame'] = shot.get('start_frame')
                newshot['has_gfx'] = False
                newshot['name'] = 'Empty'
                yield newshot
                yield shot
            else:
                first_shot = shot
            prev_shot = shot

    if prev_shot['end_frame'] < duration:    
        last_shot = prev_shot.copy()
        last_shot['start_frame'] = prev_shot.get('end_frame')
        last_shot['end_frame'] = duration
        last_shot['has_gfx'] = False
        last_shot['name'] = escena + '_out'
        yield last_shot

def createMedia222(path):
    pathModoLig = path.split("/in")[0]
    partesPath = path.split("/")
    for obj in ["INTERNO","MEDIA", "in"]:
        partesPath.remove (obj)
    partesNum = len(partesPath)
    partesPath = partesPath[0:3] + ["episodios"] + partesPath[3:partesNum]

    partesNum = len(partesPath)
    partesPath = partesPath[0:5] + ["secuencias"] + partesPath[5:partesNum]

    partesNum = len(partesPath)
    partesPath = partesPath[0:7] + ["shots"] + partesPath[7:partesNum]
    newPath = "___"
    for obj in partesPath:
        newPath = newPath + obj + "/"
    newPath = newPath.split ("___")[-1]
    abcPath = newPath + "Publish/"
    newPath = newPath + "Animacion_A/"
    alembicFile = None
    movFile = None
    pathAlmm = None
    pathMov = None
    
    bool = os.path.exists(abcPath)
    if bool == True:
        os.startfile(abcPath)
        dirList = os.listdir(abcPath)
        listAbcPublish = []
        contador = 0
        for obj in dirList:
            if obj.endswith('.abc'):
                nomPartes = obj.split ("_")
                if nomPartes[-1] == "edit.abc":
                    alembicFile = obj
                    pathAlmm = abcPath + alembicFile
                    listAbcPublish.append(pathAlmm)
                if nomPartes[-1] == "modo.abc":
                    alembicFile = obj
                    pathAlmm = abcPath + alembicFile
                    listAbcPublish.append(pathAlmm)
        try:
            for o in listAbcPublish:
                #nuke.message (o)
                if os.path.exists(o):
                    cam = nuke.nodes.Camera2()
                    cam.setXYpos(0,0)
                    cam.autoplace()
                    nuke.zoom(.5, [cam.xpos(), cam.ypos()])
                    if contador == 0:
                        cam.setName("camaraHalideEdit")
                        contador = contador + 1
                    else:
                        cam.setName("camaraHalideModo")
                        cam.knob("read_from_file").setValue(True)
                        cam.knob("file").setValue(o)
                else:
                    nuke.message (" Ruta o archivo alembic no encontradoo "  )
        except Exception:
            pass
    if bool == False :
        nuke.message (" Ruta o archivo alembic no encontradooooo "  )    
    
    bool = os.path.exists(newPath)
    if bool == True:
        os.startfile( newPath )
        dirList = os.listdir(newPath)
        for obj in dirList:
            if obj.endswith('.mov'):
                movFile = obj
                pathMov = newPath + movFile

    bool = os.path.exists(str(pathMov))
    bool = str(bool)
    if bool == "True":
        n = nuke.createNode("Read", "file {"+ pathMov +"}")
        n.setXYpos(0,0)
        n.autoplace()
        nuke.zoom(.5, [n.xpos(), n.ypos()])
    else:
        print " Ruta o archivos no encontrados "
        nuke.message (" Ruta o archivo .mov no encontrado ")
    pathModoLigIncompleta = pathModoLig
    pathModoLig = pathModoLig + "/modo/Lighting/"
    if os.path.exists(pathModoLig):
        os.startfile( pathModoLig )
        dirList = os.listdir(pathModoLig)
        for obj in dirList:
            if obj.endswith('.exr'):
                partesName = obj.split ("_")
                passType = partesName[-2]
                patron = partesName[-1]
                pathModoLigPatron = pathModoLig + "*" + patron
                patronPath = glob.glob( pathModoLigPatron )
                name = None
                contador = 0
                for exr in patronPath:
                    exr = exr.split("\\")[-1]
                    exrPartes = exr.split("_")
                    shotNameList = exrPartes
                    shotNameList.remove(shotNameList[-1])
                    numPartes = len(exrPartes)
                    name = "___"
                    for i, obj in enumerate(exrPartes):
                        if i < numPartes - 1:
                            name = name + obj + "_"
                    name = name.split("___")[-1]
                    numFrRange = glob.glob( pathModoLig + "*" + passType + "*" )
                    #sorted( numFrRange )
                    listaValorFrame = []
                    for obj in numFrRange:
                        frame = obj.split("\\")[-1]
                        frame = frame.split("_")[-1]
                        frame = frame.split(".exr")[0]
                        frame2 = "___"
                        for obj in frame:
                            booleano = obj.isdigit()
                            if booleano == True:
                                frame2 = frame2 + obj
                            else:
                                if contador == 0:
                                    nuke.message ("error de nomenclatura en los renders de modo...")
                                    contador = contador + 1
                        frame2 = frame2.split("___")[-1]
                        frame = int(frame2)
                        listaValorFrame.append(frame)
                    listaValorFrame = sorted(listaValorFrame)
                    numPartName = len(shotNameList)
                    shotName = "___"
                    for i, obj in enumerate(shotNameList):
                        if i < numPartName - 1:
                            shotName = shotName + obj + "_"
                        else:
                            shotName = shotName + obj
                    shotName = shotName.split("___")[-1]
                    readNode = nuke.nodes.Read(file = pathModoLig + shotName +  "_" + "%04d.exr" , first = listaValorFrame[0], last = listaValorFrame[-1], origfirst = listaValorFrame[0], origlast = listaValorFrame[-1] )
                    readNode.setXYpos(0,0)
                    readNode.autoplace()
                    nuke.zoom(.5, [readNode.xpos(), readNode.ypos()])
                break
    else:
        nuke.message ("error de nomenclatura en los renders de modo...")
        os.startfile( pathModoLigIncompleta )

def createMedia(path):
    #try:
    createMedia222(mediaPath())
    #except Exception:
    #    pass
    color_space='0.0'
    if os.path.exists(path):
        nodes = []
        sequences = get_sequences(path)
        fullres = nuke.toNode('fullres')

        if fullres:
            color_space = str(fullres['colorspace'].getValue())

        while sequences:
            sequence = sequences.pop()
            if os.path.isdir(sequence.path()):
                sequences.extend(get_sequences(sequence.path()))
                continue

            if media.isMedia(sequence.name) and not sequence.dirname().endswith('proxy'):
                if media.isMovie(sequence.name):
                    media_path = sequence.path().replace('\\', '/')
                    proxy_path = sequence.format(r'%D\proxy\%h').replace('\\', '/')
                    proxy_seq = get_sequences(os.path.splitext(proxy_path)[0] + '.#.jpg')
                    n = nuke.createNode('Read', 'file "%s"' % media_path)
                    n.setXYpos(0,0)
                    n.autoplace()
                    nuke.zoom(.5, [n.xpos(), n.ypos()])

                    if proxy_seq:
                        proxy_seq = proxy_seq[0]
                        n['proxy'].setValue(proxy_seq.format(r'%D\%h%p%t').replace('\\', '/'))
                        n['first'].setValue(int(proxy_seq.start()))
                        n['last'].setValue(int(proxy_seq.end()))
                        n['origfirst'].setValue(int(proxy_seq.start()))
                        n['origlast'].setValue(int(proxy_seq.end()))

                elif media.isImage(sequence.name):
                    proxy_seq = get_sequences(sequence.format(r'%D\proxy\%h.#.jpg').replace('\\', '/'))
                    media_path = sequence.format(r'%D\%h%p%t').replace('\\', '/')

                    n = nuke.nodes.Read(file=media_path)
                    n['on_error'].setValue('1.0')
                    n['first'].setValue(int(sequence.start()))
                    n['last'].setValue(int(sequence.end()))
                    n['origfirst'].setValue(int(sequence.start()))
                    n['origlast'].setValue(int(sequence.end()))

                    if proxy_seq:
                        proxy_seq = proxy_seq[0]
                        n['proxy'].setValue(proxy_seq.format(r'%D\%h%p%t').replace('\\', '/'))

                n['colorspace'].setValue(color_space)
                nodes.append(n)
                sleep(1)
        return nodes
    else:
        raise Exception('No se encontro Footage.')


def createMediaMaya(path):
    print mediaPath()


def createPreRender():
    #name = getUniqueName('PreRender')
    #node = nuke.createNode('Write', 'name %s' % name)
    node = nuke.createNode('Write')
    node.knob('file').setValue('[python functions.prerenderPath()]')
    node.knob('beforeRender').setValue('createWriteDir()')
    node.knob('channels').setValue('rgba')
    #node.knob('interleave').setValue(3)
    node.knob('file_type').setValue(3)
    node.knob('reading').setValue(1)
    node.knob('checkHashOnRead').setValue(1)
    node.knob('on_error').setValue(3)
    node.knob('colorspace').setValue(int(node['colorspace'].getValue()))
    return node

def createProxyPreRender():
    #name = getUniqueName('PreRender')
    #node = nuke.createNode('Write', 'name %s' % name)
    node = nuke.createNode('Write')
    node.knob('file').setValue('[python functions.proxyprerenderPath()]')
    node.knob('beforeRender').setValue('createWriteDir()')
    node.knob('channels').setValue('rgba')
    #node.knob('interleave').setValue(3)
    node.knob('file_type').setValue(3)
    node.knob('reading').setValue(1)
    node.knob('checkHashOnRead').setValue(1)
    node.knob('on_error').setValue(3)
    node.knob('colorspace').setValue(int(node['colorspace'].getValue()))
    return node
	
	

def createRead():
    global recentFootage
    fullres = nuke.toNode('fullres')

    if fullres:
        color_space = str(fullres['colorspace'].getValue())
    else:
        color_space = None

    for node in nuke.selectedNodes():
        for knob in node.allKnobs():
            if 'file' in knob.name():
                value = node.knob('file').value()
                if value.startswith('[python'):
                    path = node.knob('file').getEvaluatedValue()

                if not value:
                    break
                else:
                    path = value

                range = lenSequence(value)

                if range:
                    path += ' %d-%d' % (range[0], range[1])

                for newpath, seq in nuke_filedialog(path):
                    node = nuke.createNode('Read', 'file "%s"' % newpath)
                    node.knob('cacheLocal').setValue(0)
                    dir, base = os.path.split(path)
                    name, rest = base.split('.', 1)

                    if seq:
                        node.knob('origfirst').setValue(seq[0])
                        node.knob('origlast').setValue(seq[1])
                        node.knob('first').setValue(seq[0])
                        node.knob('last').setValue(seq[1])

                    proxy_seq = os.path.join(dir, 'proxy', name) + '.#.jpg'

                    if existsSequence(proxy_seq):
                        seq = get_sequences(proxy_seq)[0]
                        node.knob('proxy').setValue(seq.format(r'%D\%h%p%t').replace('\\', '/'))

                if color_space:
                    node.knob('colorspace').setValue(color_space)

                return

    for newpath, seq in nuke_filedialog(recentFootage):
        node = nuke.createNode('Read', 'file "%s"' % newpath)
        node.knob('cacheLocal').setValue(0)

        for seq in get_sequences(newpath):
            if len(seq) > 1:
                node.knob('origfirst').setValue(seq.start())
                node.knob('origlast').setValue(seq.end())
                node.knob('first').setValue(seq.start())
                node.knob('last').setValue(seq.end())

                if color_space:
                    node.knob('colorspace').setValue(color_space)


def appOutputPath():
    return media.Path(nuke.root().name(), app='nuke').appOutputPath


def generate_proxy():
    proxy_status = nuke.root()['proxy'].value()
    nuke.root()['proxy'].setValue(False)

    for read in nuke.selectedNodes("Read"):
        path = read.knob('file').value()
        read.knob('file').setValue(path)
        match = re.findall('(.*?)(%\d+d|#+)(.*)', path)
        range = nuke.FrameRanges('%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame()))

        if match:
            splits = match[0]
            dir_, base = os.path.split(splits[0])
            proxy_file = '/'.join([dir_, 'proxy', base]) + splits[1] + '.jpg'
        else:
            name, ext = os.path.splitext(path)
            dir_, base = os.path.split(name)

            if ext == '.mov':
                proxy_file = '%s/proxy/%s.#####.jpg' % (dir_, base)
            else:
                proxy_file = '%s/proxy/%s.jpg' % (dir_, base)
                range = nuke.FrameRanges('1')

        try:
            w = nuke.nodes.Write(file=proxy_file)
            w.knob('file_type').setValue('jpg')
            w.knob('_jpeg_quality').setValue(0.95)
            w.knob('beforeRender').setValue('createWriteDir()')
            reformat = nuke.nodes.Reformat(type=2, scale=0.5, resize=5, filter=8)
            reformat.setInput(0, read)
            w.setInput(0, reformat)

            nuke.render(w, range)
            read.knob('proxy').setValue(proxy_file)
        except Exception, e:
            print "Cancel Generating Proxy:", str(e)
            nuke.root()['proxy'].setValue(proxy_status)

        finally:
            nuke.delete(w)
            nuke.delete(reformat)

    nuke.root()['proxy'].setValue(proxy_status)


def readFromWrite():
    print 'readFromWritewRRfunctions'
    for node in nuke.selectedNodes("Write"):
        selectedNodePremult = str(nuke.selectedNode()['premultiplied'].getValue())
        if node.Class() == 'Write':
            path = node.knob('file').getEvaluatedValue()
            dirName = os.path.dirname(path)
            if os.path.exists(dirName):
                for sequence in get_sequences(fullListdir(dirName)):
                    if os.path.basename(path).startswith(sequence.head()):
                        fullPath = sequence.format(r'%D%h%p%t').replace('\\', '/')
                        read = nuke.createNode('Read', 'file %s' % (fullPath))
                        read.setXpos(node.xpos())
                        read.setYpos(node.ypos() + 60)
                        read['file'].setValue(fullPath)
                        read['first'].setValue(int(sequence.start()))
                        read['last'].setValue(int(sequence.end()))
                        read['origfirst'].setValue(int(sequence.start()))
                        read['origlast'].setValue(int(sequence.end()))
                        read.knob('premultiplied').fromScript(selectedNodePremult)
                        if node.knob('colorspace'):
                            read['colorspace'].setValue(int(node['colorspace'].getValue())) 
                        yield read
            else:
                nuke.message("Directory Write points to does not exist")
        else:
            nuke.message("Select a Write Node") 


def createWriteDir():
    try:
        file = nuke.filename(nuke.thisNode())
    except:
        file = unicode(nuke.thisNode()['file'].getEvaluatedValue())
    try:
        dir = os.path.dirname(file)
        osdir = unicode(nuke.callbacks.filenameFilter(dir))
        
        if not os.path.exists(osdir):
            os.makedirs(osdir)
                
    except OSError:
        raise Exception('functions.createWriteDir: Error de Sistema Operativo.')
    except TypeError:
        raise Exception('functions.createWriteDir: El archivo no esta en Pipeline, no debeche estar guardado en una carpeta local.')


def browseFolder(nodes):
    for node in nodes:
        if node.knob("file"):
            f = os.path.dirname(node.knob("file").getEvaluatedValue())
            if os.path.exists(f):
                os.startfile(f)
        else:
            nuke.message("Recatate guachin!!")


def autoCropEXR(nodes=None, root=None, override=False, outpath=None):
    if not nodes:
        nodes = nuke.selectedNodes("Read")

    cropped_nodes = []

    for n in nodes:
        dir, base = os.path.split(n['file'].value())
        file, ext = os.path.splitext(base)

        if override:
            newFileName = n['file'].value()

        elif root:
            root = root.replace('\\', '/')
            if outpath:
                newdir = outpath
            else:
                newdir = dir.replace('\\', '/').replace(root, '%s_crop' % root)

            newFileName = os.path.join(newdir, file).replace('\\', '/')

        else:
            newFileName = '%s_crop/%s' % (dir, file)

        if ext in media.image_formats:
            newFileName += ext
        else:
            newFileName += '.####' + ext

        w = nuke.createNode('Write', inpanel=False)
        w['channels'].setValue(n.channels()[0].split('.')[0])
        #w['colorspace'].setValue('1.0')
        w['file'].setValue(newFileName.replace(base, file + '.exr'))
        w['file_type'].setValue("exr")
        w['datatype'].setValue("16 bit half")
        w['compression'].setValue("Zip (16 scanlines)")
        w['autocrop'].setValue(True)
        w['beforeRender'].setValue("createWriteDir()")
        w.setInput(0, n)

        cropped_nodes.append([n, w])

    return cropped_nodes


def checkLocalFiles():
    tn = nuke.thisNode()
    if "local_present" in tn.knobs():
        if tn.hasError():
            tn['local_present'].setValue('<font color="#FF3333" font size="5" style="font-weight:bold;">Rendered files are NOT present</font>')
        else:
            tn['local_present'].setValue('<FONT COLOR="#99FF66" style="font-style:italic;" font size="4">Rendered files are present</font>')


def get_free_space_mb(folder):
    if sys.platform == 'win32':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return str(free_bytes.value/1024/1024/1024)
    else:
        st = os.statvfs(folder)
        return str(st.f_bavail * st.f_frsize/1024/1024/1024)


def checkCacheSize():
    ev = os.environ['NUKE_TEMP_DIR']
    cs = get_free_space_mb(ev)
    tn = nuke.thisNode()
    if "cache_size" in tn.knobs():
        if float(cs)<30:
            tn['cache_size'].setValue('<FONT COLOR="#FF0000" font size="4">There is only</font> <font color="#FF3333" font size="5" style="font-weight:bold;">%s GB</font> <FONT COLOR="#FF0000" font size="4">left for cache!!!</font>' % cs)
        else:
            tn['cache_size'].setValue('<FONT COLOR="#99FF66" font size="3">There is</font> <font color="#CCFF66" font size="3" style="font-weight:bold;">%s GB</font> <FONT COLOR="#99FF66" font size="3">left for cache</font>' % cs)


def allRecursiveNodes():
    for node in nuke.allNodes():
        if hasattr(node, 'begin'):
            node.begin()
            for data in allRecursiveNodes():
                yield data
            node.end()

        yield node


def allRecursiveNodes2():
    nodes = nuke.allNodes()
    dropped = []

    while nodes:
        node = nodes.pop()
        if hasattr(node, 'begin'):
            node.begin()
            nodes.extend(nuke.allNodes())
            node.end()

        if not node.name() in dropped:
            dropped.append(node.name())
            yield node


def nuke_filedialog(path, filter='*.*', default=None):
    global recentFootage
    
    try:
        if not default:
            if os.path.exists(userpref):
                with open(userpref, 'r') as fpref:
                    data = json.loads(fpref.read())
                recentFootage = data['recentFootage']
                path = recentFootage
    except:
        print "Error cargando recent"
        
    title = 'Get Footage "%s""' % path
    files = nuke.getClipname(title, filter, default=path, multiple=True)
    for filename in files or []:
        target, ext = os.path.splitext(filename.replace('\\', '/'))
        try:
            seq = ext[ext.index(' ')+1:].split('-')
            if seq:
                seq = map(int, seq)
            ext = ext[:ext.find(' ')]
        except:
            seq = None

        recentFootage = target + ext
        
        with open(userpref, 'w') as f:
            f.write(json.dumps({'recentFootage': recentFootage}))
            
        yield target + ext, seq


def nuke_autofix_paths():
    fixes = {}

    for node in allRecursiveNodes():
        for knob in node.knobs():
            if knob in ['file', 'vfield_file']:
                path = node[knob].value()
                if path and not path.startswith('[python'):
                    try:
                        newpath = autofix_path(path, nuke_filedialog)
                        if newpath:
                            node[knob].setValue(newpath)
                            print 'Source: %s\nTarget: %s' % (path, newpath)
                            fixes[node.name()] = '\tSource: %s\n\tTarget: %s\n' % (path, newpath)
                    except:
                        print "No se aplico fix en el nodo: %s" % node.name()

    if fixes:
        text = ''
        for node, msg in fixes.items():
            text += '%s\n%s' % (node, msg)
    else:
        text = 'No se encontraron paths erroneos.'

    nuke.message(text)


def get_user_name():
    root_knobs = [knob.name() for knob in nuke.root().allKnobs()]
    
    if not 'user' in root_knobs:
        user_knob = nuke.String_Knob('user')
        nuke.root().addKnob(user_knob)
    
    return nuke.root()['user'].value()


def set_user_name():
    filename = os.path.basename(nuke.root().name())
    if not filename.startswith('template'):
        nuke.root()['user'].setValue(os.environ['USERNAME'])


def save_nuke(path):
    if not os.path.exists(path):
        nuke.scriptSaveAs(path)
    else:
        nuke.message("No se pueden pisar versionados", path)


def save_versioned():
    try:
        filename = nuke.scriptName()
    except:
        filename = nuke.getFilename('Save As script', '*.nk')

    SaveVersion_Publish(filename, save_nuke)


if __name__ == '__main__':
    path = r'Z:\INTERNO\MEDIA\disney\jungle_nest_01\EP10\ESC17\GFX_JN_Y01_EP10_ESC17_10\nuke\lowres'
    versions = [d for d in os.listdir(path) if os.path.isdir(path + '/' + d) and d.lower().startswith('v') and os.listdir(path + '/' + d)]
    print versions
    old_dir = max(versions)
    print old_dir

    #parsed = get_data_from_xml(r'Z:\INTERNO\MEDIA\disney\jungle_nest_01\EP10\ESC13\JN_Y01_EP10_ESC13.xml')
    #for shot in shots_with_spaces(parsed, 'ESC13'):
    #    print shot.get('name')

    #print load_python_modules()
