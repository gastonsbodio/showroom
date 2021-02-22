#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# Author: Leandro Inocencio aka Cesio (cesio.arg@gmail.com)
# Collaboration & Maintenance. Updates, new Features: Gaston Sbodio (gastonsbodio@gmail.com)


# TODO 
# integrar el pyseq para controlar los archivos de media
# Pasar Los diccionarios de shots a objectos con magic methods bien piolas
# Que los cambios en la tabla se reflejen en RAMON cuando se updatee

"""El modulo de ConformMedia gestiona la ingesta de planos que son dejados en la carpeta *Z:/In/* por la isla de edición junto con el .XML que contiene toda la metadata. La forma de detectar que un plano de la edición tiene un plano con GFX es poniendole un efecto de texto con una nomenclatura (:ref:`nomenclatura`) que es interpretada por el script sacando información util para poder armar la estructura de carpetas.

El box desplegable de **Nomenclatura** permite elegir la convención adoptada por **edición** o por **cámara**, generalmente se usa la convención de **edición**, en caso de que no funcione se puede usar la de **cámara**.

"""

from __init__ import *
from urllib import urlopen
from subprocess import Popen
from functools import partial
from datetime import datetime, date
from collections import OrderedDict

try:    # Nuke < 11
    from PySide.QtCore import *
    from PySide.QtGui import *
except: # Nuke > 11
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

from lasp.recent import Recent
from lasp.qt import load_ui
from lasp.tactic.Xmlparser import NoLabels, get_data_from_xml, get_mov, NoRules
from lasp.tactic.extractor import Extractor, get_info_from_media
from lasp.packages.timecode import Timecode, ffmpeg_fmt
from lasp.tactic.ConformMedia.checkNomencla import CheckNomencla
from lasp.tactic.sobjects import *                                                

import re
import os
import stat
import json
import time
import locale
import shutil
import httplib
import hashlib
import xmlrpclib
import lasp.qt as qt
import lasp.packages.pyseq as pyseq
import lasp.tactic.Xmlparser as xmlparser
import lasp.tactic.extractor as extractor
import lasp.packages.timecode as tc         
import lasp.tactic.media as media            
import lasp.tactic.sobjects as sobjects
import metadata_module as metadata_generator

reload(extractor)
reload(xmlparser)
reload(qt)
reload(tc)
reload(sobjects)

#Variable a modificar donde se localiza ffmpeg para Halide------------------------------------------------------------
#ffmpeg_dir = "C:/ffmpeg/ffmpeg-64.exe"
ffmpeg_dir = "Z:/INTERNO/TOOLS/cmdtools/ffmpeg/bin/ffmpeg.exe"
halideExtractor_dir = "Z:/INTERNO/TOOLS/cmdtools/Halide/HalideExtractor00.exe"



Status = {'fail': {'color':QColor(150, 0 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'media_ok': {'color':QColor(0, 200 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00004'},
              'target_ok': {'color':QColor(0, 150, 100), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00004'},
              'source_ok': {'color':QColor(200, 100, 100), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00002'},
              'missing_target_frames': {'color':QColor(200, 200 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'missing_target_movies': {'color':QColor(200, 200 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'missing_source_frames': {'color':QColor(150, 0 ,150), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'missing_source_movies': {'color':QColor(150, 0 ,150), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'no_source': {'color':QColor(150, 150 ,150), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00002'},
              'in_process': {'color':QColor(0, 0 ,150), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00008'},
              'fail_proxy': {'color':QColor(150, 0 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00005'},
              'unknown': {'color':QColor(0, 0 ,0), 'tipo_media':'TIPO_ESTADO_DE_MEDIA00002'}}


isla_in_paths = {'file://localhost/Volumes/xs_lasp/in':'Z:/in', 
                         'file://localhost/Volumes/xs_lasp': 'Z:',
                         'file://localhost/Volumes/xs_ingesta/LASP/in':'Z:', 
                         'file://localhost/Volumes/JungleNestIn':'Z:/in/JungleNestIn',
                         'file://localhost/Volumes/JrExpressIn':'Z:/in/JrExpressIn'}


Columns = OrderedDict()
Columns['slot'] = {'label': 'Slot', 'order': 0, 'ui':None}
Columns['image'] = {'label': 'Thumbnail', 'order': 1, 'ui':None}
Columns['name'] = {'label': 'Name', 'order': 2, 'ui':None}
Columns['start_frame'] = {'label': 'Start', 'order': 3, 'ui':None}
Columns['end_frame'] = {'label': 'End', 'order': 4, 'ui':None}
Columns['handler_in'] = {'label': 'Handler In', 'order': 5, 'ui':None}
Columns['handler_out'] = {'label': 'Handler Out', 'order': 6, 'ui':None}
Columns['ext'] = {'label': 'Extension', 'order': 7, 'ui':None}
Columns['status'] = {'label': 'Status', 'order': 8, 'ui':None}
Columns['proxy'] = {'label': 'Proxy', 'order': 9, 'ui':None}
Columns['ramon'] = {'label': 'Ramon', 'order': 10, 'ui':None}
Columns['export_date'] = {'label': 'Date', 'order': 11, 'ui':None}


XmlMatch = {'frame_in':'handler_in',
                   'frame_out': 'handler_out',
                   'camara_velocidad': 'fps',
                   'tc_frame_start': 'start_frame',
                   'tc_frame_end': 'end_frame'}


def columns_label():
    labels = []
    for key, value in Columns.items():
        labels.append(value['label'])
    return labels


def get_name_multi(path, name, index):
    """Cuando un shot esta compuesto por multiples clips (Foreground, Background, Matte) con el nombre del Shot y para diferenciar el footage se le agrega una letra al final (A, B, C, etc)
    
    :param str path: Ruta del footage
    
    :param str name: Nombre del Shot
    
    :param int index: El indice que es transformado despues en letra.
    """

    subname = re.findall('(.*?)(A?B?C?D?E?F?G?H?I?J?K?$)', name)[0][0]
    dirname, basename = os.path.split(path)
    filename = basename[:basename.index('.')]
    rest = basename[basename.index('.'):]
    return (dirname + '/' + subname + chr(65 + index) + rest).replace('\\', '/')


def add(self):
    self.setValue(self.value() + 1)


class ImagePopup():
    """Funcion que genera un popup con una imagen
    
    :param str bitmap: Filename de la imagen que se va a ver en el popup.
    
    :param int w: Ancho del popup.
    
    :param int h: Alto del popup.
    """
    def __init__(self, bitmap, w=640, h=360):
        self.image = QLabel()
        self.image.show()
        self.image.setScaledContents(True)
        pixmap = QPixmap(bitmap)
        self.image.setPixmap(pixmap)
        self.image.resize(w, h)


class LoadShotData(QThread):
    """Esta clase carga la informacion de los shots que se extrae de los XML de edición abriendo un nuevo QThread. Devuelve cada shot en la señal **LoadedShots** como un diccionario. 
    
    :param parsed_files: Lista de parseadores tipo :class:`Xmlparser.Scratch` o :class:`Xmlparser.FinalCut`.
    
    :param digicuts: Lista de diccionarios con información sobre archivos .MOV de donde se extraen frames para usarlos de preview. Ver en :func:`extractor.Extractor.get_info_from_media`
    """
    
    ConnectCombo = Signal(bool)
    LoadedShots = Signal(dict)
    StatusMessage = Signal(str)
    nomenclaError = Signal(list)

    def __init__(self, parsed_files=[], digicuts=[]):
        QThread.__init__(self)
        self.files = parsed_files
        self.digicuts = digicuts
        self.searchMOVs = digicuts is []

    def __del__(self):
        self.wait()

    def run(self):
        shots = []
        
        try:
            for parsed in self.files:
                self.ConnectCombo.emit(False)

                for shot in parsed.shots:
                    if shot:
                        self.StatusMessage.emit('Shot:%s, Start:%s, End:%s, Seq:%s' % (shot['name'], shot['start_frame'], shot['end_frame'], shot['sequence']))
                        self.LoadedShots.emit(shot)
                        shots.append(shots)

                if self.searchMOVs:
                    digipath = os.path.splitext(parsed.filename)[0] + '.mov'
                    if os.path.exists(digipath):
                        info = get_info_from_media(digipath)
                        self.digicuts.append(info)
                    else:
                        self.digicuts.append({'filepath': digipath})

            if shots == 0:
                self.StatusMessage.emit('No se encontraron Shots en el XML.' % (len(shots)))
                
            elif shots == 1:
                self.StatusMessage.emit('%d Shot cargado' % (len(shots)))
                
            else:
                self.StatusMessage.emit('%d Shots cargados' % (len(shots)))
        
        except xmlparser.NoRules, e:
            self.nomenclaError.emit([e[1], self.files, self.digicuts])

            

class AddShotRow(QThread):
    """Esta clase envia un Signal **recibeData** con un diccionario que se vuelca en cada row de la tabla :class:`.ConformMedia.ui.shotsTable`. 
    
    :param shot: Diccionario con data del shot, el cual permite definir parametros de los row :class:`.ConformMedia.ui.shotsTable`. 
    """
    recibeData = Signal(dict)

    def __init__(self, shot):
        QThread.__init__(self)
        self.shot = shot

    def __del__(self):
        self.wait()

    def run(self):
        data = {}
        for column, info in Columns.items():
            data[column] = {}
            if column == 'status' or column == 'proxy' or column == 'ramon':
                data[column]['value'] = 'unknown'
                data[column]['editable'] = False

            elif column == 'ext':
                data[column]['value'] = self.shot[column]
                data[column]['editable'] = False

            elif column == 'export_date':
                date = time.strftime('%d/%m/%Y\n%H:%M:%S', time.gmtime(self.shot.get('export_date')))
                data[column]['value'] = date
                data[column]['editable'] = False

            elif column == 'image':
                data[column]['value'] = 'No image'
                data[column]['editable'] = False

            else:
                data[column]['value'] = self.shot.get(column)

        self.recibeData.emit(data)


class LoadImageFromUrl(QThread):
    """Esta clase envia un Signal **recibeImage** con un bitmap que se inserta en un QLabel. 
    
    :param url: Direccion URL donde se encuentra la imagen.
    
    :param w: Ancho de la imagen
    
    :param h: Alto de la imagen.
    """
    recibeImage = Signal(dict)

    def __init__(self, url, w, h):
        QThread.__init__(self)
        self.url = url
        self.w = w
        self.h = h

    def __del__(self):
        self.wait()

    def run(self):
        try:
            if self.url:
                data = urlopen(self.url).read()
                self.recibeImage.emit(data)

        except IOError, e:
            print 'LoadImageFromUrl: %s' % unicode(e)


class GetProjects(QThread):
    """Esta clase envia un Signal **recibeProjects** con un objeto tipo Projects, con todos los proyectos de Ramon, que no sean template o de sistema. 
    """

    recibeProjects = Signal(dict)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        self.recibeProjects.emit(Projects(filters=[('is_template', False), ('type_project', "!~",'system')]))


class MakeThumbnail(QThread):
    """Esta clase genera thumbnails de los digicuts en una carpeta temporal y emite tres Signal, **recibeThumbnail** con el path donde se encuentra la imagen, **recibeShot** lleva el objeto **shot** con el key *thumbnail* con el path de la imagen, **deSelectShot** avisa que el row se deselecione.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param get_source: Función que devuelve los filepaths de las sequencias de imagenes.
    
    :param digicuts: Lista de diccionarios con información sobre archivos .MOV de donde se extraen frames para usarlos de preview. Ver en :func:`extractor.get_info_from_media`
    
    :param size: Alto  y ancho de la imagen, en el formato "%sx%s" % (w, h).
    
    :param override: Si este argumento es True, el thumbnail generado sobreescribe a la imagen existente. 
    """
    
    recibeThumbnail = Signal(basestring)
    recibeShot = Signal(dict)
    deSelectShot = Signal(dict, bool)

    def __init__(self, shot, get_source, digicuts, size='320x180', override=False):
        QThread.__init__(self)
        self.shot = shot
        self.get_source = get_source
        self.digicuts = digicuts
        self.size = size
        self.override = override

    def __del__(self):
        self.wait()

    def run(self):
        """base = os.environ['TEMP']
        basePartes = base.split("\\")
        numBaseP = len(basePartes)
        nom = "___"
        for i, obj in enumerate(basePartes):
            if i < numBaseP - 1 :
                nom = nom  + obj + '/'
        nom = nom.split("___")[-1]
        outfile = nom + '/conform_thumbnail/' + self.shot.get('name') + '.jpg'"""
        #outfile = os.environ['TEMP'] + '/conform_thumbnail/' + self.shot.get('name') + '.jpg'
        outfile = os.environ['TEMP'] + '\\conform_thumbnail\\' + self.shot.get('name') + '.jpg'
        outfile = outfile.encode(locale.getpreferredencoding())        
        if self.override or not os.path.exists(outfile) or os.path.getmtime(outfile) < self.shot.get('export_date'):
            if self.shot['ext'] == '.ari' or self.shot['ext'] == '.exr':
                for item in self.get_source(self.shot):
                    item = item.encode(locale.getpreferredencoding())
                    if os.path.exists(item):
                        Extractor(item, outfile, size=self.size).extract()
                        break 

            elif self.shot['ext'] == '.mov' or self.shot['ext'] == '.MOV':
                medio = (self.shot['start_frame'] + self.shot['end_frame']) / 2
                try:
                    movinfo = get_mov(self.shot, self.digicuts)
                except tc.FrameRateError, e:
                    print 'Framerate error: El framerate (%s) del shot %s no es valido.' % (movinfo.get('fps'), self.shot['name'])
                    movinfo = None
                
                if movinfo and movinfo.get('fps'):
                    movfile = movinfo.get('filepath').encode(locale.getpreferredencoding())
                    numBlancos = len (movfile.split(" "))
                    if numBlancos >= 2:
                        #QMessageBox.warning(None, u' Error',  'Error, Usted dejó espacios en los nombres de directorios o archivos, arreglelo ATR !!!!')
                        print (" ****                                                                                                    *************")
                        print (" ****            Error, Usted dejó espacios en los nombres de directorios o archivos, arreglelo ATR !!!!     *********")
                        print (" ****                                                                                                    *************")
                    fps = movinfo.get('fps')
                    timecode = movinfo.get('timecode')
                    timemov = Timecode(fps, start_timecode=timecode)
                    timexml = Timecode(fps, frames=medio)
                    timeseq = Timecode(fps, self.shot['sequence_timecode'])
                    timemedio = timeseq + timexml - timemov
                    
                    if timemov.hrs < 1:
                        starttime = timexml.format(ffmpeg_fmt)     
                        
                    elif (timeseq + timexml).hrs < 1:
                        starttime = timexml.format(ffmpeg_fmt)

                    elif timecode and timemov.hrs < 3:
                        starttime = timemedio.format(ffmpeg_fmt)                     
                    else:
                        starttime = timexml.format(ffmpeg_fmt)
                    
                    try:
                        if movfile.split (".M")[-1]== "OV":
                            fileSinMOV = movfile.split (".MOV")[0]
                            movfile = fileSinMOV + ".mov"
                        for exe in Extractor(movfile, outfile, timecode=starttime, size=self.size, fps=fps).extract():
                            exe.wait()

                    except Exception, e:
                        print 'MakeThumbnail: %s' % unicode(e)
                        return
 
 
        if os.path.exists(outfile):
            self.shot['thumbnail'] = outfile
            self.recibeShot.emit(self.shot)
            self.recibeThumbnail.emit(outfile)
            self.deSelectShot.emit(self.shot, False)


class CheckShotStatus(QThread):
    """Esta clase checkea si el footage del shot esta completo o no existe en la carpeta donde se dosifica y emite una Signal **recibeShotStatus** con el status del Shot.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param source: Función que devuelve los filepaths de la ruta de origen, de las sequencias de imagenes del shot.
    
    :param target: Función que devuelve los filepaths de la ruta de destino, de las sequencias de imagenes del shot.
    
    :param newroot: Función que reemplaza el root *source* por el valor de :class:`ConformMedia.ui.sourceRoots`.
    """
    recibeShotStatus = Signal(dict)

    def __init__(self, shot, source, target, newroot):
        QThread.__init__(self)
        self.shot = shot
        self.source = source
        self.target = target
        self.newroot = newroot

    def __del__(self):
        self.wait()

    def check_missing_movies(self):
        """Revisa que todos los clips de un Shot existan y devuelve el estado del footage.

        :rtype: string
        """
        
        sources = []
        targets = []
        missing_source = 0
        
        for clip in self.shot['clips']:
            if clip.file and clip.file.pathurl:
                source = self.newroot(clip.file.pathurl)
                if os.path.exists(source):
                    if not source in sources:
                        sources.append((source, os.stat(source)))
                else:
                    missing_source += 1
        
        if missing_source > 0:
            return 'missing_source_movies'
            
        count_source = len(sources)
        if count_source == 0:
            return 'no_source'
            
        target_dir = os.path.dirname(list(self.target(self.shot))[0])
        
        if os.path.exists(target_dir):
            sizes_in_target = [(os.path.join(target_dir, f), os.stat(os.path.join(target_dir, f))) for f in os.listdir(target_dir)]

            while sources:
                fsource, source = sources.pop()
                for ftarget, target in sizes_in_target:
                    if target.st_size == source.st_size:
                        targets.append(ftarget)
                        break

            if count_source - len(targets) == 0:
                return 'media_ok'
            else:
                return 'missing_target_movies'
        else:
            return 'source_ok'

    def run(self):   # TODO usar pyseq para controlar los archivos.
        shot = self.shot
        if self.shot['ext'] == '.mov':
            try:
                shot['status'] = self.check_missing_movies()
            except:
                shot['status'] = 'fail'

            self.recibeShotStatus.emit(shot)
            return 

        try:
            shot['handler_in'] = int(shot['ui']['handler_in'].text())
            shot['handler_out'] = int(shot['ui']['handler_out'].text())
        except:
            pass

        try:
            source_files = list(self.source(shot))
        except CantResolvePath:
            try:
                print "Error in source."
                source_files = list(self.target(shot))  # HACK pedorro
            except CantResolvePath:
                shot['status'] = 'fail'
                self.recibeShotStatus.emit(shot)
                return

        try:
            target_files = list(self.target(shot))
        except (CantResolvePath, NoDestinationPath, NoChapters):
            target_files = source_files

        all_source = missing_source = len(source_files)
        
        if os.path.exists(os.path.dirname(source_files[0])):
            if source_files[0].endswith('.mov'):
                #no puedo printear el path del .mov cuando hay caracteres raros
                if os.path.exists(source_files[0]):
                    missing_source = 0
                else:
                    missing_source = all_source
            else:
                for file in source_files:
                    if os.path.exists(file):
                        missing_source -= 1

        try:
            if os.path.exists(os.path.dirname(target_files[0])):
                for file in target_files:
                    if os.path.exists(file):
                        missing_target -= 1

        except (CantResolvePath, NoDestinationPath, NoChapters):
            pass

        if missing_target == 0 and missing_source == 0:
            shot['status'] = 'media_ok'

        elif missing_target > 0 and missing_target < all_source:
            shot['status'] = 'missing_target_frames'

        elif missing_target == 0 and missing_source == all_source:
            shot['status'] = 'target_ok'

        elif missing_source == 0 and missing_target == all_source:
            shot['status'] = 'source_ok'

        elif missing_source == all_source:
            shot['status'] = 'no_source'

        elif missing_source > 0:
            shot['status'] = 'missing_source_frames'

        else:
            shot['status'] = 'unknown'

        self.recibeShotStatus.emit(shot)


class CheckShotProxy(QThread):
    """Esta clase checkea si el proxy del footage del shot esta completo o no existe en la carpeta donde se dosifica y emite una Signal **recibeShotProxy** con el status del proxy.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param source: Función que devuelve los filepaths de la ruta de origen, de las sequencias de imagenes del shot.
    """
    recibeShotProxy = Signal(basestring)

    def __init__(self, shot, source):
        QThread.__init__(self)
        self.shot = shot
        self.proxy_frames_from_shot = source

    def __del__(self):
        self.wait()

    def run(self):
        shot = self.shot
        try:
            found = []
            files_proxy = list(self.proxy_frames_from_shot(shot))

            total_files = len(files_proxy)

            if files_proxy and os.path.exists(os.path.dirname(files_proxy[0])):
                while files_proxy:
                    file = files_proxy.pop()
                    file = file[:file.rindex('.')] + '.jpg'
                    if os.path.exists(file):
                        found.append(file)

            if len(found) == total_files:
                shot['proxy'] = 'done'
            elif not found:
                shot['proxy'] = 'no_proxy' 
            elif len(found) < total_files:
                shot['proxy'] = '%d missing' % (total_files - len(found))

        except Exception, e:
            print 'CheckShotProxy: %s' % unicode(e)
            shot['proxy'] = 'fail'

        self.recibeShotProxy.emit(shot)


class CheckShotTable(QThread):
    """Esta clase gestiona todos los QThreads que se crean y se eliminan en ConformMedia, emite cinco Signal **adjust** ajusta el tamaño de la :class:`.ConformMedia.ui.shotsTable`, **StatusMessage** lleva un mensaje sobre el estado de los QThreads, **setProgressRange** setea el rango de :class:`.ConformMedia.ui.progress`, **CompleteTask** avisa cuando se finalizó un QThread, , **CompleteJobs** avisa cuando se finalizó todos los QThread,
    
    :param shot: Diccionario con informacion del Shot.
    
    :param source: Función que devuelve los filepaths de la ruta de origen, de las sequencias de imagenes del shot.
    """
    adjust = Signal()
    StatusMessage = Signal(str, int)
    setProgressRange = Signal(int, int)
    CompleteTask = Signal()
    CompleteJobs = Signal()

    def __init__(self):
        QThread.__init__(self)
        self.jobs = {}
        self.count_tasks = 0

    def __del__(self):
        self.wait()

    @property
    def all_tasks(self):
        count = 0
        for type_, jobs in self.jobs.items():
            for funct_name, tasks in jobs.items():
                if isinstance(tasks, list):
                    count += len(tasks)

        return count

    @property
    def no_check_tasks(self):
        count = 0
        for type_, jobs in self.jobs.items():
            if type_ != 'checks':
                for funct_name, tasks in jobs.items():
                    if isinstance(tasks, list):
                        count += len(tasks)

        return count

    def run(self):
        while True:
            self.msleep(250)

            if self.all_tasks == 0:
                self.CompleteJobs.emit()
                self.count_tasks = 0

            elif self.count_tasks < self.no_check_tasks:
                self.count_tasks = self.no_check_tasks
                self.setProgressRange.emit(1, self.count_tasks)

            for type_job, alltasks in self.jobs.items():
                for func_name, tasks in alltasks.items():
                    if isinstance(tasks, list):
                        for task in tasks:
                            if alltasks['max'] > alltasks['running'] and not task.isRunning() and not task.isFinished():
                                task.start()
                                self.jobs[type_job]['running'] += 1

                            elif task.isFinished():
                                self.jobs[type_job][func_name].remove(task)
                                self.jobs[type_job]['running'] -= 1
                                self.jobs[type_job]['finished'] += 1

                                if type_job != 'checks':
                                    self.CompleteTask.emit()

                        if not tasks:
                            self.jobs[type_job].pop(func_name)
                            self.adjust.emit()
                            self.jobs[type_job]['running'] = 0

                            if type_job != 'checks':
                                self.StatusMessage.emit('%d %s actions terminados' % (self.jobs[type_job]['finished'], type_job), 500)

                            self.jobs[type_job]['finished'] = 0


class CheckShotRamon(QThread):
    """Esta clase checkea si existe un Shot en Ramon y emite un Signal **recibeShotRamon** con el estado del Shot en Ramon. 
    
    :param shot: Diccionario con informacion del Shot.
    
    :param ramon_shot: Función que devuelve una lista de Shots en un proyecto.
    """
    recibeShotRamon = Signal(dict)

    def __init__(self, shot, ramon_shot):
        QThread.__init__(self)
        self.shot = shot
        self.ramon_shot = ramon_shot

    def __del__(self):
        self.wait()

    def run(self):
        shot = self.shot

        if not shot.get('project'):
            shot['ramon'] = 'No exists'
        else:
            if self.ramon_shot:
                shot['ramon'] = 'Done'
                '''
                self.ramon_shot.update_data()
                for ramon_attr, xml_attr in XmlMatch.items():
                    if str(shot.get(xml_attr)) != str(self.ramon_shot.data.get(ramon_attr)):
                        shot['ramon'] = 'Not Updated'
                        break
                else:
                    shot['ramon'] = 'Done'
                '''
            else:
                shot['ramon'] = 'No exists'

        self.recibeShotRamon.emit(shot)


class CopyShotMovie(QThread):
    """Esta clase copia si existe media en formato de video de Shot y emite un Signal **recibeShotRamon** con el estado del Shot en Ramon. 
    
    :param shot: Diccionario con informacion del Shot.
    
    :param ramon_shot: Función que devuelve una lista de Shots en un proyecto.
    """
    StatusMessage = Signal(str)
    In_Progress = Signal()
    MediaOk = Signal()
    Fail = Signal()
    status = None

    def __init__(self, shot, newroot, target_file, checkMD5):
        QThread.__init__(self)
        self.shot = shot
        self.target_file = target_file
        self.newRoot = newroot
        self.checkMD5 = checkMD5

    def __del__(self):
        self.wait()

    def movie_count(self, clips):
        movies = []
        for clip in clips:
            if clip.file and clip.file.pathurl and clip.file.extension in media.movie_formats:
                if not clip.file.pathurl in movies:
                    movies.append(clip.file.pathurl)

        return len(movies)

    @property
    def clips(self):
        clips = []
        for clip in self.shot['clips']:
            if clip.file and not clip.file.pathurl in clips:
                yield clip

    def run(self):
        self.In_Progress.emit()
        self.StatusMessage.emit('Copying Movie Footage from shot %s' % self.shot.get('name'))
        targets = []
        multi = False
        fail = False

        try:
            if self.movie_count(self.shot['clips']) > 1:
                print "%s Contiene multiples Movie clips!!" % self.shot['name']
                multi = True

            for index, clip in enumerate(self.clips):
                source_file = self.newRoot(clip.file.pathurl)
                target_dir = os.path.dirname(self.target_file(self.shot))



                if not clip.file.extension in media.media_formats:
                    if not clip.file.basename:
                        print "Clip Filename no existe."
                        continue

                    target_file = os.path.join(target_dir, clip.file.basename)

                # Agregado por Eduardo - Identifica videos en 4k
                elif self.digicutIs4K(str(source_file)):
                    index2 = target_dir.find('in') + 2
                    target_dir = os.path.normpath(target_dir[:index2] + '/4k' + target_dir[index2:])
                    target_file = self.target_file(self.shot)
                    base, file = os.path.split(target_file)
                    target_file = os.path.join(target_dir, file)

                else:
                    target_file = self.target_file(self.shot)


                if not ConformMedia.are_same(source_file, target_file, self.checkMD5):
                    if not os.path.isdir(target_dir):
                        os.makedirs(target_dir)

                    try:
                        if multi:
                            target_file = get_name_multi(target_file, self.shot.get('name'), index)

                        if not target_file in targets:
                            shutil.copy2(source_file, target_file)
                            targets.append(target_file)
                            
                    except Exception, e:
                        print 'CopyShotMovie: %s' % unicode(e)
                        self.StatusMessage.emit('Error trying copying Footage from shot %s' % self.shot.get('name'))
                        self.status = 'fail'
                        self.Fail.emit()
                        fail = True

        except Exception, e:
            print 'CopyShotMovie: %s' % unicode(e)
            self.status = 'fail'
            return self.Fail.emit()

        if not fail:
            self.status = 'done'
            self.MediaOk.emit()


#Agregado por Eduardo - Identifica videos en 4k
    def digicutIs4K(self, digicut):
        """Agregado para corroborar si el digicut es 4k"""
        image_width = metadata_generator.metadata_for(digicut)
        if image_width:
            key, data = str(image_width).split(":")
            pixels = data.split(" ")
            pixels = int(pixels[1])
            if pixels <= 3900:
                return False
            else:
                return True


class CopyShotFootage(QThread):
    """Esta clase copia si existe media en formato de secuencias de imagenes y emite cuatro Signals **StatusMessage** con el estado del proceso, **In_Progress** envia estado en progreso. **MediaOk** envia estado media completa y en su lugar, **Fail** envia estado fallado.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param newroot: Función que reemplaza el root *source* por el valor de :class:`ConformMedia.ui.sourceRoots`.
    
    :param target: Función que devuelve los filepaths de la ruta de destino, de las sequencias de imagenes del shot.
    
    :param checkMD5: Activa el checkeo de MD5 en la comparacion de archivos.
    """
    StatusMessage = Signal(str)
    In_Progress = Signal()
    MediaOk = Signal()
    Fail = Signal()
    status = None

    def __init__(self, shot, newroot, target, checkMD5):
        QThread.__init__(self)
        self.shot = shot
        self.target = target
        self.newRoot = newroot
        self.checkMD5 = checkMD5

    def __del__(self):
        self.wait()

    def run(self):
        self.In_Progress.emit()
        self.StatusMessage.emit('Copying Footage from shot %s' % self.shot.get('name'))
        targets = []
        multi = False
        fail = False

        try:
            if self.movie_count(self.shot['clips']) > 1:
                print "%s Contiene multiples Movie clips!!" % self.shot['name']
                multi = True

            for index, clip in enumerate(self.clips):
                source_file = self.newRoot(clip.file.pathurl)
                target_dir = os.path.dirname(self.target(self.shot))

                if not clip.file.extension in media.media_formats:
                    if not clip.file.basename:
                        print "Clip Filename no existe."
                        continue

                    target = os.path.join(target_dir, clip.file.basename)
                else:
                    target = self.target(self.shot)

                if not ConformMedia.are_same(source_file, target, self.checkMD5):
                    if not os.path.isdir(target_dir):
                        os.makedirs(target_dir)

                    try:
                        if multi:
                            target = get_name_multi(target, self.shot.get('name'), index)

                        if not target in targets:
                            shutil.copy2(source_file, target)
                            targets.append(target)
                            
                    except Exception, e:
                        print 'CopyShotMovie: %s' % unicode(e)
                        self.StatusMessage.emit('Error trying copying Footage from shot %s' % self.shot.get('name'))
                        self.status = 'fail'
                        self.Fail.emit()
                        fail = True

        except Exception, e:
            print 'CopyShotMovie: %s' % unicode(e)
            self.status = 'fail'
            return self.Fail.emit()

        if not fail:
            self.status = 'done'
            self.MediaOk.emit()
        

class InsertShotRamon(QThread):
    """Esta clase crea en Ramon el SObject Shot, y su jeraquia Secuencias, Episodios, emite tres Signals **StatusMessage**, **CheckShotStatus**, **deSelectShot**
    
    :param shot: Diccionario con informacion del Shot.
    
    :param tactic_shots: Función que devuelve una lista de Shots en un proyecto.
    
    :param replacePreview: Si es True, reemplaza la imagen de preview existente en Ramon por la que se genero localmente.
    """
    StatusMessage = Signal(str, int)
    CheckShotStatus = Signal(dict)
    deSelectShot = Signal(dict, bool)

    def __init__(self, shot, tactic_shots, replacePreview):
        QThread.__init__(self)
        self.tactic_shots = tactic_shots
        self.shot = shot
        self.replacePreview = replacePreview

    def run(self):
        for current in self.tactic_shots(self.shot['project']).from_name(self.shot['name']):
            current.update_data()
            status = Status.get(self.shot['status']).get('tipo_media', 'TIPO_ESTADO_DE_MEDIA00005')
            current.tipo_estado_de_media_code = status
            current.start = self.shot['start_frame']
            current.end = self.shot['end_frame']
            current.frame_in = self.shot['handler_in']
            current.frame_out = self.shot['handler_out']
            current.clips_id = self.shot.get('clips_id')
            self.StatusMessage.emit('Updating shot "%s" to Ramon.' % self.shot['name'], 500)
            current.update()
            if not current.thumbnail and 'thumbnail' in self.shot or self.replacePreview:
                current.add_preview(self.shot['thumbnail'])

            break
        else:
            self.insert_tactic_data(self.shot)

        self.CheckShotStatus.emit(self.shot)
        self.deSelectShot.emit(self.shot, False)

    def insert_tactic_data(self, shot):
        self.StatusMessage.emit('Add shot "%s" to Ramon.' % (shot['name']), 500)

        chapter = {}
        sequence = None

        if shot.get('episodio'):
            chapters = Episodios()
            if not chapters.name_in(shot.get('episodio')):
                chapter = chapters.insert({'name': shot['episodio']})
            else:
                for chapter in chapters.from_name(shot['episodio']):
                    chapter = chapter.data
                    break

        if shot.get('sequence'):
            sequences = Sequences()

            if not sequences.name_in(shot.get('sequence')):
                if chapter:
                    sequence = sequences.insert({'name': shot['sequence'], 'episodios_code': chapter['code']})
                else:
                    sequence = sequences.insert({'name': shot['sequence']})
            else:
                for sequence in sequences.from_name(shot.get('sequence')):
                    if sequence.episodios_code == chapter.get('code', None):
                        sequence = sequence.data
                        break
                else:
                    if chapter:
                        sequence = sequences.insert({'name': shot['sequence'], 'episodios_code': chapter['code']})
                    else:
                        sequence = sequences.insert({'name': shot['sequence']})

        data = {}
        data['name'] = shot['name']

        if sequence:
            data['secuencias_code'] = sequence['code']
            
        data['tipo_estado_de_media_code'] = Status.get(shot['status']).get('tipo_media', 'TIPO_ESTADO_DE_MEDIA00005')
        data['frame_in'] = shot['handler_in']
        data['frame_out'] = shot['handler_out']
        data['camara_velocidad'] = shot['fps']
        data['tc_frame_start'] = shot['start_frame']
        data['tc_frame_end'] = shot['end_frame']
        data['clips_id'] = shot.get('clips_id')

        new_shot = SObject(self.tactic_shots(shot['project']).insert(data), shot['project'])

        if 'thumbnail' in shot:
            new_shot.add_preview(shot['thumbnail'])

        self.StatusMessage.emit('Shot "%s" added to Ramon.' % (shot['name']), 500)


class MakeProxy(QThread):
    """Esta clase genera proxys del footage de un shot. y emite cuatro Signal **In_Progress** avisa que esta en proceso, **Done** avisa que termino bien, **Fail** avisa que no termino el proceso, **StatusMessage** envia un mensaje de status.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param new_root: Función que reemplaza el root *source* por el valor de :class:`ConformMedia.ui.sourceRoots`.
    
    :param target: Función que devuelve los filepaths de la ruta de estino, de las sequencias de imagenes del shot.
        
    :param digicuts: Lista de diccionarios con información sobre archivos .MOV de donde se extraen frames para usarlos de preview. Ver en :func:`extractor.get_info_from_media`
        
    :param size: Alto  y ancho de la imagen, en el formato "%sx%s" % (w, h).
    """
    In_Progress = Signal(dict)
    Done = Signal(dict)
    Fail = Signal(dict)
    StatusMessage = Signal(str)

    def __init__(self, shot, new_root, target, digicuts=None, size=None):
        QThread.__init__(self)
        self.shot = shot
        vformat = shot['video_format']
        if not size:
            self.size = '%sx%s' % (vformat.width/2,vformat.height/2)
        self.target_proxy_file = target
        self.newRoot = new_root
        self.digicuts = digicuts
        
    def __del__(self):
        self.wait()

    def extract_audio(self):
        """Extrae el audio de un archivo de video"""
        self.StatusMessage.emit('Extract Audio from shot %s' % self.shot.get('name'))

        infile = self.digicuts[0]['filepath']
        fps = self.digicuts[0]['fps']
        frame_in = self.shot['start_frame']
        frame_out = self.shot['end_frame']
        start = 1
        starttime = Timecode(fps, frames=frame_in).format(ffmpeg_fmt)
        outdir = os.path.dirname(self.target_proxy_file(self.shot)).replace(r'\proxy', '')
        dirname, filename = os.path.split(infile)
        name, ext = os.path.splitext(filename)
        seqaudiofile = '%s\%s.aac' % (dirname, name)
        audiofile = r'%s\audio\%s.aac' % (outdir, self.shot['name'])
        proxyfile = r'%s\proxy\%s.%%0%dd.jpg' % (outdir, self.shot['name'], len(str(self.shot['end_frame'])) + 1)
        
        duration = frame_out - frame_in
        Extractor(infile, proxyfile, timecode=starttime, start_frame=start, duration=duration, fps=fps, size=self.size).extract()
        
        if not os.path.exists(seqaudiofile):
            print "Generando Audio de Animatic"
            Extractor(infile, seqaudiofile, timecode=starttime, start_frame=start, duration=0, fps=fps, size=self.size).extract()
            
        Extractor(seqaudiofile, audiofile, timecode=starttime, start_frame=start, duration=duration, fps=fps, size=self.size).extract()
        
    def run(self):
        self.shot['proxy'] = 'In Progress'
        self.In_Progress.emit(self.shot)

        for index, clip in enumerate(self.shot['clips']):
            if clip.file and clip.file.pathurl:
                if clip.file.extension == '.ari':
                    try:
                        infile = self.newRoot(clip.file.pathurl)
                        basename = os.path.basename(infile)
                        soloname = os.path.splitext(basename)[0]
                        outpath = os.path.join(os.path.dirname(infile), 'proxy')
                        try:
                            start = int(os.path.splitext(soloname)[1][1:])
                        except (ValueError, TypeError):
                            start = 0

                        outfile = os.path.join(outpath, soloname) + '.jpg'
                        Extractor(infile, outfile, start_frame=start, size=self.size).extract()
                    except Exception, e:
                        print 'MakeProxy: %s' % unicode(e)
                        return self.error()

                elif clip.file.extension == '.mov':
                    try:
                        self.StatusMessage.emit('Making Proxy from shot %s' % self.shot.get('name'))

                        infile = self.newRoot(clip.file.pathurl)
                        if os.path.exists(infile):
                            frame_in = clip.In
                            frame_out = clip.Out
                        else:
                            #self.extract_audio()
                            raise Exception('No in file')

                        start = 1
                        starttime = Timecode(clip.fps, frames=frame_in).format(ffmpeg_fmt)
                        outfile = os.path.splitext(self.target_proxy_file(self.shot))[0] + '.%%0%dd.jpg' % (len(str(self.shot['end_frame'])) + 1)
                        outfile = get_name_multi(outfile, self.shot.get('name'), index)
                        #Extractor(infile, outfile, timecode=starttime, start_frame=start, duration=duration, fps=fps, size=self.size).extract()
                        #Extractor(infile, outfile, timecode=starttime, duration=clip.duration, fps=clip.fps, size=self.size).extract()
                        Extractor(infile, outfile, duration=clip.duration, start_frame=start, fps=clip.fps, size=self.size).extract()

                    except Exception, e:
                        print 'MakeProxy: %s' % unicode(e)
                        return self.error()
                        
            else:
                self.extract_audio()
                break

        self.shot['proxy'] = 'Done'
        self.Done.emit(self.shot)

    def error(self):
        self.StatusMessage.emit('Error trying making Proxy from shot %s' % self.shot.get('name'))
        self.shot['proxy'] = 'Fail'
        self.Fail.emit(self.shot)


class ExtractShotFootage(QThread):
    """Esta clase genera proxys del footage de un shot. y emite cuatro Signal **In_Progress** avisa que esta en proceso, **MediaOk** avisa que termino bien, **Fail** avisa que no termino el proceso, **StatusMessage** envia un mensaje de status.
    
    :param shot: Diccionario con informacion del Shot.
    
    :param target: Función que devuelve los filepaths de la ruta de estino, de las sequencias de imagenes del shot.
        
    :param toImages: Si es True transforma el footage en secuencias de imagenes
        
    :param toMovie: Si es True transforma el footage en una archivo de video.
    
    :param newroot: Función que reemplaza el root *source* por el valor de :class:`ConformMedia.ui.sourceRoots`.

    :param haride: Obtiene un .wav del digicut acotado entre el tiempo de inicio y el tiempo final del shot(Edu)

    """
    StatusMessage = Signal(str)
    In_Progress = Signal()
    MediaOk = Signal()
    Fail = Signal()

    def __init__(self, shot, target, toImages, toMovie, newroot, haride):
        QThread.__init__(self)
        self.shot = shot
        self.toImages = toImages
        self.toMovie = toMovie
        self.target = target
        self.newRoot = newroot
        self.haride = haride

    def __del__(self):
        self.wait()

    def run(self):
        self.In_Progress.emit()
        start = int(self.shot['start_frame']) - self.shot['handler_in']
        if start < 0:
            start = 0

        end = int(self.shot['end_frame']) + self.shot['handler_out']
        duration = end - start
        infile = self.newRoot(self.shot['file'])
        fps = get_info_from_media(infile)['fps']
        starttime = Timecode(str(fps), frames=start).format(ffmpeg_fmt)

        if self.toImages:
            try:
                self.StatusMessage.emit('Extracting Images from shot %s' % self.shot.get('name'))
                outfile = os.path.splitext(self.target(self.shot))[0] + '%04d.dpx'
                Extractor(infile, outfile, timecode=starttime, start_frame=start, duration=duration, fps=fps).extract()
            except Exception, e:
                print 'ExtractShotFootage to Images: %s' % unicode(e)
                self.Fail.emit()
                return

        elif self.toMovie:
            try:
                self.StatusMessage.emit('Extracting Movie from shot %s' % self.shot.get('name'))
                outfile = os.path.splitext(self.target(self.shot))[0] + '.mov'
                Extractor(infile, outfile, timecode=starttime, duration=duration, fps=fps).extract()
            except Exception, e:
                print 'ExtractShotFootage to Movie: %s' % unicode(e)
                self.Fail.emit()
                return

        self.MediaOk.emit()


class MyQComboBox(QComboBox):
    """Este QComboBox se le agrega el Signal **enterPressed** que se emite cada vez que se preciona Enter.
    """
    enterPressed = Signal(int)

    def __init__(self, *args):
        QComboBox.__init__(self, *args)
        self.setEnabled(False)
        self.setEditable(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

    def event(self, event):
        if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_Return):
            self.enterPressed.emit(self.currentIndex())
            return True

        return QComboBox.event(self, event)


class MyQTable(QTableWidget):
    """QTable que se le agrega la funcion de Drag&Drop con el Signal **Dropped**, ademas de seteos particuales de la tabla"""
    Dropped = Signal(list)

    def __init__(self, parent=None):
        super(MyQTable, self).__init__(parent)
        self.setAcceptDrops(True)
        #self.setSortingEnabled(True)    TODO: Se rompe todo si se activa, buscar solucion!!.
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setMinimumSectionSize(50)
        self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(unicode(url.toLocalFile()))
            self.Dropped.emit(links)
        else:
            event.ignore()

    def adjust(self):
        """Auto ajusta el tamaño de las columnas de la tabla"""
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)


class Filters(QWidget):
    """Esta clase es usada para filtrar los shots que se cargan del XML.
    
    :param tactic_shots: Función que devuelve una lista de Shots en un proyecto.
    """

    checkers = ['not_ramon_names', 'ramon_names', 'with_source', 'done_frames', 'missing_source_frames', 'missing_target_frames']

    def __init__(self, tactic_shots, parent=None):
        QWidget.__init__(self, parent)
        self.ui = load_ui(os.path.dirname(__file__) + '/FiltersDialog.ui', None)
        self.tactic_shots = tactic_shots
        self.connect_select_all()

    def toggle(self):
        """ Oculta o muestra la UI de filtro"""
        if self.ui.isVisible():
            self.ui.hide()
        else:
            self.ui.show()

    @property
    def select_all_state(self):
        """Devuelve si esta tildado el checker select_all"""
        return self.ui.select_all.isChecked()

    @staticmethod
    def meta_generate(func):
        """Esta función genera property apartir de los checkbox del .UI"""
        def meta(self, source):
            return eval(source)

        for widget in func.ui.__dict__:
            type = getattr(func.ui, widget).__class__.__name__
            if type == 'QCheckBox':
                code = 'self.ui.%s.checkState() == Qt.Checked' % widget
                setattr(Filters, widget, property(partial(meta, source=code)))

    def inRamonDB(self, shot):
        """Devuelve True si el shot se encuentra en Ramon
        
        :param shot: Diccionario con data del shot.
        """

        return self.tactic_shots(shot.get('project')).name_in(shot.get('name'))

    def only_filtered(self, shot):
        """Devuelve True si pasa el filtro, sino False
        
        :param shot: Diccionario con data del shot.
        """
        inDB = self.inRamonDB(shot)

        if inDB:
            if self.ramon_names:
                return True

        elif self.not_ramon_names:
                return True

        elif self.with_source:
            if shot['status'] == 'media_ok':
                return True

        elif self.done_frames:
            if shot['status'] == 'media_ok':
                return True

        elif self.done_frames:
            if shot['status'] == 'missing_source_frames':
                return True

        elif self.done_frames:
            if shot['status'] == 'missing_target_frames':
                return True

        return False

    def connect_select_all(self):
        """El QCheckBox select_all activa o desactiva los demas checkers. """
    
        for check in self.checkers:
            func = partial(eval('self.ui.%s.setChecked' % check))
            self.ui.select_all.toggled.connect(func)

    def connect_table(self, func):
        """Conecta los checkes a la tabla"""
        for check in self.checkers:
            eval('self.ui.%s.stateChanged.connect' % check)(func)


class ConformMedia(QMainWindow):
    """Clase principal que maneja la UI del ConformMedia"""
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.ui = load_ui(os.path.dirname(__file__) + '/ConformMedia.ui', None)
        self.filters = Filters(self.tactic_shots)
        Filters.meta_generate(self.filters)

        self.recent = Recent(self.ui)
        self.recent.load()
        
        self.shots = {}
        self.parsed_files = []
        self.digicuts = []
        self.construct = ''

        self.server = server
        
        setattr(self.ui.progress, 'add', partial(add, self.ui.progress))

        self.ui.shotsTable = MyQTable()
        self.ui.shotsTable.Dropped.connect(self.get_dropped)#Detecta cuando se dejan archivos en la tabla
        self.ui.verticalLayout_3.insertWidget(2, self.ui.shotsTable)
        self.ui.shotsTable.itemChanged.connect(self.change_value)
        self.ui.shotsTable.cellDoubleClicked.connect(self.view_thumbnail)

        self.ui.sourceRoots = MyQComboBox()
        self.ui.horizontalLayout_3.insertWidget(1, self.ui.sourceRoots)

        self.ui.replaceRoots.toggled.connect(self.enable_replace_roots)
        self.ui.browseXmlPushButton.clicked.connect(self.load_xmlfilename)
        self.ui.xmlfilename.currentIndexChanged.connect(self.load_xml_selected)

        self.ui.newSourceRoot.returnPressed.connect(self.checkAll)
        self.ui.sourceRoots.enterPressed.connect(self.cleanCombo)

        self.ui.browseDestination.clicked.connect(self.browseDestination)
        self.ui.copyPushButton.clicked.connect(self.copyShot)
        self.ui.allPushButton.clicked.connect(self.selectAll)
        self.ui.nonePushButton.clicked.connect(self.deselectAll)
        self.ui.togglePushButton.clicked.connect(self.toggleSel)
        self.ui.selFailedPushButton.clicked.connect(self.selFailed)
        self.ui.refreshButton.clicked.connect(self.refresh_table)
        self.ui.checkAllpushButton.clicked.connect(self.checkAll)
        self.ui.filtersButton.clicked.connect(self.filters.toggle)
        self.ui.browseNewRoot.clicked.connect(self.browseNewRoot)
        self.ui.destinationPath.currentIndexChanged.connect(self.checkAll)

        self.filters.connect_table(self.populate_shotTable)
        self.ui.shotsTable.customContextMenuRequested.connect(self.on_context_menu)
        self.popMenu = QMenu(self.ui.shotsTable)

        actions = [('Regenerate Thumbnail', self.regenerate_thumbnail),
                        ('Open source files dir', self.open_source_dir),
                        ('Open target files dir', self.open_target_dir),
                        ('Play source media', self.play_source_media),
                        ('Play target media', self.play_target_media),
                        ('Actualizar planos selecionados en Ramon', self.update_shot_ramon)]

        #IMPORTANTE!!! (Para que funcione 'Generate GFX sequence' hay que agregar el .xml y el .mov juntos al conformedia!)
        self.escenasMenu = self.popMenu.addMenu('Generate GFX sequence')
        
        for title, function in actions:
            action = QAction(title, self.ui.shotsTable)
            self.popMenu.addAction(action)
            action.triggered.connect(function)

        self.checkThreads = CheckShotTable()
        self.checkThreads.adjust.connect(self.ui.shotsTable.adjust)
        self.checkThreads.StatusMessage.connect(self.progress_message)
        self.checkThreads.setProgressRange.connect(self.ui.progress.setRange)
        self.checkThreads.CompleteTask.connect(self.ui.progress.add)
        self.checkThreads.CompleteJobs.connect(self.ui.progress.reset)
        self.checkThreads.start()
        
        self.ui.closeEvent = self.closeEvent
        
        '''
        self.get_projects = GetProjects()
        self.get_projects.recibeProjects.connect(self.populate_project_combo)
        self.get_projects.start()
        '''
        
    @staticmethod
    def meta_generate(func):
        """Esta función genera propertys apartir de los QCheckBox, QComboBox, QLineEdit y QSpinBox del .UI, para obtener los valores de los widgets de forma simple."""
        def meta(self, source):
            return eval(source)

        for widget in func.ui.__dict__:
            type = getattr(func.ui, widget).__class__.__name__
            if type == 'QCheckBox':
                source = 'self.ui.%s.checkState() == Qt.Checked' % widget
            elif type == 'QComboBox':
                source = 'unicode(self.ui.%s.currentText())' % widget
            elif type == 'QLineEdit':
                source = 'unicode(self.ui.%s.text())' % widget
            elif type == 'QSpinBox':
                source = 'int(self.ui.%s.value())' % widget
            else:
                continue

            setattr(ConformMedia, widget, property(partial(meta, source=source)))

    def populate_gfx_sequences(self):
        """Carga en el menu contextual las escenas del XML."""
        self.escenasMenu.clear()
        for escena in self.xml_escenas:
            action = QAction(escena, self.ui.shotsTable)
            self.escenasMenu.addAction(action)
            action.triggered.connect(partial(self.generate_gfx_sequence_nuke, escena))

    def on_context_menu(self, point):
        """Detecta si se hizo right-click en :class:`ConformMedia.ui.shotsTable`
        
        :param point: Coordenadas del mouse
        """
        if self.ui.shotsTable.currentRow() >= 0:
            self.popMenu.exec_(self.ui.shotsTable.mapToGlobal(point))

    def view_thumbnail(self, row, column):
        """Muestra el thumbnail del shot selecionado en un popup"""
        if column == Columns['image']['order']:
            shot = self.get_shot_from_row(row)
            self.ViewThumbnail = ImagePopup(shot['thumbnail'])

    def regenerate_thumbnail(self):
        """Genera nuevamente el thumbnail de un shot"""
        for shot in self.selectedShots:
            self.MakeThumbnail(shot, shot['ui']['image'], override=True)

    def open_source_dir(self):
        """Abre el explorador de windows con la ruta del footage del shot"""
        shot = self.get_shot_from_row(self.ui.shotsTable.currentRow())
        source_dir = os.path.dirname(self.newRoot(shot['file']))

        if os.path.exists(source_dir):
            Popen('explorer "%s"' % source_dir.replace('/', '\\'))
        else:
            QMessageBox.warning(self, 'Ruta inexistente', 'No existe el path.', QMessageBox.Ok)

    def open_target_dir(self):
        #  Gastoncho ...     esta funcionalidad esta adaptada para que ahora liste las tomas seleccionadas y la funcionalidad open target dir
        # se las ejecute a todas ellas y no solo a la current...
        selectedShots = list(self.selectedShots)
        """Abre el explorador de windows con la ruta de la media dosificada del shot"""
        for i, shot in enumerate(selectedShots):
            if i == 0:
                #shot = self.get_shot_from_row(self.ui.shotsTable.currentRow())
			try:
				target_dir = os.path.dirname(self.target_file(shot))
				if os.path.exists(target_dir):
					Popen('explorer "%s"' % target_dir.replace('/', '\\'))
				else:
					raise CantResolvePath

			except CantResolvePath:
				def create_dir(dialog, path):
					dialog.close()
					os.makedirs(path)
					Popen('explorer "%s"' % path.replace('/', '\\'))
					
				self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				self.buttonBox.setWindowTitle('La carpeta no existe')
				
				self.buttonBox.accepted.connect(partial(create_dir, self.buttonBox, target_dir))
				self.buttonBox.rejected.connect(self.buttonBox.close)
				self.buttonBox.show()
            else:
			    try:
				    target_dir = os.path.dirname(self.target_file(shot))
				    if os.path.exists(target_dir):
					    Popen('explorer "%s"' % target_dir.replace('/', '\\'))
				    else:
					    raise CantResolvePath
			    except CantResolvePath:
				    def create_dir2(path):
					    os.makedirs(path)
					    Popen('explorer "%s"' % path.replace('/', '\\'))
#				    self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
				    create_dir2(target_dir)

    def play_source_media(self):
        """No implementado """
        QMessageBox.warning(self, 'No funciona', 'Todavia no esta implemantado.', QMessageBox.Ok)
        return
        
        shot = self.get_shot_from_row(self.ui.shotsTable.currentRow())

        if shot['ext'] == '.ari':
            filename = shot['file'].replace('#' * 7, '%07d')
            cmd = pdplayer_app % (filename % (shot['startid']))
        else:
            cmd = djv_app % (self.newRoot(shot['file']))

        ret = Popen(cmd)

    def play_target_media(self):
        """No implementado """
        return
        shot = self.get_shot_from_row(self.ui.shotsTable.currentRow())

        if shot['ext'] == '.ari':
            try:
                filename = self.target_file(shot).replace('#' * 7, '%07d')
                cmd = pdplayer_app % (filename % (shot['startid']))
                ret = Popen(cmd)
            except:
                QMessageBox.warning(self, 'Ruta inexistente', 'No existe el path.', QMessageBox.Ok)
                
        if shot['ext'] == '.mov':
            command = ('open', '-a', 'Quicktime Player 7', self.target_file(shot))
            Popen(command, shell=True)
        
        else:
            QMessageBox.warning(self, 'No funciona', 'No se puede abrir el tipo de archivo.', QMessageBox.Ok)
        
    def update_shot_ramon(self):
        """Hace un update de los shots seleccionados en ramon"""
        total = len(list(self.selectedShots))
        current = 0

        for shot in self.selectedShots:
            current += 1
            self.InsertShotRamon(shot)

    def tactic_shots(self, project=None, update=False):
        """Devuelve todos los shots de un proyecto que esta en Ramon."""
        columns = ['code', 
                         'name',
                         'tipo_estado_de_media_code',
                         'frame_in', 
                         'frame_out', 
                         'camara_velocidad', 
                         'tc_frame_start', 
                         'tc_frame_end']

        if not project:
            project = self.server.project_code

        if not '_tactic_shots' in dir(self):
            self._tactic_shots = {}

        if not self._tactic_shots or not project in self._tactic_shots or update:
            self._tactic_shots[project] = Shots(columns=columns, project=project)

        return self._tactic_shots[project]

    def updateShot(self, shot):
        """ Actualiza un shot del diccionario self.shots donde se encuentran todos los shots que se cargaron del .XML"""
        self.shots[shot.get('name')] = shot

#Toma los archivos (XML y .mov) que se sueltan en la tabla y extrae sus datos**************************************************************************
    def get_dropped(self, files):
        """Esta funcion extrae la informacion de los archivos dropeados en la tabla. Solo se aceptan dos tipos de formatos .XML y .MOV. De los .MOVs se extrae informacion de fps, duracion, etc, de los .XML se parsea la informacion de los shots, y luego se         popula la tabla."""
        valids = []
        self.digicuts = []

        for file in files:
            if file.endswith('.MOV'):
                fileSinMOV = file.split (".MOV")[0] # Gastoncho, con este if quiero atajar la posibilidad que draguen archivos con la extension .MOV (con mayusculas)
                # ademas fuerzo a que se conviertan automaticamente los archivos externos en .mov (con minuscula ) para evitar tocar funcionalidad
                os.rename (file, fileSinMOV + ".mov")
            if file.lower().endswith('.mov'):
                numBlancos = len (file.split(" "))
                if numBlancos >= 2:
                    # Gastoncho
                    # Este if con esta advertencia es para advertir sobre espacios " " que se dejan en los nombres de archivos mov o xml y en sus carpetas contenedoras
                    QMessageBox.warning(None, u' Error',  'Error, Usted dejó espacios en los nombres de directorios o archivos, arreglelo ATR !!!!')
                self.digicuts.append(get_info_from_media(file))#Extrae info del .mov y guarda en 'digicuts'

            elif file.lower().endswith('.xml'):
                numBlancos = len (file.split(" "))
                if numBlancos >= 2:
                    QMessageBox.warning(None, u' Error',  'Error, Usted dejó espacios en los nombres de directorios o archivos, arreglelo ATR !!!!')
                s = open(file).read()
                s = s.replace('MOV', 'mov')
                f = open(file, 'w')
                f.write(s)
                f.close()
                valids.append(file)
            else:
                print "Error: %s, only XML and MOVs files." % file

        for f in valids:
            if f:
                self.parsed_files.append(get_data_from_xml(f, self.NomenclaBox, self.checkSnap))

        # self.parsed_files = [get_data_from_xml(f, self.NomenclaBox, self.checkSnap) for f in valids if f]# Obtiene los datos de los xml
        self.LoadShotData(self.parsed_files)
        
    def refresh_table(self):
        """Refresca la tabla con los parseos del .XML cargado en memoria."""
        if self.parsed_files:
            self.LoadShotData(self.parsed_files)
        
    def load_xmlfilename(self):
        """Abre un QFileDialog para poder seleccionar un .XML, luego parsealo y cargarlo a la Tabla. """
        recent_dir = os.path.dirname(self.xmlfilename)#el parametro en ningun momento existe
        files, filter = QFileDialog.getOpenFileNames(parent=None, caption='Select XML file with shots info',
                dir=recent_dir, filter='*.xml')

        self.parsed_files = [get_data_from_xml(f, self.NomenclaBox, self.checkSnap) for f in files if f]
        self.LoadShotData(self.parsed_files)

    def load_xml_selected(self, index_file):
        path_file = self.ui.xmlfilename.itemText(index_file)
        self.parsed_files = [get_data_from_xml(path_file, self.NomenclaBox, self.checkSnap)]
        self.LoadShotData(self.parsed_files)

    def make_table(self):
        """Seteo de inicializacion de la tabla"""
        table = self.ui.shotsTable
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(0)

        #Agrega columnas con sus nombres
        for index, column in enumerate(columns_label()):
            table.insertColumn(index)

        table.setHorizontalHeaderLabels(columns_label())
        self.ui.shotsTable.sortItems(2)

    def set_destinationPath(self):
        """Agrega el path de destino de la Media al QComboBox ui.destinationPath """
        self.ui.destinationPath.clear()
        self.ui.destinationPath.addItem(os.environ.get('MEDIA_PATH', 'Z:/INTERNO/MEDIA'))
        
		
    def populate_shotTable(self, shot):
        """Este método agrega un shot filtrado a la tabla de shots, y agrega los roots de la media a ui.sourceRoots
        
        :param shot: Diccionario con data del shot
        """
        self.shots[shot['name']] = shot

        if self.ui.project_combo.currentIndex() >= 0:
            self.set_combo_project(shot['project'])

        if self.filters.only_filtered(shot):
            self.AddShotRow(shot)

        self.populate_sourceRoots(shot)

    def add_shot_row(self, data):
        """Este método es llamado por el Signal **recibeData** del QThread :class:`AddShotRow` para agregar un shot a la :class:`ui.shotsTable`
        
        :param data: Diccionario con información para cargar a la tabla de Shots.
        """
        
        self.ui.shotsTable.setSortingEnabled(False)
        row = self.ui.shotsTable.rowCount()
        self.ui.shotsTable.insertRow(row)
        shot = self.shots[unicode(data['name']['value'])]

        for column in sorted(data.keys()):
            item = QTableWidgetItem()
            item.id_row = row
            item.setTextAlignment(Qt.AlignCenter)
            shot['ui'][column] = item
            item.setText(unicode(data[column].get('value')))

            if 'editable' in data[column] and not data[column].get('editable'):
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

            self.ui.shotsTable.setItem(row, Columns[column]['order'], item)

            if column == 'image':
                self.MakeThumbnail(shot, item)

            if column == 'status' and self.checkonline:
                self.CheckShotStatus(shot)

            elif column == 'proxy' and self.checkonline:
                self.CheckShotProxy(shot)

            elif column == 'ramon' and self.checkonline:
                if shot.get('project') and None:
                    for ramon_shot in self.tactic_shots(shot['project']).from_name(shot['name']):
                        self.CheckShotRamon(shot)
                        break
                    else:
                        data[column]['value'] = 'No exists'

        self.ui.shotsTable.setSortingEnabled(True)
        
        if row == 1:
            self.ui.shotsTable.adjust()
            self.populate_gfx_sequences()

    def LoadImagetoTable(self, table, item, w, h, bitmap):
        """Carga una imagen en un QLabel
        
        :param table: QTableWidget en la que se carga el QLabel
        
        :param item: QTableWidgetItem donde se va a cargar la imagen
        
        :param w: Ancho de la imagen
        
        :param h: Alto de la imagen
        
        :param bitmap: Mapa de bit de la imagen
        """
        try:
            if bitmap:
                row = item.row()
                column = item.column()
                image = QLabel()
                table.setCellWidget(row, column, image)
                table.setRowHeight(row, h)
                image.setScaledContents(True)
                
                if isinstance(bitmap, basestring):
                    pixmap = QPixmap(bitmap).scaled(w, h)
                else:
                    pixmap = QPixmap()
                    pixmap.loadFromData(bitmap).scaled(w, h)
            
                image.setPixmap(pixmap)
            else:
                raise Exception('No bitmap loaded')

        except Exception, e:
            print "ConformMedia.LoadImagetoTable: %s" % unicode(e)

            item = QTableWidgetItem()
            item.setText('No Image')
            table.setItem(row, column, item)
    
    @property
    def xml_escenas(self):
        """Property que devuelve todas las escenas que se encuentran los .XML parseados"""
        
        escenas = []
        for shot in self.shots.values():
            escena = shot["sequence"]
            if not escena in escenas:
                escenas.append(escena)
        print sorted(escenas)
        # for parsed in self.parsed_files:
        #     for escena in parsed.escenas.keys():
        #         if not escena in escenas:
        #             escenas.append(escena)
        # # print sorted(escenas)
        return sorted(escenas)

        
    def get_row_shot(self, shot):
        """Devuelve el row de la tabla donde se encuentra el shot
        
        :param shot: Diccionario con data del shot
        """
        return shot['ui']['name'].row()

    def enable_replace_roots(self, value):
        """Habilita la opcion para reemplazar los root de los paths del footage original, por que generalmente en los .XML empiezan en formato de URL.
        
        :param value: Activa o desactiva el reemplazo de roots
        """
        self.ui.sourceRoots.setEnabled(value)
        if value:
            self.checkAll()

    def browseNewRoot(self):
        """Abre un QFileDialog para poder buscar un nuevo root para reemplazar los que vienen en el .XML"""
        
        recent_dir = os.path.dirname(self.destinationPath)
        result = QFileDialog.getExistingDirectory(parent=None, caption='Select Folder to New Root',
                directory=recent_dir, options=QFileDialog.ShowDirsOnly)
                
        if result:
            self.ui.newSourceRoot.setText(result.replace('\\', '/'))
            self.checkAll()

    def browseDestination(self):
        """Abra un QFileDialog para elegir una carpeta para el destino del footage"""
        
        if os.path.exists(self.ui.sourceRoots.currentText()):
            recent_dir = self.ui.sourceRoots.currentText()

        elif os.path.exists(self.destinationPath):
            recent_dir = self.destinationPath

        else:
            recent_dir = 'M:'

        result = QFileDialog.getExistingDirectory(parent=None, caption='Select Folder to Output Frames',
                dir=recent_dir, options=QFileDialog.ShowDirsOnly)

        if result:
            index = self.ui.destinationPath.findText(result)
            if index >= 0:
                self.ui.destinationPath.setCurrentIndex(index)
            else:
                self.ui.destinationPath.insertItem(0, result)
                self.ui.destinationPath.setCurrentIndex(0)

            self.recent.save()

    def set_row_foreground(self, shot, color):
        """Cambia el color de las letras de un QWidget
        
        :param dict shot: Diccionario con data del shot
        
        :param QColor color: Color
        """
        
        shot['ui']['status'].setText(shot.get('status'))

        for index, column in enumerate(Columns.keys()):
            try:
                #if not shot['ui'][column].__class__.__name__ == 'QLabel':
                shot['ui'][column].setForeground(QBrush(color))
            except:
                pass

    @property
    def projects(self):
        """:return: Todos los projectos de Tactic, exceptuando los templates y los de sistema"""
        
        if not '_projects' in dir(self):
            self._projects = Projects(filters=[('is_template', False), ('type_project', "!~",'system')])
        return self._projects

    def set_project(self, index):
        """Cambia el proyecto actual de Tactic
        
        :param int index: Indice del QComboBox *project_combo*
        """
        project = self.ui.project_combo.itemText(index)
        self.server.set_project(project)

    def set_combo_project(self, project):
        """Cambia el proyecto actual de Tactic
        
        :param str project: Nombre del proyecto
        """
    
        index = self.ui.project_combo.findText(project)
        self.ui.project_combo.setCurrentIndex(index)
        self.set_project(index)

    @property
    def sourceRootsTexts(self):
        """:return: El contenido del QComboBox *ConformMedia.ui.sourceRoots*
        """
        for index in range(self.ui.sourceRoots.count()):
            yield self.ui.sourceRoots.itemText(index)

    def populate_sourceRoots(self, shot):
        """Popula el QComboBox *ConformMedia.ui.sourceRoots*
        
        :param dict shot: Diccionario con data del shot
        """
        for clip in shot['clips']:
            if clip.file:
                filepath = clip.file.pathurl
            else:
                continue

            if filepath:
                path = os.path.dirname(filepath)
                if self.digicuts:
                    new_path = os.path.dirname(self.digicuts[0]['filepath'])
                    self.ui.newSourceRoot.setText(new_path)
    
                for isla_path, in_source in isla_in_paths.items():
                    if path.startswith(isla_path):
                        new_path = path.replace(isla_path, in_source)
                        if os.path.exists(new_path):
                            self.ui.newSourceRoot.setText(new_path)

                if not path in self.sourceRootsTexts and path:
                    for source in self.sourceRootsTexts:
                        if path.startswith(source):
                            self.ui.sourceRoots.addItem(path)
                            break
                    else:
                        self.ui.sourceRoots.addItem(path)

    def populate_project_combo(self, projects):
        """Popula el QComboBox *ConformMedia.ui.project_combo* con los nombres de los proyectos
        
        :param list projects: Lista de proyectos de Tactic
        """
        if projects:
            self.ui.project_combo.clear()
            for project in projects:
                self.ui.project_combo.addItem(project.code)

            self.ui.project_combo.currentIndexChanged.connect(self.set_project)

    def cleanCombo(self, index):
        """Sanitiza y agrega un texto al QComboBox *ConformMedia.ui.sourceRoots*
        
        :param int index:
        """
        current = self.ui.sourceRoots.currentText()
        if current.endswith('/'):
            current = current[:-1]

        source = self.ui.sourceRoots.itemText(index)

        if source.startswith(current):
            insert = current
            self.ui.sourceRoots.removeItem(index)
        else:
            insert = source

        if not insert in self.sourceRootsTexts:
            self.ui.sourceRoots.addItem(insert)

    def target_proxy_file(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: La ruta completa al target de proxy
        """
        
        dir, base = os.path.split(self.target_file(shot))
        base, ext = os.path.splitext(base)
        base = shot['name'] + '.jpg'
        return os.path.join(dir, 'proxy', base)

    def target_file(self, shot, type=None, tries=0):
        """Este método genera la ruta completa de destino del footage :func:`ConformMedia.ConformMedia.destinationPath`
        
        :param dict shot: Diccionario con data del shot
        
        :return: La ruta completa al *destinationPath*
        """

        if self.pathOverCheck:
            try:
                if not os.path.exists(self.destinationPath):
                    raise NoDestinationPath
                #Agregado por Eduardo LASP------------------------------------------------------------------------------------------------
                if type is "halide":
                    destination_halide_path = "Z:/{Client}/{Project}/episodios/{Chapter}/secuencias/{Sequence}/shots/{Shot}/Animacion_A"
                    path = destination_halide_path
                    fields = ['Z:', 'Client', 'Project', 'Chapter', 'Shot', 'Sequence', 'Animacion_A']

                else:
                    path = self.pathOverCombo
                    fields = ['destinationPath', 'Client', 'Project', 'Chapter', 'Ext', 'Shot', 'Plano', 'JrShot', 'LastFolder', 'Sequence', 'Filename', 'Clip', 'Slot']

                if '{' in path and '}' in path:
                    for key in fields:
                        if '{' + key + '}' in path:

                            value = getattr(self, key)
                            if hasattr(value, '__call__'):
                                value = value(shot)

                            if not value:
                                value = 'NO_PARENT'

                            elif value.endswith('/') or value.endswith('\\'):
                                value = value[:-1]

                            path = path.replace('{' + key + '}', value)

            except (TypeError, SourceNotFound, BadShotName, NoChapters):
                raise CantResolvePath(path)

            #except (httplib.CannotSendHeader, httplib.CannotSendRequest, httplib.ResponseNotReady, xmlrpclib.ProtocolError):
            except Exception, e:
                print 'target_file: ', unicode(e)
                if tries < 3:
                    tries += 1
                    time.sleep(2)
                    return self.target(shot, tries)
                raise Exception('target_file: Tres intentos y nada.')

            return path.replace(' ', '_')

        else:
            raise Exception('Not Implemented')

    def LastFolder(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: La ultima carpeta de *shot.get('file')*
        """
        infile = self.newRoot(shot.get('file'))
        return os.path.split(os.path.split(infile)[1])[1]

    def Ext(self, shot):
        """:param dict shot: Diccionario con data del shot:
        
        :return: Nombre de la Extensión del archivo de footage
        """
        return shot.get('ext')

    def Shot(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del plano
        """

        return shot.get('name')

    def Plano(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del plano
        """

        return shot.get('plano')
        
    def Clip(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del clip
        """
        infile = self.newRoot(shot.get('file'))
        return os.path.split(os.path.dirname(infile))[1]

    def Slot(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del slot
        """
        return str(shot['slot'])

    def inRamonDB(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: True si el shot se encuentra en Tactic
        """
        
        if 'project' in shot:
            return self.tactic_shots(shot['project']).name_in(shot.get('name'))

    def Sequence(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre de la secuencia
        """
        return shot.get('sequence')

    def Chapter(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del episodio
        """
        try:
            return shot['episodio']
        except:
            raise NoChapters("Este proyecto no tiene episodios.")

    def Project(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del proyecto
        """
        return shot.get('project')

    def Client(self, shot):
        """:param dict shot: Diccionario con data del shot
        
        :return: Nombre del cliente
        """
        for project in self.projects:
            if shot.get('project') == project.code:
                return project.client

    def Filename(self, shot):
        return os.path.basename(shot['file'])

    @property
    def tableRowShots(self):
        """:return: Los shots que se encuentran el la tabla *ConformMedia.ui.shotsTable* """
        
        for row in range(self.ui.shotsTable.rowCount()):
            yield self.shots[self.ui.shotsTable.item(row, 2).text()]

    def selectAll(self):
        """Seleciona todas las filas de la tabla"""
        
        for shot in self.tableRowShots:
            self.select_row(shot, True)

    def deselectAll(self):
        """Deseleciona todas las filas de la tabla"""
    
        for shot in self.tableRowShots:
            self.select_row(shot, False)

    def toggleSel(self):
        """Togglea las filas seleccionadas seleccionadas"""
    
        for shot in self.tableRowShots:
            self.select_row(shot, not shot['ui']['slot'].isSelected())

    def get_shot_from_row(self, row):
        """:param int row: Numero de fila
        
        :return: El shot que se encuentra en la fila
        """
        
        return self.shots[self.ui.shotsTable.item(row, 2).text()]

    def isRowSelected(self, row):
        """:param int row: Numero de fila
        
        :return: True si la fila esta selecionada 
        """
        items = self.ui.shotsTable.selectedItems()
        for item in items:
            if self.ui.shotsTable.row(item) == row:
                return True
        return False

    def selFailed(self):
        """Seleciona las filas con shots fallados"""
        
        self.deselectAll()
        for name, shot in self.shots.items():
            if shot.get('status') == 'fail':
                self.select_row(shot, True)

    def confirmPathDialog(self, path):
        """Confirma que el path sea correcto
        
        :param str path: Ruta a footage
        
        :return: La ruta confirmada
        """
        confirmedPath, bool = QInputDialog.getText (self, 'WARNING!', 'This Path is Weird, Please Confirm',
                    QLineEdit.Normal, path)
        return str(confirmedPath)

    def select_row(self, shot, bool):
        """Selecciona un fila de la tabla *ConformMedia.ui.shotsTable* donde se encuentra el shot
        
        :param dict shot: Diccionario con data del shot
        
        :param bool bool: Selecionada o Deselecionada
        """
        
        for column in range(self.ui.shotsTable.columnCount()):
            item = self.ui.shotsTable.item(self.get_row_shot(shot), column)
            if item:
                item.setSelected(bool)

    def change_value(self, item):
        column = self.ui.shotsTable.column(item)
        for name, info in Columns.items():
            if info['order'] == column:
                break

    @property
    def selectedShots(self):
        """:return: Todos los shots seleccionados en la tabla"""
    
        rows = []
        shots = OrderedDict()
        for item in self.ui.shotsTable.selectedItems():
            row = self.ui.shotsTable.row(item)
            if not row in rows:
                rows.append(row)
                name = unicode(self.ui.shotsTable.item(row, 2).text())
                shots[name] = self.shots[name]
        
        for sortkey in sorted(shots.keys()):
            yield shots[sortkey]

    @property
    def sortedShots(self):
        """:return: Todos los shots de la tabla ordenados"""
        
        names = []
        for name, shot in self.shots.items():
            names.append(shot['name'])

        for name in sorted(names):
            yield self.shots[name]

    def progress_message(self, text, msecs=0):
        """Muestra un mensaje en el QStatusBar
        
        :param str text: Texto que aparecera en el *QStatusBar*

        :param int msecs: Milisegundos que permanecera el mensaje en el *QStatusBar*
        """
        self.ui.statusbar.showMessage(text, msecs=0)
        print text

# ///Copy shot! action: (ver)
    def copyShot(self):
        """Este método transfiere el footage original a la carpeta de destino en la forma especificada"""

        selection = list(self.selectedShots)
        if len(selection) == 0:
            QMessageBox.information(self, 'Sin seleccion', 'Seleccione planos para cargar a ramon', QMessageBox.Ok)

        xmlfilename = selection[0]['xml']
        project = selection[0]['project']
        for i, shot in enumerate(selection):
            row = self.ui.shotsTable.row(shot['ui']['slot'])
            name = shot.get('name')
            shot['handler_in'] = int(shot['ui']['handler_in'].text())
            shot['handler_out'] = int(shot['ui']['handler_out'].text())
            if not self.isnamevalid(os.path.dirname(self.newRoot(shot['file']))):
                sourceFolderOverride = self.confirmPathDialog(self.newRoot(shot['file']))

            if self.pathOverCheck:
                dstFolderOverride = self.pathOverCombo

            if shot['ui']['ramon'].text() in ['No exists', 'unknown']:
                self.InsertShotRamon(shot)

            try:
                if not self.testCheck:
                    if shot['ext'] in media.movie_formats:#Chequea que el archivo sea de ext valida
                        self.set_shot_status('in_process', shot)
                        if self.copyFootage:
                            if shot['ext'] in media.image_formats:
                                self.copyShotFootage(shot)
                            else:
                                self.CopyShotMovie(shot)
                        # elif self.toImages:
                        #     self.ExtractShotFootage(shot)

                        #Agregado para extrar audio con in y out (Halide)------------------------------------------------
                        elif self.toHalide:
                            self.ExtractShotAudio(shot)

                    if self.makeProxyCheck:
                        self.MakeProxy(shot)

            except NoDestinationPath:
                QMessageBox.information(self, 'Ruta inexistente', 'Por favor, setear un path de destino que exista.', QMessageBox.Ok)
                return
            continue
        self.saveXmlFileItemToCombo(xmlfilename)
        self.saveProjectItemToCombo(project)

#FUNCION DE HALIDE: EXTRAE AUDIO MEDIANTE UN IN Y UN OUT DEL SHOT Y LO COPIA EN LA CARPETA CORRESPONDIENTE--------------------------------
    def ExtractShotAudio(self, shot):
        try:
            self.destinationHalidePath = self.target_file(shot, "halide")
            fps = int(shot["fps"])
            starFrameFrameFormat = int(shot['start_frame'])   # Esta variable la creó Gastoncho
            if starFrameFrameFormat > 2:
                starFrameFrameFormat = starFrameFrameFormat - 3
            if starFrameFrameFormat > 1:
                starFrameFrameFormat = starFrameFrameFormat - 2
            if starFrameFrameFormat > 0:
                starFrameFrameFormat = starFrameFrameFormat - 1
            endFrameFrameFormat = int(shot['end_frame'])   # Esta variable la creó Gastoncho
            endFrameFrameFormat = endFrameFrameFormat + 3
            start_frame = Timecode(fps, frames = starFrameFrameFormat).format(fmt=ffmpeg_fmt)
            end_frame = Timecode(fps, frames = endFrameFrameFormat).format(fmt=ffmpeg_fmt)
            digicut = self.digicuts[0]["filepath"]
            #Agregar condicional para saber si ya existen los archivos a crear---------------
            audio_cortado_dir = self.generaPathDeDestino(shot['name'], ".wav")
            digicut_Shot_dir = self.generaPathDeDestino(shot['name'], ".mov")
            self.mayacam_dir = self.generaPathDeDestino(shot['name'], ".ma")
            self.mayapy_dir = self.generaPathDeDestino(shot['name'], ".bat")
            comando_halide_video = ffmpeg_dir + ' -i ' + digicut + ' -ar 48000 -ab 16 ' +' -ss ' + start_frame + ' -r 24 '+' -to ' + end_frame + " -c copy " + digicut_Shot_dir
            comando_halide_audio = ffmpeg_dir + ' -i ' + digicut + ' -ar 48000 -ab 16 ' +' -ss ' + start_frame + ' -to ' + end_frame + " -acodec copy " + audio_cortado_dir
            comando_halide_MayaCam = halideExtractor_dir + " " + audio_cortado_dir
            #La linea siguiente crea el archivo .bat que mediante el echo le agrega la linea mayapy + el path.ma correspondiente

            if not os.path.exists(audio_cortado_dir):
                os.system(comando_halide_audio)
                time.sleep(2)
            else:
                print "No se pudo crear el archivo: " + audio_cortado_dir + ". Archivo ya creado!!"
            if not os.path.exists(digicut_Shot_dir):
                os.system(comando_halide_video)
                time.sleep(2)
            else:
                print "No se pudo crear el archivo: " + comando_halide_video + ". Archivo ya creado!!"
            #una vez que tenga el halideExtractor, veo el nombre con que se crea el archivo y genero un if para restrkngir que no se cree devuelta el archivo si ya estaba creado
            if not os.path.exists(self.mayacam_dir):
                os.system(comando_halide_MayaCam)
            else:
                print "No se pudo crear el archivo: " + self.mayacam_dir + ". Archivo ya creado!!"

            #Codigo que se encarga de fijarse si existe el bat, crearlo y rellenarlo
            if not os.path.exists(self.mayapy_dir):
                comando_halide_mayapy = 'echo mayapy ' + self.destinationHalidePath + '/ma2abc.py > ' + self.mayapy_dir
                os.system(comando_halide_mayapy)
                print('mayapy ' + self.destinationHalidePath + "/ma2abc.py agregado al archivo .bat con exito!!")
                # Comando de CMD para borrar el archivo ma2fbx------------------------------------------------------
                self.add_del_line_to_bat()
            else:
                if not self.checkBat():
                    comando_halide_mayapy = 'echo mayapy ' + self.destinationHalidePath + '/ma2abc.py >> ' + self.mayapy_dir
                    os.system(comando_halide_mayapy)
                    print('mayapy ' + self.destinationHalidePath + "/ma2abc.py agregado al archivo .bat con exito!!")
                    # Comando de CMD para borrar el archivo ma2fbx------------------------------------------------------
                    self.add_del_line_to_bat()
                else:
                    print('No se ha podido agregar al .bat: mayapy ' + self.destinationHalidePath + "/ma2abc.py. Ya existente!!")
            self.add_ma2fbx_to_shot()
            self.add_ma2abc_to_shot()
            self.addConvetorDirecto()

        except Exception, e:
            print "Error!: ", e

    def add_del_line_to_bat(self):
        os.system("echo cd " + self.destinationHalidePath + " >> " + self.mayapy_dir)
        #os.system("echo Z: >> " + self.mayapy_dir)
        os.system("echo del /F /Q ma2abc.py >> " + self.mayapy_dir)
        os.system("echo timeout /t 2 /nobreak >> " + self.mayapy_dir)
# aca hice unas modificaciones para que la funcion de generar la linea del fbx ejecute la generacion del alembic en vez de los fbx en el bat que ejecuta todos los shots
    def add_ma2fbx_to_shot(self):
        for file in os.listdir('.'):
            if file == "ma2abc.py":
                try:
                    shutil.copyfile("./ma2abc.py", os.path.join(self.destinationHalidePath, file))
                except Exception, e:
                    print e
                return

        print "No existe el archivo ma2abc.py. Por favor instale el mismo en el directorio de 'Conformedia'"


    def add_ma2abc_to_shot(self):
        for file in os.listdir('.'):
            if file == "ma2abc.py":
                try:
                    shutil.copyfile("./ma2abc.py", os.path.join(self.destinationHalidePath, file))
                except Exception, e:
                    print e
                return

        print "No existe el archivo ma2abc.py. Por favor instale el mismo en el directorio de 'Conformedia'"		
		

    def addConvetorDirecto(self):
        for file in os.listdir('.'):
            if file == "ConverorDirecto.bat":
                try:
                    shutil.copyfile("./ConverorDirecto.bat", os.path.join(self.destinationHalidePath, file))
                except Exception, e:
                    print e
                return

        print "No existe el archivo ConverorDirecto.bat. Por favor instale el mismo en el directorio de 'Conformedia'"		

		
    def checkBat(self):
        bat_file = open(self.mayapy_dir, 'r')
        new_ma2fbx_line = 'mayapy ' + self.destinationHalidePath + '/ma2abc.py'
        for existing_line in bat_file.readlines():
            existing_line = unicode(existing_line.split(" \n", 2)[0])
            if new_ma2fbx_line == existing_line:
                return True
        return False

    def generaPathDeDestino(self, name, ext):
        if not os.path.exists(self.destinationHalidePath):
            os.makedirs(self.destinationHalidePath)
        if ext == ".bat":
            parts = name.split('_')
            parts = parts[0:-1]
            esc_name = "_".join(parts)
            pathBat = self.destinationHalidePath.split("shots", 2)
            arch = os.path.normpath(os.path.join(pathBat[0], esc_name + ext))

            #arch = os.path.normpath(os.path.join(self.destinationHalidePath, name + ext))
            return arch
        else:
            arch = os.path.normpath(os.path.join(self.destinationHalidePath, name + "_halide" + ext))
            return arch

    def saveXmlFileItemToCombo(self, fileXml):
        # print self.ui.xmlfilename.itemText(0)
        fileXml = os.path.normpath(fileXml)
        search = self.ui.xmlfilename.findText(fileXml)
        if search == -1:
            self.ui.xmlfilename.addItem(fileXml)

    def saveProjectItemToCombo(self, project):
        project = os.path.normpath(project)
        search = self.ui.project_combo.findText(project)
        if search == -1:
            self.ui.project_combo.addItem(project)

    def set_shot_status(self, status, shot):
        """Cambia el status de un shot
        
        :param str status: Texto sobre el status del shot
        
        :param dict shot: Diccionario con data del shot
        """
        self.shots[shot['name']]['status'] = status
        self.set_row_foreground(shot, Status.get(status)['color'])
        self.set_tooltip(shot)

    def update_shot_status(self, shot):
        """Actualiza el status de un shot

        :param dict shot: Diccionario con data del shot
        """
        self.set_row_foreground(shot, Status.get(shot.get('status'))['color'])
        self.set_tooltip(shot)

    def update_shot_proxy_status(self, shot):
        #self.shots[shot['name']]['ui']['proxy'].setText(shot['proxy'])
        pass

    def update_shot_ramon_status(self, shot):
        """Actualiza el status del Tactic de un shot

        :param dict shot: Diccionario con data del shot
        """
        self.shots[shot['name']]['ui']['ramon'].setText(shot['ramon'])

    def set_tooltip(self, shot):
        """Setea tooltips a una fila de la tabla de shots

        :param dict shot: Diccionario con data del shot
        """
        row = self.get_row_shot(shot)
        duration = int(shot['end_frame']) -  int(shot['start_frame']) + 1
        tooltip = 'XML: %s\nID: %s\nSource: %s\nDuration: %d\nFPS: %s\nProyecto: %s\nEpisodio: %s\nSecuencia: %s\nPlano: %s\nClips: %s' % (
        shot['xml'], shot['id'], shot['file'], duration, shot.get('fps'), shot.get('project'), shot.get('episodio'), shot.get('sequence'), shot.get('plano'), shot.get('clips_id'))        
        self.ui.shotsTable.item(row, 0).setToolTip(tooltip)
        try:
            mov = get_mov(shot, self.digicuts)
        except tc.FrameRateError, e:
            QMessageBox.warning(self, 'Framerate error.', 'El framerate (%s) del shot %s no es valido.' % (e.args[1], shot['name']), QMessageBox.Ok)
            mov = None

        if mov and mov.get('fps'):
            fps = mov.get('fps')

            timestart = Timecode(fps, frames=shot.get('start_frame'))
            timeend = Timecode(fps, frames=shot.get('end_frame'))

            if shot.get('sequence_timecode'):
                timeseq = Timecode(fps, shot.get('sequence_timecode'))
                start_timecode = str(timeseq + timestart) + ' - ' + mov.get('filepath')
                end_timecode = str(timeseq + timeend) + ' - ' + mov.get('filepath')
            else:
                start_timecode = timestart
                end_timecode = timeend

            self.ui.shotsTable.item(row, 3).setToolTip(start_timecode)
            self.ui.shotsTable.item(row, 4).setToolTip(end_timecode)

        if shot['clips']:
            clips = ',\n'.join([self.newRoot(clip.file.pathurl) for clip in shot['clips'] if clip.file and clip.file.pathurl])
            self.ui.shotsTable.item(row, 7).setToolTip(clips)

    def newRoot(self, source):
        """Cambia el root del source por uno de los que se encuentran en el QComboBox *ConformMedia.ui.newSourceRoot*

        :param str source: Ruta del footage 
        """
        
        if self.replaceRoots and source:
            for root in self.sourceRootsTexts:
                if source.startswith(root):
                    return source.replace(root, self.newSourceRoot)

        return source

    def source_frames_from_shot(self, shot):
        source = self.newRoot(shot.get('file'))
        if shot['ext'] == '.ari':
            return self.ari_frames(shot, source)

        elif shot['ext'] == '.mov':
            return self.mov_source(source)

        else:
            return source

    def target_frames_from_shot(self, shot, proxy=False):
        source = self.target_file(shot)

        if shot['ext'] == '.ari':
            return self.frames_source(shot, source)

        elif shot['ext'] == '.mov':
            return self.mov_target(shot, source, proxy)
        else:
            return source

    def proxy_frames_from_shot(self, shot):
        source = self.target_proxy_file(shot)

        if shot['ext'] == '.ari':
            return self.frames_source(shot, source)
            
        elif shot['ext'] == '.mov':
            return self.mov_target(shot, source, True)

        else:
            return source

    def ari_frames(self, shot, input):
        start = shot['startid'] - int(shot['ui']['handler_in'].text())
        end = shot['endid'] + int(shot['ui']['handler_out'].text()) + 1
        for frame in range(start, end):
            yield unicode(self.newRoot(input.replace('#' * 7, '%07d' % frame)))
            
    def frames_source(self, shot, input):
        start = shot['startid'] - int(shot['ui']['handler_in'].text())
        end = shot['endid'] + int(shot['ui']['handler_out'].text()) + 1
        for frame in range(start, end):
            yield unicode(self.newRoot(input.replace('#' * 7, '%07d' % frame)))
            
    def mov_source(self, input):
        yield unicode(self.newRoot(input).replace('\\', '/'))

    def mov_target(self, shot, input, proxy):
        if proxy:
            # En el caso que se haga un extract del .mov para sacar frames individuales
            for sequences in pyseq.get_sequences(os.path.splitext(input)[0] + '.#.jpg'):
                for sequence in sequences:
                    for frame in sequence:
                        yield frame.path
                    break
        else:
            yield unicode(self.newRoot(input).replace('\\', '/'))

    @staticmethod
    def check_md5(filepath):
        """:param str filepath: Ruta al archivo al que se le saca el MD5

        :return: Un string de hash MD5 de un archivo
        """
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(filepath, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def checkAll(self):
        """Hace un check general del todos los shots de la tabla"""
        
        self.deselectAll()
        for name, shot in self.shots.items():
            self.CheckShotStatus(shot)
            self.CheckShotProxy(shot)
            self.CheckShotRamon(shot)

    def saveUiLog(self):
        result = QFileDialog.getSaveFileName (parent = None, caption = 'Select text file to write',
                directory = self.defaultDir, filter = '*.txt')
                
        try:
            with open(result, 'w') as f:
                f.writelines(self.logTextEdit.toPlainText())
        except Exception,e:
            print 'could not save ui log to %s because %s' % (result, e)

    def isnamevalid(self, path):
        """:param str path: Ruta de un archivo
        
        :return: Si es valido una ruta de un archivo"""
        
        return re.match('[a-zA-Z0-9/\\:\. _()\-]*', path)

    def validateSourceFile(self, file):
        """Checkea que la ruta no tenga caracteres invalidos y que no exista
        
        :param str file: Ruta de archivo
        
        :return: Si es correcta la ruta
        """

        if not self.isnamevalid(file):
            raise InvalidFileName(file)

        if not os.path.isfile(file):
            raise SourceNotFound(file)

    @staticmethod
    def are_same(source, target, md5=False):
        """Checkea si dos archivos son iguales en fecha de creacion, tamaño, y en contenido por medio de hash MD5 (opcional) 
        
        :param str source: Ruta de archivo source
        
        :param str target: Ruta de archivo target
        
        :param bool md5: Chekear si son iguales en contenido por medio de hash MD5
        
        :return: Si True si los archivos son iguales
        """
        
        if os.path.isfile(target) and os.path.isfile(source):
            if os.path.getsize(source) == os.path.getsize(target):
                if os.path.getmtime(source) == os.path.getmtime(target):
                    if md5:
                        md5a = ConformMedia.check_md5(source)
                        md5b = ConformMedia.check_md5(target)
                        if md5a == md5b:
                            return True
                    else:
                        return True
                        
        return False
    #CHECK_NOMECLA**************************************************************///////////////////////////////////////////////////////////////////////////////////
    def checkNomenclaUI(self, data):
        nomencla, parsed_files, digicuts = data
        result = CheckNomencla.makeRule(nomencla)
        print result
        if result:
            self.LoadShotData(parsed_files)
    
    def save_thread(self, thread, type_='checks'):
        """Guarda un QThread en un diccionario dentro de :class:`CheckShotTable`
        
        :param QThread thread: Proceso de checkeo o copiado de footage
        
        :param str type_: Tipo de proceso que se lleva a cabo
        """
        
        func_name = thread.__class__.__name__

        if not type_ in self.checkThreads.jobs:
            self.checkThreads.jobs[type_] = {'max':1, 'running':0,'finished':0}
            
            if type_ == 'checks':
                self.checkThreads.jobs[type_]['max'] = 15
            
        if not func_name in self.checkThreads.jobs[type_]:
            self.checkThreads.jobs[type_][func_name] = []

        self.checkThreads.jobs[type_][func_name].append(thread)

    def connectSignalsStatus(self, thread, shot):
        """Este método conecta las Signal de un QThread a sus respectivas funciones
        
        :param QThread thread: QThread que es usado para hacer un proceso
        
        :param dict shot: Diccionario con data del shot
        """
        thread.In_Progress.connect(partial(self.set_shot_status, 'in_process', shot))
        thread.Fail.connect(partial(self.set_shot_status, 'fail', shot))
        thread.MediaOk.connect(partial(self.StatusMediaOk, shot))
        thread.StatusMessage.connect(self.progress_message)

    def StatusMediaOk(self, shot):
        """Setea el status de la media como Ok
        
        :param dict shot: Diccionario con data del shot
        """
        self.set_shot_status('media_ok', shot)
        self.select_row(shot, False)

    def LoadShotData(self, files):
        """Funcion que llama al QThread :class:`LoadShotData`
        
        :param str file: Archivos .XML para parsear
        """
        # path_file = self.ui.xmlfilename.itemText(file)
        self.make_table()
        self.ui.sourceRoots.clear()
        self.ui.newSourceRoot.clear()
        self.shots = {}

        data = LoadShotData(files, self.digicuts)
        data.LoadedShots.connect(self.populate_shotTable)
        data.StatusMessage.connect(self.progress_message)
        # data.ConnectCombo.connect(self.connection_Combo)#No hace falta este thread, trula el recent
        data.nomenclaError.connect(self.checkNomenclaUI)
        self.save_thread(data)

    def connection_Combo(self, state):
        """Conecta o desconecta el :class:`PySide.QtCore.Signal` del :class:`ConformMedia.ui.xmlfilename`
        
        :param bool state: Estado de QComboBox
        """
        if state:
            self.ui.xmlfilename.currentIndexChanged.disconnect(self.LoadShotData)
        else:
            self.ui.xmlfilename.currentIndexChanged.connect(self.LoadShotData)

    def AddShotRow(self, shot):
        """Funcion que llama al QThread :class:`AddShotRow`
        
        :param dict shot: Diccionario con data del shot
        """
        thread = AddShotRow(shot)
        thread.recibeData.connect(self.add_shot_row)
        self.save_thread(thread)

    def MakeThumbnail(self, shot, item, override=False):
        """Funcion que llama al QThread :class:`MakeThumbnail`
        
        :param shot: Diccionario con data del shot
        
        :param item: QTableItem donde se ubicara el thumbnail
        
        :param override: si es True Reemplaza el thumbnail existente
        """
        func = partial(self.LoadImagetoTable, self.ui.shotsTable, item, 90, 60)
        thumbnail = MakeThumbnail(shot, self.source_frames_from_shot, self.digicuts, override=override)
        thumbnail.recibeShot.connect(self.updateShot)
        thumbnail.recibeThumbnail.connect(func)
        thumbnail.deSelectShot.connect(self.select_row)
        self.save_thread(thumbnail)

    def CheckShotStatus(self, shot):
        """Funcion que llama al QThread :class:`CheckShotStatus`
        
        :param shot: Diccionario con data del shot
        """
        status = CheckShotStatus(shot, self.source_frames_from_shot, self.target_frames_from_shot, self.newRoot)
        status.recibeShotStatus.connect(self.update_shot_status)
        self.save_thread(status)

    def CheckShotProxy(self, shot):
        """Funcion que llama al QThread :class:`CheckShotRamon`
        
        :param shot: Diccionario con data del shot
        """
        if self.checkproxys:
            proxy = CheckShotProxy(shot, self.proxy_frames_from_shot)
            proxy.recibeShotProxy.connect(self.update_shot_proxy_status)
            self.save_thread(proxy)

    def CheckShotRamon(self, shot):
        """Funcion que llama al QThread :class:`CheckShotRamon`
        
        :param shot: Diccionario con data del shot
        """
        for ramon_shot in self.tactic_shots(shot['project']).from_name(shot['name']):
            ramon = CheckShotRamon(shot, ramon_shot)
            ramon.recibeShotRamon.connect(self.update_shot_ramon_status)
            self.save_thread(ramon)
            break

    def MakeProxy(self, shot):
        """Funcion que llama al QThread :class:`MakeProxy`
        
        :param shot: Diccionario con data del shot
        """
        def In_Progress(self, shot):
            self.update_shot_proxy_status(shot)
            self.set_shot_status('in_process', shot)
            
        def Done(self, shot):
            self.CheckShotProxy(shot)
            self.set_shot_status(shot['status'], shot)
            
        def Fail(self, shot):
            self.CheckShotProxy(shot)
            self.set_shot_status(shot['status'], shot)
            
        proxy = MakeProxy(shot, self.newRoot, self.target_proxy_file, self.digicuts)
        proxy.In_Progress.connect(partial(In_Progress, self))
        proxy.Fail.connect(partial(Fail, self))
        proxy.Done.connect(partial(Done, self))
        self.save_thread(proxy, 'jobs')

    def ExtractShotFootage(self, shot):
        """Funcion que llama al QThread :class:`ExtractShotFootage`
        
        :param shot: Diccionario con data del shot
        """
        extract = ExtractShotFootage(shot, self.target_file, self.toImages, self.toMovie, self.newRoot, self.haride)
        self.connectSignalsStatus(extract, shot)
        self.save_thread(extract, 'jobs')

    def CopyShotMovie(self, shot):
        """Funcion que llama al QThread :class:`CopyShotMovie`
        
        :param shot: Diccionario con data del shot
        """
        copy = CopyShotMovie(shot, self.newRoot, self.target_file, self.checkMD5)
        self.connectSignalsStatus(copy, shot)
        self.save_thread(copy, 'jobs') 

    def InsertShotRamon(self, shot):
        """Funcion que llama al QThread :class:`InsertShotRamon`
        
        :param shot: Diccionario con data del shot
        """
        insert = InsertShotRamon(shot, self.tactic_shots, self.replacePreview)
        insert.StatusMessage.connect(self.progress_message)
        insert.CheckShotStatus.connect(self.CheckShotStatus)
        insert.deSelectShot.connect(self.select_row)
        self.save_thread(insert, 'ramons')

    def copyShotFootage(self, shot):      # TODO Usar pyseq para las secuencias
        """Copia las secuencias de imagenes del footage de un shot a la carpeta de destino
        
        :param shot: Diccionario con data del shot
        """

        target_file = self.target_file(shot)
        target_dir = os.path.dirname(target_file)

        success = 0
        no_source = 0
        name = shot.get('name')

        files = list(self.source_frames_from_shot(shot))

        for i, source_file in enumerate(files):
            try:
                batchStamp = str(datetime.now())
                self.validateSourceFile(source_file)

                if not self.testCheck:
                    if not ConformMedia.are_same(source_file, target_file, self.checkMD5):
                        if not os.path.isdir(target_dir):
                            os.makedirs(target_dir)
                            
                        self.progress_message('Copiando footage de %s - Files %d / %d' % (shot['name'], i, len(files)), 100)
                        shutil.copy2(source_file, target_file)

                success += 1

                if self.logVerbose:
                    print 'Source:', source_file, '\nTarget: ', target_file
                    self._formattedLog(batchStamp, name, source_file, 'Copied OK', '')

            except SourceNotFound, e:
                print 'WARNING! not found', e
                no_source += 1
                if self.logErrors:
                    self._formattedLog(batchStamp, name, source_file, 'Not found', '')

            except InvalidFileName, e:
                print 'WARNING! invalid name', e
                if self.logErrors:
                    self._formattedLog(batchStamp, name, source_file, 'Bad Name', '')

            except CantResolvePath, e:
                print 'WARNING! Cant resolve path', e.message, 'for', name
                results.append(['Cant resolve path', source_file, name])
                if self.logErrors:
                    self._formattedLog(batchStamp, name, source_file, 'Cant resolve path', '')

            except Exception, e:
                print 'failed', source_file, e
                if self.logErrors:
                    self._formattedLog(batchStamp, name, source_file, 'ERROR', unicode(e))

            except KeyboardInterrupt:
                break

        if success==len(files):
            self.set_shot_status('media_ok', shot)
            
        elif success==0:
            if no_source==len(files):
                self.set_shot_status('missing_source', shot)
            else:
                self.set_shot_status('fail', shot)
        else:
            self.set_shot_status('missing_target', shot)


    def generate_gfx_sequence_nuke(self, escena):
        """Funcion que llama a nuke_fucntions.build_sequence() 
        
        :param str escena: Nombre de escena para armar
        
        """
        import lasp.nuke.functions as nuke_fucntions
        reload(nuke_fucntions)

        # for parsed in self.parsed_files:
        #     # for shot in parsed.clips:
        for shot in self.shots.values():
            if shot.get('project') and shot.get('episodio') and shot.get('sequence') and shot.get('name'):
                path = 'Z:/%s/%s/episodios/%s/secuencias/%s/shots/%s/Compo_Final/%s_Compo_Final.nk' % (self.Client(shot), shot.get('project'), shot.get('episodio'), shot.get('sequence'), shot.get('name'), shot.get('name'))
                # print 'PATH: ' + path
                info = nuke_fucntions.build_sequence(self.parsed_files[0], self.digicuts, self.Client(shot), escena)

                #Codigo viejo
                # if self.parsed_files[0].escenas:
                    # info = nuke_fucntions.build_sequence(self.parsed_files[0], self.digicuts, self.Client(shot), escena)
                # else:
                #     for shot in self.shots.values():
                #         escena = {}
                #         escena[] = shot["start_frame"]
                return

    @property
    def logFile(self):
        try:
            return self._logFile
        except:
            try:
                now = str(datetime.now()).replace(' ', '_').replace('-', '').replace(':', '').replace('.', '_')
                self._logFile = os.path.join(self.destinationPath, 'edlParserLogFile%s.log' % now)
                with open(self._logFile, 'w'):
                    pass
                return self._logFile
                
            except Exception,e :
                raise CantWriteLog('cant create or edit log file %s %s' % (self.logFile, unicode(e)) )

    def __log(self, message):
        try:
            with open(self.logFile, 'a') as f:
                try:
                    f.writelines(message)
                except:
                    pass

        except Exception,e :
            raise CantWriteLog('cant log to file %s %s' % (self.logFile, unicode(e)) )

    def _formattedLog(self, batch, shot, file, status, info):
        try:
            user = os.environ['USERNAME']
        except Exception,e:
            user = 'MAC'
            
        time = str(datetime.now())
        
        try:
            machine = os.environ['COMPUTERNAME']
        except Exception,e:
            machine = 'MAC'

        msg = '|'.join([time, machine, user, status, shot, info, file, batch]) + '\n'
        self.__log(msg)

    def closeEvent(self, event):
        print "Exit!!!"
        self.recent.save()

        if can_exit:
            event.accept() # let the window close
        else:
            event.ignore()


class CantWriteLog(Exception):
    """No es posible escribir el log"""
    pass


class SourceNotFound(Exception):
    """El footage no se encuentra en la ruta del .XML"""
    pass


class InvalidFileName(Exception):
    """El nombre del archivo contiene caracteres invalidos """
    pass


class CantResolvePath(Exception):
    """No se puede resolver el path, faltan definir variables"""
    pass


class BadShotName(Exception):
    """El nombre del shot es erroneo"""
    pass


class NoDestinationPath(Exception):
    """No esta definido el lugar donde se guarda el footage"""
    pass


class NoChapters(Exception):
    """No hay episodios"""
    pass


if __name__ == "__main__":
    with qt.GetApp(True) as app:
        app.setStyle("plastique")
        main_window = ConformMedia()
        ConformMedia.meta_generate(main_window)
        app.lastWindowClosed.connect(main_window.recent.save)
        main_window.ui.show()
