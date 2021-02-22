#python

# Author: Gaston Sbodio (gastonsbodio@gmail.com) 
import lx
import os
import sys
import fnmatch
import shutil

import modo
from PySide import QtGui


import lasp.modo.mddImport as mddImport
reload (mddImport)
import lasp.modo.modoDialogs as modoDialogs
reload (modoDialogs)
import lasp.modo.modoClasses as modoClasses
reload (modoClasses)

lx.eval("pref.value application.indexStyle none");
def modoRenderPath():
# lista los objetos que son renderOutput
    itemNum = lx.eval ("query sceneservice item.N ? ");
    itemNumList = range (0, itemNum);
    renderOutputList = []
    for item in itemNumList:
	    itemType = lx.eval ("query sceneservice item.type ? %s" %item );
	    itemName = lx.eval ("query sceneservice item.name ? %s" %item );
	    if itemType == "renderOutput":
		    renderOutputList.append (itemName)
########################
# busca y crea la ruta correspondiente donde guardar los render, y si no existe la crea
    currentfile = modoClasses.modoScene.currentFile()
    dirname, name = os.path.split(currentfile)
    endName = name.split ("_")
    endName = endName[-1].split (".lxo")[0]
    name = name.split (".lxo")[0]
    name = name + "_"
    subFolderList = dirname.split("\\")
    for obj in ["Z:","episodios", "secuencias", "shots", "Lighting"]:
        subFolderList.remove(obj)
    path = "Z:\\INTERNO\\MEDIA"
    for obj in subFolderList:
        path = path +"\\"+ obj
        try:
            os.mkdir(path)
        except Exception:
            pass
    path = path + "\\modo"
    try:
        os.mkdir(path)
    except Exception:
        pass
    path = path + "\\" + endName
    lx.out (path)
    lx.out("tendria que ser parche")
    try:
        os.mkdir(path)
    except Exception:
	    pass
    lx.out (path)
    path = path + "\\borrar"
    try:
        os.mkdir(path)
    except Exception:
        pass

    pathFull = path
    path = os.path.join(path)
    contador1 = 0
    contador2 = 0
    if os.path.exists(path):
        path = os.path.join(os.path.dirname(path), name )
        try:
            renderOutputList.remove("Alpha Output (2)")
            renderOutputList.remove("Alpha Output")
            renderOutputList.remove("Alpha Output2")
        except Exception:
            pass
        for renOutp in renderOutputList:
            if str(renOutp) != "Alpha Output (2)" or str(renOutp) != "Alpha Output":
                if len(renOutp.split(" ")) < 2:
                    lx.eval ( "select.subItem %s set textureLayer;render;environment;light;camera;scene;replicator;bake;mediaClip;txtrLocator" % renOutp );
                    lx.eval('item.channel renderOutput$filename "%s"' % path)
                    lx.eval('item.channel renderOutput$format openexr')
                    contador1 = contador1 + 1
                else:
                    QtGui.QMessageBox.warning(None, u' Error de Nomenclatura',  ' espacios o caracteres especiales en la nomenclatura de ' + renOutp + "     " )
                    contador2 = contador2 + 1
        if contador1 != 0 and contador2 == 0:
            QtGui.QMessageBox.warning(None, u' Grositud',  "Proceso terminado sin errores" )
    else:
        print (" parece que no existe  dirMedia ")
    shutil.rmtree(pathFull)
modoRenderPath()

