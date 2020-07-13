#python

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

lx.eval('user.value sceneio.alembic.save.scale 1.0')
def abcExport():
	currentfile = modoClasses.modoScene.currentFile()
	dirname, name = os.path.split(currentfile)
	lx.out(dirname)
	partesName = dirname.split("\\")
	contador = 0
	for obj in partesName:
		if obj == "Animacion_A" or obj == "02_Layout" or obj == "Lighting" or obj == "02_layout":
			partesName.remove(obj)
			contador = contador + 1
	if contador < 1:
		QtGui.QMessageBox.warning(None, u' Error ',  ' Nomenclatura o ruta erroneo... '  )
	else:
		nameAbc = partesName[-1]
		newPath = "___"
		numpartesName = len(partesName)
		for i, obj in enumerate(partesName):
			newPath = newPath + obj + "\\"
			newPath = newPath.split("___")[-1]
			basePath = newPath + "Publish\\"
		if not os.path.exists(basePath):
			os.mkdir(basePath)
		newPath = basePath + "borrar"
		if not os.path.exists(newPath):
			os.mkdir(newPath)
		pathTemp = newPath
		nameAbc = nameAbc + "_edit.abc"
		path = os.path.join(os.path.dirname(newPath), nameAbc )
		if os.path.exists(path):
			os.remove(path)
			lx.eval ('export.selected 3 false false true  {%s}' % path)
			QtGui.QMessageBox.warning(None, u' Joya',   "Exito al publicar la camara" )
		else:
			lx.out(basePath)
			lx.eval ('export.selected 3 false false true  {%s}' % path)
			QtGui.QMessageBox.warning(None, u' Joya',   "Exito al publicar la camara" )
		shutil.rmtree(pathTemp)
		os.startfile(basePath)
abcExport()