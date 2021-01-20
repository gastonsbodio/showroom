from __future__ import division
import pymel.core as pm
import maya.cmds as mc
import os
import shutil
import subprocess
import sys

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2.QtCore import Signal, QThread, Qt, QRect
import time
import maya.OpenMayaUI as mui
import shiboken2

import ast


import ctypes
from ctypes import wintypes
mpr = ctypes.WinDLL('mpr')
ERROR_SUCCESS   = 0x0000
ERROR_MORE_DATA = 0x00EA
wintypes.LPDWORD = ctypes.POINTER(wintypes.DWORD)
mpr.WNetGetConnectionW.restype = wintypes.DWORD
mpr.WNetGetConnectionW.argtypes = (wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.LPDWORD)

def getRealServerName( local_name):
	length = (wintypes.DWORD * 1)()
	result = mpr.WNetGetConnectionW(local_name, None, length)
	if result != ERROR_MORE_DATA:
		raise ctypes.WinError(result)
	remote_name = (wintypes.WCHAR * length[0])()
	result = mpr.WNetGetConnectionW(local_name, remote_name, length)
	if result != ERROR_SUCCESS:
		raise ctypes.WinError(result)
	return remote_name.value



username = os.environ['username']
temp_folder = "C:/Users/" + username + "/AppData/Local/Temp" # ff

path = os.path.join( temp_folder + "/", "localizer_path_presets.json" )
if not os.path.isfile( path ):
	task_manager_presets_var = '{"projectFolder" : "drive:/preFolders/projects", "localProjRoot" : "C:/someFolders/Project_local_drive" , "alternativeDrive" : "P"}'
	with open( temp_folder + "/localizer_path_presets.json", "w") as file:
		file.write(task_manager_presets_var)
		file.close()

with open( temp_folder + "/localizer_path_presets.json") as fi:
	data = fi.readlines()[0]
	dict = ast.literal_eval(data)
	fi.close()


class funcClass():
	alternative_local_drive = dict["alternativeDrive"]
	net_Drive = dict['projectFolder'].split(":/")[0]
	
	listaNSpace = mc.namespaceInfo( lon = True)
	listaNSpace.remove ('UI')
	listaNSpace.remove ('shared')

	def inicialize (self):
		try:
			getRealServerName( self.net_Drive + ':')
			self.currentNetwork_drive = self.net_Drive + ':/'
		except WindowsError:
			self.currentNetwork_drive = self.alternative_local_drive + ':/'	
			
	def read_json(self):
		with open( temp_folder + "/localizer_path_presets.json") as fi:
			data = fi.readlines()[0]
			dict = ast.literal_eval(data)
			fi.close()
		return (dict['projectFolder'].split(":/")[0], dict )

	def sitchNetwork_action(self):
		net_Drive = self.read_json()[0]
		window.pushButtonLocal.setEnabled(True)
		window.pushButton_NetWork.setEnabled(False)
		window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
		window.pushButtonLocal.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")
		window.labelSelectedEstado.setText( "Drive: Setted on:\n       -NetWork- " )
		try:
			getRealServerName( self.net_Drive + ':')
			QtWidgets.QMessageBox.information(window, u' Restart ',self.net_Drive + ": Drive already setted as Network ")
		except WindowsError:
			subprocess.call([r'C:/Users/' + username + '/Documents/setDrive_network.bat'])


		#subprocess.call([r'C:/Users/' + username + '/Documents/setDrive_network.bat'])

		QtWidgets.QMessageBox.information(window, u' Restart '," Restart Maya to load NetWork Drive")
		try:
			getRealServerName( net_Drive + ':')
			self.currentNetwork_drive = net_Drive + ':/'
		except WindowsError:
			self.currentNetwork_drive = self.alternative_local_drive + ':/' 
		drive = net_Drive + ':/'
		os.startfile( drive )

	def switchLocal_action(self):
		net_Drive = self.read_json()[0]
		dict = self.read_json()[1]
		if not os.path.exists( str (dict['localProjRoot'])  ):
			os.makedirs( dict['localProjRoot'] )
		window.pushButtonLocal.setEnabled(False)
		window.pushButton_NetWork.setEnabled(True)
		window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
		window.pushButton_NetWork.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")
		window.labelSelectedEstado.setText( "Drive: Setted on:\n         -Local- ")
		subprocess.call([r'C:/Users/' + username + '/Documents/setDrive_local.bat'])
		QtWidgets.QMessageBox.information(window, u' Restart '," Restart Maya to load Local Drive")
		#setDrive_2_local = 'SUBST ' + altern_local_drive + ': /D \n'
		try:
			getRealServerName( net_Drive + ':')
			self.currentNetwork_drive = net_Drive + ':/'
		except WindowsError:
			self.currentNetwork_drive = self.alternative_local_drive + ':/'  
		drive = net_Drive + ':/'
		os.startfile( drive )

	def dialog_setProjRoot(self):
		self.alternative_local_drive = str( window.textEdAlternativeDrive.toPlainText())
		if self.alternative_local_drive.isalpha() and len(self.alternative_local_drive) == 1:
			alternDriveDicc = '"alternativeDrive" : "' + self.alternative_local_drive + '" }'
			selectedPath = QtWidgets.QFileDialog().getExistingDirectory(None, 'Choose Project Network Folder', "C:/", QtWidgets.QFileDialog.ShowDirsOnly)
			window.labProjectPath2.setText(selectedPath)
			if len(selectedPath) > 3:
				window.pButton_setProjRoot.setText("Project Path Setted")
				window.labProjectPath2.setStyleSheet("background-color: rgb(100,100,100); color: rgb(0,175,0)")
	
			with open( temp_folder + "/localizer_path_presets.json") as fi:
				data = fi.readlines()[0]
				dict = ast.literal_eval(data)
				fi.close()
				
			dicc_LOcalFoldRoot = ' "localProjRoot" : "' + dict["localProjRoot"] + '" , '
			task_manager_presets_var = '{"projectFolder" : "' + selectedPath + '",' + dicc_LOcalFoldRoot
			with open( temp_folder + "/localizer_path_presets.json", "w") as file:    #  contruyo el json nuevamente
				file.write( task_manager_presets_var + alternDriveDicc )
				file.close()		
			
			net_Drive = selectedPath.split(":")[0]
			window.pushButtonLocal.setText("Switch " + net_Drive + " to Local")
			window.pushButton_NetWork.setText("Switch " + net_Drive + " to NetWork")
			try:
				realServerRoot = getRealServerName( net_Drive + ':')
			except Exception:
				print "Project root Not Founded"
				#realServerRoot
			self.bat_creation(net_Drive,self.alternative_local_drive, dict['localProjRoot'].replace("/","\\"), selectedPath.replace("/","\\") , realServerRoot )	
			butonsLocalsNetworkStates()

	def dialog_setLOcalFoldRoot(self):
		dict = self.read_json()[1]
		self.alternative_local_drive = str(window.textEdAlternativeDrive.toPlainText())
		if self.alternative_local_drive.isalpha() and len(self.alternative_local_drive) == 1:
			alternDriveDicc = '"alternativeDrive" : "' + self.alternative_local_drive + '" }'
			selectedPath = QtWidgets.QFileDialog().getExistingDirectory(None, 'Choose Local Folder as Future Drive', "C:/", QtWidgets.QFileDialog.ShowDirsOnly)
			window.labRootLocalPath2.setText(selectedPath)
			if len(selectedPath) > 3:
				window.pButton_setLOcalFoldRoot.setText("Local Folder Path Setted")
				window.labRootLocalPath2.setStyleSheet("background-color: rgb(100,100,100); color: rgb(0,175,0)")
				#validationProjRoot = True
			with open( temp_folder + "/localizer_path_presets.json") as fi:
				data = fi.readlines()[0]
				dict = ast.literal_eval(data)
				fi.close()
			
		dicc_ProjRoot ='{"projectFolder" : "' + dict["projectFolder"] + '" , '
		task_manager_presets_var = dicc_ProjRoot + '"localProjRoot" : "' + selectedPath + '" , '
		with open( temp_folder + "/localizer_path_presets.json", "w") as file:    #  contruyo el json nuevamente
			file.write( task_manager_presets_var + alternDriveDicc )
			file.close()
		net_Drive = self.read_json()[0]
		try:
			realServerRoot = getRealServerName( net_Drive + ':')
		except Exception:
			print "Project root Not Founded"
		self.bat_creation(net_Drive,self.alternative_local_drive , selectedPath.replace("/","\\"), dict['projectFolder'].replace("/","\\") ,realServerRoot)
		#subst W: "C:\Users\Gas\Desktop\gaston\local_PaperB_drive" 
		set_local_alternativeDrive = 'SUBST ' + self.alternative_local_drive + ': ' + selectedPath.replace("/","\\")
		with open( 'C:/Users/' + username + '/Documents/create_'+ self.alternative_local_drive +'.bat', "w") as file:
			file.write(set_local_alternativeDrive)
			file.close()		
		subprocess.call([r'C:/Users/' + username + '/Documents/create_'+ self.alternative_local_drive +'.bat'])
		butonsLocalsNetworkStates()

	def bat_creation (self, net_Drive, altern_local_drive,localProjRoot, projectFolder ,realServerRoot):
		setDrive_2_local = 'subst ' + altern_local_drive + ': /D \n'
		setDrive_2_local+='net use /del ' + net_Drive + ':   /y \n'
		setDrive_2_local+='net use ' + altern_local_drive + ': "%s"  /y \n' %realServerRoot
		setDrive_2_local+='subst ' + net_Drive + ': "' + localProjRoot + '" \n'

		#setDrive_2_network = 'IF EXIST "'+ projectFolder +'\\netWork_Checker.py"' + ' ( \n'
		#setDrive_2_network+='	ECHO ' + net_Drive + ' Drive already setted as Network \n'
		#setDrive_2_network+=') ELSE ( \n'
		setDrive_2_network ='subst ' + net_Drive + ': /d \n'
		setDrive_2_network+='net use /del ' + altern_local_drive + ':  /y \n'
		setDrive_2_network+='subst ' + altern_local_drive + ': "' + localProjRoot + '" \n'
		setDrive_2_network+='net use ' + net_Drive + ': "%s"  /y ' %realServerRoot
		#setDrive_2_network+=")"
		with open( 'C:/Users/' + username + '/Documents/setDrive_network.bat', "w") as file:
			file.write(setDrive_2_network)
			file.close()
		with open( 'C:/Users/' + username + '/Documents/setDrive_local.bat', "w") as file:
			file.write(setDrive_2_local)
			file.close()

	def blankDrivesFunc(self):
		if os.path.isfile( os.path.join( temp_folder + "/", "localizer_path_presets.json")):
			os.remove(os.path.join( temp_folder + "/", "localizer_path_presets.json" ))
		if os.path.isfile( 'C:/Users/' + username + '/Documents/setDrive_network.bat'):
			os.remove('C:/Users/' + username + '/Documents/setDrive_network.bat')
		if os.path.isfile( 'C:/Users/' + username + '/Documents/setDrive_local.bat'):
			os.remove('C:/Users/' + username + '/Documents/setDrive_local.bat')
		window.wind.close()


class CopyLocalThread(QThread):
	change_value = Signal(float)
	def __init__(self, parent=None):
		super(CopyLocalThread, self).__init__(parent)
		self.cn=funcClass()
		dict = self.cn.read_json()[1]
		self.localDrive = dict['localProjRoot'] + '/'
		self.projRoot = dict['projectFolder'] + '/'
		self.worongPathList=[]
		window.barraProgreso.show()
		try:
			getRealServerName( self.cn.net_Drive + ':')
			self.currentNetwork_drive = self.cn.net_Drive + ':/'
			self.localDrive = self.cn.alternative_local_drive + ':/' 
		except WindowsError:
			self.currentNetwork_drive = self.cn.alternative_local_drive + ':/'
			self.localDrive = self.cn.net_Drive + ':/' 
		fileList = mc.ls(type='file')
		rootReference = mc.file(r=True, q=True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True )
			if subReferences != None:
				todasLasReferencias = todasLasReferencias + subReferences		
		self.rutaRefList=[]
		for ref in todasLasReferencias:
			rutaRef = mc.referenceQuery ( ref, filename = True )
			self.rutaRefList.append(rutaRef)

		self.filepath_maya = mc.file(q=True, sn=True)

		self.pathFileNodLs=[]
		for f in fileList:
			t = mc.getAttr(f + '.fileTextureName')
			self.pathFileNodLs.append(t)

		cache_node_list = mc.ls(type='ExocortexAlembicFile')
		self.pathCache=[]
		for cache_node in cache_node_list:
			ruta_Ca = mc.getAttr(cache_node + '.fileName')
			self.pathCache.append(ruta_Ca)

		window.barraProgreso.minimum = 1
		window.barraProgreso.maximum = 100
		self.cantidad_archivos = len(self.pathFileNodLs) + len(self.rutaRefList) + len(self.pathCache) + 1
		self.unidad_porcentual = 100 / self.cantidad_archivos

	def run (self):
		window.barraProgreso.setValue(0)
		progress = self.unidad_porcentual
		for i, rutaRef in enumerate (self.pathFileNodLs + self.rutaRefList  + self.pathCache + [self.filepath_maya]):
			if i + 1 == self.cantidad_archivos :
				progress = 100
			try:
				if rutaRef.startswith(self.projRoot):
					path_sin_drive = rutaRef.split (":/") [-1]
					file_name = path_sin_drive.split ('/')[-1]
					path_sin_drive = path_sin_drive.split (file_name)[0]
					local_path = self.localDrive + path_sin_drive
					netWork_path = self.currentNetwork_drive + path_sin_drive
				else:
					self.worongPathList.append(rutaRef)
			except Exception:
				pass
			try:
				if not os.path.exists( local_path ):
					os.makedirs( local_path )   # 104
			except Exception:
				pass
			try:
				if os.path.isfile( local_path  + file_name ) :
					if window.checkBoxCopyOnlyUpdated.isChecked() == True or rutaRef == self.filepath_maya:
						time_local = os.stat(os.path.join(local_path, file_name )).st_mtime
						time_network = os.stat(os.path.join(netWork_path, file_name)).st_mtime
						time_local = str(time_local)
						time_network = str(time_network)
						if float(time_network) > float(time_local):
							shutil.copy2( os.path.join(netWork_path  , file_name  ) , os.path.join(local_path  , file_name ))
							window.listWidFilesCopied.addItem( local_path + file_name )
							self.change_value.emit(progress)
						else:
							self.change_value.emit(progress)
				else:
					shutil.copy2( os.path.join(netWork_path  , file_name  ) , os.path.join(local_path  , file_name ))
					window.listWidFilesCopied.addItem( local_path + file_name )
					self.change_value.emit(progress)
				progress = progress + self.unidad_porcentual
			except Exception as e:
				print str(e) + "    *****  Try Error "
				self.change_value.emit(progress)
				progress = progress + self.unidad_porcentual
				pass


class CopyBackThread(QThread):
	change_value = Signal(float)
	def __init__(self, parent=None):
		super(CopyBackThread, self).__init__(parent)
		self.cn=funcClass()
		dict = self.cn.read_json()[1]
		self.localDrive = dict['localProjRoot'] + '/'
		self.projRoot = dict['projectFolder'] + '/'
		self.worongPathList=[]
		window.barraProgBack.show()
		try:
			getRealServerName( self.cn.net_Drive + ':')
			self.currentNetwork_drive = self.cn.net_Drive + ':/'
			self.localDrive = self.cn.alternative_local_drive + ':/' 
		except WindowsError:
			self.currentNetwork_drive = self.cn.alternative_local_drive + ':/'
			self.localDrive = self.cn.net_Drive + ':/' 

		self.filepath_maya = mc.file(q=True, sn=True)	
		path_sin_drive = self.filepath_maya.split (":/") [-1]
		file_name = path_sin_drive.split ('/')[-1]
		path_sin_drive = path_sin_drive.split (file_name)[0]
		self.netWork_path = self.currentNetwork_drive + path_sin_drive

		
		# Gets all 'file' nodes in maya
		fileList = mc.ls(type='file')

		self.pathfileList = []
		for f in fileList:
			t = mc.getAttr(f + '.fileTextureName')
			self.pathfileList.append(t)
		
		rootReference = mc.file(r = True, q = True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True )
			if subReferences != None:
				todasLasReferencias = todasLasReferencias + subReferences
				
		self.pathReferenceList = []
		for ref in todasLasReferencias:
			try:
				ruta = mc.referenceQuery ( ref, filename = True )
				self.pathReferenceList.append(ruta)
			except Exception as e:
				pass
				
		cache_node_list = mc.ls(type='ExocortexAlembicFile')
		
		self.rutaCache_node_list = []
		for cache_node in cache_node_list:
			ruta_Ca = mc.getAttr(cache_node + '.fileName')
			self.rutaCache_node_list.append(ruta_Ca)		
		
		
		window.barraProgBack.minimum = 1
		window.barraProgBack.maximum = 100
		self.cantidad_archivos = len(self.pathfileList) + len(self.pathReferenceList) + len(self.rutaCache_node_list) + 1
		self.unidad_porcentual = 100 / self.cantidad_archivos
				
	def run(self):
		progress = self.unidad_porcentual
		window.barraProgBack.setValue(0)
		for i, ruta in enumerate (self.pathfileList + self.pathReferenceList + self.rutaCache_node_list + [self.filepath_maya]):
			if i + 1 == self.cantidad_archivos :
				progress = 100
			if window.checkBoxCopyBackExter.isChecked() == True or ruta == self.filepath_maya:
				try:
					if ruta.startswith(self.projRoot):
						path_sin_drive = ruta.split (":/") [-1]
						file_name = path_sin_drive.split ('/')[-1]
						path_sin_drive = path_sin_drive.split (file_name)[0]
						local_path = self.localDrive + path_sin_drive
						self.netWork_path = self.currentNetwork_drive + path_sin_drive
					else:
						self.worongPathList.append(ruta)
				except Exception:
					pass
				try:
					if not os.path.exists( self.netWork_path ):
						os.makedirs( self.netWork_path )   # 104
				except Exception:
					pass
				try:
					if os.path.isfile( self.netWork_path  + file_name ) :
						time_local = os.stat(os.path.join(local_path, file_name )).st_mtime
						time_network = os.stat(os.path.join( self.netWork_path, file_name )).st_mtime
						time_local = str(time_local)
						time_network = str(time_network)
						if float(time_local) > float(time_network):
							shutil.copy2( os.path.join(local_path  , file_name  ) ,	 os.path.join(self.netWork_path  , file_name ))
							window.listWidFilesCopied.addItem( self.netWork_path + file_name )
							self.change_value.emit(progress)
						else:
							self.change_value.emit(progress)
					else:
						shutil.copy2( os.path.join(local_path  , file_name  ) ,	 os.path.join(self.netWork_path  , file_name ))
						window.listWidFilesCopied.addItem( self.netWork_path + file_name )
						self.change_value.emit( progress )
					progress = progress + self.unidad_porcentual
				except Exception as e:
					self.change_value.emit(progress)
					progress = progress + self.unidad_porcentual
					pass


def getMayaWindow():
	pointer = mui.MQtUtil.mainWindow()
	return shiboken2.wrapInstance(long(pointer), QtWidgets.QWidget)
	
class Window (QtWidgets.QDialog):
	def __init__(self):
		super( Window, self ).__init__()
		parent = getMayaWindow()
		self.wind = QtWidgets.QMainWindow(parent)
		self.wind.setWindowTitle(" VPN_Drive   Switcher ")
		self.wind.setGeometry(500,200,1000, 735)
		self.InitUI()
		#self.wind.show()
		
	def InitUI(self):
		self.cn=funcClass()
		self.cn.inicialize ()
		self.wid = QtWidgets.QWidget()
		self.wind.setCentralWidget(self.wid)
		
		self.barraProgreso = QtWidgets.QProgressBar(self.wind)
		self.barraProgreso.setGeometry(QRect(50, 558, 900, 18))
		self.barraProgreso.setProperty("value", 24)
		self.barraProgreso.setValue(0)
		self.barraProgreso.hide()

		self.barraProgBack = QtWidgets.QProgressBar(self.wind)
		self.barraProgBack.setGeometry(QRect(50, 558, 900, 18))
		self.barraProgBack.setProperty("value", 24)
		self.barraProgBack.setValue(0)
		self.barraProgBack.hide()


		self.listWidFilesCopied = QtWidgets.QListWidget(self.wind)
		self.listWidFilesCopied.setTextElideMode(Qt.ElideMiddle)
		self.listWidFilesCopied.setGeometry(QRect(48, 300, 900, 250))

		# create buttons
		self.labAlternaDrive = QtWidgets.QLabel(self.wind)
		self.labAlternaDrive.setGeometry(QRect(58,  8, 100, 25))
		self.labAlternaDrive.setText("Alternative Drive:")
		self.labAlternaDrive.setStyleSheet("color: rgb(210,115,35)") # background-color: rgb(68,68,68);

		self.textEdAlternativeDrive = QtWidgets.QTextEdit( self.wind )
		self.textEdAlternativeDrive.setGeometry(QRect(153,  8, 25, 25))
		self.textEdAlternativeDrive.setText( dict["alternativeDrive"] )

		self.labDrive = QtWidgets.QLabel(self.wind)
		self.labDrive.setGeometry(QRect(180,  8, 25, 25))
		self.labDrive.setText(":/")
		self.labDrive.setStyleSheet("color: rgb(210,115,35)") # background-color: rgb(68,68,68);

		self.labAlterDriveExplain = QtWidgets.QLabel(self.wind)
		self.labAlterDriveExplain.setGeometry(QRect(206,  8, 350, 25))
		self.labAlterDriveExplain.setText("Choose a Non Used Drive as Alternative, like:  P:/, X:/, Z:/ ")
		self.labAlterDriveExplain.setStyleSheet("color: rgb(140,140,140)") # background-color: rgb(68,68,68);
	
		self.labProjectRoot = QtWidgets.QLabel(self.wind)
		self.labProjectRoot.setGeometry(QRect(240,  65, 300, 25))
		self.labProjectRoot.setText("Project Root is the Containing -Project- Folder")
		self.labProjectRoot.setStyleSheet("color: rgb(95,95,95)") # background-color: rgb(68,68,68);

		self.pButton_setProjRoot = QtWidgets.QPushButton(self.wind)
		self.pButton_setProjRoot.setStyleSheet("background-color: rgb(210,135,20); color: rgb(0,0,0)")
		self.pButton_setProjRoot.setText("Set Project Folder ")
		self.pButton_setProjRoot.setGeometry(QRect(50, 43, 120, 30))
		self.pButton_setProjRoot.clicked.connect( self.cn.dialog_setProjRoot )

		self.labProjectPath2 = QtWidgets.QLabel(self.wind)
		self.labProjectPath2.setGeometry(QRect(200,  49, 350, 21))
		self.labProjectPath2.setText( dict['projectFolder'] )

		if "drive:/preFolders/projects" == self.labProjectPath2.text():
			self.labProjectPath2.setStyleSheet("background-color: rgb(175,175,175); color: rgb(0,0,0)")
		else:
			self.labProjectPath2.setStyleSheet("background-color: rgb(180,180,180); color: rgb(0,125,0)")

		self.pButton_setLOcalFoldRoot= QtWidgets.QPushButton(self.wind)
		self.pButton_setLOcalFoldRoot.setStyleSheet("background-color: rgb(210,135,20); color: rgb(0,0,0)")
		self.pButton_setLOcalFoldRoot.setText("Set Local Folder Root")
		self.pButton_setLOcalFoldRoot.setGeometry(QRect(50, 98, 140, 30))
		self.pButton_setLOcalFoldRoot.clicked.connect( self.cn.dialog_setLOcalFoldRoot )

		self.qBut_BlanckDriveSett= QtWidgets.QPushButton(self.wind)
		self.qBut_BlanckDriveSett.setStyleSheet("background-color: rgb(170,170,170); color: rgb(0,0,0)")
		self.qBut_BlanckDriveSett.setText("Blank Drives Settings")
		self.qBut_BlanckDriveSett.setGeometry(QRect(60, 160, 120, 30))
		self.qBut_BlanckDriveSett.clicked.connect( self.cn.blankDrivesFunc )

		self.labRootLocalPath2 = QtWidgets.QLabel(self.wind)
		self.labRootLocalPath2.setGeometry(QRect(200,  102, 350, 21))
		self.labRootLocalPath2.setText(dict['localProjRoot'])
		if "C:/someFolders/Project_local_drive" == self.labRootLocalPath2.text():
			self.labRootLocalPath2.setStyleSheet("background-color: rgb(175,175,175); color: rgb(0,0,0)")
		else:
			self.labRootLocalPath2.setStyleSheet("background-color: rgb(180,180,180); color: rgb(0,125,0)")

		self.labSwitchDrives = QtWidgets.QLabel(self.wind)
		self.labSwitchDrives.setGeometry(QRect(737,  8, 350, 25))
		self.labSwitchDrives.setText("Switch Project Drive")
		self.labSwitchDrives.setStyleSheet("color: rgb(210,115,35)") # background-color: rgb(68,68,68);

		# create close button
		self.pushButtonLocal = QtWidgets.QPushButton(self.wind)
		self.pushButtonLocal.setGeometry(QRect(640, 40, 120, 41))
		self.pushButtonLocal.setText("Switch " + self.cn.net_Drive + " to Local")
		self.pushButtonLocal.clicked.connect(self.cn.switchLocal_action)
		self.pushButtonLocal.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")

		self.pushButton_NetWork = QtWidgets.QPushButton(self.wind)
		self.pushButton_NetWork.setText("Switch " + self.cn.net_Drive + " to NetWork")
		self.pushButton_NetWork.setGeometry(QRect(820, 40, 120, 41))
		self.pushButton_NetWork.clicked.connect(self.cn.sitchNetwork_action)
		self.pushButton_NetWork.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")

		self.pushButtonCopyExternalFiles = QtWidgets.QPushButton(self.wind)
		self.pushButtonCopyExternalFiles.setStyleSheet("background-color: rgb(70,25,70); color: rgb(200,200,200)")
		self.pushButtonCopyExternalFiles.setGeometry(QRect(720, 170, 140, 65))
		self.pushButtonCopyExternalFiles.setText("Copy External \n Files to Local\n  <==(Pull)")
		self.pushButtonCopyExternalFiles.clicked.connect ( self.copy_curentScene_and_externalFiles_2Local)

		self.checkBoxCopyOnlyUpdated = QtWidgets.QCheckBox(self.wind)
		self.checkBoxCopyOnlyUpdated.setText("Copy Updated\n      Files Too")
		self.checkBoxCopyOnlyUpdated.setStyleSheet("color: rgb(210,115,35)")
		self.checkBoxCopyOnlyUpdated.setGeometry(QRect(875, 183, 200, 35))
		self.checkBoxCopyOnlyUpdated.setChecked(True)

		#  copy back to Scene NetWork button
		self.pushButtonCopyBackCurrenFile = QtWidgets.QPushButton(self.wind)
		#pushButtonCopyBackCurrenFile.setFont(font)
		self.pushButtonCopyBackCurrenFile.setGeometry(QRect(45, 610, 150, 65))
		self.pushButtonCopyBackCurrenFile.setStyleSheet("background-color: rgb(70,25,70); color: rgb(200,200,200)")
		self.pushButtonCopyBackCurrenFile.setText("Copy Back Current \nMaya Scene to NetWork\n     (Push) ==>")
		self.pushButtonCopyBackCurrenFile.clicked.connect( self.copy_back_currentScene_2_network )

		#checkBoxCopyAll.setEnabled(False)
		self.checkBoxCopyBackExter = QtWidgets.QCheckBox(self.wind)
		self.checkBoxCopyBackExter.setText(" Copy Back New and Updated\n    externals files to network ")
		self.checkBoxCopyBackExter.setStyleSheet("color: rgb(210,115,35)")
		self.checkBoxCopyBackExter.setGeometry(QRect(210, 623, 200, 35))
		self.checkBoxCopyBackExter.setChecked(True)

		self.labelSelectedEstado = QtWidgets.QLabel(self.wind)
		self.labelSelectedEstado.setGeometry(QRect (743, 55, 100, 100))
		self.labelSelectedEstado.setStyleSheet("color: rgb(30,210,210)")

		self.labelEndCopy = QtWidgets.QLabel(self.wind)
		self.labelEndCopy.setGeometry(QRect(460, 560, 230, 23))
		self.labelEndCopy.setText("							 FINISHED!!!!")
		self.labelEndCopy.hide()

	def copy_curentScene_and_externalFiles_2Local(self):
		self.startProgBar2Local()

	def copy_back_currentScene_2_network(self):
		self.startProgBar2Network()
	
	def startProgBar2Local(self):
		self.thread = CopyLocalThread()
		self.thread.change_value.connect(self.setProgressVal)
		self.thread.start()
		self.thread.finished.connect(self.apagarBarra)

	def startProgBar2Network(self):
		self.threadNet = CopyBackThread()
		self.threadNet.change_value.connect(self.setProgressValBack)
		self.threadNet.start()
		self.threadNet.finished.connect(self.apagarBarraNet)
		
	def setProgressVal(self, val):
		self.barraProgreso.setValue(val)

	def setProgressValBack(self, val):
		self.barraProgBack.setValue(val)

	def apagarBarra(self):
	
		if len(self.thread.worongPathList) < 1 :
			QtWidgets.QMessageBox.information(window, u' Copy to Local '," Finished Process")
		else:
			mensaje = " Finished Process \n\n\n Warning! \n Wrong path files non copied:\n\n  "
			for p in self.thread.worongPathList:
				mensaje = mensaje + p + " \n  "
			QtWidgets.QMessageBox.information(window, u' Copy to Local ', mensaje)	
		os.startfile( self.thread.localDrive )
		self.barraProgreso.hide()
		
	def apagarBarraNet(self):
		if len(self.threadNet.worongPathList) < 1 :
			QtWidgets.QMessageBox.information(window, u' Copy to Network '," Finished Process")
		else:
			mensaje = " Finished Process \n\n\n Warning! \n Wrong path files non copied:\n\n  "
			for p in self.threadNet.worongPathList:
				mensaje = mensaje + p + " \n  "
			QtWidgets.QMessageBox.information(window, u' Copy to Network ', mensaje)
		self.labelEndCopy.show()
		os.startfile( self.threadNet.netWork_path )
		self.barraProgBack.hide()

App = QtWidgets.QApplication.instance()
window=Window()
#sys.exit(App.exec() )

def butonsLocalsNetworkStates():
	net_Drive = str( window.labProjectPath2.text() ).split(":/")[0]
	try:
		getRealServerName( net_Drive + ':')

		if str( window.labRootLocalPath2.text() ) != "C:/someFolders/Project_local_drive"  :
			if str( window.textEdAlternativeDrive.toPlainText() )  != "" :

				window.pushButton_NetWork.setEnabled(False)
				window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
				window.pushButtonLocal.setEnabled(True)
				window.pushButtonLocal.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")
				window.labelSelectedEstado.setText("Drive: Setted on:\n       -NetWork- ")
				window.labelSelectedEstado.setStyleSheet("color: rgb(30,210,210)")

			else:
				window.pushButton_NetWork.setEnabled(False)
				window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
				window.pushButtonLocal.setEnabled(False)
				window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
				window.labelSelectedEstado.setText("Drive: Setted on:\n         -None- ")
				window.labelSelectedEstado.setStyleSheet("color: rgb(180,0,0)")
	
		else:
			window.pushButton_NetWork.setEnabled(False)
			window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
			window.pushButtonLocal.setEnabled(False)
			window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
			window.labelSelectedEstado.setText("Drive: Setted on:\n         -None- ")
			window.labelSelectedEstado.setStyleSheet("color: rgb(180,0,0)")

	#else:
	except WindowsError:
		if "drive" != net_Drive:
			if str( window.labProjectPath2.text() ) !=  "drive:/preFolders/projects" :
				if str( window.labRootLocalPath2.text() ) != "C:/someFolders/Project_local_drive"  :
					if str( window.textEdAlternativeDrive.toPlainText() )  != "" :
						window.pushButton_NetWork.setEnabled(True)
						window.pushButton_NetWork.setStyleSheet("background-color: rgb(30,70,30); color: rgb(200,200,200)")
						window.pushButtonLocal.setEnabled(False)
						window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
						window.labelSelectedEstado.setText("Drive: Setted on:\n         -Local- ")
						window.labelSelectedEstado.setStyleSheet("color: rgb(30,210,210)")

			else:
				window.pushButton_NetWork.setEnabled(False)
				window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
				window.pushButtonLocal.setEnabled(False)
				window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
				window.labelSelectedEstado.setText("Drive: Setted on:\n         -None- ")
				window.labelSelectedEstado.setStyleSheet("color: rgb(180,0,0)")

		else:
			window.pushButton_NetWork.setEnabled(False)
			window.pushButton_NetWork.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
			window.pushButtonLocal.setEnabled(False)
			window.pushButtonLocal.setStyleSheet("background-color: rgb(70,100,70); color: rgb(200,200,200)")
			window.labelSelectedEstado.setText("Drive: Setted on:\n         -None- ")
			window.labelSelectedEstado.setStyleSheet("color: rgb(180,0,0)")
			
butonsLocalsNetworkStates()		
filepath_maya = mc.file(q=True, sn=True)
if filepath_maya != '':
	path = filepath_maya.split(":/")[-1]
	ruta_netWork = str(  window.textEdAlternativeDrive.toPlainText() ) + ":/" + path
	ruta_local = dict['localProjRoot'] + path
	if os.path.isfile(ruta_netWork):
		if os.path.isfile(ruta_local):
			time_local = os.stat(ruta_local).st_mtime
			time_network = os.stat(ruta_netWork).st_mtime
			time_local = str(time_local)
			time_network = str(time_network)
			if float(time_local) > float(time_network):
				window.pushButtonCopyBackCurrenFile.setStyleSheet("background-color:red;")