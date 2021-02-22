# Author:  Gaston Sbodio (gastonsbodio@gmail.com)


import os
import json
from functools import partial
import ast
import sqlite3
import re
from string import printable
import glob
import shutil
from datetime import datetime
import sys
from subprocess import call
import time
try:
    #globals().update(ensure_module('PySide'))
    from PySide  import QtCore
    from PySide.QtGui import *
except: # Nuke > 11
	from PySide2 import QtCore
	from PySide2.QtGui import *
	from PySide2.QtWidgets import *
	import maya.OpenMayaUI as mui
	import shiboken2
	import maya.mel as mm
	import maya.cmds as mc

user = os.environ['USERNAME']
sys.path.append('C:/Users/' + user + '/Documents/Pr_G/PACKAGES/')
sys.path.append('C:/Users/' + user + '/Documents/Pr_G/')


pipeline_root_path = "C:/Users/Gas/Desktop/pipeline"  #  local Gastoncho
#pipeline_root_path = "W:/Pr_G_Pipeline"
#pipeline_root_path = "W:/PAPERBIRDS/PIPELINE"  #  paper birds

"""import PACKAGES.oauth2client.service_account as ServiceAcc
import gspread   # # # # # # passwordservice@projectogpasssheet.iam.gserviceaccount.com

scope = [ "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets" , "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"  ]
creds = ServiceAcc.ServiceAccountCredentials.from_json_keyfile_name( pipeline_root_path + "/TOOLS/creds/creds.json", scope)
client = gspread.authorize (creds)
sheet = client.open("testPrG").sheet1
data = sheet.get_all_records()
"""
#masterPass = data[0]["passinput"]
masterPass = "pepito"

with open( pipeline_root_path + "/projects_list_pipeline.json") as fi:
	data = fi.readlines()[0]
	try:
		dict = ast.literal_eval(data)
		project_list = dict['projects_list']
	except Exception:
		pass	

####   ####   parches   ###   ### 

parchePB01 = "" #  / TIM, proyectos de Santi Tereso    #parchePB01 = "/ASSETS" #  /ASSETS
parchePB_Copy2publiFol = False   # para los proyectos de Santi es False    #  para papperbirds es True
parcheSantiT02 = "/05_SEQUENCES"  # "/SCENES"
assetMayaFol = "/04_ASSETS/" #  "/ASSETS/"   # papper birds 
concepts_folder = "concepts"  #  "CONCEPTS"
version_folder = "work"  # "WIP" papper birds
publish_folder = "publish"
cache_folder = "cache"
playblaset_fol = "playblast"
compo_folder = "CMP"
cg_fol = "cg"
assetsCompo_folder = "ASSETS"
matchMovFolder = 'MCH'
roto_folder = 'RTO'

Approved_fol = "Approved"

shad_folder = "SHD"
rig_folder = "RIG"
mod_folder = "MOD"
rsh_folder = "RSH"
text_folder = "TEXT"
art_folder = "ART"



char_folder = "CHARACTERS"
props_folder = "PROPS"
sets_folder = "SETS"
module_folder = "MODULES"


publish_folder_alternativePB = "/PUBLISH"   # NOOOO  DEBERIA EXISTIR!!!!!!!!!!!!!!!!!!!!!

anim_fol = "ANM"
layout_fol = "LAY"
lit_fol = "LGT"
exp_folder = "EXP"
sim_fol = "SIM"
sha_shots_fol = 'SHA'
sets_shots_fol = "SET" 

###   ###   ###   ###  ## 
animTamplate = "ANIM_TEMPLATE"
modTemplate = "MOD_TEMPLATE"
emptyTempla = "EMPTY_TEMPLATE"
rigCharPropTempl = "RIGGEDASS_TEMPLATE"
escenarioTempl = "SET_TEMPLATE"
moduleTempl = "MODULE_TEMPLATE"
litTempla = "LIT_TEMPLATE"

refeGrp = "REFES_grp"

defaultRenderFol = compo_folder + "/" + cg_fol + "/"
######################################

mayaExtenList = [ "-default-" ,".ma", ".mb"]

mayaTemListNa = [ animTamplate, modTemplate, emptyTempla, rigCharPropTempl, escenarioTempl, moduleTempl , litTempla ]
status_list =   ["On Hold", "Done", "Wip" , "Not Started" ]
statusOnlySuperv_list = [ Approved_fol ] 
area_listt =    ["3D", "CMP", "UNI" ]
special_area_ls = ["COORD" ]
asset_type_list = [ char_folder, props_folder, sets_folder, module_folder ]
frameRateList = ["-default-" , "24", "25" , "12" , "48" , "15", "30" ]
projResolutList = ["-default-" , "w3840,h2160", "w2048,h1080","w1080,h720" ]
previewFormatList = [ "-default-" , "avi", "qt" ]
colorManagList = [ "-default-", "lut" ]
#mayaShTasksList = [ "-default-" ,"ANM", "LAY" , "SIM" , "LGT" ,"EXP" ,"SET" ]    #  papper birds type
mayaShTasksList = [ "-default-" ,anim_fol, layout_fol , sim_fol , lit_fol ,exp_folder ,"SET" ,'SHA' ]
nukeShTasks = [ compo_folder, assetsCompo_folder ,matchMovFolder , roto_folder ]
nukeShTasksList = ["-default-"] + nukeShTasks
mayaAsTasksList = ["-default-" ,mod_folder, shad_folder , rig_folder, rsh_folder,text_folder, art_folder ]   #  no modificar el orden de estas variables!!!!!!!!!!!!!
#mayaAsTasksList = ["-default-" ,"MOD", "SHD" , rig_folder, "RSH","TEXT" ]   #  papperbirds


######################################

temp_folder = "C:/Users/" + user + "/AppData/Local/Temp"
listaTempFiles = os.listdir(temp_folder)
user_Default = {"user" :"None"}

caracteresProhibidos = ["-","_","@","%", "$","?", "!", "|","*",".",",",";"]

path = os.path.join( temp_folder + "/", "project_task_manager_presets.json" )
if not os.path.isfile( path ) or  len(project_list) == 0:
	task_manager_presets_var = '{"project" : "", "proRoot" : "drive:/someFolders/projects/"}'
	with open( temp_folder + "/project_task_manager_presets.json", "w") as file:
		file.write(task_manager_presets_var)
		file.close()

if 'user_task_manager_presets.json' not in listaTempFiles:
	user_presets_var = '{"user" : "None" }'
	with open( temp_folder + "/user_task_manager_presets.json", "w") as file:
		file.write(user_presets_var)
		file.close()
else:
	with open( temp_folder + "/user_task_manager_presets.json" ) as fi:
		data = fi.readlines()[0]
		dict = ast.literal_eval(data)
		user_Default = dict['user']
		fi.close()

excutSource = type (sys.stdout)
# Result: <type 'maya.Output'> #
if len(str(excutSource).split("maya")) == 2:
	# Result: <type 'maya.Output'> # 
	def getWindow():
		pointer = mui.MQtUtil.mainWindow()
		return shiboken2.wrapInstance(long(pointer), QWidget)		

class MainWindow(QWidget):
	def __init__(self, parent=None):
		if len(str(excutSource).split("maya")) != 2:
			super(MainWindow, self).__init__(parent)
			self.wind = QMainWindow()
			self.wind.setStyleSheet(" background-color: rgb(46,47,48)") # background-color: rgb(128,128,128);
		else:
			super(MainWindow, self).__init__()
			parent = getWindow()
			self.wind = QMainWindow(parent)
			self.wind.setStyleSheet(" background-color: rgb(46,47,48)")
		self.wind.setWindowTitle("Pr-G  Manager")
		self.iconPrg = QPixmap( pipeline_root_path + '/icon/Pr_G.png')
		self.wind.setWindowIcon(self.iconPrg)
		self.wind.setMinimumSize(QtCore.QSize(1500, 800))
		self.wind.setMaximumSize(QtCore.QSize(1500, 800))
		#self.wind.setSizeIncrement(QtCore.QSize(826, 673))
		#self.wind.setBaseSize(QtCore.QSize(826, 673))
		
		self.usuarios_list = [ ]
		self.lideres_list = [ ]
		self.productores_list = [ ]
		
		self.lastRowAssetSelected = 0
		self.lastRowShotSelected = 0
		self.lastRowUserSelected = 0
		self.key01 = False
		self.key04 = False
		self.key03 = False
		self.key05 = False
		self.key_loadSh = False
		self.key_loadAss = False
		self.key_loadUse = False
		self.validationProjSett = False
		
				
		with open(temp_folder + "/project_task_manager_presets.json") as fi:
			data = fi.readlines()[0]
			self.diccUsSlack = {}
			dicct = ast.literal_eval(data)
			if dicct["proRoot"] != "drive:/someFolders/projects/":
				name = dicct["project"].split("/")[-1]
				self.projectDataBase = dicct["project"] + "/PIPELINE/DATABASE/" + name + "_dataBase.db"
				self.projectDataBase =  self.projectDataBase.replace ("\\", "/")
				self.projName = dicct["project"].split("/")[-1]
				self.projName  = self.projName.replace ("\\", "/")
				self.root = str(dicct["proRoot"])
				self.root = self.root.replace ("\\", "/")
				if os.path.isfile( self.projectDataBase ):
					tuplaList = self.selectAllDB_lessBlackL ( self.projectDataBase,'users' ) 
					for tupla in tuplaList:
						if tupla[5] == special_area_ls[0]:   #  [5] le corresponde a la columna de area
							self.productores_list.append(tupla[1])
							self.diccUsSlack [tupla[1]] = tupla[7]
						else:
							self.usuarios_list.append(tupla[1])
							self.diccUsSlack [tupla[1]] = tupla[7]
						if tupla[6] == 1:
							self.lideres_list.append(tupla[1])
		self.scripts_folder = dicct ["project"] + "/DATA/TOOLS/"
		self.scripts_folder = self.scripts_folder.replace ("\\", "/")
		#self.newfont = QFont("Arial", 11, QFont.Bold) 
		#self.newfont2 = QFont("Arial", 9, QFont.Bold) 
		self.newfont = QFont() 
		self.newfont2 = QFont()
		self.newfont.setFamily(u"Arial")
		self.newfont2.setFamily(u"Arial")
		self.newfont.setBold(True)
		self.newfont2.setBold(True)		
		# create a widget
		self.wid = QWidget() # Main
		self.widSetProject = QWidget()
		self.widShots = QWidget()
		self.widAssets = QWidget()
		self.widProduction = QWidget()
		self.widBar = QWidget()		
		
		self.wind.setCentralWidget(self.wid)
		self.wind.setCentralWidget(self.widBar)
		# create a layout
		self.layoutSetProject = QVBoxLayout(self.widSetProject)
		self.layoutShots = QVBoxLayout(self.widShots)
		self.layoutAssets = QVBoxLayout(self.widAssets)
		self.layoutProduction = QVBoxLayout(self.widBar)
		self.widSetProject.setLayout(self.layoutSetProject)
		self.widShots.setLayout(self.layoutShots)
		self.widAssets.setLayout(self.layoutAssets)
		self.widProduction.setLayout(self.layoutProduction)
		self.tab_1= QTabWidget(self.wind)
		self.tab_1.setStyleSheet(" background-color: rgb(65,65,65); border-width: 3px;")  #   border-style: groove;
		self.tab_1.setGeometry(QtCore.QRect(10, 90, 1480, 705))
		

		size = QtCore.QSize(80, 22)
		
		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconSetProject.png')
 		self.tab_1.addTab(self.widSetProject, icon, "")
		self.tab_1.tabBar().setIconSize(size)
		
		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconShots.png')
		self.tab_1.addTab(self.widShots, icon, "")

		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconAssets.png')
		self.tab_1.addTab(self.widAssets, icon, "")

		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconProduction.png')
		self.tab_1.addTab(self.widProduction, icon, "")


		############################################
		#########  barra superiot de la ventana (user name, proj name   documentation)  + tab set project)
		######################################################################################################
		
		# label prefix artista
		
		
		imagemap = QPixmap ( self.root + self.projName  + '/PIPELINE/iconUser.png')
		self.labPreUserName = QLabel(self.wind)
		self.labPreUserName.setGeometry(QtCore.QRect(290, 30, 50, 50))
		self.labPreUserName.setPixmap (imagemap)		
		
		
		
		#self.labPreUserName = QLabel(self.wind)
		#self.labPreUserName.setGeometry(QtCore.QRect(290, 35, 300, 30))
		#self.labPreUserName.setText("Artist Name: ")
		#self.labPreUserName.setStyleSheet("color: rgb(200,200,200)")
		#self.labPreUserName.setFont(self.newfont)





		# label artista seteado
		self.labUserName = QLabel(self.wind)
		self.labUserName.setGeometry(QtCore.QRect(355, 45, 300, 15))
		self.labUserName.setFont(self.newfont)
		path = os.path.join( temp_folder + "/", "user_task_manager_presets.json" )
		if os.path.isfile( path ):
			with open( temp_folder + "/user_task_manager_presets.json", "r" ) as fi:
				user_Default = json.load(fi)
				fi.close()
			if str(user_Default ["user"]) == "None":
				self.labUserName.setText("None")
				self.labUserName.setStyleSheet("color: rgb(160,0,0)")
				self.userName = "None"
			else:
				if str(user_Default ["user"]) in  self.usuarios_list + self.productores_list :		
					self.labUserName.setText(str(user_Default ["user"]) )
					self.userName = str(user_Default ["user"])
					self.labUserName.setStyleSheet("color: rgb(10, 170, 160)")
				else:
					self.labUserName.setStyleSheet("color: rgb(160,0,0)")
					self.labUserName.setText("None")
					self.userName = "None"
		else:
			self.labUserName.setText("None")
			self.userName = "None"
			
		self.projecScripts(self.scripts_folder)
		# etiqueta prefija del proyecto que se seleccionara
		#self.labPreSelectedProject = QLabel(self.wind)
		#self.labPreSelectedProject.setGeometry(QtCore.QRect(83, 40, 150, 20))
		#self.labPreSelectedProject.setText( "Current Project:")
		#self.labPreSelectedProject.setFont(self.newfont)
		#self.labPreSelectedProject.setStyleSheet("color: rgb(200,200,200)")

		altoBoton1 = 100
		anchoBis = 1000
		altoBis = 95

		# label para visualizar el path Root de los proyectos
		self.labRootProjectPath = QLabel(self.widSetProject)
		self.labRootProjectPath.setGeometry(QtCore.QRect( anchoBis + 170 , altoBis+11, 250, 21))
		with open(temp_folder + "/project_task_manager_presets.json") as fi:
			data = fi.readlines()[0]
			try:
				self.res = ast.literal_eval(data)
			except Exception:
				pass
		self.labRootProjectPath.setText(str(self.res["proRoot"]))
		self.labRootProjectPath.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)")
		self.labRootProjectPath.setFont(self.newfont)
		anchoComboPro = 30
		# donde visualizo el proyecto seleccionado  para todo el browser 
		self.labWinProject = QLabel(self.wind)
		self.labWinProject.setGeometry(QtCore.QRect(75, 40, 180, 30))
		
		self.labTamplateActive = QLabel(self.widSetProject)
		self.labTamplateActive.setGeometry(QtCore.QRect(anchoComboPro + 150, 265, 120, 41))
		self.labTamplateActive.setText("")
		self.labTamplateActive.setStyleSheet("background-color: rgb(65,65,65); color: rgb(200,200,200)")
		self.labTamplateActive.setFont(self.newfont)
			
		if str(self.res["project"]).split("/")[-1] == "None" or str(self.res["project"]).split("/")[-1] == "" :
			self.labWinProject.setText("None")  # rojo!!!!!
			self.labWinProject.setStyleSheet("color: rgb(160,0,0)")
		else:
			self.labWinProject.setText(self.projName)
			self.labWinProject.setStyleSheet("color: rgb(10, 170, 160)")
			#####################scenes tamplates vars##############################
			path = os.path.join( self.root + self.projName + "/PIPELINE/CONFIGURATION/", "project_tamplate_activation.json" )
			if os.path.isfile( path ):
			
				with open(path) as fi:
					data = fi.readlines()[0]
					dict = ast.literal_eval(data)
					main_list = dict["templeVasData"]			
			
				self.labTamplateActive.setText("Activated")
				self.labTamplateActive.setStyleSheet("background-color: rgb(65,65,65);color: rgb(10, 170, 160)")
				self.EMPTY_TEMPLATE= ["*"]
				self.MOD_TEMPLATE = main_list[1]
				self.MODULE_TEMPLATE = main_list[5]
				self.RIGGEDASS_TEMPLATE = main_list[3]
				self.SET_TEMPLATE = main_list[4]
				self.ANIM_TEMPLATE = main_list[0]
				self.LIT_TEMPLATE = main_list[6]
			else:
				self.labTamplateActive.setText("Non Activated")
				self.labTamplateActive.setStyleSheet("color: rgb(160,0,0)")
				self.EMPTY_TEMPLATE=["*"]
				self.MOD_TEMPLATE = ["*"]
				self.MODULE_TEMPLATE = ["*"]
				self.RIGGEDASS_TEMPLATE = ["*"]
				self.SET_TEMPLATE = ["*"]
				self.ANIM_TEMPLATE = ["*"]
				self.LIT_TEMPLATE = ["*"]
				
			#####################scenes tamplates vars##############################			
			
		self.labWinProject.setFont(self.newfont)
		
		#label prefijo para senialar donde se elige proyecto
		self.labProjectsCombo = QLabel(self.widSetProject)
		self.labProjectsCombo.setGeometry(QtCore.QRect(anchoComboPro + 5, 40, 131, 21))
		self.labProjectsCombo.setText("Choose Project   ")
		self.labProjectsCombo.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")

		# combo box para seleccionar la variedad de proyectos
		self.comboBoxProject = QComboBox(self.widSetProject)
		self.comboBoxProject.setGeometry(QtCore.QRect(anchoComboPro, 65, 150, 30)) 
		self.listProjects = self.listarProj( )
		self.comboBoxProject.addItems(self.listProjects)   
		self.comboBoxProject.currentIndexChanged.connect(self.choosingProject)
		self.comboBoxProject.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	
		
		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconProjectGeneric.png')
		self.comboBoxProject.setItemIcon(0, icon)
		AllItems = [self.comboBoxProject.itemText(i) for i in range(self.comboBoxProject.count())]
		size = QtCore.QSize(20, 20)
		self.comboBoxProject.setIconSize( size )		
		

		# combo box de artistas para setear
		self.comboBoxUsers = QComboBox(self.widSetProject)
		self.comboBoxUsers.setGeometry(QtCore.QRect(anchoComboPro, 165, 150, 30))
		self.comboBoxUsers.addItems ( [ "    "] + self.usuarios_list + self.productores_list )
		self.comboBoxUsers.currentIndexChanged.connect(self.choosingUser)
		self.comboBoxUsers.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	
		
		
		icon = QIcon(self.root + self.projName  + '/PIPELINE/iconUser.png')
		self.comboBoxUsers.setItemIcon(0, icon)
		AllItems = [self.comboBoxUsers.itemText(i) for i in range(self.comboBoxUsers.count())]
		size = QtCore.QSize(20, 20)
		self.comboBoxUsers.setIconSize( size )

		self.qButSetTemplates = QPushButton(self.widSetProject)
		self.qButSetTemplates.setFont(self.newfont)
		self.qButSetTemplates.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 15px; border-style: groove;")
		self.qButSetTemplates.setText("Set Templates")
		self.qButSetTemplates.setGeometry(QtCore.QRect(anchoComboPro, 265, 130, 41))
		self.qButSetTemplates.clicked.connect(self.templateIstruction)
		
		self.setButUsOnOff(self.qButSetTemplates)


		self.labProjectPreference = QLabel(self.widSetProject)
		self.settin_list = self.set_settingsVariables()
		try:
			texto = self.textLoadSettings(self.root, self.settin_list[0], self.settin_list[1], self.settin_list[2], self.settin_list[3], self.settin_list[4], self.settin_list[5], self.settin_list[6], self.settin_list[7] , self.settin_list[8] , self.settin_list[11])
			self.labProjectPreference.setStyleSheet("background-color: rgb(65,65,65); color: rgb(10, 170, 160)")
		except AttributeError:
			self.root = "drive:/someFolders/projects/"
			self.projName = "None" #""
			texto = self.textLoadSettings(self.root, self.settin_list[0], self.settin_list[1], self.settin_list[2], self.settin_list[3], self.settin_list[4], self.settin_list[5], self.settin_list[6], self.settin_list[7] , self.settin_list[8] , self.settin_list[11])
			self.labProjectPreference.setStyleSheet("background-color: rgb(65,65,65); color: rgb(200, 200, 200)")
		self.labProjectPreference.setGeometry(QtCore.QRect(anchoBis+80, -25, 500, 500))
		self.labProjectPreference.setText( texto )
		self.labProjectPreference.setFont(self.newfont2)

		###### structure ##########
		structure = "                                                                                    PROJECT FOLDER STRUCTURE: \n\n\n\n"
		struc =     "                    05_SEQUENCES                                                                             " + assetMayaFol + "\n\n\n"
		s     =     "                                |                                     CHARACTERS                  PROPS                     MODULES                      SETS\n\n"
		mayaScene = "                        SceneName                            CharName                  PropName                ModuleName                 SetName\n\n\n      "  
		taskFol=    "         [ Publis.m*, ANM, LAY, EXP ]      [     Publis.ma,      MOD,       SHD,    "+  rig_folder + ",     TEXT     ]    [ Publis.m*, MOD, SHD, TEXT ]\n\n"
		publish =   "                               work                          [                                 Publis_TASK.m*                                    work                                  ]  \n\n"
		ver =       "            SceneName_TASK_v00*.m*                                                             AssetName_TASK_v00*.m*  "
		self.labStructureProj = QLabel(self.widSetProject)
		self.labStructureProj.setGeometry(QtCore.QRect(335, 145, 650, 300))
		self.labStructureProj.setText( structure +  struc + s + mayaScene + taskFol + publish + ver)
		self.labStructureProj.setStyleSheet("color: rgb(0,0,0)")
		#self.labPreSelectedProject.setFont(self.newfont)

		# label imagen del proyecto
		imagemap = QPixmap ( self.root + self.projName  + '/PIPELINE/iconProject.png')
		self.lab_image = QLabel(self.wind)
		self.lab_image.setGeometry(QtCore.QRect(10, 30, 50, 50))
		self.lab_image.setPixmap (imagemap)

		# label para el tab de los Assets
		self.labSceneShots = QLabel(self.widAssets)
		self.labSceneShots.setGeometry(QtCore.QRect(80, 20, 150, 60))
		self.labSceneShots.setText("Assets")

		#########################   tab Assets         #############################
		self.tabAssetsTableUi()
		#########################   tab shots         #############################
		self.tabShotTableUi()
		#########################   tab Prod         #############################
		self.tabProducUi()
		self.scripJCounter1 = 0
		self.scripJCounter2 = 0
		self.listaProjects = self.listarProj( )

	def shadowButt ( self, shadow):
		shadow.setEnabled(True)
		color = QColor (20,20,20)
		shadow.setColor (color)
		shadow.setBlurRadius(30)
		shadow.setOffset(5)
		

		#from subprocess import call
		#call([r"ffplay","prG.mp3"])
		#############################################################
	def templateIstruction(self):
		#listaTemplates = os.listdir(self.root + "/" + self.projName + "/PIPELINE/TEMPLATES/SCENE/"	)
		#if len(listaTemplates) != 0 :	
		winSetTemp = setTemplateWin()
		winSetTemp.show()
		#try:
		if winSetTemp.exec_():
			print " "
		#except Exception:
		#	pass	

	def slackBot(self , mensasje ,chanelUser ):
		if self.settin_list[9] != "":
			if chanelUser != "":
				from slacker import Slacker
				slack = Slacker (self.settin_list[9])
				message = "@channel" + mensasje
				try:
					slack.chat.post_message (chanelUser, message, username = "PrG_Bot", link_names = True, as_user = True)
				except Exception:
					pass

	def slackUserImporter (self):
		if self.settin_list[9] != "":
			from slacker import Slacker
			from slackclient import SlackClient
			slack = Slacker (self.settin_list[9])
			slacCl = SlackClient (self.settin_list[9])
			api = slacCl.api_call("users.list")
			self.diccUsSlack  = {}
			id_tuplalist = self.selectAllDB (self.projectDataBase,"users" )
			id_list = []
			for tupla in id_tuplalist:
				id_list.append(tupla[0])
			for item in api["members"]:
				self.diccUsSlack [ item['name'] ] = item['id']
				print "Importing  " + item['name'] + "  ..."
				i = 1
				conn = sqlite3.connect ( self.projectDataBase )
				c = conn.cursor()
				if i in id_list:
					while i in id_list:
						i+= 1
					id_list.append (i)
					c.execute("INSERT INTO users ( id ,first_name , last_name, pass, email, area, approver, slack_code, blackListed ) VALUES (?,?,?,?,?,?,?,?,?)" ,(i, item['name'], "", "123", "", "3D", 0, item['id'],0 ))
					self.usuarios_list.append(item['name'])
					self.comboBoxUsers.addItems( [item['name']] )
				else:
					id_list.append (i)
					c.execute("INSERT INTO users ( id ,first_name , last_name, pass, email, area, approver, slack_code, blackListed  ) VALUES (?,?,?,?,?,?,?,?,?)" ,(i, item['name'], "", "123", "", "3D", 0, item['id'],0))
					self.usuarios_list.append(item['name'])
					self.comboBoxUsers.addItems( [item['name']] )
				conn.commit()
				conn.close()
			if self.key_loadUse:
				self.refresh_user_table()
			else:
				self.load_user_button()
			QMessageBox.information(None, u' Succes!', "     Users Imported !!!!! " )
		else:
			QMessageBox.warning(None, u' ', "\n   Go to     https://'your-project-name'.slack.com/apps/manage       \n\nand look for   'Bots'   on the top main 'searching Bar' \n\n                  and follow the steps...    then \n\n  Insert Slack Project Code on Project Settings Preset\n\n" )

	def projecScripts(self, scripts_folder):
		self.menuBar_help = QMenuBar(self.widBar)
		self.menuBar_help.setGeometry(QtCore.QRect(10, 7, 1400, 30))
		#self.menuBar_help.setStyleSheet("color: rgb(0,0,0)")
		
		self._3DarMenu = self.menuBar_help.addMenu("&                                                                                                                                                                              ")
		self._3DarMenu = self.menuBar_help.addMenu("&Company Documentation")
		self._3DarMenu.setStyleSheet("background-color: rgb(200,200,200); color: rgb(200,200,200)")		
		self._3DarPeopleAct = QAction("&3DarPeople",self.wind, triggered = self.printing)
		self._3DarMenu.addAction(self._3DarPeopleAct)
		#self.pipeNomenclature = QAction("&Nomenclature",self.wind, triggered = self.nomenclaDoc)
		#self.pipeDocumentationMenu.addAction(self.pipeNomenclature)

		self.pipeDocumentationMenu = self.menuBar_help.addMenu('&Pipeline Documentation')
		self.pipeDocumentationMenu.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)")	

	
		self.pipeWelc = QAction("&Welcome to Pr-G",self.wind, triggered = self.welcomeDocClic)
		self.tabSetProject = QAction("&Set Project and Log in",self.wind, triggered = self.tabSetProjectClic)		
		self.generalTableUses = QAction("&General Tables Uses",self.wind, triggered = self.generalTableUsesClic)
		self.taPopulaFiltering = QAction("&Table Population and Filtering",self.wind, triggered = self.taPopulaFilteringClic)
		self.assetCreation = QAction("&Asset Creation and First Task",self.wind, triggered = self.assetCreationClic)
		self.assetNextSteps = QAction("&Asset Next Steps",self.wind, triggered = self.assetNextStepsClic)
		self.callPublishAss = QAction("&Call Publish Assets",self.wind, triggered = self.callPublishAssClic)
		self.lockScenes = QAction("&Lock Scenes",self.wind, triggered = self.lockScenesClic)
		self.callPublishModule = QAction("&Call Publish Module",self.wind, triggered = self.callPublishModuleClic)
		self.slackConect = QAction("&Slack Connection",self.wind, triggered = self.slackConectClic)
		self.makeThumbNail = QAction("&Make ThumbNail",self.wind, triggered = self.makeThumbNailClic)
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			self.standAloneVer = QAction("&Stand Alone Version and Nomenclature",self.wind, triggered = self.standAloneVerClic)
			self.createProjectUsers = QAction("&Create Projects and  Users",self.wind, triggered = self.createProjectUsersClic)
			self.templatesHelp = QAction("&Templates Help",self.wind, triggered = self.templatesHelpClic)

			self.pipeDocumentationMenu.addAction(self.standAloneVer)
			self.pipeDocumentationMenu.addAction(self.createProjectUsers)
			self.pipeDocumentationMenu.addAction(self.templatesHelp)
			
		self.pipeDocumentationMenu.addAction(self.pipeWelc)
		self.pipeDocumentationMenu.addAction(self.tabSetProject)
		self.pipeDocumentationMenu.addAction(self.generalTableUses)
		self.pipeDocumentationMenu.addAction(self.taPopulaFiltering)
		self.pipeDocumentationMenu.addAction(self.assetCreation)
		self.pipeDocumentationMenu.addAction(self.assetNextSteps)
		self.pipeDocumentationMenu.addAction(self.callPublishAss)
		self.pipeDocumentationMenu.addAction(self.lockScenes)
		self.pipeDocumentationMenu.addAction(self.callPublishModule)
		self.pipeDocumentationMenu.addAction(self.slackConect)
		self.pipeDocumentationMenu.addAction(self.makeThumbNail)

		self.projectToolsMenu = self.menuBar_help.addMenu('&Project Tools')
		self.projectToolsMenu.setStyleSheet("background-color: rgb(0,0,0); color: rgb(200,200,200)")
		self.pipeDocumentationMenu = self.menuBar_help.addMenu('&                                                                                                                          ')
		mel_list = glob.glob (scripts_folder + "/*.mel")
		for script in mel_list:
			path_name = script.split("\\")
			if path_name[-1].endswith(".mel"):
				scrpiptName = path_name[-1].split(".mel")[0]
				self.scriptShoot = QAction("&%s" %scrpiptName, self.wind, triggered = lambda: self.executeMelMAyaScri ( path_name[0] + "/" + path_name[-1]) )
				self.projectToolsMenu.addAction(self.scriptShoot)

	def welcomeDocClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=o4ND1Wl8EZQ	', new=2)
	
	def tabSetProjectClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=J-f3ZWG7H00', new=2)
		
	def generalTableUsesClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=1wLgZjc3iuM', new=2)

	def standAloneVerClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=PaJsLM7WRs4', new=2)

	def taPopulaFilteringClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=w0Xy84lLTCg', new=2)
		
	def assetCreationClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=knfWY6JLaNY', new=2)

	def assetNextStepsClic (self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=uU_KhcMxPZI', new=2)

	def callPublishAssClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=DQr3whz9m4M', new=2)
	
	def lockScenesClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=FtX98btu65A', new=2)

	def callPublishModuleClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=6WkfbU3pHWA', new=2)

	def slackConectClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=AXrFPv4rWvM', new=2)

	def makeThumbNailClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=yv9D-nwf0VI', new=2)

	def createProjectUsersClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=_3KisZe675M', new=2)

	def templatesHelpClic(self):
		import webbrowser
		webbrowser.open('www.youtube.com/watch?v=AIab-goAA3Q', new=2)

	#def nomenclaDoc (self):
	#	import webbrowser
	#	webbrowser.open('https://drive.google.com/open?id=1fbOXIGOGApMW5spBIflP0KoWcx-gT5YQ8q7zDz3pRU8', new=2)

	def changeSeletedAssetRowColor ( self, table, columnAmount , rowsBlackListed, rowsLockedList):
		for col in columnAmount:
			if self.lastRowAssetSelected % 2 == 0:
				table.item(self.lastRowAssetSelected, col).setBackground(QColor(200, 200, 200)  )
			else:
				table.item(self.lastRowAssetSelected, col).setBackground(QColor(180, 180, 190)  )
			if self.lastRowAssetSelected in rowsLockedList:
				table.item(self.lastRowAssetSelected, col).setBackground(QColor(125,125,125))
			if self.lastRowAssetSelected in rowsBlackListed:
				table.item(self.lastRowAssetSelected, col).setBackground(QColor(45,45,43))
		selectedRow = table.currentRow()
		if selectedRow not in rowsBlackListed and rowsBlackListed != None and selectedRow != None and selectedRow != -1:
			for col in columnAmount:
				table.item(selectedRow, col).setBackground(QColor(80,130,166))
			self.lastRowAssetSelected = selectedRow

	def changeSeletedShotRowColor ( self, table, columnAmount , rowsBlackListed, rowsLockedList):
		for col in columnAmount:
			if self.lastRowShotSelected % 2 == 0:
				table.item(self.lastRowShotSelected, col).setBackground(QColor(200, 200, 200)  )
			else:
				table.item(self.lastRowShotSelected, col).setBackground(QColor(180, 180, 190)  )
			if self.lastRowShotSelected in rowsLockedList:
				table.item(self.lastRowShotSelected, col).setBackground(QColor(125,125,125))
			if self.lastRowShotSelected in rowsBlackListed:
				table.item(self.lastRowShotSelected, col).setBackground(QColor(45,45,43))
		selectedRow = table.currentRow()
		if selectedRow not in rowsBlackListed and rowsBlackListed != None and selectedRow != None and selectedRow != -1:
			for col in columnAmount:
				table.item(selectedRow, col).setBackground(QColor(80,130,166))
			self.lastRowShotSelected = selectedRow

	def changeSeletedUserRowColor ( self, table, columnAmount , rowsBlackListed):
		for col in columnAmount:
			if self.lastRowUserSelected % 2 == 0:
				table.item(self.lastRowUserSelected, col).setBackground(QColor(210, 210, 195)  )
			else:
				table.item(self.lastRowUserSelected, col).setBackground(QColor(190, 190, 182)  )
			if self.lastRowUserSelected in rowsBlackListed:
				table.item(self.lastRowUserSelected, col).setBackground(QColor(45,45,43))
		selectedRow = table.currentRow()
		if selectedRow not in rowsBlackListed and rowsBlackListed != None and selectedRow != None and selectedRow != -1:
			for col in columnAmount:
				table.item(selectedRow, col).setBackground(QColor(80,130,166))
			self.lastRowUserSelected = selectedRow


	
	def referencePublishedAsset (self):
		idd = self.currentRowText(self.tablaWidgAssets ,self.idAss_column_idx)
		dbRowLoaded = self.selectDbRow( self.projectDataBase,"assets" , idd)
		if dbRowLoaded[0][10] == 1:
			AssetFileName = dbRowLoaded[0][3]
			tipo_asset = dbRowLoaded[0][2]
			type_task = dbRowLoaded[0][5]
			path =  self.root  + self.projName  + assetMayaFol + tipo_asset  + "/" + AssetFileName + "/" + type_task + "/" + publish_folder  + "/" + AssetFileName + self.settin_list[5]
			nameSpace = mc.file (path, r = True, ns = AssetFileName)
			num = len (nameSpace.split("{") + nameSpace.split("}"))
			if num == 4:
				AssetFileName = AssetFileName + nameSpace.split("{")[-1].split("}")[0]
			if tipo_asset == char_folder:
				mc.parent ( AssetFileName + ":" + self.RIGGEDASS_TEMPLATE[0] , self.ANIM_TEMPLATE[0])
			elif tipo_asset == props_folder:
				mc.parent ( AssetFileName + ":" + self.RIGGEDASS_TEMPLATE[0] , self.ANIM_TEMPLATE[0])
			elif tipo_asset == sets_folder :
				for fol in self.SET_TEMPLATE:
					if len ( mc.ls( AssetFileName + ":" + fol ) ) > 0:
						mc.parent ( AssetFileName + ":" + fol , self.ANIM_TEMPLATE[2])
			elif tipo_asset == module_folder:
				for fol in self.MODULE_TEMPLATE:
					if len ( mc.ls( AssetFileName + ":" + fol ) ) > 0:
						mc.parent ( AssetFileName + ":" + fol , self.ANIM_TEMPLATE[2])			
		else:
			QMessageBox.information(None, u' ',  " Asset Not Published")		

	def referenceModule (self):
		if self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx) == module_folder:
			idd = self.currentRowText(self.tablaWidgAssets ,self.idAss_column_idx)
			dbRowLoaded = self.selectDbRow( self.projectDataBase,"assets" , idd)
			if dbRowLoaded[0][10] == 1:
				AssetFileName = dbRowLoaded[0][3]
				tipo_asset = dbRowLoaded[0][2]
				type_task = dbRowLoaded[0][5]
				path =  self.root + self.projName  + assetMayaFol + tipo_asset  + "/" + AssetFileName +   "/" + type_task  + "/" + publish_folder + "/" + AssetFileName + self.settin_list[5]
				allReferencePath = mc.file(r = True, q = True)
				list = []
				for nr in allReferencePath:
					nsc = nr.split("{")[0]
					list.append(nsc)
				counter = 0
				for r in list:
					if str(r) == path:
						counter+= 1
				objRefefList = mc.file (path, r = True, uns = False , returnNewNodes = True, renamingPrefix = AssetFileName  + "_" +str(counter))
				list = []
				for item in objRefefList:
					list.append (str ("|" + str(item) ))
				list = mc.ls(list, type = "transform")
				allMain = mc.ls("|*")
				for o in list :
					if o in allMain:
						mc.parent ( o, self.SET_TEMPLATE[1])
			else:
				QMessageBox.information(None, u' ',  " Module you Choose is not Published")
		else:
			QMessageBox.information(None, u' ',  " You must choose a Module type")	

	def importInterPu (self):
		if self.key01 == True:
			if self.checkBoxMODAss.isChecked() or self.checkBoxMODSh.isChecked():
				key = True
				type_task = mod_folder
			elif self.checkBoxSHDAss.isChecked() or self.checkBoxSHDSh.isChecked():
				key = True
				type_task = shad_folder
			else:
				key = False
			if key:
				if self.tipo_Asset == char_folder or self.tipo_Asset == props_folder:  # si es rig o prop
					path = self.root  + self.projName + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + type_task + "/" + publish_folder + "/"
					path  = os.path.join( path,  self.AssetFileName + "_" + type_task + self.settin_list[5] )
				else:
					path = self.root + self.projName + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + publish_folder + "/"
					path  = os.path.join( path,  self.AssetFileName + self.settin_list[5] )
				if os.path.isfile( path ):
					importedObje = mc.file( path , i=True, uns = False , returnNewNodes = True)
					list = []
					for item in importedObje:
						list.append (str ("|" + str(item) ))
					list = mc.ls(list, type = "transform")
					allMain = mc.ls("|*")
					for o in  list:
						if o in allMain:
							folNa = mc.rename (o, o.split(self.AssetFileName + "_" + type_task + "_")[-1])
							if self.type_task == rig_folder:  # rig 
								mc.parent (folNa,self.RIGGEDASS_TEMPLATE[0])   # self.ANIM_TEMPLATE:
							elif sets_folder == self.tipo_Asset :
								if self.type_task == mod_folder:
									try:
										mc.parent (folNa , self.SET_TEMPLATE[1])  # self.
									except Exception:
										pass
							elif module_folder == self.tipo_Asset:
								if self.type_task == mod_folder:
									try:
										mc.parent (folNa , self.MODULE_TEMPLATE[1])  # self.
									except Exception:
										pass
				else:
					QMessageBox.information(None, u' Not Published  ', " Publish first, the internal asset task you have choosen" )	
			else:
				QMessageBox.information(None, u' No CheckBox choosen  ', "  Choose one import option" )	

	def textLoadSettings (self, root, sett01, sett02, sett03, sett04, sett05, sett06, sett07, sett08, sett09,sett12):
		texto = """PROJECT SETTINGS:\n\n\n Project Root:  %s \n\n FPS:  %s \n\n Project Resolution:  %s \n\n Preview Resolution:  %s \n\n Preview Format:  %s \n\n Color Management:  %s \n\n Maya Extension Files:  %s \n\n Maya Assets type tasks: %s  \n\n Maya Shots type tasks:  %s \n\n Nuke Shots type tasks:  %s \n\n 3D Render Root   %s """ %(root, sett01, sett02, sett03, sett04, sett05, sett06, sett07, sett08, sett09, sett12)
		return texto

	def selectAllDB (self, DBpath,table ):

		conn = sqlite3.connect ( DBpath)
		c = conn.cursor()
		query = 'SELECT * FROM %s;' %table
		c.execute(query)
		tuplasRows = c.fetchall()
		conn.close()
		return tuplasRows

	def selectAllDB_lessBlackL (self, DBpath,table ):

		conn = sqlite3.connect ( DBpath)
		c = conn.cursor()
		query = 'SELECT * FROM %s WHERE blackListed LIKE 0;' %table
		c.execute(query)
		tuplasRows = c.fetchall()
		conn.close()
		return tuplasRows

	def selectDbRow( self, DBpath,table , id):
		conn = sqlite3.connect ( DBpath)
		c = conn.cursor()
		query = 'SELECT * FROM %s WHERE id=?;' %table
		c.execute( query, (id,))
		row = c.fetchall()
		conn.close()
		return row

	def	getAllIDs(self, DBpath,table ):
		checkID_list = self.selectAllDB ( DBpath,table )
		id_list = []
		for id in checkID_list:
			id_list.append (id[0])
		return id_list

	def updateValueOnColumn( self, DBpath,table ,column,value, id):
		conn = sqlite3.connect ( DBpath)
		c = conn.cursor()	
		query = "UPDATE %s SET %s=? WHERE id=?" %(table,column)
		c.execute(query , (value,id))						
		conn.commit()
		conn.close()

	def tabAssetsTableUi(self):
		# tabla Assets
		self.getTableAsset()

		horizonTalButton=20
		# carga la tabla con Assets
		self.qButtLoadAssets = QPushButton(self.widAssets)
		self.qButtLoadAssets.setFont(self.newfont)
		self.qButtLoadAssets.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtLoadAssets.setGeometry(QtCore.QRect(20, horizonTalButton, 110, 41))
		self.qButtLoadAssets.setText(" Load Assets \n task Table")
		self.qButtLoadAssets.clicked.connect(self.load_asset_button)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtLoadAssets.setGraphicsEffect(shadow)


		# crea nuevos Assets
		self.qButtCreateAssets = QPushButton(self.widAssets)
		self.qButtCreateAssets.setFont(self.newfont)
		self.qButtCreateAssets.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 20px; border-style: groove; ")
		self.qButtCreateAssets.setGeometry(QtCore.QRect(140, horizonTalButton, 110, 41))
		self.qButtCreateAssets.setText(" Create Assets \n task")
		self.setButUsOnOff( self.qButtCreateAssets)
		self.qButtCreateAssets.clicked.connect(self.create_Asset_button)



		# refresh Assets button
		self.qButtRefreshAssT = QPushButton(self.widAssets)
		self.qButtRefreshAssT.setFont(self.newfont)
		self.qButtRefreshAssT.setEnabled(False)
		self.qButtRefreshAssT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px; border-style: groove")
		self.qButtRefreshAssT.setGeometry(QtCore.QRect(260, horizonTalButton, 120, 41))
		self.qButtRefreshAssT.setText(" Refresh Assets \n task Table")
		self.qButtRefreshAssT.clicked.connect(self.refresh_assets_table)
		
		
		
	    #  #   #   #   #   #    #     #    #    #    #    #    #    #
		###############################################################

		self.checkBShowAssBlackList = QCheckBox(self.widAssets)
		self.checkBShowAssBlackList.setGeometry(QtCore.QRect( 457, 28, 150, 41) )
		self.checkBShowAssBlackList.setText("BlackListed")
		self.checkBShowAssBlackList.setStyleSheet("color: rgb(210,135,20);")
		self.checkBShowAssBlackList.setChecked(False)
		#self.setButUsOnOff (self.checkBShowAssBlackList)
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			self.checkBShowAssBlackList.setEnabled(True)
		else:
			self.checkBShowAssBlackList.setEnabled(False)
		#######################################################
		self.labAssFilters = QLabel(self.widAssets)
		self.labAssFilters.setGeometry(QtCore.QRect(460, 10, 150, 15))
		self.labAssFilters.setText( " Filters: ")
		self.labAssFilters.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labAssFilters.setFont(self.newfont)


		self.labFiltAssType = QLabel(self.widAssets)
		self.labFiltAssType.setGeometry(QtCore.QRect(560, 10, 80, 30))
		self.labFiltAssType.setText( " asset type ")
		self.labFiltAssType.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterAssetType = QComboBox(self.widAssets)
		self.comboBfilterAssetType.setGeometry(QtCore.QRect(550, 40, 80, 20)) 
		self.comboBfilterAssetType.addItems(["All"] + asset_type_list)
		self.comboBfilterAssetType.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")

		self.labFiltAssStatus= QLabel(self.widAssets)
		self.labFiltAssStatus.setGeometry(QtCore.QRect(660, 10, 80, 30))
		self.labFiltAssStatus.setText( " status ")
		self.labFiltAssStatus.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterAssStatus = QComboBox(self.widAssets)
		self.comboBfilterAssStatus.setGeometry(QtCore.QRect(650, 40, 80, 20)) 
		self.comboBfilterAssStatus.addItems(["All"] + status_list + statusOnlySuperv_list) 
		self.comboBfilterAssStatus.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")


		self.labFiltAssTaskTy= QLabel(self.widAssets)
		self.labFiltAssTaskTy.setGeometry(QtCore.QRect(760, 10, 80, 30))
		self.labFiltAssTaskTy.setText( " task type ")
		self.labFiltAssTaskTy.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterAssTaskType = QComboBox(self.widAssets)
		self.comboBfilterAssTaskType.setGeometry(QtCore.QRect(750, 40, 80, 20))
		try:
			self.comboBfilterAssTaskType.addItems(["All"] + self.settin_list[6])
		except TypeError:
			self.comboBfilterAssTaskType.addItems(["All"] )
		self.comboBfilterAssTaskType.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")


		self.labFiltAsigned = QLabel(self.widAssets)
		self.labFiltAsigned.setGeometry(QtCore.QRect(860, 10, 80, 30))
		self.labFiltAsigned.setText( " assigned to ")
		self.labFiltAsigned.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterAsigned = QComboBox(self.widAssets)
		self.comboBfilterAsigned.setGeometry(QtCore.QRect(850, 40, 80, 20))
		self.comboBfilterAsigned.addItems(["All"] + self.usuarios_list + ["Set Artist"])
		self.comboBfilterAsigned.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")
		

		self.labFiltPublished = QLabel(self.widAssets)
		self.labFiltPublished.setGeometry(QtCore.QRect(960, 10, 80, 30))
		self.labFiltPublished.setText( " publish ")
		self.labFiltPublished.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterPublished= QComboBox(self.widAssets)
		self.comboBfilterPublished.setGeometry(QtCore.QRect(950, 40, 80, 20)) 
		self.comboBfilterPublished.addItems(["All", "Published", "Not Published"] )
		self.comboBfilterPublished.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	
		

		self.labFiltAsset = QLabel(self.widAssets)
		self.labFiltAsset.setGeometry(QtCore.QRect(1060, 10, 80, 30))
		self.labFiltAsset.setText( " asset name ")
		self.labFiltAsset.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")

		self.textEdFiltAsset  = QTextEdit(self.widAssets)
		self.textEdFiltAsset.setGeometry(QtCore.QRect(1050, 40, 90, 30))
		self.textEdFiltAsset.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0) ; border: 2px ridge gray; border-radius: 3px")
		
		#########################################################################
		# open scene button
		offserAlto = 30
		self.qButtOpenAsset = QPushButton(self.widAssets)
		self.qButtOpenAsset.setFont(self.newfont)
		self.qButtOpenAsset.setGeometry(QtCore.QRect(1185, 100 + offserAlto, 120, 40))
		self.qButtOpenAsset.setText(" Open ")
		self.qButtOpenAsset.setStyleSheet(" background-color: rgb(150,150,150) ; color: rgb(200,200,200) ;border-radius: 20px; border-style: groove")
		self.qButtOpenAsset.clicked.connect(self.openAssetBut)
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtOpenAsset.setGraphicsEffect(shadow)


		# save version Assets button
		self.qButtSaveAssetVers = QPushButton(self.widAssets)
		self.qButtSaveAssetVers.setFont(self.newfont)
		self.qButtSaveAssetVers.setGeometry(QtCore.QRect(1185, 160 + offserAlto, 120, 40))
		self.qButtSaveAssetVers.setText(" Save Version ")
		self.qButtSaveAssetVers.setStyleSheet(" background-color: rgb(150,150,150) ; color: rgb(200,200,200) ;border-radius: 20px; border-style: groove")
		self.qButtSaveAssetVers.clicked.connect(self.saveVersAssetBut)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtSaveAssetVers.setGraphicsEffect(shadow)


		self.qButtPublishAsset = QPushButton(self.widAssets)
		self.qButtPublishAsset.setFont(self.newfont)
		self.qButtPublishAsset.setGeometry(QtCore.QRect(1185, 220 + offserAlto, 120, 40))
		self.qButtPublishAsset.setText(" Publish ")
		self.qButtPublishAsset.setStyleSheet(" background-color: rgb(150,150,150) ; color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtPublishAsset.clicked.connect(self.publishAssetBut)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtPublishAsset.setGraphicsEffect(shadow)


		# publish-master Assets button
		self.qButImpInternalPAss = QPushButton(self.widAssets)
		self.qButImpInternalPAss.setFont(self.newfont)
		self.qButImpInternalPAss.setGeometry(QtCore.QRect(1250, 320+ offserAlto, 120, 40))
		self.qButImpInternalPAss.setText(" Import Internal \n Area Publish")
		self.qButImpInternalPAss.clicked.connect(self.importInterPu)
		self.qButImpInternalPAss.setEnabled(False)
		self.qButImpInternalPAss.setStyleSheet("background-color: rgb(100,75,100); color: rgb(140,140,140) ;border-radius: 4px ; border-style: groove")

		self.checkBoxMODAss = QCheckBox(self.widAssets)
		self.checkBoxMODAss.setGeometry(QtCore.QRect(1390, 320+ offserAlto, 120, 20))
		self.checkBoxMODAss.setText("MOD")
		self.checkBoxMODAss.stateChanged.connect(self.stateCheckChangeAss) 
		self.checkBoxMODAss.setStyleSheet("color: rgb(210,135,20)")

		self.checkBoxSHDAss = QCheckBox(self.widAssets)
		self.checkBoxSHDAss.setGeometry(QtCore.QRect(1390, 340+ offserAlto, 120, 20))
		self.checkBoxSHDAss.setText("SHD")
		self.checkBoxSHDAss.stateChanged.connect( self.stateCheckChange2Ass )
		self.checkBoxSHDAss.setStyleSheet("color: rgb(210,135,20)")

		self.checkBoxMODAss.setEnabled(False)
		self.checkBoxSHDAss.setEnabled(False)


		self.labSHeaderAs = QLabel(self.widAssets)
		self.labSHeaderAs.setGeometry(QtCore.QRect(1180, 54 + offserAlto , 285, 25))
		self.labSHeaderAs.setText( " ")
		self.labSHeaderAs.setStyleSheet("background-color: rgb(53,53,53); color: rgb(10, 170, 160) ;border-radius: 5px")


		self.labSceneAssetName = QLabel(self.widAssets)
		self.labSceneAssetName.setGeometry(QtCore.QRect(1180, 54 + offserAlto , 285, 25))
		self.labSceneAssetName.setText( " ")
		self.labSceneAssetName.setFont(self.newfont)
		self.labSceneAssetName.setStyleSheet("background-color: rgb(53,53,53); color: rgb(10, 170, 160) ;border-radius: 5px")
		self.labSceneAssetName.hide()

		self.labSceneAssetVers = QLabel(self.widAssets)
		self.labSceneAssetVers.setGeometry(QtCore.QRect(1330, 160 + offserAlto, 200, 40))
		self.labSceneAssetVers.setText( "v001")
		self.labSceneAssetVers.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		self.labSceneAssetVers.setFont(self.newfont)
		self.labSceneAssetVers.hide()

		# publish date
		self.labPublishAssetDate = QLabel(self.widAssets)
		self.labPublishAssetDate.setGeometry(QtCore.QRect(1330, 220 + offserAlto, 150, 40))
		self.labPublishAssetDate.setText( " ")
		self.labPublishAssetDate.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		self.labPublishAssetDate.setFont(self.newfont)
		self.labPublishAssetDate.hide()

		self.labSceAssetisLOcked = QLabel(self.widAssets)
		self.labSceAssetisLOcked.setGeometry(QtCore.QRect(1415, 5, 50, 50))
		self.image = QPixmap ( self.root + self.projName + '/PIPELINE/padlock.png')
		self.labSceAssetisLOcked.setPixmap (self.image)
		self.labSceAssetisLOcked.hide()

	def stateCheckChangeAss(self):
		if self.checkBoxMODAss.isChecked():
			self.checkBoxMODSh.setChecked(True)
			self.checkBoxSHDAss.setChecked(False)
			self.checkBoxSHDSh.setChecked(False)

	def stateCheckChange2Ass(self):
		if self.checkBoxSHDAss.isChecked():		
			self.checkBoxSHDSh.setChecked(True)
			self.checkBoxMODAss.setChecked(False)
			self.checkBoxMODSh.setChecked(False)

	def stateCheckChangeSh(self):
		if self.checkBoxMODSh.isChecked():
			self.checkBoxMODAss.setChecked(True)
			self.checkBoxSHDAss.setChecked(False)
			self.checkBoxSHDSh.setChecked(False)

	def stateCheckChange2Sh(self):
		if self.checkBoxSHDSh.isChecked():		
			self.checkBoxSHDAss.setChecked(True)
			self.checkBoxMODAss.setChecked(False)
			self.checkBoxMODSh.setChecked(False)

	def tabAssManipLabOff(self):
		self.labSceneAssetName.hide()
		self.labSceneAssetVers.hide()
		self.labPublishAssetDate.hide()
		self.labSceAssetisLOcked.hide()
		self.labSceneAssetName.setText("")
		self.labSceneAssetVers.setText("")
		self.labPublishAssetDate.setText("")

	def currentRowText(self,tabla ,index_column):
		texto = tabla.item( tabla.currentRow(),index_column)   # el index de la columna de lo que quiera saber
		texto = str (texto.text())
		return texto

	def load_asset_button(self):   #este metodo dispara  menuAssetDespleg()
		self.key_loadAss = True
		self.refresh_assets_table()
		self.tablaWidgAssets.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tablaWidgAssets.customContextMenuRequested.connect(self.menuAssetDespleg)
		self.tablaWidgAssets.itemSelectionChanged.connect( lambda: self.changeSeletedAssetRowColor ( self.tablaWidgAssets, [1,2,3,4,5,6,7,8], self.rowsAssBlackListed, self.rowsAssLockedList))
		self.qButtRefreshAssT.setEnabled(True)
		self.qButtRefreshAssT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtRefreshAssT.setGraphicsEffect(shadow)
		
		self.qButtLoadAssets.setEnabled(False)
		self.qButtLoadAssets.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px ; border-style: groove")
		
		shadow = QGraphicsDropShadowEffect(self)
		shadow.setEnabled(False)
		self.qButtLoadAssets.setGraphicsEffect(shadow)
		
	# al crear la sequencia solo caracteres numericos
	def create_Asset_button(self):
		key = []
		lsTemplatAssets = os.listdir(self.root  + self.projName + "/PIPELINE/TEMPLATES/ASSET/"	)
		#remove "ANIM_TEMPLATE",
		for temple in mayaTemListNa:
			if temple != animTamplate and temple != litTempla:
				if temple + self.settin_list[5]  not in lsTemplatAssets:
					key.append (temple + self.settin_list[5])
		if masterPass != "unable":
			if len (key) < 1 :
				winCreaAsset = createAssetWin()
				winCreaAsset.WinCA.show()
				#try:
				if winCreaAsset.exec_():
					print " "
				#except Exception:
				#	pass
			else:
				QMessageBox.information(None, u' Missing Templates', str (key))

	def refreshAssDB (self):
		query ='SELECT * FROM assets'
		counter = 0
		if str(self.comboBfilterAssetType.currentText()) == "All":
			assType = "%"
		else:
			assType = str(self.comboBfilterAssetType.currentText())
			query = query + ' WHERE asset_type LIKE "%s" ' %assType
			counter = counter + 1 
		if self.comboBfilterAssStatus.currentText() == "All":
			status = "%"
		else:
			status = str(self.comboBfilterAssStatus.currentText())
			if counter > 0:
				query = query + ' AND status LIKE "%s" ' %status
				counter = counter + 1 
			else:
				query = query + ' WHERE status LIKE "%s" ' %status
				counter = counter + 1 
		if self.comboBfilterAssTaskType.currentText() == "All":
			task = "%"
		else:
			task = str(self.comboBfilterAssTaskType.currentText())
			if counter > 0:
				query = query + ' AND task_type LIKE "%s" ' %task
				counter = counter + 1 
			else:
				query = query + ' WHERE task_type LIKE "%s" ' %task
				counter = counter + 1
		if self.comboBfilterAsigned.currentText() == "All":
			userName = "%"
		else:
			userName =  str(self.comboBfilterAsigned.currentText())
			if counter > 0:
				query = query + ' AND asignado LIKE "%s" ' %userName
				counter = counter + 1 
			else:
				query = query + ' WHERE asignado LIKE "%s" ' %userName
				counter = counter + 1 
		if self.comboBfilterPublished.currentText() == "All":
			published = "%"
		else:
			published = str( self.comboBfilterPublished.currentText())
			if published == "Published":
				bool = 1
			else:
				bool = 0
			if counter > 0:
				query = query + ' AND isPublished LIKE %s ' %bool
				counter = counter + 1 
			else:
				query = query + ' WHERE isPublished LIKE %s ' %bool
				counter = counter + 1				
		if str(self.textEdFiltAsset.toPlainText()) == "":
			assName = "%"
		else:
			assName = str(self.textEdFiltAsset.toPlainText()) + "%"
			if counter > 0:
				query = query + ' AND asset_name LIKE "%s" ' %assName
				counter = counter + 1
			else:
				query = query + ' WHERE asset_name LIKE "%s" ' %assName
				counter = counter + 1

		if not self.checkBShowAssBlackList.isChecked ():
			if counter > 0:
				query = query + ' AND blackListed LIKE %s ' %0
			else:
				query = query + ' WHERE blackListed LIKE %s ' %0
		else:
			if counter > 0:
				query = query + ' AND blackListed LIKE %s' %1
			else:
				query = query + ' WHERE blackListed LIKE %s' %1		

		query = query + ' ;'
		self.dbAsInformLoaded = self.selectAllDB ( self.projectDataBase,"assets" )
		conn = sqlite3.connect ( self.projectDataBase )
		c = conn.cursor()
		c.execute(query)
		self.dbAsInformFiltered = c.fetchall()   #  en formato de lista de tuplas
		conn.close()

	def refresh_assets_table (self):
		self.refreshAssDB ()
		self.tablaWidgAssets.setRowCount(len(self.dbAsInformFiltered ))
		self.tablaWidgAssets.setColumnCount(10)     #  setea la cantidad de columnas!!!!!
		for i, header in enumerate (['Thumbnail','Asset Type','Asset',"Nice_Name" , 'Task_Type', 'Comments', "Assigned", "ID" , "Status" ,"\n "]):
			locals()["item"+ str(i)] = QTableWidgetItem(header)
			#locals()["item"+ str(i)].setBackground(QColor(5, 40, 40))
			locals()["item"+ str(i)].setBackground(QColor( 100, 65, 100 ) )
						
			self.tablaWidgAssets.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )
		
		#################  columnas      0           1          2         3              4           5           6           7          8     
		
		################# DB_column      1           2          3         4              5           6           8           0          7
		self.idAss_column_idx = 7
		self.thumnbAss_column_idx = 0
		self.assetType_column_idx = 1
		self.asset_column_idx = 2
		self.niceAssName_column_idx = 3
		self.taskAssType_column_idx = 4
		self.statusAss_column_idx = 8
		self.commentAss_column_idx = 5
		self.asignAss_column_idx = 6
		self.tablaWidgAssets.setColumnWidth(9, 1)
		self.tablaWidgAssets.setColumnWidth(self.thumnbAss_column_idx, 180)
		self.tablaWidgAssets.setColumnWidth(self.commentAss_column_idx, 316)   #  seteo el ancho en la columna de comentarios
		self.tablaWidgAssets.setColumnWidth(self.idAss_column_idx, 50)
		self.tablaWidgAssets.setColumnWidth(self.taskAssType_column_idx, 79)
		self.tablaWidgAssets.setColumnWidth(self.asset_column_idx, 100)
		self.tablaWidgAssets.setColumnWidth(self.assetType_column_idx, 80)
		self.tablaWidgAssets.setColumnWidth(self.niceAssName_column_idx, 90)
		self.tablaWidgAssets.setColumnWidth(self.statusAss_column_idx, 120)
		self.rowsAssLockedList = []
		self.rowsAssBlackListed = []
		for i,dbCellData in enumerate(self.dbAsInformFiltered ):
			self.tablaWidgAssets.setRowHeight(i, 120)
			id = str(dbCellData[0]) #  es el index en la base de datos
			assetType = str(dbCellData[2])
			aName = str(dbCellData[3])
			niceName = str(dbCellData[4])
			task_type = str(dbCellData[5])
			status = str(dbCellData[7])
			comentarios = str(dbCellData[6])
			artist = str(dbCellData[8])
			self.isLocked = str(dbCellData[12])
			self.tablaWidgAssets.setCellWidget(i, self.thumnbAss_column_idx, getThumbnClass(self, self.labRootProjectPath.text() + "/" + self.projName + assetMayaFol + assetType + "/" + aName + "/" + aName  + "_thumbnail.jpg" ))

			dBidexList = [id, assetType, aName  , niceName , task_type , status, comentarios, artist]
			tableColumIndlist = [self.idAss_column_idx, self.assetType_column_idx, self.asset_column_idx, self.niceAssName_column_idx, self.taskAssType_column_idx, self.statusAss_column_idx, self.commentAss_column_idx, self.asignAss_column_idx]
			for idx, column in enumerate (tableColumIndlist):
				item = QTableWidgetItem(dBidexList[idx])
				if i % 2 == 0:
					item.setBackground(QBrush(QColor(200, 200, 200)))
				else:
					item.setBackground(QBrush(QColor(180, 180, 190)))
				item.setForeground(QBrush(QColor(0, 0, 0)))					
				if column == self.statusAss_column_idx:
				
					labStatus = QLabel(dBidexList[idx])
					labStatus.setGeometry(QtCore.QRect( 0 , 0, 120, 20))
					labStatus.setAlignment(QtCore.Qt.AlignCenter)
					
					if status_list[0] == item.text():
						labStatus.setStyleSheet("background-color: rgb(190, 90, 90); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 15px; border-style: solid;")
					if status_list[1] == item.text():
						labStatus.setStyleSheet("background-color: rgb(150, 215, 150); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
					if status_list[2] == item.text():
						labStatus.setStyleSheet("background-color: rgb(210, 210, 120); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
					if status_list[3] == item.text():
						labStatus.setStyleSheet("background-color: rgb(170, 205, 220); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
					if statusOnlySuperv_list [0]  == item.text():
						labStatus.setStyleSheet("background-color: rgb(80, 190, 80); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
					self.tablaWidgAssets.setCellWidget(i ,column, labStatus)
					
				if column == self.asset_column_idx:
					item.setForeground(QBrush(QColor(180, 110, 45)))
				if column == self.asignAss_column_idx:
					if "Set Artist" != item.text():
						item.setForeground(QBrush(QColor(175, 50, 175)))
				if column == self.taskAssType_column_idx:
					item.setFont(self.newfont2)
					try:
						if item.text() == self.settin_list[6][0]:
							item.setForeground(QBrush(QColor(70, 175, 145)))
						elif item.text() == self.settin_list[6][1]:
							item.setForeground(QBrush(QColor(175, 70, 145)))
						elif item.text() == self.settin_list[6][2]:
							item.setForeground(QBrush(QColor(60, 90, 175)))
						elif item.text() == self.settin_list[6][3]:
							item.setForeground(QBrush(QColor(170, 170, 80)))
						elif item.text() == self.settin_list[6][4]:
							item.setForeground(QBrush(QColor(25, 160, 160)))
					except:
						pass				
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				self.tablaWidgAssets.setItem(i ,column, item)
				if int(self.isLocked) == 1 and  self.userName != self.dbAsInformFiltered[i][8] :
					self.rowsAssLockedList.append(i)
					self.tablaWidgAssets.item(i, column).setBackground(QColor(125,125,125))
					self.tablaWidgAssets.item(i, column).setForeground(QColor(150,150,150))
				if self.dbAsInformFiltered[i][13] == 1 :
					self.rowsAssBlackListed.append(i)
					self.tablaWidgAssets.item(i, column).setBackground(QColor(45,45,43))
					self.tablaWidgAssets.item(i, column).setForeground(QColor(125,125,125))
		curreRow = self.tablaWidgAssets.currentRow()
		if curreRow == None or curreRow == -1:
			if 0 not in self.rowsAssBlackListed:
				self.tablaWidgAssets.setCurrentCell(0,9)
		else:
			if curreRow not in self.rowsAssBlackListed:
				self.tablaWidgAssets.setCurrentCell(curreRow,9)
				
	def thumbMayanailCommand(self, h,w, path, name):
		frame = mc.currentTime(q=1)
		currentPanel = mc.playblast( ae = True )
		mc.modelEditor (currentPanel, edit = True, grid = False, hud = False  ,alo = False)
		mc.modelEditor (currentPanel, edit = True, polymeshes = True,str = True , da = "smoothShaded")
		mc.setAttr ('defaultRenderGlobals.imageFormat', 8)
		mc.playblast( format = "image", cf = path + "/" + name , h = h, w = w, fr = [frame], viewer = False, orn = False, fp = 0, fo = True, p = 100, qlt = 100)

	def lockAssetsAction(self):

		curreRow = self.tablaWidgAssets.currentRow()
		currentID = self.tablaWidgAssets.item( curreRow,self.idAss_column_idx)  # saber el id
		currentID = currentID.text()
		self.updateValueOnColumn( self.projectDataBase ,"assets" ,"isLocked",1, currentID)
		self.key03 = True
		assetName = self.labSceneAssetName.text().split("   ")
		type_asset = self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)		
		name = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)
		type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
		self.refresh_assets_table ()		
		if self.key01 and assetName[0]==type_asset and assetName[1]== name and assetName[2]== type_task:
			self.labSceAssetisLOcked.show()
			self.labSceShotisLOcked.show()
		else:
			QMessageBox.information(None, u' Locked ', "  " + type_asset + "  " +  name + "  " + type_task + "  Locked !!!  ( is not actually  Opened Scene )" )

	def unlockAssetsAction(self):
		curreRow = self.tablaWidgAssets.currentRow()
		currentID = self.tablaWidgAssets.item( curreRow,self.idAss_column_idx)  # saber el id
		currentID = currentID.text()
		self.updateValueOnColumn( self.projectDataBase ,"assets" ,"isLocked",0, currentID)
		assetName = self.labSceneAssetName.text().split("   ")
		type_asset = self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)		
		name = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)
		type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
		self.refresh_assets_table ()
		if self.key01 and assetName[0]==type_asset and assetName[1]== name and assetName[2]== type_task:
			self.labSceAssetisLOcked.hide()
			self.labSceShotisLOcked.hide()
		else:
			QMessageBox.information(None, u' Unocked ', "  " + type_asset + "  " +  name + "  " + type_task + "  Unocked !!!  ( is not actually  Opened Scene )" )
	
	def openAssetBut (self):
		self.dbIdx_isPublishAss = 10
		self.dbIdx_datePublisAss = 11
		self.dbIdx_isLockedAss = 12
		self.labSceAssetisLOcked.hide()
		self.labSceShotisLOcked.hide()
		type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
		if type_task in self.settin_list[6]:
			items_list = self.tablaWidgAssets.selectedItems()
			selectedRow=[]
			for i in  items_list:
				selectedRow.append ( i.row())
			if selectedRow == []:
				QMessageBox.warning(None, u' ', " Select at least one row task")
			elif len (selectedRow) > 1:
				QMessageBox.warning(None, u' ', " Select only one row task")
			elif len (selectedRow) == 1:
				self.open_ver_row = selectedRow [0]
				if self.userName != "None":
					self.idd = self.currentRowText(self.tablaWidgAssets ,self.idAss_column_idx)
					dbRowShLoaded = self.selectDbRow( self.projectDataBase,"assets" , self.idd  )	
					if dbRowShLoaded[0][12] == 1: #or self.key03 == True :
						if  self.userName ==  self.tablaWidgAssets.item( selectedRow[0], self.asignAss_column_idx ).text(): #or self.tablaWidgAssets.item( selectedRow[0], self.asignAss_column_idx ).text() == "Set Artist":
							self.openAss ()
							self.labSceAssetisLOcked.show()
							self.labSceShotisLOcked.show()
						else:
							QMessageBox.warning(None, u' ', " Scene Locked ")
					elif  self.dbAsInformFiltered[ selectedRow [0] ] [self.dbIdx_isLockedAss] == 0:
						self.openAss ()
				else:
					QMessageBox.warning(None, u'No User ', " None User Can not Open Scenes")
		else:
			QMessageBox.warning(None, u' ', "Choose Task Type First")

	def openAss (self):
		self.current = self.tablaWidgAssets.currentRow()
		self.scripJCounter1 = self.scripJCounter1 + 1
		self.wind.setWindowTitle("Pr-G  Manager" )
		#self.tabShManipLabOff()
		self.key04 = False
		self.key01 = True
		self.checkBoxMODSh.setEnabled(True)	 #checkBoxSHDSh
		self.checkBoxSHDSh.setEnabled(True)
		self.AssetFileName = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)
		self.tipo_Asset = self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)
		self.type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
		self.assetPath =  self.root  + self.projName + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + self.type_task + "/" + version_folder
		file_list =  glob.glob (self.assetPath + "/" + self.AssetFileName + "_" + self.type_task + "_v*" + self.settin_list[5] )
		mc.file( file_list[-1] ,o = True , force = True )
		self.labSceneAssetName.setText( self.tipo_Asset  + "   " + self.AssetFileName + "   " + self.type_task )
		self.labSceneShotName.setText( self.tipo_Asset  + "   " + self.AssetFileName + "   " + self.type_task )
		self.wind.setWindowTitle("Pr-G  Manager" + "     " + self.tipo_Asset  + " " + self.AssetFileName + " " + self.type_task )
		self.labSceneAssetName.show()
		self.labSceneShotName.show()		
		self.labSceneAssetVers.setText( "_v" + file_list[-1].split("_v")[-1].split(self.settin_list[5])[0])
		self.labSceneShotVers.setText( "_v" + file_list[-1].split("_v")[-1].split(self.settin_list[5])[0])
		self.labSceneAssetVers.show()
		self.labSceneShotVers.show()
		self.dbRowAssLoaded = self.selectDbRow( self.projectDataBase,"assets" , self.idd )
		self.labPublishAssetDate.show()
		self.labPublishShotDate.show()
		
		self.qButImpInternalPAss.setEnabled(True)
		self.qButImpInternalPAss.setStyleSheet("background-color: rgb(85,30,85); color: rgb(250,250,250) ;border-radius: 4px ; border-style: groove")
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButImpInternalPAss.setGraphicsEffect(shadow)
		
		self.qButImpInternalPSh.setEnabled(True)
		self.qButImpInternalPSh.setStyleSheet("background-color: rgb(85,30,85); color: rgb(250,250,250) ;border-radius: 4px ; border-style: groove")
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButImpInternalPSh.setGraphicsEffect(shadow)

		self.checkBoxMODAss.setEnabled(True)	 #checkBoxSHDSh
		self.checkBoxSHDAss.setEnabled(True)
		self.checkBoxMODSh.setEnabled(True)	 #checkBoxSHDSh
		self.checkBoxSHDSh.setEnabled(True)
		
		if self.dbRowAssLoaded[0][self.dbIdx_isPublishAss] == 0:
			self.labPublishAssetDate.setText( "Not Published" )
			self.labPublishShotDate.setText( "Not Published" )
		else:
			date = self.dbRowAssLoaded[0][self.dbIdx_datePublisAss]
			time = "  last publish: \n " + date
			self.labPublishAssetDate.setText( time )
			self.labPublishShotDate.setText( time )

	def saveVersAssetBut (self):
		if self.key01 == True:
			if  self.dbRowAssLoaded[ 0 ] [self.dbIdx_isLockedAss] == 0:
				self.saveVersAss ()
			elif self.dbRowAssLoaded[ 0 ] [self.dbIdx_isLockedAss] == 1 and  self.userName ==  self.tablaWidgAssets.item( self.open_ver_row, self.asignAss_column_idx ).text():
				self.saveVersAss ()
			else:
				QMessageBox.warning(None, u' ', " Scene Locked")

	def saveVersAss (self):
		current_fps = mc.currentUnit(query=True, time=True)
		if current_fps == "game": 
			current_fps = "15"
		elif current_fps == "film":
			current_fps = "24"
		elif current_fps == "pal": 
			current_fps = "25" 
		elif current_fps == "ntsc": 
			current_fps = "30" 
		elif current_fps == "show": 
			current_fps = "48" 
		elif current_fps == "palf": 
			current_fps = "50"
		elif current_fps == "ntscf": 
			current_fps = "60" 
		if self.settin_list [0] != current_fps:
			QMessageBox.warning(None, u' take care ', " Be carefull, frame rate setting is not: " + self.settin_list [0]  + " fps")
		list = glob.glob (self.generatePath()[0] + "/*" + self.settin_list [0])
		checlList=[]
		for i, obj in enumerate (list):
			for idx in range (len(list)):
				if obj != list[idx]:
					checlList.append(list[idx-1])
		wversion = doVersionClass() 
		version = wversion.execution(self.settin_list [5], self.generatePath()[0], self.generatePath()[1] )
		self.labSceneAssetVers.show()
		self.labSceneAssetVers.setText(version)
		self.labSceneShotVers.show()
		self.labSceneShotVers.setText(version)
		
	def publishAssetBut (self):
		if self.key01 == True:
			if  self.dbRowAssLoaded[0] [self.dbIdx_isLockedAss] == 0:
				self.publiAssDb()
				
			elif self.dbRowAssLoaded[ 0 ] [self.dbIdx_isLockedAss] == 1 and  self.userName ==  self.tablaWidgAssets.item( self.open_ver_row, self.asignAss_column_idx ).text():
				self.publiAssDb()
				
			else:
				QMessageBox.warning(None, u' ', " Scene Locked")

	def publiAssDb(self):
		assPublish =  publishAssetClass()
		if self.tipo_Asset == char_folder or self.tipo_Asset == props_folder:
			if self.type_task == rig_folder:   #  esto pregunta si no esta en la etapa rig
				path = self.root  + self.projName + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + self.type_task + "/" + publish_folder + "/"
				name = self.AssetFileName
				key = True
			else:
				path = self.root  + self.projName  + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + self.type_task + "/" + publish_folder + "/"
				name = self.AssetFileName +"_" + self.type_task
				key = False
		elif self.tipo_Asset == sets_folder or self.tipo_Asset == module_folder:
			path = self.root + self.projName + assetMayaFol + self.tipo_Asset  + "/" + self.AssetFileName + "/" + self.type_task + "/" + publish_folder + "/"
			name = self.AssetFileName
			key = True			
		executionSucces = assPublish.execution( path , name, self.settin_list [5])
		if executionSucces:
			QMessageBox.information(None, u' ',  " Succes!! Asset Published!!!!  ")
			now = datetime.now()
			assDate = str (now.day) + " / "+ str(now.month) +" __ "+ str(now.hour) + ":" + str(now.minute)
			time = "  last publish: \n " + assDate
			self.updateValueOnColumn( self.projectDataBase ,"assets" ,"isPublished",1, self.idd)			
			self.updateValueOnColumn( self.projectDataBase ,"assets" ,"lastPublishDate",assDate, self.idd)
			
			self.labPublishAssetDate.show()
			self.labPublishAssetDate.setText( time)	
			self.labSceneAssetVers.show()
			self.labSceneAssetVers.setText("Publish Version\n   -not editable-")
			
			self.labPublishShotDate.show()
			self.labPublishShotDate.setText( time)	
			self.labSceneShotVers.show()
			self.labSceneShotVers.setText("Publish Version\n   -not editable-")			
			
			mensaje = "    Just Published :    " + self.AssetFileName + "_" + self.type_task + "    !!!!!! "
			self.slackBot( mensaje, self.settin_list[10] )
			if key and  parchePB_Copy2publiFol :
				if not os.path.exists(self.root  + self.projName + assetMayaFol + publish_folder_alternativePB.split("/")[-1] + "/"+self.tipo_Asset +"/"+self.AssetFileName+"/" ):
					os.makedirs(self.root  + self.projName + assetMayaFol + publish_folder_alternativePB.split("/")[-1] + "/" + self.tipo_Asset + "/" + self.AssetFileName + "/" )
				shutil.copy2( os.path.join( path , name+self.settin_list[5] ), os.path.join( self.root  + self.projName + assetMayaFol + publish_folder_alternativePB.split("/")[-1] + "/" + self.tipo_Asset + "/" +self.AssetFileName + "/" ,  name + self.settin_list [5] ) )

		else:
			print "publishing failiture"

	def openFolder(self,path):
		os.startfile(path)

	def textDone(self, qtable, db_table,dbColumnName, textEdit, column_idx, ID_column_idx , rowsLockedList, rowsBlackListed):
		texto = str(textEdit.toPlainText())
		item = QTableWidgetItem(texto)
		item.setTextAlignment(QtCore.Qt.AlignCenter)
		if qtable.currentRow() in rowsLockedList :
			item.setBackground(QColor(125,125,125))
			item.setForeground(QColor(150,150,150))
		else:
			if qtable.currentRow() % 2 == 0:
				item.setBackground(QBrush(QColor(200, 200, 200)))
			else:
				item.setBackground(QBrush(QColor(180, 180, 190)))		
		
			item.setForeground(QBrush(QColor(0, 0, 0)))
		if qtable.currentRow() in rowsBlackListed :
			item.setBackground(QColor(45,45,43))
			item.setForeground(QColor(125,125,125))			
		qtable.setItem( qtable.currentRow(), column_idx, item ) 
		currentID = qtable.item( qtable.currentRow(),ID_column_idx)  # saber el id
		self.updateValueOnColumn( self.projectDataBase ,db_table ,dbColumnName,texto, currentID.text())
	
	def colorizeRows (self, row, item, rowsBlackListed, rowsLockedList):
		if row % 2 == 0:
			item.setBackground(QBrush(QColor(200, 200, 200)))
		else:
			item.setBackground(QBrush(QColor(180, 180, 190)))
		item.setForeground(QBrush(QColor(0, 0, 0)))
		if row in rowsLockedList:
			item.setBackground(QColor(125,125,125))
			item.setForeground(QColor(150,150,150))
		if row in rowsBlackListed:
			item.setBackground(QColor(45,45,43))
			item.setForeground(QColor(125,125,125))

	def textAssNiceName(self, textEdit):
		assetName =  self.currentRowText(self.tablaWidgAssets , self.asset_column_idx)
		assetType =  self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)
		texto = str(textEdit.toPlainText())
		for i, tupla in enumerate ( self.dbAsInformLoaded):
			if tupla[3] == assetName and tupla[2] and assetType :
				id = tupla[0]
				self.updateValueOnColumn( self.projectDataBase ,"assets" ,"nice_name",texto, id)
		for i, tupla in enumerate ( self.dbAsInformFiltered):
			if tupla[3] == assetName and tupla[2] and assetType :
				item = QTableWidgetItem(texto)
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				self.colorizeRows (i, item, self.rowsAssBlackListed, self.rowsAssLockedList)				
				self.tablaWidgAssets.setItem( i, self.niceAssName_column_idx, item ) 

	def blackListItemAsset (self, dbTable, dbColumn, value, currentID):
		self.updateValueOnColumn( self.projectDataBase,dbTable,dbColumn,value,currentID )
		self.refresh_assets_table()
	
	def menuAssetDespleg(self, position):  # menu flotante que se despliega con clic derecho en las celdas
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			key01 = True
			key02 = True
		else:
			key01 = False
			if self.userName ==  self.currentRowText(self.tablaWidgAssets , self.asignAss_column_idx):
				key02 = True
			else:
				key02 = False
		items_list = self.tablaWidgAssets.selectedItems()
		selectedRow=[]
		for i in  items_list:
			selectedRow.append ( i.row())
		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Status':
			if key01 or key02:
				if self.userName in self.lideres_list:
					self.status_list = status_list + statusOnlySuperv_list
				else:
					if self.userName ==  self.currentRowText(self.tablaWidgAssets , self.asignAss_column_idx) or self.userName in self.productores_list:
						self.status_list = status_list
					else:
						self.status_list = []
				menuAss02 = QMenu()
				menuAss02.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				for status in self.status_list:
					statusAction = menuAss02.addAction(status)			
				actionAss02 = menuAss02.exec_(self.tablaWidgAssets.mapToGlobal(position))
				if actionAss02 != None :  # es un objeto
					#curreRoww = self.tablaWidgAssets.currentRow()
					mensaje = ""
					idtuple = [str(actionAss02.text())]
					query = "UPDATE assets SET status=? WHERE id IN ("
					for i, curreRow in enumerate(selectedRow) :
						item = QTableWidgetItem(actionAss02.text())
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						
						labStatus = QLabel(actionAss02.text())
						labStatus.setGeometry(QtCore.QRect( 0 , 0, 100, 20))
						labStatus.setAlignment(QtCore.Qt.AlignCenter)						
						
						self.tablaWidgAssets.setItem( curreRow,self.statusAss_column_idx, item )
						self.tablaWidgAssets.setCellWidget(curreRow ,self.statusAss_column_idx, labStatus)

						if status_list[0] == item.text():
							labStatus.setStyleSheet("background-color: rgb(190, 90, 90); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 15px; border-style: solid;")
						if status_list[1] == item.text():
							labStatus.setStyleSheet("background-color: rgb(150, 215, 150); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")

						if status_list[2] == item.text():
							labStatus.setStyleSheet("background-color: rgb(210, 210, 120); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
						if status_list[3] == item.text():																
							labStatus.setStyleSheet("background-color: rgb(170, 205, 220); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")
							
						if statusOnlySuperv_list[0] == item.text():
							labStatus.setStyleSheet("background-color: rgb(80, 190, 80); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 60px; padding: 5px; border-style: solid;")

						if curreRow in self.rowsAssLockedList:
							self.tablaWidgAssets.item(curreRow, self.statusAss_column_idx).setBackground(QColor(125,125,125))
							self.tablaWidgAssets.item(curreRow, self.statusAss_column_idx).setForeground(QColor(150,150,150))
							
						if curreRow in self.rowsAssBlackListed:
							self.tablaWidgAssets.item(curreRow, self.statusAss_column_idx).setBackground(QColor(45,45,43))
							self.tablaWidgAssets.item(curreRow, self.statusAss_column_idx).setForeground(QColor(125,125,125))
						currentID = self.tablaWidgAssets.item( curreRow,self.idAss_column_idx)  # saber el id
						currentID = currentID.text()
	
						if i < len(selectedRow) -1:
							query = query + " ?, "
						elif i == len(selectedRow) -1:
							query = query + " ? "
						idtuple.append (int (currentID))
						#self.updateValueOnColumn( self.projectDataBase ,"assets" ,"status",actionAss02.text(), currentID)
						type_task = self.tablaWidgAssets.item( curreRow,self.taskAssType_column_idx) 
						asset = self.tablaWidgAssets.item( curreRow,self.asset_column_idx)   # el index de la columna de lo que quiera saber	
						mensaje = mensaje + "     " +  str (asset.text())	 +"   "+ str(type_task.text())+"  is " + actionAss02.text() + " ...\n"
					query = query + "); "
					idtuple = tuple( idtuple )
					conn = sqlite3.connect ( self.projectDataBase )
					c = conn.cursor()	
					c.execute( query, idtuple )
					conn.commit()
					conn.close()
					nombre =  self.currentRowText(self.tablaWidgAssets ,self.asignAss_column_idx)
					self.slackBot( mensaje, self.diccUsSlack [ nombre ] )
					self.slackBot( mensaje, self.settin_list[10] )
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
				
			def updateValueOnColumn( self, DBpath,table ,column,value, id):
				conn = sqlite3.connect ( DBpath)
				c = conn.cursor()	
				query = "UPDATE %s SET %s=? WHERE id=?" %(table,column)
				c.execute(query , (value,id))						
				conn.commit()
				conn.close()

		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Comments':
			if key02 == True :
				menuAss00 = QMenu()
				menuAss00.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				commentAction = menuAss00.addAction("                                    Done",lambda: self.textDone(self.tablaWidgAssets, "assets","comments", self.textEdCommAss, self.commentAss_column_idx, self.idAss_column_idx, self.rowsAssLockedList, self.rowsAssBlackListed ))
				self.textEdCommAss  = QTextEdit(menuAss00)
				self.textEdCommAss.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdCommAss.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionAss00 = menuAss00.exec_(self.tablaWidgAssets.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Nice_Name':
			if key02:
				menuAssNice = QMenu()
				menuAssNice.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				niceAction = menuAssNice.addAction("                                    Done", lambda : self.textAssNiceName( self.textEdNiceNamAss ) )
				self.textEdNiceNamAss  = QTextEdit(menuAssNice)
				self.textEdNiceNamAss.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionAssNice = menuAssNice.exec_(self.tablaWidgAssets.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
		
		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Asset':
			if self.userName != "None":
				menuAss01 = QMenu()
				menuAss01.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				currentID = self.currentRowText(self.tablaWidgAssets ,self.idAss_column_idx)
				dbRowAssLoaded = self.selectDbRow( self.projectDataBase,"assets" , currentID)
				if key01:
					if dbRowAssLoaded[0][13] == 0:
						blackLAction = menuAss01.addAction("BlackList task", lambda : self.blackListItemAsset( "assets","blackListed",1,currentID ) )
					elif dbRowAssLoaded[0][13] == 1:
						blackLAction = menuAss01.addAction("WhiteList task", lambda : self.blackListItemAsset( "assets","blackListed",0,currentID ) )
				if dbRowAssLoaded[0][10] == 1:
					isPublishAction = menuAss01.addAction("Published:  " + dbRowAssLoaded[0][11] )
				else:
					isPublishAction = menuAss01.addAction("Not Published ")
				doThumbnailAction = menuAss01.addAction("Do Thumbnail",self.clickedAssetThumb)
				doThumbImagAction = menuAss01.addAction("Do Image Thumb",self.clickedAssetImageThumb )
				type_asset= self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)	
				type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
				asset = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)	
				assetPath =  win.root + win.projName  + assetMayaFol + type_asset  + "/" + asset + "/" + type_task + "/" 
				exploreAction = menuAss01.addAction("Explore", lambda: self.openFolder(assetPath))
				try:
					name = str(self.labSceneShotName.text())
				except Exception:
					name = " "
				if len(name.split("   ") ) == 2 or len(name.split("_SUB") ) == 2 :    #"_SUB"
					if name.split("   ")[-1] == anim_fol or name.split("   ")[-1] == layout_fol or name.split("   ")[-1].startswith( anim_fol) or name.split("   ")[-1].startswith( layout_fol):
						if type_asset == sets_folder or type_asset == module_folder:
							callPublAss = menuAss01.addAction("Call Publish Asset to current Scene", self.referencePublishedAsset)
						else:
							if type_task.startswith( rig_folder ) :   #elif actionSho04.text().startswith("create")
								callPublAss = menuAss01.addAction("Call Publish Asset to current Scene", self.referencePublishedAsset)
				try:
					name = str(self.labSceneAssetName.text())
				except Exception:
					name = " "
				if len(name.split("   ") ) == 3:
					if name.split("   ")[-1] == mod_folder or name.split("   ")[-1] == shad_folder:
						if type_asset == module_folder:  # module type
							callModule = menuAss01.addAction("Call Publish Module ", self.referenceModule)
				if self.userName ==  dbRowAssLoaded[0][8]:
					for i, tupla in enumerate (self.dbAsInformFiltered):
						if i == self.tablaWidgAssets.currentRow():
							bool = tupla[12]
					if bool:
						unlockAssetsAction = menuAss01.addAction("Unlock Current Task", self.unlockAssetsAction)				
					else:
						lockAssetsAction = menuAss01.addAction("Lock Current Task", self.lockAssetsAction)
				else:
					if self.tablaWidgAssets.currentRow() in  self.rowsAssLockedList:
						unlockableAc = menuAss01.addAction("Can not unlock")
					
				conceptPath = assetPath + concepts_folder + "/"
				if not os.path.exists ( conceptPath ):
					os.makedirs( conceptPath )
				lockAssCaptureConcept = menuAss01.addAction("Capture Concepts", lambda: self.makeConceptCapture( conceptPath , asset + "_" + type_task) )
				actionAss01 = menuAss01.exec_(self.tablaWidgAssets.mapToGlobal(position))   # la variable action la uso si necesito sub acciones
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))

		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Assigned':	
			if key01:
				menuAss03 = QMenu()
				menuAss03.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				for user in self.usuarios_list:
					if user != "     --- User Name ---":
						userAction = menuAss03.addAction(user)
				userAction = menuAss03.addAction( "Set Artist" )
				actionAss03 = menuAss03.exec_(self.tablaWidgAssets.mapToGlobal(position))
				if actionAss03 != None :
					for curreRow in selectedRow :
						item = QTableWidgetItem(actionAss03.text())
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgAssets.setItem( curreRow,self.asignAss_column_idx, item )  #  la columna de asignados
						item.setForeground(QBrush(QColor(175, 50, 175)))
						if curreRow % 2 == 0:
							item.setBackground(QBrush(QColor(200, 200, 200)))
						else:
							item.setBackground(QBrush(QColor(180, 180, 190)))
						if curreRow in self.rowsAssLockedList:
							self.tablaWidgAssets.item(curreRow, self.asignAss_column_idx).setBackground(QColor(125,125,125))
							self.tablaWidgAssets.item(curreRow, self.asignAss_column_idx).setForeground(QColor(150,150,150))
						if curreRow in self.rowsAssBlackListed:
							self.tablaWidgAssets.item(curreRow, self.asignAss_column_idx).setBackground(QColor(45,45,43))
							self.tablaWidgAssets.item(curreRow, self.asignAss_column_idx).setForeground(QColor(125,125,125))
						currentID = self.tablaWidgAssets.item( curreRow,self.idAss_column_idx)  # saber el id
						currentID = currentID.text()
						self.updateValueOnColumn( self.projectDataBase ,"assets" ,"asignado",actionAss03.text(), currentID)
						if "Set Artist" != item.text() and  self.diccUsSlack [ str (actionAss03.text() ) ] != "-":
							asset = self.tablaWidgAssets.item( curreRow,self.asset_column_idx)
							type_task = self.tablaWidgAssets.item( curreRow,self.taskAssType_column_idx)
							mensaje = "       Task  " + str (asset.text()) + "  " + str(type_task.text()) + "   Assigned"
							self.slackBot( mensaje, self.diccUsSlack [ str (actionAss03.text() ) ] )
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
				
		if self.tablaWidgAssets.horizontalHeaderItem(self.tablaWidgAssets.currentColumn()).text() == 'Task_Type':						
			if key01 and masterPass != "unable":						
				menuAss04 = QMenu()
				menuAss04.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				curreRow = self.tablaWidgAssets.currentRow()
				task_listt = self.settin_list[6]
				niceName = self.currentRowText(self.tablaWidgAssets ,self.niceAssName_column_idx)
				type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
				type_asset= self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)
				asset = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)
				task_instance = []
				for row in self.dbAsInformLoaded:
					if asset == row[3] and type_asset == row[2]:
						task_instance.append (row[5])
				taskk = " "

				for task in task_listt:
					if task not in task_instance:
						if type_asset == sets_folder and task == rig_folder:
							print " "
						else:
							taskAction = menuAss04.addAction("create " + task + " task")
							taskk = task
				if len (task_instance) == len (task_listt) :
					taskAction = menuAss04.addAction("no more task for create")
				actionAss04 = menuAss04.exec_(self.tablaWidgAssets.mapToGlobal(position))
				task_listt = self.settin_list[6]
				if actionAss04 != None:
					if actionAss04.text() != "no more task for create":
						type_asset= self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)	
						id_list = self.getAllIDs(self.projectDataBase,"assets")
						id = len(id_list)
						if id in id_list:
							while id in id_list:
								id+= 1
						vacio = " "
						conn = sqlite3.connect ( self.projectDataBase)
						c = conn.cursor()
						taskk =  actionAss04.text().split(" ")[1]
						c.execute("INSERT INTO assets (id, asset_name, asset_type, nice_name, comments, status, task_type, asignado, priority, isPublished, lastPublishDate,isLocked, blackListed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)" ,(id, asset ,type_asset, niceName, vacio, status_list[3], taskk, "Set Artist",0,0,vacio,0,0))
						conn.commit()
						conn.close()
						self.refresh_assets_table()						
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
				
	def tabShotTableUi(self):
		# tabla shots
		self.getTableShot()

		horizonTalButton=20
		# carga la tabla con shots
		self.qButtLoadShots = QPushButton(self.widShots)
		self.qButtLoadShots.setFont(self.newfont)
		self.qButtLoadShots.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtLoadShots.setGeometry(QtCore.QRect(20, horizonTalButton, 110, 41))
		self.qButtLoadShots.setText("Load Shots\n task Table  ")
		self.qButtLoadShots.clicked.connect(self.load_shot_button)
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtLoadShots.setGraphicsEffect(shadow)

		# crea nuevas tomas, en una secuencia existente o nueva
		self.qButtCreateShots = QPushButton(self.widShots)
		self.qButtCreateShots.setFont(self.newfont)
		self.qButtCreateShots.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200) ;border-radius: 20px; border-style: groove")
		self.qButtCreateShots.setGeometry(QtCore.QRect(140, horizonTalButton, 110, 41))
		self.qButtCreateShots.setText(" Create Shots \n task")
		self.setButUsOnOff( self.qButtCreateShots)
		self.qButtCreateShots.clicked.connect(self.create_shot_button)

		# refresh shots button
		self.qButtRefreshShotT = QPushButton(self.widShots)
		self.qButtRefreshShotT.setFont(self.newfont)
		self.qButtRefreshShotT.setEnabled(False)
		self.qButtRefreshShotT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px; border-style: groove")
		self.qButtRefreshShotT.setGeometry(QtCore.QRect(260, horizonTalButton, 120, 41))
		self.qButtRefreshShotT.setText(" Refresh Shots\n task Table ")
		self.qButtRefreshShotT.clicked.connect(self.refresh_shots_table)


###################################################

		self.checkBShowShBlackList = QCheckBox(self.widShots)
		self.checkBShowShBlackList.setGeometry(QtCore.QRect( 457, 28, 150, 41) )
		self.checkBShowShBlackList.setText("BlackListed")
		self.checkBShowShBlackList.setStyleSheet("color: rgb(210,135,20);")
		self.checkBShowShBlackList.setChecked(False)
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			self.checkBShowShBlackList.setEnabled(True)
		else:
			self.checkBShowShBlackList.setEnabled(False)
			
###################################################

		self.labShoFilters = QLabel(self.widShots)
		self.labShoFilters.setGeometry(QtCore.QRect(460, 10, 150, 15))
		self.labShoFilters.setText( " Filters: ")
		self.labShoFilters.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		self.labShoFilters.setFont(self.newfont)


		self.labFiltShoArea = QLabel(self.widShots)
		self.labFiltShoArea.setGeometry(QtCore.QRect(560, 10, 80, 30))
		self.labFiltShoArea.setText( "     Area ")
		self.labFiltShoArea.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		
		# combo box 
		self.comboBfilterShotArea= QComboBox(self.widShots)
		self.comboBfilterShotArea.setGeometry(QtCore.QRect(550, 40, 80, 20)) 
		self.comboBfilterShotArea.addItems(["All"] + area_listt)
		self.comboBfilterShotArea.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")

		self.labFiltShStatus= QLabel(self.widShots)
		self.labFiltShStatus.setGeometry(QtCore.QRect(660, 10, 80, 30))
		self.labFiltShStatus.setText( " status ")
		self.labFiltShStatus.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")

		# combo box 
		self.comboBfilterShStatus = QComboBox(self.widShots)
		self.comboBfilterShStatus.setGeometry(QtCore.QRect(650, 40, 80, 20)) 
		self.comboBfilterShStatus.addItems(["All"] + status_list + statusOnlySuperv_list) 
		self.comboBfilterShStatus.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")



		self.labFiltShoTaskTy= QLabel(self.widShots)
		self.labFiltShoTaskTy.setGeometry(QtCore.QRect(760, 10, 80, 30))
		self.labFiltShoTaskTy.setText( " task type ")
		self.labFiltShoTaskTy.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterShoTaskType = QComboBox(self.widShots)
		self.comboBfilterShoTaskType.setGeometry(QtCore.QRect(750, 40, 80, 20))
		try:
			self.comboBfilterShoTaskType.addItems(["All"] + self.settin_list[7]) 
		except TypeError:		
			self.comboBfilterShoTaskType.addItems(["All"]) 		
		self.comboBfilterShoTaskType.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")


		self.labFiltShAsigned = QLabel(self.widShots)
		self.labFiltShAsigned.setGeometry(QtCore.QRect(860, 10, 80, 30))
		self.labFiltShAsigned.setText( " assigned to ")
		self.labFiltShAsigned.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		# combo box 
		self.comboBfilterShAsigned = QComboBox(self.widShots)
		self.comboBfilterShAsigned.setGeometry(QtCore.QRect(850, 40, 80, 20))
		self.comboBfilterShAsigned.addItems(["All"] + self.usuarios_list + ["Set Artist"])
		self.comboBfilterShAsigned.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")
		

		self.labFiltShPublished = QLabel(self.widShots)
		self.labFiltShPublished.setGeometry(QtCore.QRect(960, 10, 80, 30))
		self.labFiltShPublished.setText( " publish ")
		self.labFiltShPublished.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")

		# combo box 
		self.comboBfilterShPublish= QComboBox(self.widShots)
		self.comboBfilterShPublish.setGeometry(QtCore.QRect(950, 40, 80, 20)) 
		self.comboBfilterShPublish.addItems(["All", "Published", "Not Published"] )
		self.comboBfilterShPublish.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")		
		

		self.labFiltShot = QLabel(self.widShots)
		self.labFiltShot.setGeometry(QtCore.QRect(1060, 10, 80, 30))
		self.labFiltShot.setText( " Shot name ")
		self.labFiltShot.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		
		self.textEdFiltShot  = QTextEdit(self.widShots)
		self.textEdFiltShot.setGeometry(QtCore.QRect(1050, 40, 90, 30))
		self.textEdFiltShot.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0) ; border: 2px ridge gray; border-radius: 3px")	

		############################################################
		offserAlto = 30
		# open scene button
		self.qButtOpenScene = QPushButton(self.widShots)
		self.qButtOpenScene.setFont(self.newfont)
		self.qButtOpenScene.setGeometry(QtCore.QRect(1185, 100 + offserAlto, 120, 40))
		self.qButtOpenScene.setText(" Open ")
		self.qButtOpenScene.setStyleSheet("background-color: rgb(150,150,150); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtOpenScene.clicked.connect(self.openShotBut)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtOpenScene.setGraphicsEffect(shadow)

	
		# save version shots button
		self.qButtSaveVersion = QPushButton(self.widShots)
		self.qButtSaveVersion.setFont(self.newfont)
		self.qButtSaveVersion.setGeometry(QtCore.QRect(1185, 160 + offserAlto, 120, 40))
		self.qButtSaveVersion.setText(" Save Version ")
		self.qButtSaveVersion.setStyleSheet("background-color: rgb(150,150,150); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtSaveVersion.clicked.connect(self.saveVersShotBut)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtSaveVersion.setGraphicsEffect(shadow)


		# publish-master shots button
		self.qButtPublishShot = QPushButton(self.widShots)
		self.qButtPublishShot.setFont(self.newfont)
		self.qButtPublishShot.setGeometry(QtCore.QRect(1185, 220+ offserAlto, 120, 40))
		self.qButtPublishShot.setText(" Publish ")
		self.qButtPublishShot.setStyleSheet("background-color: rgb(150,150,150); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		self.qButtPublishShot.clicked.connect(self.publishShotBut)

		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtPublishShot.setGraphicsEffect(shadow)


		# publish-master Assets button
		self.qButImpInternalPSh = QPushButton(self.widShots)
		self.qButImpInternalPSh.setFont(self.newfont)
		self.qButImpInternalPSh.setGeometry(QtCore.QRect(1250, 320+ offserAlto, 120, 40))
		self.qButImpInternalPSh.setText(" Import Internal \n Area Publish")
		self.qButImpInternalPSh.setStyleSheet("background-color: rgb(100,75,100); color: rgb(140,140,140) ;border-radius: 4px ; border-style: groove")
		self.qButImpInternalPSh.setEnabled(False)
		self.qButImpInternalPSh.clicked.connect(self.importInterPu)


		self.checkBoxMODSh = QCheckBox(self.widShots)
		self.checkBoxMODSh.setGeometry(QtCore.QRect(1390, 320+ offserAlto, 120, 20))
		self.checkBoxMODSh.setText("MOD")
		self.checkBoxMODSh.setEnabled(False)
		self.checkBoxMODSh.stateChanged.connect(self.stateCheckChangeSh)
		self.checkBoxMODSh.setStyleSheet("color: rgb(210,135,20)")
		
		self.checkBoxSHDSh = QCheckBox(self.widShots)
		self.checkBoxSHDSh.setGeometry(QtCore.QRect(1390, 340+ offserAlto, 120, 20))
		self.checkBoxSHDSh.setText("SHD")
		self.checkBoxSHDSh.setEnabled(False)
		self.checkBoxSHDSh.stateChanged.connect(self.stateCheckChange2Sh)
		self.checkBoxSHDSh.setStyleSheet("color: rgb(210,135,20)")

		#######
		#######
		#######
		
		offserAlto02 = 30
		
		self.labSHeaderSh = QLabel(self.widShots)
		self.labSHeaderSh.setGeometry(QtCore.QRect(1180, 54 + offserAlto02 , 285, 25))
		self.labSHeaderSh.setText( " ")
		self.labSHeaderSh.setStyleSheet("background-color: rgb(53,53,53); color: rgb(10, 170, 160) ;border-radius: 5px")
		
		self.labSceneShotName = QLabel(self.widShots)
		self.labSceneShotName.setGeometry(QtCore.QRect(1180, 54 + offserAlto02 , 285, 25))
		self.labSceneShotName.setText( " ")
		self.labSceneShotName.setFont(self.newfont)
		self.labSceneShotName.setStyleSheet("background-color: rgb(53,53,53); color: rgb(10, 170, 160) ;border-radius: 5px")
		self.labSceneShotName.hide()

		self.labSceneShotVers = QLabel(self.widShots)
		self.labSceneShotVers.setGeometry(QtCore.QRect(1330, 160 + offserAlto02, 200, 40))
		self.labSceneShotVers.setText( "v00")
		self.labSceneShotVers.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		self.labSceneShotVers.setFont(self.newfont)
		self.labSceneShotVers.hide()

		# publish date
		self.labPublishShotDate = QLabel(self.widShots)
		self.labPublishShotDate.setGeometry(QtCore.QRect(1330, 220 + offserAlto02, 150, 40))
		self.labPublishShotDate.setText( " ")
		self.labPublishShotDate.setStyleSheet(" background-color: rgb(65,65,65) ; color: rgb(210,135,20)")
		self.labPublishShotDate.setFont(self.newfont)
		self.labPublishShotDate.hide()


		self.labSceShotisLOcked = QLabel(self.widShots)
		self.labSceShotisLOcked.setGeometry(QtCore.QRect(1415, 5, 50, 50))
		self.image = QPixmap ( self.root + self.projName + '/PIPELINE/padlock.png')
		self.labSceShotisLOcked.setPixmap (self.image)
		self.labSceShotisLOcked.hide()


	def tabShManipLabOff(self):
		self.labSceneShotName.hide()
		self.labSceneShotVers.hide()
		self.labPublishShotDate.hide()
		self.labSceShotisLOcked.hide()
		self.labSceneShotName.setText("")
		self.labSceneShotVers.setText("")
		self.labPublishShotDate.setText("")
		
	def lockShotsAction(self):
		curreRow = self.tablaWidgShots.currentRow()
		currentID = self.tablaWidgShots.item( curreRow,self.idSh_column_idx)  # saber el id
		currentID = currentID.text()
		self.updateValueOnColumn( self.projectDataBase ,"shots" ,"isLocked",1, currentID)
		self.key05 = True
		shotName = self.labSceneShotName.text().split("   ")
		name = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
		type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
		self.refresh_shots_table ()
		if self.key04 and shotName[0]== name and shotName[1]== type_task :
			self.labSceShotisLOcked.show()
			self.labSceAssetisLOcked.show()
		else:
			QMessageBox.information(None, u' Locked ', "  " +  name + "  " + type_task + "  Locked !!!  ( is not actually  loaded scene )" )

	def unlockShotsAction(self):
		curreRow = self.tablaWidgShots.currentRow()
		currentID = self.tablaWidgShots.item( curreRow,self.idSh_column_idx)  # saber el id
		currentID = currentID.text()
		self.updateValueOnColumn( self.projectDataBase ,"shots" ,"isLocked",0, currentID)
		shotName = self.labSceneShotName.text().split("   ")
		name = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
		type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
		self.refresh_shots_table ()		
		if self.key04 and shotName[0]== name and shotName[1]== type_task :
			self.labSceShotisLOcked.hide()
			self.labSceAssetisLOcked.hide()
		else:
			QMessageBox.information(None, u' Unlocked ',  "  " +  name + "  " + type_task + "  Unlocked !!!  ( is not actually  loaded scene )" )

	def openShotBut (self):
		self.dbIdx_isPublishSh = 11
		self.dbIdx_datePublisSh = 12
		self.dbIdx_isLockedSh = 14
		self.labSceShotisLOcked.hide()
		self.labSceAssetisLOcked.hide()
		typeSh_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
		if typeSh_task.split("_")[0] in self.settin_list[7]:
			items_list = self.tablaWidgShots.selectedItems()
			selectedRow=[]
			for i in  items_list:
				selectedRow.append ( i.row())
			if selectedRow == []:
				QMessageBox.warning(None, u' ', " Select at least one row task")
			elif len (selectedRow) > 1:
				QMessageBox.warning(None, u' ', " Select only one row task")
			elif len (selectedRow) == 1:
				self.openSh_ver_row = selectedRow [0]
				if self.userName != "None":
					self.iddSho = self.currentRowText(self.tablaWidgShots ,self.idSh_column_idx)
					dbRowShLoaded = self.selectDbRow( self.projectDataBase,"shots" , self.iddSho  )				
					if dbRowShLoaded[0][14] == 1: # or self.key05 == True :
						if  self.userName ==  self.tablaWidgShots.item( selectedRow[0], self.asignSh_column_idx ).text():
							self.openSho ()
							self.labSceShotisLOcked.show()
							self.labSceAssetisLOcked.show()
						else:
							QMessageBox.warning(None, u' ', " Scene Locked")
					elif  self.dbShInformFiltered[ selectedRow [0] ] [self.dbIdx_isLockedSh] == 0:
						self.openSho ()
				else:
					QMessageBox.warning(None, u'No User ', " None User Can not Open Scenes")				

		else:
			QMessageBox.warning(None, u' ', "Choose Task Type First")


	def openSho (self):
		self.wind.setWindowTitle("Pr-G  Manager")
		self.scripJCounter1= self.scripJCounter1 + 1
		#self.tabAssManipLabOff()
		self.qButImpInternalPAss.setEnabled(False)
		self.qButImpInternalPSh.setEnabled(False)		
		self.qButImpInternalPAss.setStyleSheet("background-color: rgb(100,75,100); color: rgb(140,140,140) ;border-radius: 4px; border-style: groove")
		shadow = QGraphicsDropShadowEffect(self)
		shadow.setEnabled(False)
		self.qButImpInternalPAss.setGraphicsEffect(shadow)

		self.qButImpInternalPSh.setStyleSheet("background-color: rgb(100,75,100); color: rgb(140,140,140) ;border-radius: 4px; border-style: groove")
		shadow = QGraphicsDropShadowEffect(self)
		shadow.setEnabled(False)
		self.qButImpInternalPSh.setGraphicsEffect(shadow)
		
		self.key01 = False
		self.key04 = True
		self.ShotFileName = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
		self.typeSh_task = self.currentRowText(self.tablaWidgShots , self.taskShType_column_idx)
		self.seqName = self.currentRowText(self.tablaWidgShots , self.seq_column_idx)
		if len (self.typeSh_task.split("_SUB") ) < 2:
			shotPathEnd = self.typeSh_task + "/" + version_folder
		else:
			taskSub = self.typeSh_task.split("_")
			shotPathEnd = taskSub[0] + "/_" + taskSub[1] + "/" + version_folder
			
		pathUntilSeq = win.root + "/" + win.projName + parchePB01 + parcheSantiT02
		self.shotPath = pathUntilSeq + "/" + self.seqName + "/" + self.ShotFileName  +  "/" + shotPathEnd

		if self.typeSh_task == lit_fol:
			self.setRenderPath( pathUntilSeq , self.seqName, self.shotPath)

		file_list =  glob.glob (self.shotPath + "/" + self.ShotFileName + "_" + self.typeSh_task + "_v*" + self.settin_list[5] )
		mc.file( file_list[-1] ,o = True , force = True )
		self.labSceneShotName.setText(  self.ShotFileName + "   " + self.typeSh_task )
		self.wind.setWindowTitle("Pr-G  Manager" + "     " +self.ShotFileName + " " + self.typeSh_task )
		self.labSceneShotName.show()
		self.labSceneShotVers.setText( "_v" + file_list[-1].split("_v")[-1].split(self.settin_list[5])[0])
		self.labSceneShotVers.show()
		self.labSceneAssetName.setText(  self.ShotFileName + "   " + self.typeSh_task )
		self.labSceneAssetName.show()
		self.labSceneAssetVers.setText( "_v" + file_list[-1].split("_v")[-1].split(self.settin_list[5])[0])
		self.labSceneAssetVers.show()
		id = self.currentRowText(self.tablaWidgShots ,self.idSh_column_idx)
		self.dbRowShLoaded = self.selectDbRow( self.projectDataBase,"shots" , id)
		self.labPublishShotDate.show()
		self.labPublishAssetDate.show()
		if self.dbRowShLoaded[0][self.dbIdx_isPublishSh] == 0:
			self.labPublishShotDate.setText( "Not Published" )
			self.labPublishAssetDate.setText( "Not Published" )
		else:
			date = self.dbRowShLoaded[0][self.dbIdx_datePublisSh]
			time = "  last publish: \n " + date
			self.labPublishShotDate.setText( time )
			self.labPublishAssetDate.setText( time )
		#else:
		#	print "No Proper Pipeline Use"


	def setRenderPath( self, pathUntilSeq , seqName, shotPath):
		filepath_root = shotPath.split(lit_fol)[0].split(":/")[-1]
		path_render_root = shotPath.split( pathUntilSeq )
		end_path = path_render_root[-1].split( lit_fol )[0]
		scenenName = shotPath.split("/")[-1]
		version = scenenName.split("_v")[-1]
		version = version.split (".m")[0]
		version = "v" + version
		render_path =  self.settin_list[11] + end_path + defaultRenderFol + version + "/"
		#  esta es la ruta que inserte recien

		if not os.path.exists(render_path):
			os.makedirs(render_path) 
		pm.workspace(fileRule=['images', render_path])
		mm.eval ('setAttr -type "string" defaultRenderGlobals.imageFilePrefix "%s<Camera>_<RenderLayer>";' %render_path)



	def saveVersShotBut (self):
		if self.key04 == True:
			if  self.dbRowShLoaded[ 0 ] [self.dbIdx_isLockedSh] == 0:
				self.saveVersSho ()
			elif self.dbRowShLoaded[ 0 ] [self.dbIdx_isLockedSh] == 1 and  self.userName ==  self.tablaWidgShots.item( self.openSh_ver_row, self.asignSh_column_idx ).text():
				self.saveVersSho ()
			else:
				QMessageBox.warning(None, u' ', " Scene Locked")

	def saveVersSho (self):
		current_fps = mc.currentUnit(query=True, time=True)
		if current_fps == "game": 
			current_fps = "15"
		elif current_fps == "film":
			current_fps = "24"
		elif current_fps == "pal": 
			current_fps = "25" 
		elif current_fps == "ntsc": 
			current_fps = "30" 
		elif current_fps == "show": 
			current_fps = "48" 
		elif current_fps == "palf": 
			current_fps = "50"
		elif current_fps == "ntscf": 
			current_fps = "60" 
		if self.settin_list [0] != current_fps:
			QMessageBox.warning(None, u' take care ', " Be carefull, frame rate setting is not: " + self.settin_list [0]  + " fps")
		list = glob.glob (self.generatePath()[0] + "/*" + self.settin_list [0])
		checlList=[]
		for i, obj in enumerate (list):
			for idx in range (len(list)):
				if obj != list[idx]:
					checlList.append(list[idx-1])
		wversion = doVersionClass() 
		version = wversion.execution(self.settin_list [5], self.generatePath()[0], self.generatePath()[1] )
		self.labSceneShotVers.show()
		self.labSceneShotVers.setText(version)
		self.labSceneAssetVers.show()
		self.labSceneAssetVers.setText(version)


	def publishShotBut (self):
		if self.key04 == True:
			if  self.dbRowShLoaded[ 0 ] [self.dbIdx_isLockedSh] == 0:
				self.publiShoDb()
				self.labSceneShotVers.setText("Publish Version\n   -not editable-")
				self.labSceneAssetVers.setText("Publish Version\n   -not editable-")				
			elif self.dbRowShLoaded[ 0 ] [self.dbIdx_isLockedSh] == 1 and  self.userName ==  self.tablaWidgShots.item( self.openSh_ver_row, self.asignSh_column_idx ).text():
				self.publiShoDb()
				self.labSceneShotVers.setText("Publish Version\n   -not editable-")
				self.labSceneAssetVers.setText("Publish Version\n   -not editable-")
			else:
				QMessageBox.warning(None, u' ', " Scene Locked")

	def publiShoDb(self):
		shoPublish =  publishShotClass()
		path = self.shotPath.split( "/" + version_folder  )[0]
		print path
		path = path + "/" + publish_folder
		print path
		name = self.ShotFileName + "_" + self.typeSh_task
		executionSucces = shoPublish.execution( path , name, self.settin_list [5])
		if executionSucces:			
			#self.publiAssembAndNon(self.typeSh_task, self.ShotFileName, path)
			now = datetime.now()
			date = str (now.day) + " / "+ str(now.month) +" __ "+ str(now.hour) + ":" + str(now.minute)
			self.updateValueOnColumn( self.projectDataBase ,"shots" ,"isPublished",1, self.iddSho)			
			self.updateValueOnColumn( self.projectDataBase ,"shots" ,"lastPublishDate",date, self.iddSho)
			time = "  last publish: \n " + date
			self.labPublishShotDate.setText( time)
			self.labSceneShotVers.setText("Publish Version\n   -not editable-")	
			self.labPublishShotDate.show()
			self.labSceneShotVers.show()
			
			self.labPublishAssetDate.setText( time)
			self.labSceneAssetVers.setText("Publish Version\n   -not editable-")	
			self.labPublishAssetDate.show()
			self.labSceneAssetVers.show()			
			
			if len ( path.split("_SUB") ) < 2 and parchePB_Copy2publiFol == True :   # este publish no es el de la carpeta de publicado
				assetFoldPrence = parchePB01.split("/")[-1]
				publishFolPath = path.split( parcheSantiT02.split("/")[-1] ) #     
				if not os.path.exists( publishFolPath[0]  + parcheSantiT02 + publishFolPath[1] ):
					os.makedirs( publishFolPath[0] + publish_folder_alternativePB + parcheSantiT02 + publishFolPath[1] )
				shutil.copy2( os.path.join( path , self.ShotFileName + "_" + self.typeSh_task + self.settin_list[5] ), os.path.join( publishFolPath[0] + publish_folder_alternativePB + parcheSantiT02 + publishFolPath[1] ,  self.ShotFileName + "_" + self.typeSh_task + self.settin_list [5] ) )
			QMessageBox.information(None, u' ',  " Succes!! Scene Published!!!!  ")
			mensaje = "    Just Published :    " + self.ShotFileName + "_" + self.typeSh_task  + "    !!!!!! "
			self.slackBot( mensaje, self.settin_list[10] )
		else:
			QMessageBox.information(None, u' publishing failiture',  "  Error Publishing ")

	def generatePath(self):
		self.filepath_maya = mc.file(q=True, sn=True)
		pathLavelList = self.filepath_maya.split ("/")
		currentFileName = pathLavelList[-1]
		pathOnly = self.filepath_maya.split(currentFileName)[0]
		return (pathOnly, currentFileName)

#####################################################################

	def tabProducUi(self):  #   saca un poco de codigo del _init_ para descomprimir
		#########################    tab production         #####################################
	
		self.plavCreaProName = QLabel(self.widProduction)
		self.plavCreaProName.setText("Create New Project")
		self.plavCreaProName.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.plavCreaProName.setFont(self.newfont)
		self.plavCreaProName.setGeometry(QtCore.QRect( 170 , 10, 200, 41))		

		altura = 60
		self.labProjectName = QLabel(self.widProduction)
		self.labProjectName.setGeometry(QtCore.QRect(80, altura -5, 150, 60))
		self.labProjectName.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labProjectName.setText("   Project Name:")
		#self.labProjectName.setText("   Project Name:")

		self.textEdProjectName = QTextEdit(self.widProduction)
		self.textEdProjectName.setGeometry(QtCore.QRect(170, altura +15, 150, 25))
		self.textEdProjectName.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0) ; border: 2px ridge gray; border-radius: 3px")
		#self.textEdProjectName.setStyleSheet(" background: transparent; border-bottom-width: 1px solid #000; color: rgb(0,0,0)")

		self.pButton_setProjRoot = QPushButton(self.widProduction)
		self.pButton_setProjRoot.setFont(self.newfont) # linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1)100%)
		self.pButton_setProjRoot.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 10px; border-style: groove;")
		#self.pButton_setProjRoot.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 10px; border-style: groove;")
		self.pButton_setProjRoot.setText("Set Project Root ")
		self.pButton_setProjRoot.setGeometry(QtCore.QRect(80, altura + 80, 156, 30))
		self.pButton_setProjRoot.clicked.connect(self.dialogRootProject)
		
		self.shadow1 = QGraphicsDropShadowEffect(self)
		self.shadowButt ( self.shadow1)
		self.pButton_setProjRoot.setGraphicsEffect( self.shadow1 )


		self.labProjectRoot = QLabel(self.widProduction)
		self.labProjectRoot.setGeometry(QtCore.QRect(280, altura + 43, 250, 40))
		self.labProjectRoot.setText("Project Root (extremely important), set on a \n   -project folder-.  Example:  Y:/__projects__")
		self.labProjectRoot.setStyleSheet("color: rgb(95,95,95)") # background-color: rgb(65,65,65);

		self.labRootProjectPath2 = QLabel(self.widProduction)
		self.labRootProjectPath2.setGeometry(QtCore.QRect(245, altura + 85, 300, 21))

		self.labRootProjectPath2.setStyleSheet("background-color: rgb(140,145,145); color: rgb(0,0,0) ;border-radius: 3px")
		self.selectedPath = "drive:/someFolders/projects"
		self.labRootProjectPath2.setText( self.selectedPath )
		 
		self.pButtonCreateProjSettings= QPushButton(self.widProduction)
		self.pButtonCreateProjSettings.setFont(self.newfont)
		self.pButtonCreateProjSettings.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200) ;border-radius: 10px ; border-style: groove")
		self.pButtonCreateProjSettings.setText("Create Project Settings")
		self.pButtonCreateProjSettings.setGeometry(QtCore.QRect(80, altura + 160, 210, 30))
		self.pButtonCreateProjSettings.clicked.connect(self.openCreaProjSett)
		

		self.shadow2 = QGraphicsDropShadowEffect(self)
		self.shadowButt ( self.shadow2)	
		self.pButtonCreateProjSettings.setGraphicsEffect(self.shadow2)
		
		
		
		
	
		self.qBut_CreateNewProj = QPushButton(self.widProduction)
		self.qBut_CreateNewProj.setFont(self.newfont)
		self.qBut_CreateNewProj.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200) ;border-radius: 10px; border-style: groove")
		self.qBut_CreateNewProj.setText("Create New Project")
		self.qBut_CreateNewProj.setGeometry(QtCore.QRect(40, 600, 170, 41))
		self.qBut_CreateNewProj.clicked.connect(self.projectCreateRequeriment)
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qBut_CreateNewProj.setGraphicsEffect(shadow)

		self.lab_editCurrentProj = QLabel(self.widProduction)
		self.lab_editCurrentProj.setGeometry(QtCore.QRect(730, 5, 170, 30))
		self.lab_editCurrentProj.setFont(self.newfont)
		self.lab_editCurrentProj.setStyleSheet("color: rgb(210,135,20);")
		self.lab_editCurrentProj.setText("  Edit:    " + self.projName + " ")

		self.qButEditProjSett = QPushButton(self.widProduction)
		self.qButEditProjSett.setFont(self.newfont)
		self.qButEditProjSett.setText(" Edit Settings ")
		self.qButEditProjSett.setGeometry(QtCore.QRect(730, 43, 120, 30))
		self.qButEditProjSett.clicked.connect(self.openEditProjSett)
		self.qButEditProjSett.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200) ;border-radius: 10px")
		
		self.setButUsOnOff(self.qButEditProjSett)

		self.getTableUser()


		self.qButSetRenderRoot = QPushButton(self.widProduction)
		self.qButSetRenderRoot.setFont(self.newfont)
		self.qButSetRenderRoot.setText(" Set 3D Render Root ")
		self.qButSetRenderRoot.setGeometry(QtCore.QRect(870, 43, 120, 30))
		self.qButSetRenderRoot.clicked.connect(  self.dialogRenderRootPath  )
		self.qButSetRenderRoot.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 10px")
		
		self.setButUsOnOff(self.qButSetRenderRoot)

		self.labRootRenderPath = QLabel(self.widProduction)
		self.labRootRenderPath.setGeometry(QtCore.QRect(1010, 48, 350, 23))
		self.labRootRenderPath.setStyleSheet("background-color: rgb(140,145,145); color: rgb(0,0,0) ;border-radius: 3px")
		
		
		
		
		path = os.path.join( self.root  + self.projName + "/PIPELINE/CONFIGURATION/" , "project_config_preset.json" )
		if os.path.isfile( path ) :
			with open( path) as fi:
				data = fi.readlines()[0]
				fi.close()
				try:
					dicct_proj_settings = ast.literal_eval(data)
				except Exception:
					pass		
			self.labRootRenderPath.setText( dicct_proj_settings["render_root"] )
		else:
			self.labRootRenderPath.setText( "drive:/someFolders/Renders" )
			
		self.qButEditUsers = QPushButton(self.widProduction)
		self.qButEditUsers.setFont(self.newfont)
		self.qButEditUsers.setText(" Edit Users ")
		self.qButEditUsers.setGeometry(QtCore.QRect(730, 90, 120, 30))
		self.qButEditUsers.clicked.connect ( self.load_user_button )
		self.qButEditUsers.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200);border-radius: 20px")

		self.setButUsOnOff(self.qButEditUsers)

		self.qButImportSkacUs = QPushButton(self.widProduction)
		self.qButImportSkacUs.setFont(self.newfont)
		self.qButImportSkacUs.setText("Import SlackUsers")
		self.qButImportSkacUs.setGeometry(QtCore.QRect(870, 90, 120, 30))
		self.qButImportSkacUs.clicked.connect(self.slackUserImporter)
		self.qButImportSkacUs.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200);border-radius: 20px")

		self.setButUsOnOff(self.qButImportSkacUs)


		self.qButAddProArtist = QPushButton(self.widProduction)
		self.qButAddProArtist.setFont(self.newfont)
		self.qButAddProArtist.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200);border-radius: 20px")
		self.qButAddProArtist.setText("Add User")
		self.qButAddProArtist.setGeometry(QtCore.QRect(1010, 90, 120, 30))
		self.qButAddProArtist.clicked.connect(self.openAddUserWin)


		self.setButUsOnOff( self.qButAddProArtist)
		
		
	def createProject(self):
		if self.inputValidation:
			self.newProjName = self.textEdProjectName.toPlainText()
			try:
				value = self.AdvertSpecialChars(str(self.newProjName))
			except UnicodeEncodeError:
				QMessageBox.warning(None, u' invalid parameter ', " No Special Character are allowed " )
			if self.validationProjRoot:
				if self.validationProjSett:
					for char in caracteresProhibidos + [" "]:
						if len(self.newProjName.split(char)) > 1:
							QMessageBox.warning(None, u' invalid parameter ', "Forbidden Characters  :  " + str(listaCaracteres + [" "]) )
					else:
						with open(pipeline_root_path + "/projects_list_pipeline.json") as fi:
							data = fi.readlines()[0]
							dict = ast.literal_eval(data)
							listaProj = dict["projects_list"]
						if self.newProjName in listaProj:
							QMessageBox.information(None, u'Choose Other Name', " This Project Name was used before " )
						else:
							self.comboBoxProject.addItems([self.newProjName])
							listaProj = listaProj + [ self.selectedPath + "/" + self.newProjName ]
							with open ( pipeline_root_path + "/projects_list_pipeline.json", "w") as file:
								file.write('{"projects_list" : %s }' %listaProj)
								file.close()		
							if not os.path.exists(self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/"):
								os.makedirs(self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/")
							path = os.path.join( self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/", "project_config_preset.json" )
							if not os.path.isfile( path ):

								project_config_var = '{"frame_rate" : "%s", "project_resolution" : "%s" ,"preview_resolution" : "%s", "preview_format" : "%s" , "ColorSpace": "%s" , "maya_exten" : "%s" , "maya_assets_tasks" : %s , "maya_shots_tasks" : %s , "nuke_tasks" : %s , "slack_proj_code" : %s , "slack_channel" : %s , "slack_channel" : %s , "render_root" : %s }' %(self.winProjSett.fps, self.winProjSett.resolu, self.winProjSett.prev_resolu, self.winProjSett.prev_formatss, self.winProjSett.color_manag, self.winProjSett.maya_exen, self.winProjSett.listAssetsTask, self.winProjSett.listMayaShTask, self.winProjSett.listNukeShTask , self.winProjSett.slackCode, self.winProjSett.slackChannel, self.winProjSett.renderRootPath  )
								with open( path, "w") as file:
									file.write(project_config_var)
									file.close()
							if not os.path.exists(self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/TOOLS/nircmd/"):
								os.makedirs(self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/TOOLS/nircmd/")
							#PIPELINE/CONFIGURATION/TOOLS/nircmd/nircmd.exe
							nircmdToolKit = os.listdir (pipeline_root_path + "/TOOLS/nircmd/")
							for file in nircmdToolKit:
								if file != "ffmpeg.exe":
									shutil.copy2( os.path.join(pipeline_root_path + "/TOOLS/nircmd/" , file), os.path.join( self.selectedPath + "/" + self.newProjName + "/PIPELINE/CONFIGURATION/TOOLS/nircmd/" ,file) )
							if not os.path.exists(self.selectedPath + "/" + self.newProjName + "/PIPELINE/DATABASE/"):
								os.makedirs(self.selectedPath + "/" + self.newProjName + "/PIPELINE/DATABASE/")
							sql = sqlTableData()
							sql.createShotsTable(self.selectedPath + "/" + self.newProjName + "/PIPELINE/DATABASE/" + self.newProjName + "_dataBase.db")
							sql.createAssetTable(self.selectedPath + "/" + self.newProjName + "/PIPELINE/DATABASE/" + self.newProjName + "_dataBase.db")
							sql.createUsersTable(self.selectedPath + "/" + self.newProjName + "/PIPELINE/DATABASE/" + self.newProjName + "_dataBase.db")
							templatePathList = [self.selectedPath + "/" + self.newProjName + "/PIPELINE/TEMPLATES/ASSET/", self.selectedPath + "/" + self.newProjName + "/PIPELINE/TEMPLATES/SCENE/"]
							for path in templatePathList:
								if not os.path.exists(path):
									os.makedirs(path)
							if not os.path.exists(self.selectedPath + "/" + self.newProjName + "/DATA/TOOLS/"):
								os.makedirs(self.selectedPath + "/" + self.newProjName + "/DATA/TOOLS/")
							self.qBut_CreateNewProj.setText(" New Project Created ")
							self.qBut_CreateNewProj.setStyleSheet("background-color: rgb(210,135,20); color: rgb(0,120,0); border-style: groove")
							shutil.copy2( os.path.join( pipeline_root_path , "iconProject.png"), os.path.join( self.selectedPath + "/" + self.newProjName + "/PIPELINE/", "iconProject.png" ) )
							shutil.copy2( os.path.join( pipeline_root_path , "padlock.png"), os.path.join( self.selectedPath + "/" + self.newProjName + "/PIPELINE/", "padlock.png" ) )
			else:
				QMessageBox.information(None, u'settings', " please, set project settings" )

	
	def projectCreateRequeriment(self):
		if masterPass != "unable":
			self.passWinP = masterPassWin()
			self.passWinP.WinMP.show()
			self.passWinP.labNotice.setText("           Remember, no special character \n   no spaces , and set the root and settings")
			self.passWinP.btnSetMasterPass.clicked.connect(self.chek_passAndCreaProject)
			#try:
			if self.passWinP.exec_():
				print " "
			#except Exception:
			#	pass
	def chek_passAndCreaProject(self):
		if masterPass == str(self.passWinP.textEdPass.toPlainText()):
			self.inputValidation = True
			self.createProject()
			self.passWinP.WinMP.close()
		else:
			QMessageBox.warning(None, u' try again', " set the proper password" )


	def userCreateRequeriment(self):
		if masterPass != "unable":
			self.passWinU = masterPassWin()
			self.passWinU.WinMP.show()
			self.passWinU.btnSetMasterPass.clicked.connect(self.chek_passAndCreaUser)
			#try:
			if self.passWinU.exec_():
				print " "
			#except Exception:
			#	pass
	def chek_passAndCreaUser (self):

		if masterPass == str(self.passWinU.textEdPass.toPlainText()):
			self.qButAddProArtist.setEnabled(True)
			self.qButAddProArtist.setStyleSheet("background-color: rgb(210,135,20); color: rgb(0,100,0); border-style: groove")  # fuente gris
			self.inputValidation = True
			self.passWinU.WinMP.close()
		else:
			QMessageBox.warning(None, u' try again', " set the proper password" )

#####################################################################
	def executeMelMAyaScri(self, full_path):
		mel.eval('source "%s"' %full_path)

	def AdvertSpecialChars(self, stringWord ):
		obj_con_ec = []
		if set(stringWord).difference(printable):
			obj_con_ec.append (stringWord)
		if obj_con_ec != []:
			QMessageBox.information(None, u' issue '," Specials Characters found: " + str(obj_con_ec))
			return  True
		else:
			return False

	def getTableShot(self):
		# tabla shots
		self.tablaWidgShots = QTableWidget(self.widShots)
		self.tablaWidgShots.setGeometry(QtCore.QRect(20, 85, 1145, 590))
		self.tablaWidgShots.setTextElideMode(QtCore.Qt.ElideMiddle)
		self.tablaWidgShots.verticalHeader().hide()
		self.tablaWidgShots.setStyleSheet("background-color: rgb(128,124,120); border-width: 2px; padding: 5px; border-radius: 15px")
		self.tablaWidgShots.setShowGrid(False)

	def getTableUser(self):
		# tabla shots
		self.tablaWidgUsers = QTableWidget(self.widProduction)
		self.tablaWidgUsers.setGeometry(QtCore.QRect(730, 140, 720, 510))
		self.tablaWidgUsers.setTextElideMode(QtCore.Qt.ElideMiddle)
		self.tablaWidgUsers.verticalHeader().hide()
		self.tablaWidgUsers.setStyleSheet("background-color: rgb(128,124,120); border-width: 2px; padding: 5px; border-radius: 15px") 
		self.tablaWidgUsers.setShowGrid(False)

	def getTableAsset(self):
		# tabla shots
		self.tablaWidgAssets = QTableWidget(self.widAssets)
		self.tablaWidgAssets.setGeometry(QtCore.QRect(20, 85, 1145, 590))
		self.tablaWidgAssets.setTextElideMode(QtCore.Qt.ElideMiddle)
		self.tablaWidgAssets.verticalHeader().hide()
		self.tablaWidgAssets.setStyleSheet("background-color: rgb(128,124,120); border-width: 2px; padding: 5px; border-radius: 15px")
		self.tablaWidgAssets.setShowGrid(False)
		
	def setButUsOnOff (self, button):
		if self.userName != "None":
			if len(self.usuarios_list + self.productores_list) > 0: 
				if self.userName not in self.lideres_list + self.productores_list:
					button.setEnabled(False)
					button.setStyleSheet("background-color: rgb(190,160,150); color: rgb(70,70,70); border-width: 3px; border-radius: 15px; border-style: groove;")
					shadow = QGraphicsDropShadowEffect(self)
					shadow.setEnabled(False)	
					button.setGraphicsEffect(shadow)

				else:
					button.setEnabled(True)
					button.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200);overflow: visible;; border-width: 3px; border-radius: 15px; border-style: groove;")
					shadow = QGraphicsDropShadowEffect(self)
					self.shadowButt ( shadow )	
					button.setGraphicsEffect(shadow)
			else:
				button.setEnabled(False)
				button.setStyleSheet("background-color: rgb(190,160,150); color: rgb(70,70,70); border-width: 3px; border-radius: 15px; border-style: groove;")
				shadow = QGraphicsDropShadowEffect(self)
				shadow.setEnabled(False)	
				button.setGraphicsEffect(shadow)
	
		else:
			button.setEnabled(False)
			button.setStyleSheet("background-color: rgb(190,160,150); color: rgb(70,70,70); border-width: 3px; border-radius: 15px; border-style: groove;") 
			shadow = QGraphicsDropShadowEffect(self)
			shadow.setEnabled(False)	
			button.setGraphicsEffect(shadow)

	def openAddUserWin(self):
		if self.userName != "None":
			if self.userName in self.lideres_list + self.productores_list or self.inputValidation:
				winAddUser = addUserWin()
				winAddUser.show()
				#try:
				if winAddUser.exec_():
					print " "
				#except Exception:
				#	pass
		else:
			QMessageBox.information(None, u' No Logged in User '," Log in as an Allowed User ")	
			
	def openCreaProjSett (self):
		if self.textEdProjectName.toPlainText()!= "":
			self.winProjSett = creaSettingWin()
			self.winProjSett.show()
			self.validationProjSett = True
			#try:
			if self.winProjSett.exec_():
				print " "
			#except Exception:
			#	pass
		else:
			QMessageBox.information(None, u' Second Step ', " Set The Project Name First " )

	def openEditProjSett (self):
		if self.projName!= "None":
			self.winEdPrSett = creaSettingWin()
			for i , item in enumerate (frameRateList):
				if self.settin_list[0] == item:	
					self.winEdPrSett.comboFrameRate.setCurrentIndex( i )
			for i , item in enumerate (projResolutList):
				if self.settin_list[2] == item:	
					self.winEdPrSett.comboProjResolut.setCurrentIndex( i )
			for i , item in enumerate (projResolutList):
				if self.settin_list[3] == item:	
					self.winEdPrSett.combPreviewResolu.setCurrentIndex( i )
			for i , item in enumerate (previewFormatList):
				if self.settin_list[4] == item:	
					self.winEdPrSett.combPreviewFormat.setCurrentIndex( i )
			for i , item in enumerate (mayaExtenList):
				if self.settin_list[5] == item:	
					self.winEdPrSett.comboMayaExtens.setCurrentIndex( i )
			self.winEdPrSett.lsWidMayaAsTasks.addItems(self.settin_list[6])
			self.winEdPrSett.lsWidMayaShTasks.addItems(self.settin_list[7])
			self.winEdPrSett.lsWidNukeShTasks.addItems(self.settin_list[8])
			self.winEdPrSett.textEdSlackProjCode.setText(self.settin_list[9])
			self.winEdPrSett.textEdSlackChannel.setText(self.settin_list[10])
			self.winEdPrSett.btnSaveProjSettings.setText('Save Edited Settings')
			self.winEdPrSett.btnSaveProjSettings.clicked.connect(self.saveEditedConfigPreset)			
			self.winEdPrSett.show()
			#try:
			if self.winEdPrSett.exec_():
				print " "
			#except Exception:
			#	pass
		else:
			QMessageBox.information(None, u' Choose Project ', " No  Project Logged In " )

	def saveEditedConfigPreset(self):
		path = os.path.join( self.root + self.projName + "/PIPELINE/CONFIGURATION/", "project_config_preset.json" )
		project_config_var = '{"frame_rate" : "%s", "project_resolution" : "%s" ,"preview_resolution" : "%s", "preview_format" : "%s" , "ColorSpace": "%s" , "maya_exten" : "%s" , "maya_assets_tasks" : %s , "maya_shots_tasks" : %s , "nuke_tasks" : %s , "slack_proj_code" : "%s" , "slack_channel" : "%s" , "render_root" : "%s" }' %(self.winEdPrSett.fps, self.winEdPrSett.resolu, self.winEdPrSett.prev_resolu, self.winEdPrSett.prev_formatss, self.winEdPrSett.color_manag, self.winEdPrSett.maya_exen, self.winEdPrSett.listAssetsTask, self.winEdPrSett.listMayaShTask, self.winEdPrSett.listNukeShTask , self.winEdPrSett.slackCode, self.winEdPrSett.slackChannel, self.labRootRenderPath.text()  )
		with open( path, "w") as file:
			file.write(project_config_var)
			file.close()
		self.tablaWidgShots.clear()
		self.tablaWidgAssets.clear()
		self.getTableShot()
		self.getTableAsset()
		self.settin_list = self.set_settingsVariables()
		texto = self.textLoadSettings(self.root, self.settin_list[0], self.settin_list[1], self.settin_list[2], self.settin_list[3], self.settin_list[4], self.settin_list[5], self.settin_list[6], self.settin_list[7] , self.settin_list[8], self.settin_list[11])
		self.labProjectPreference.setText(texto)
		self.labProjectPreference.setStyleSheet("background-color: rgb(65,65,65); color: rgb(10, 170, 160)")

	def listarProj(self):
		with open(pipeline_root_path + "/projects_list_pipeline.json") as fi:
			data = fi.readlines()[0]
			dict = ast.literal_eval(data)
			listaProj = [""]
			for proj in dict["projects_list"]:
				proj = proj.split("/")[-1]
				listaProj.append (proj)
		return listaProj

	def dialogRootProject(self):
		if self.textEdProjectName.toPlainText()!= "":
			self.selectedPath = QFileDialog().getExistingDirectory(None, 'Choose Project Root Directory', "C:/", QFileDialog.ShowDirsOnly)

			self.labRootProjectPath2.setText(self.selectedPath)
			if len(self.selectedPath) > 3:
				self.pButton_setProjRoot.setText("Root Path Setted")
				self.labRootProjectPath2.setFont(self.newfont)
				self.labRootProjectPath2.setStyleSheet("background-color: rgb(100,100,100); color: rgb(0,175,0)")
				self.validationProjRoot = True
		else:
			QMessageBox.information(None, u' Second Step ', " Set The Project Name First " )

	def printing(self):
		print (" disparando accion")






	def dialogRenderRootPath(self):
		self.selectedRenderPath = QFileDialog().getExistingDirectory(None, 'Choose Render Root Directory', "C:/", QFileDialog.ShowDirsOnly)
		self.labRootRenderPath.setText(self.selectedRenderPath)
		if len(self.selectedRenderPath) > 3:
			self.pButton_setProjRoot.setText("Render Root Setted")
			self.labRootRenderPath.setFont(self.newfont)
			self.labRootRenderPath.setStyleSheet("background-color: rgb(100,100,100); color: rgb(0,175,0)")

			path = os.path.join( self.root  + self.projName + "/PIPELINE/CONFIGURATION/" , "project_config_preset.json" )
			if os.path.isfile( path ) :
				with open( path) as fi:
					data = fi.readlines()[0]
					fi.close()
					#try:
					#	dicct_proj_settings = ast.literal_eval(data)
					#except Exception:
					#	pass
			json_dict_start = data.split("render_root")[0]
			
			with open( path, "w") as file:
				file.write( json_dict_start + 'render_root" : "' + self.selectedRenderPath + '" }' )
				file.close()



	def set_settingsVariables (self):
		# visualiza las preferencias que vienen asociadas al proyecto
		try:
			path = os.path.join( self.root  + self.projName + "/PIPELINE/CONFIGURATION/" , "project_config_preset.json" )
			if os.path.isfile( path ) :
				with open( path) as fi:
					data = fi.readlines()[0]
					fi.close()
					try:
						dicct_proj_settings = ast.literal_eval(data)
					except Exception:
						pass		
				fps = dicct_proj_settings ["frame_rate"]
				pro_resolution = dicct_proj_settings ["project_resolution"]
				prev_resolu = dicct_proj_settings ["preview_resolution"]
				prev_format = dicct_proj_settings ["preview_format"]
				color_space = dicct_proj_settings ["ColorSpace"]
				maya_exten = dicct_proj_settings ["maya_exten"]
				maya_AsTasks_type = dicct_proj_settings ["maya_assets_tasks"]
				maya_ShTasks_type = dicct_proj_settings ["maya_shots_tasks"]
				nuke_ShTasks_type = dicct_proj_settings ["nuke_tasks"]
				slackPrCode = dicct_proj_settings ["slack_proj_code"]
				slackChanel = dicct_proj_settings ["slack_channel"]
				renderRootPath = dicct_proj_settings ["render_root"]					
				return (fps, pro_resolution, prev_resolu, prev_format, color_space, maya_exten ,maya_AsTasks_type, maya_ShTasks_type, nuke_ShTasks_type, slackPrCode, slackChanel,renderRootPath)
			else:
				return ( "  --  ", "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "", "" ,"drive:/someFolders/Renders")
		except AttributeError:
			return ( "  --  ", "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "  --  " , "", "" ,"drive:/someFolders/Renders")
			self.root = "drive:/someFolders/projects/"

	#def createTable (self):
	def choosingProject(self):
		self.projName = str(self.comboBoxProject.currentText() ) #  agregar proyectos nuevos a esta variable
		self.projName = self.projName.replace ("\\", "/")
		self.lab_editCurrentProj.setText("  Edit:    " + self.projName + " ")
		if self.projName != "":
			with open(pipeline_root_path + "/projects_list_pipeline.json") as fi:
				data = fi.readlines()[0]
				try:
					dict = ast.literal_eval(data)
					self.projectRoot_list = dict['projects_list']
				except Exception:
					pass
			self.tabAssManipLabOff()
			self.tabShManipLabOff()
			self.key01 = False
			self.key04 = False
			self.scripJCounter1 = 0
			self.scripJCounter2 = 0
			for p in self.projectRoot_list:
				if self.projName == p.split("/")[-1]:
					self.root = p.split(self.projName)[0]
			self.labRootProjectPath.setText(self.root)
			self.labWinProject.setText(self.projName)
			self.labWinProject.setStyleSheet("color: rgb(10, 170, 160)")			
			if os.path.isfile(temp_folder + "/project_task_manager_presets.json") :
				with open( temp_folder + "/project_task_manager_presets.json", "w") as file:
					imagemap = QPixmap ( self.root + self.projName + '/PIPELINE/iconProject.png')
					self.lab_image.setPixmap (imagemap)
					file.write('{"project" : "%s", "proRoot" : "%s"}' %( self.root + self.projName , self.root ) )
					file.close()
			self.tablaWidgShots.clear()
			self.tablaWidgAssets.clear()
			self.tablaWidgUsers.clear()
			
			self.qButtRefreshShotT.setEnabled(False)
			self.qButtRefreshShotT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px ; border-style: groove")  # fuente gris
			shadow = QGraphicsDropShadowEffect(self)
			shadow.setEnabled(False)
			self.qButtRefreshShotT.setGraphicsEffect(shadow)
			
			self.qButtLoadShots.setEnabled(True)
			self.qButtLoadShots.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
			shadow = QGraphicsDropShadowEffect(self)
			self.shadowButt ( shadow )	
			self.qButtLoadShots.setGraphicsEffect(shadow)

			self.qButtRefreshAssT.setEnabled(False)
			self.qButtRefreshAssT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px ; border-style: groove")  # fuente gris
			shadow = QGraphicsDropShadowEffect(self)
			shadow.setEnabled(False)
			self.qButtRefreshAssT.setGraphicsEffect(shadow)
			
			
			self.qButtLoadAssets.setEnabled(True)
			self.qButtLoadAssets.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
			shadow = QGraphicsDropShadowEffect(self)
			self.shadowButt ( shadow )	
			self.qButtLoadAssets.setGraphicsEffect(shadow)

			# tablas... las creo de vuelta
			self.getTableShot()
			self.getTableAsset()
			self.getTableUser()
			# donde visualizo el proyecto seleccionado  para todo el browser 
			self.settin_list = self.set_settingsVariables()
			#self.root
			texto = self.textLoadSettings(self.root, self.settin_list[0], self.settin_list[1], self.settin_list[2], self.settin_list[3], self.settin_list[4], self.settin_list[5], self.settin_list[6], self.settin_list[7] , self.settin_list[8], self.settin_list[11])
			self.labProjectPreference.setText(texto)
			self.labProjectPreference.setStyleSheet("background-color: rgb(65,65,65); color: rgb(10, 170, 160)")
			self.labWinProject.setText(self.projName)
			self.labWinProject.setStyleSheet("color: rgb(10, 170, 160)")	
			self.projectDataBase = self.root + self.projName + "/PIPELINE/DATABASE/" +  self.projName + "_dataBase.db"
			self.scripts_folder = self.root + self.projName + "/DATA/TOOLS/"
			self.projecScripts(self.scripts_folder)
			
			tuplaList = self.selectAllDB_lessBlackL (self.projectDataBase,"users" )#  selectAllDB_lessBlackL	

			self.usuarios_list = []
			self.lideres_list = []
			self.productores_list = []
			self.diccUsSlack = {}
			for tupla in tuplaList:
				if tupla[5] == special_area_ls [0]:   #  [5] le corresponde a la columna de area
					self.productores_list.append(tupla[1])
					self.diccUsSlack [tupla[1]] = tupla[7]
				else:
					self.usuarios_list.append(tupla[1])
					self.diccUsSlack [tupla[1]] = tupla[7]
				if tupla[6] == 1:
					self.lideres_list.append(tupla[1])
		
			self.comboBoxUsers.clear()
			self.comboBoxUsers.addItems ( [ "     --- User Name ---"] + self.usuarios_list + self.productores_list )

			if self.userName not in self.usuarios_list + self.productores_list:
				self.labUserName.setText("None")
				self.labUserName.setStyleSheet("color: rgb(160,0,0)")				
				self.userName = None
				with open( temp_folder + "/user_task_manager_presets.json", "w") as file:
					file.write('{"user" : "None"}')
					file.close()
			self.setButUsOnOff(self.qButAddProArtist)
			self.setButUsOnOff( self.qButtCreateShots)
			self.setButUsOnOff( self.qButtCreateAssets)
			self.setButUsOnOff(self.qButSetTemplates)
			self.setButUsOnOff(self.qButImportSkacUs)
			self.setButUsOnOff(self.qButEditUsers)
			self.setButUsOnOff(self.qButEditProjSett)
			self.setButUsOnOff(self.qButSetRenderRoot)
			
			if self.userName in self.productores_list or self.userName in self.lideres_list:
				self.checkBShowShBlackList.setEnabled(True)
				self.checkBShowAssBlackList.setEnabled(True)
			else:
				self.checkBShowShBlackList.setEnabled(False)
				self.checkBShowAssBlackList.setEnabled(False)
				self.checkBShowShBlackList.setChecked(False)
				self.checkBShowAssBlackList.setChecked(False)
				
			self.tabAssetsTableUi()
			self.tabShotTableUi()
			self.tabProducUi()
			if len(self.usuarios_list + self.productores_list) == 0:
				self.userCreateRequeriment()

	def choosingUser(self):
		self.userName = str (self.comboBoxUsers.currentText())
		if self.userName != "     --- User Name ---":
			self.labUserName.setText( self.userName )
			self.labUserName.setStyleSheet("color: rgb(10, 170, 160)")
			with open( temp_folder + "/user_task_manager_presets.json", "w") as file:
				file.write('{"user" : "%s"}' %str( self.userName))
				file.close()
			self.setButUsOnOff(self.qButAddProArtist)
			self.setButUsOnOff( self.qButtCreateShots)
			self.setButUsOnOff( self.qButtCreateAssets)
			self.setButUsOnOff(self.qButSetTemplates)
			self.setButUsOnOff(self.qButImportSkacUs)
			self.setButUsOnOff(self.qButEditUsers)
			self.setButUsOnOff(self.qButEditProjSett)
			self.setButUsOnOff(self.qButSetRenderRoot)
			if self.userName in self.productores_list or self.userName in self.lideres_list:
				self.checkBShowShBlackList.setEnabled(True)
				self.checkBShowAssBlackList.setEnabled(True)
			else:
				self.checkBShowShBlackList.setEnabled(False)
				self.checkBShowAssBlackList.setEnabled(False)
				self.checkBShowShBlackList.setChecked(False)
				self.checkBShowAssBlackList.setChecked(False)

			self.getTableShot()   # esto me resetea la tabla
			self.getTableAsset()
			self.getTableUser()
			
			self.tablaWidgShots.clear()
			self.tablaWidgAssets.clear()
			
			self.qButtRefreshShotT.setEnabled(False)
			self.qButtRefreshShotT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px; border-style: groove")  # fuente gris
			shadow = QGraphicsDropShadowEffect(self)
			shadow.setEnabled(False)
			self.qButtRefreshShotT.setGraphicsEffect(shadow)
			
			self.qButtLoadShots.setEnabled(True)
			self.qButtLoadShots.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px; border-style: groove")
			shadow = QGraphicsDropShadowEffect(self)
			self.shadowButt ( shadow )	
			self.qButtLoadShots.setGraphicsEffect(shadow)

			self.qButtRefreshAssT.setEnabled(False)
			self.qButtRefreshAssT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px; border-style: groove")  # fuente gris
			shadow = QGraphicsDropShadowEffect(self)
			shadow.setEnabled(False)
			self.qButtRefreshAssT.setGraphicsEffect(shadow)
		
			self.qButtLoadAssets.setEnabled(True)
			self.qButtLoadAssets.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px; border-style: groove")
			shadow = QGraphicsDropShadowEffect(self)
			self.shadowButt ( shadow )	
			self.qButtLoadAssets.setGraphicsEffect(shadow)

	def textFramesDone(self):
		if str( self.textEdFramesSh.toPlainText() ).isdigit():
			self.textDone(self.tablaWidgShots, "shots","frames_cant", self.textEdFramesSh, self.fpsCant_column_idx, self.idSh_column_idx , self.rowsShLockedList, self.rowsShBlackListed )
		else:
			QMessageBox.information(None, u' invalid parameter ', " Only Digit Characters" )

	def textFullItemDone(self, textEdit,column_idx,dbColumn ):
		shotName =  self.currentRowText(self.tablaWidgShots , self.shot_column_idx)
		seq =  self.currentRowText(self.tablaWidgShots ,self.seq_column_idx)
		texto = str(textEdit.toPlainText())
		for i, tupla in enumerate ( self.dbShInformLoaded):
			if tupla[2] == shotName and tupla[4] and seq :
				id = tupla[0]
				self.updateValueOnColumn( self.projectDataBase ,"shots" ,dbColumn,texto, id)			
		for i, tupla in enumerate ( self.dbShInformFiltered):
			if tupla[2] == shotName and tupla[4] and seq :
				item = QTableWidgetItem(texto)
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				if i % 2 == 0:
					item.setBackground(QBrush(QColor(200, 200, 200)))
				else:
					item.setBackground(QBrush(QColor(180, 180, 190)))
				item.setForeground(QBrush(QColor(0, 0, 0)))
				if i in self.rowsShLockedList:
					item.setBackground(QColor(125,125,125))
					item.setForeground(QColor(150,150,150))
				if i in self.rowsShBlackListed:
					item.setBackground(QColor(50,45,45))
					item.setForeground(QColor(125,125,125))				
				self.tablaWidgShots.setItem( i, column_idx, item )

	def makePlatblast( self, path):
		filepath_maya = mc.file(q=True, sn=True)
		nameSceneVer = filepath_maya.split("/")[-1]
		name =  nameSceneVer.split(".m")
		now = datetime.now()
		date = "d" + str (now.day) + "_m" + str(now.month) + "_h" + str(now.hour) + "_" + str(now.minute)
		name = name[0] + "__"+ date
		wh = self.settin_list[2].split(",")
		w = int( wh[0].split("w")[-1] )
		h = int( wh[1].split("h")[-1] )
		start = int (mc.playbackOptions( min=True, q =True ))
		end = int (mc.playbackOptions( max=True, q =True ))
		lista = []
		for f in range(start,end):
			n = f + start
			lista.append(n)
		currentPanel = mc.playblast( ae = True )
		mc.modelEditor (currentPanel, edit = True, grid = False, hud = False  ,alo = False)
		mc.modelEditor (currentPanel, edit = True, polymeshes = True,str = True , da = "smoothShaded")
		mc.playblast( format = self.settin_list[3], f = path  + name , h = h, w = w, frame = lista , viewer = True, orn = False, fp = 3, fo = True, p = 100, qlt = 100)
		os.startfile( path )

	def makeConceptCapture(self, path, name):
		#if os.path.isfile( "C:/Users/" + user + "/Documents/prG.mp3" ):
		#	shutil.copy2( os.path.join( "W:/PAPERBIRDS/PIPELINE/TOOLS/" ,"prG.mp3" ), os.path.join( "C:/Users/" + user + "/Documents/ ,"prG.mp3")  )
		nircmd_exec = "nircmd_exec.bat"
		vbsCurrentLines = self.vbsCreator( nircmd_exec )
		now = datetime.now()
		date = "d" + str (now.day) + "_m" + str(now.month) + "_h" + str(now.hour) + "_" + str(now.minute)
		name = name + "__"+ date
		imagPath = path.replace ("/", "\\")
		nircmdFilePath = self.root + self.projName
		nircmdFilePath = nircmdFilePath.replace ("/", "\\")
		nircmdFilePath = nircmdFilePath   + "\\PIPELINE\\CONFIGURATION\\TOOLS\\nircmd\\nircmd.exe"
		linesBat = nircmdFilePath + " cmdwait 2500 savescreenshotwin " + imagPath + name + ".png" + "  beep 1600 500"
		with open( temp_folder + "/"+nircmd_exec, "w") as file:
			file.write( linesBat)
			file.close()		
		with open( temp_folder + "/vbs_batExcuter.vbs", "w") as file:
			file.write( vbsCurrentLines )
			file.close()
		call([r"" + temp_folder + "/nircmd_exec.bat"])
		#call([r"ffplay","prG.mp3"])
		#os.system("c:\blabla\SysWoW64\cscript.exe  " + temp_folder.replace("/", "\\") + "\\vbs_batExcuter.vbs"  )
		#from subprocess import Popen
		#Popen(temp_folder + "/vbs_batExcuter.vbs")
		#call([r"" + temp_folder.replace("/", "\\")+ "\\vbs_batExcuter.vbs"])
		#time.sleep (3)
		if os.path.isfile( path + name + ".png" ):
			os.startfile( path + name + ".png")

	def vbsCreator (self, batName):
		fileVbs = 'Set oShell = CreateObject ("Wscript.Shell") \nDim strArgs  \nstrArgs = "cmd /c '+ batName + '" \noShell.Run strArgs, 0, false  '
		return fileVbs

	def clickedShotMediaThumb(self, shpath, shname):
		#if self.scripJCounter1 == self.scripJCounter2 and self.key04 == True:
		type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
		nircmd_exec = "nircmd_exec.bat"
		#self.thumbMayanailCommand( 100,145, shotPath, self.ShotFileName  + "_thumbnail.jpg")
		#shotPath + "/" + self.ShotFileName  + "_thumbnail.jpg" 
		imagPath = shpath.replace ("/", "\\")
		projPath = self.root + self.projName
		projPath = projPath.replace ("/", "\\")
		nircmdFilePath = projPath   + "\\PIPELINE\\CONFIGURATION\\TOOLS\\nircmd\\nircmd.exe"
		linesBat = nircmdFilePath + " cmdwait 1500 savescreenshotwin " + imagPath +"\\" + shname + "_thumbnail.jpg" + "  beep 1600 500"
		ffmepgLine = "\n" + temp_folder.replace("/", "\\") + "\\ffmpeg -y -i " + imagPath +"\\" + shname + "_thumbnail.jpg" + " -vf scale=145:100 " + imagPath +"\\" + shname + "_thumbnail.jpg"
		with open( temp_folder + "/" + nircmd_exec, "w") as file:
			file.write( linesBat + ffmepgLine)
			file.close()		
		call([r"" + temp_folder + "/nircmd_exec.bat"])
		self.tablaWidgShots.setCellWidget(self.tablaWidgShots.currentRow(), self.thumnbSh_column_idx, getThumbnClass(self, shpath + "/" + shname  + "_thumbnail.jpg" ))

	def clickedAssetImageThumb(self):
		tipo_Asset = self.currentRowText(self.tablaWidgAssets ,self.assetType_column_idx)
		assname = self.currentRowText(self.tablaWidgAssets ,self.asset_column_idx)
		asspath = self.root  + self.projName + assetMayaFol + tipo_Asset  + "/" + assname
		nircmd_exec = "nircmd_exec.bat"
		imagPath = asspath.replace ("/", "\\")
		projPath = self.root + self.projName
		projPath = projPath.replace ("/", "\\")
		nircmdFilePath = projPath   + "\\PIPELINE\\CONFIGURATION\\TOOLS\\nircmd\\nircmd.exe"
		linesBat = nircmdFilePath + " cmdwait 1500 savescreenshotwin " + imagPath +"\\" + assname + "_thumbnail.jpg" + "  beep 1600 500"
		ffmepgLine = "\n" + temp_folder.replace("/", "\\") + "\\ffmpeg -y -i " + imagPath +"\\" + assname + "_thumbnail.jpg" + " -vf scale=180:145 " + imagPath +"\\" + assname + "_thumbnail.jpg"
		with open( temp_folder + "/" + nircmd_exec, "w") as file:
			file.write( linesBat + ffmepgLine)
			file.close()		
		call([r"" + temp_folder + "/nircmd_exec.bat"])
		self.tablaWidgAssets.setCellWidget(self.tablaWidgAssets.currentRow(), self.thumnbAss_column_idx, getThumbnClass(self, asspath + "/" + assname  + "_thumbnail.jpg" ))

	def clickedShotThumb (self):
		#if self.scripJCounter1 == self.scripJCounter2 and self.key04 == True:
		type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
		try:
			shotPath = self.shotPath.split( "/" + self.ShotFileName)[0]
			shotPath = shotPath + "/" + self.ShotFileName
			self.thumbMayanailCommand( 100,145, shotPath, self.ShotFileName  + "_thumbnail.jpg")
			self.tablaWidgShots.setCellWidget(self.tablaWidgShots.currentRow(), self.thumnbSh_column_idx, getThumbnClass(self, shotPath + "/" + self.ShotFileName  + "_thumbnail.jpg" ))
		except AttributeError: 
			print "No Pipeline Opening"

	def clickedAssetThumb (self):
		#if self.scripJCounter1 == self.scripJCounter2 and self.key01 == True:
		type_task = self.currentRowText(self.tablaWidgAssets ,self.taskAssType_column_idx)
		try:
			assetPath = self.assetPath.split( "/" + type_task + "/" + version_folder )[0]
			self.thumbMayanailCommand( 145,180, assetPath, self.AssetFileName  + "_thumbnail.jpg")
			self.tablaWidgAssets.setCellWidget(self.tablaWidgAssets.currentRow(), self.thumnbAss_column_idx, getThumbnClass(self, assetPath + "/" + self.AssetFileName  + "_thumbnail.jpg" ))
		except AttributeError: 
			print "No Pipeline Opening"

	def blackListItemShot (self, dbTable, dbColumn, value, currentID):
		self.updateValueOnColumn( self.projectDataBase,dbTable,dbColumn,value,currentID )
		self.refresh_shots_table()
		# refresh self.tablaWidgShots
		
	def menuShotDespleg(self, position):  # menu flotante que se despliega con clic derecho en las celdas
		items_list = self.tablaWidgShots.selectedItems()
		selectedRow=[]
		for i in  items_list:
			selectedRow.append ( i.row())	
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			key01 = True
			key02 = True
		else:
			key01 = False
			if self.userName ==  self.currentRowText(self.tablaWidgShots , self.asignSh_column_idx):
				key02 = True
			else:
				key02 = False
		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Status':
			if key01 or key02:
				if self.userName in self.lideres_list:
					self.status_list = status_list + statusOnlySuperv_list
				else:
					if self.userName ==  self.currentRowText(self.tablaWidgShots , self.asignSh_column_idx) or self.userName in self.productores_list:
						self.status_list = status_list
					else:
						self.status_list = []
				menuSho02 = QMenu()
				menuSho02.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				for status in self.status_list:
					statusAction = menuSho02.addAction(status)
				action02 = menuSho02.exec_(self.tablaWidgShots.mapToGlobal(position))
				if action02 != None :  # es un objeto
					query = "UPDATE shots SET status=? WHERE id IN ("
					mensaje =  ""
					idtuple = [str(action02.text())]				
					for i, curreRow in enumerate (selectedRow) :
						item = QTableWidgetItem(action02.text())
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgShots.setItem( curreRow,self.statusSh_column_idx, item )
						
						labStatus = QLabel(action02.text())
						labStatus.setGeometry(QtCore.QRect( 0 , 0, 100, 20))
						labStatus.setAlignment(QtCore.Qt.AlignCenter)
						

						#status_list = ["On Hold", "Done", "Wip" , "Not Started"]
						if status_list[0] == item.text():
							labStatus.setStyleSheet("background-color: rgb(190, 90, 90); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 15px; border-style: solid;")
						if status_list[1] == item.text():
							labStatus.setStyleSheet("background-color: rgb(150, 215, 150); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						if status_list[2] == item.text():
							labStatus.setStyleSheet("background-color: rgb(210, 210, 120); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						if status_list[3] == item.text():
							labStatus.setStyleSheet("background-color: rgb(170, 205, 220); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
							
						if statusOnlySuperv_list[0] == item.text():
							labStatus.setStyleSheet("background-color: rgb(80, 190, 80); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						self.tablaWidgShots.setCellWidget(curreRow ,self.statusSh_column_idx, labStatus)
							
						if curreRow in self.rowsShLockedList:
							self.tablaWidgShots.item(curreRow, self.statusSh_column_idx).setBackground(QColor(125,125,125))
							self.tablaWidgShots.item(curreRow, self.statusSh_column_idx).setForeground(QColor(150,150,150))	
						if curreRow in self.rowsShBlackListed:
							self.tablaWidgShots.item(curreRow, self.statusSh_column_idx).setBackground(QColor(50,45,45))
							self.tablaWidgShots.item(curreRow, self.statusSh_column_idx).setForeground(QColor(125,125,125))	
						currentID = self.tablaWidgShots.item( curreRow,self.idSh_column_idx)  # saber el id
						currentID = currentID.text()
						if i < len(selectedRow) -1:
							query = query + " ?, "
						elif i == len(selectedRow) -1:
							query = query + " ? "
						idtuple.append (int (currentID))
						#self.updateValueOnColumn( self.projectDataBase ,"shots" ,"status",action02.text(), currentID)
						type_task = self.tablaWidgShots.item( curreRow,self.taskShType_column_idx) 
						shot = self.tablaWidgShots .item( curreRow,self.shot_column_idx)   # el index de la columna de lo que quiera saber	
						mensaje = mensaje + "     " + str (shot.text()) +"   " + str (type_task.text()) + "  is " + action02.text() + " ...\n"
					nombre =  self.currentRowText(self.tablaWidgShots ,self.asignSh_column_idx)
					self.slackBot( mensaje, self.diccUsSlack [ nombre ] )						
					self.slackBot( mensaje, self.settin_list[10] )
					query = query + "); "
					idtuple = tuple( idtuple )
					conn = sqlite3.connect ( self.projectDataBase )
					c = conn.cursor()	
					c.execute( query, idtuple )
					conn.commit()
					conn.close()
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))

		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Shot':
			if self.userName != "None":
				type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
				shot = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
				seqName = self.currentRowText(self.tablaWidgShots , self.seq_column_idx)
				thumbMediaPath = win.root + "/" + win.projName  + parchePB01 + parcheSantiT02 + "/" + seqName + "/" + shot + "/"
				shotPath = thumbMediaPath + type_task + "/"
				menuSho01 = QMenu()
				menuSho01.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				currentID = self.currentRowText(self.tablaWidgShots ,self.idSh_column_idx )
				dbRowShLoaded = self.selectDbRow( self.projectDataBase,"shots" , currentID)
				if key01:
					if dbRowShLoaded[0][16] == 0:
						blackLShAction = menuSho01.addAction("BlackList task", lambda : self.blackListItemShot( "shots","blackListed",1,currentID ) )
					elif dbRowShLoaded[0][16] == 1:
						blackLShAction = menuSho01.addAction("WhiteList task", lambda : self.blackListItemShot( "shots","blackListed",0,currentID ) )
				if dbRowShLoaded[0][11] == 1: #  coulmna de shot db
					isPublishAction = menuSho01.addAction("Published:  " + dbRowShLoaded[0][12] )
				else:
					isPublishAction = menuSho01.addAction("Not Published ")
				doThumbnailAction = menuSho01.addAction("Do Thumbnail", self.clickedShotThumb )
				doThumbnailAction = menuSho01.addAction("Do Media Thumbnail", lambda : self.clickedShotMediaThumb( thumbMediaPath , shot) )	
				sub_db_idx = dbRowShLoaded[0][15]
				if len(type_task.split ("_SUB")) > 1:
					type_tasksub = type_task.split("_")
					shotPath = win.root  + win.projName  + parchePB01 + parcheSantiT02 + "/"  + seqName + "/" + shot + "/"+ type_tasksub[0] + "/" + "_" + type_tasksub[1] + "/"
				exploreAction = menuSho01.addAction("Explore", lambda: self.openFolder(shotPath))
				if self.userName ==  dbRowShLoaded[0][9]:  # pregunta directamente a la base de datos
					for i, tupla in enumerate (self.dbShInformFiltered):
						if i == self.tablaWidgShots.currentRow():
							bool = tupla[14]
					if bool:
						unlockShotsAction = menuSho01.addAction("Unlock Current Task", self.unlockShotsAction)				
					else:
						lockShotsAction = menuSho01.addAction("Lock Current Task", self.lockShotsAction)
				else:
					if self.tablaWidgShots.currentRow() in  self.rowsShLockedList:
						unlockableShotsAc = menuSho01.addAction("Can not unlock")
				playbastAction = menuSho01.addAction("PlayBlast Options")
				action01 = menuSho01.exec_(self.tablaWidgShots.mapToGlobal(position))   # la variable action la uso si necesito sub acciones4
				if action01 == playbastAction:
					shotName = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
					seqName = self.currentRowText(self.tablaWidgShots , self.seq_column_idx)
					shTaskType = self.currentRowText(self.tablaWidgShots , self.taskShType_column_idx)
					path = self.root  + self.projName + parchePB01 + parcheSantiT02 + "/" + seqName + "/" + shotName  + "/" + shTaskType + "/"  + playblaset_fol + "/"
					subMenuPB = QMenu()
					subMenuPB.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
					playblasFiles = glob.glob( path + shot + "_" + type_task + "_v*")
					playblasFiles.sort(key=os.path.getctime) 
					SubAction01 = subMenuPB.addAction("Open last PlayBlast", lambda: self.openSelectPLayB (playblasFiles , type_task) )
					SubAction02 = subMenuPB.addAction("Explore PB Versions", lambda: os.startfile( path ) )
					SubAction02 = subMenuPB.addAction("Do PlayBlast", lambda : self.makePlatblast(path) )
					sub_Action = subMenuPB.exec_(self.tablaWidgShots.mapToGlobal(position))	

		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Comments':
			if key02:
				menuSh00 = QMenu()
				menuSh00.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				commentAction = menuSh00.addAction("                                     Done",lambda: self.textDone(self.tablaWidgShots, "shots","comments", self.textEdCommSh, self.commentSh_column_idx, self.idSh_column_idx, self.rowsShLockedList, self.rowsShBlackListed ))
				self.textEdCommSh = QTextEdit(menuSh00)
				self.textEdCommSh.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdCommSh.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionSh00 = menuSh00.exec_(self.tablaWidgShots.mapToGlobal(position))
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))

		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Nice_Name':
			if key02:
				menuShNice = QMenu()
				menuShNice.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				niceAction = menuShNice.addAction("                                     Done", lambda:  self.textFullItemDone(self.textEdNiceNamSh, self.niceShName_column_idx, "nice_name")   )
				self.textEdNiceNamSh  = QTextEdit(menuShNice)
				self.textEdNiceNamSh.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdNiceNamSh.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionShNice = menuShNice.exec_(self.tablaWidgShots.mapToGlobal(position))
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
				
		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Frames':
			if key02:
				menuShFrame = QMenu()
				menuShFrame.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				frameAction = menuShFrame.addAction("                                   Done", lambda: self.textFullItemDone(self.textEdFramesSh, self.fpsCant_column_idx, "frames_cant") )
				self.textEdFramesSh  = QTextEdit(menuShFrame)
				self.textEdFramesSh.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdFramesSh.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionShFrame = menuShFrame.exec_(self.tablaWidgShots.mapToGlobal(position))
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))		
		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Assigned':
			if key01:					
				menuSho03 = QMenu()
				menuSho03.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				for user in self.usuarios_list:
					if user != "     --- User Name ---":
						userAction = menuSho03.addAction(user)
				userAction = menuSho03.addAction("Set Artist")
				action03 = menuSho03.exec_(self.tablaWidgShots.mapToGlobal(position))
				if action03 != None :
					for curreRow in selectedRow :
						item = QTableWidgetItem(action03.text())
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgShots.setItem( curreRow,self.asignSh_column_idx, item )  #  la columna de asignados
						item.setForeground(QBrush(QColor(175, 50, 175)))
						if curreRow % 2 == 0:
							item.setBackground(QBrush(QColor(200, 200, 200)))
						else:
							item.setBackground(QBrush(QColor(180, 180, 190)))						
						if curreRow in self.rowsShLockedList:
							self.tablaWidgShots.item(curreRow, self.asignSh_column_idx).setBackground(QColor(125,125,125))
							self.tablaWidgShots.item(curreRow, self.asignSh_column_idx).setForeground(QColor(150,150,150))
						if curreRow in self.rowsShBlackListed:
							self.tablaWidgShots.item(curreRow, self.asignSh_column_idx).setBackground(QColor(50,45,45))
							self.tablaWidgShots.item(curreRow, self.asignSh_column_idx).setForeground(QColor(125,125,125))						
						currentID = self.tablaWidgShots.item( curreRow,self.idSh_column_idx)  # saber el id
						currentID = currentID.text()
						self.updateValueOnColumn( self.projectDataBase ,"shots" ,"asignado",action03.text(), currentID)
						if "Set Artist" != item.text() and  self.diccUsSlack [ str (action03.text() ) ] != "-":
							type_task = self.tablaWidgShots.item( curreRow,self.taskShType_column_idx) 
							shot = self.tablaWidgShots .item( curreRow,self.shot_column_idx)
							mensaje = "       Task  " + str (shot.text()) + "  " + str (type_task.text()) + "   Assigned"
							self.slackBot( mensaje, self.diccUsSlack [ str (action03.text() ) ] )						
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))	
				
		if self.tablaWidgShots.horizontalHeaderItem(self.tablaWidgShots.currentColumn()).text() == 'Task_Type':						
			if key01 and  masterPass != "unable":						
				menuSho04 = QMenu()
				menuSho04.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				curreRow = self.tablaWidgShots.currentRow()
				niceName = self.currentRowText(self.tablaWidgShots ,self.niceShName_column_idx)
				task_listt = self.settin_list[7]
				type_task = self.currentRowText(self.tablaWidgShots ,self.taskShType_column_idx)
				area = self.currentRowText(self.tablaWidgShots ,self.area_column_idx)
				seq = self.currentRowText(self.tablaWidgShots ,self.seq_column_idx)
				shot = self.currentRowText(self.tablaWidgShots ,self.shot_column_idx)
				currentID = self.currentRowText(self.tablaWidgShots ,self.idSh_column_idx )
				dbRowShLoaded = self.selectDbRow( self.projectDataBase,"shots" , currentID)
				sub_db_idx = dbRowShLoaded[0][15]
				if len ( type_task.split("_SUB") ) < 2:
					task_instance = []
					for row in self.dbShInformLoaded:
						if shot == row[2] and area == row[4] :
							task_instance.append (row[5])
					task_instance2 = []
					for t in task_instance:
						if len ( t.split("_SUB") ) < 2:
							task_instance2.append (t)
					for task in task_listt:
						if task not in task_instance2:
							taskAction = menuSho04.addAction("create " + task + " task")
					if len (task_instance2) == len (task_listt) :
						taskAction = menuSho04.addAction("no more task for create")
					if len ( type_task.split("_SUB") ) < 2:	
						taskAction = menuSho04.addAction("add subtask for reassign")
					if sub_db_idx > 0:
						taskAction = menuSho04.addAction("assembly publish sub tasks")
					actionSho04 = menuSho04.exec_(self.tablaWidgShots.mapToGlobal(position))
					if actionSho04 == None:
						print ""
					elif actionSho04.text() == "no more task for create":
						print ""
					elif actionSho04.text() == "assembly publish sub tasks":
						projPath = self.root + self.projName
						templatePath =  projPath + "/PIPELINE/TEMPLATES/ASSET/"
						tamplaName = "EMPTY_TEMPLATE" + self.settin_list[5]
						shotMainPubName = shot + "_" + type_task 
						shotMainPublishPath = projPath + parchePB01 + parcheSantiT02 + "/" + seq + "/" + shot + "/" + type_task +  "/" + publish_folder + "/"
						shotPathRoot = projPath + parchePB01 + parcheSantiT02 + "/" + seq + "/" + shot + "/" + type_task +  "/" 
						shutil.copy2( os.path.join( templatePath, tamplaName ) ,  os.path.join (shotMainPublishPath , shotMainPubName + self.settin_list[5] )  )						
						counter = 1
						self.scripJCounter1= self.scripJCounter1 + 1
						mc.file ( shotMainPublishPath + shotMainPubName + self.settin_list[5], o=True , force = True )
						currentSubPath = shotPathRoot + "_SUB" + str(counter) + "/" + publish_folder + "/"
						currentSubName = shotMainPubName + "_SUB" + str(counter) + self.settin_list[5]
						print currentSubPath
						print currentSubName
						if os.path.isfile( currentSubPath   + currentSubName   ) :
							name = mc.file(currentSubPath + currentSubName , i=True, uns = False, force = True  , renamingPrefix = "" )
						for i in  range(sub_db_idx - 1):
							counter+= 1
							currentSubPath = shotPathRoot + "_SUB" + str(counter) + "/" + publish_folder + "/"
							currentSubName = shotMainPubName + "_SUB" + str(counter) + self.settin_list[5]
							if os.path.isfile(currentSubPath + currentSubName) :
								name = mc.file(currentSubPath + currentSubName , i=True, uns = False, force = True  , returnNewNodes = True ) # , rnn = True  ,  mnc = True     , l = True   defaultNamespace = True , renamingPrefix = ""   , rep = False 
								#importedObje = mc.file(path , i=True, uns = False , returnNewNodes = True)
								list = []
								for item in name:
									list.append (str ("|" + str(item) ))
								list = mc.ls(list, type = "transform")
								allMain = mc.ls("|*")
								for t in  list:
									if t in allMain:
										print shotMainPubName + "_SUB" + str(counter) + "_"
										originalRootGroup = t.split ( shotMainPubName.split("_")[-1] + "_SUB" + str(counter) + "_")[-1]
										try:
											hijos = mc.listRelatives (t, c = True,type = "transform" )
											for h in hijos:
												mc.parent ( h , originalRootGroup)
										except Exception:
											pass
										mc.delete (t)
										
						mc.file(s=True , force = True )
						#self.publiAssembAndNon (type_task, shot, shotMainPublishPath) # currentID
						now = datetime.now()
						date = str (now.day) + " / "+ str(now.month) +" __ "+ str(now.hour) + ":" + str(now.minute)
						self.updateValueOnColumn( self.projectDataBase ,"shots" ,"isPublished",1, currentID)			
						self.updateValueOnColumn( self.projectDataBase ,"shots" ,"lastPublishDate",date, currentID)
						self.wind.setWindowTitle("Pr-G  Manager" + "     " + shot + " " + type_task )
						time = "  last publish: \n " + date
						self.labSceneShotName.setText(  shot + "   " + type_task)
						self.labSceneShotName.show()						
						win.labPublishShotDate.setText( time)
						win.labSceneShotVers.setText("Publish Version\n   -not editable-")	
						win.labPublishShotDate.show()
						win.labSceneShotVers.show()
						if parchePB_Copy2publiFol:
							assetFol = parchePB01.split("/")[-1]
							publishFolPath = shotMainPublishPath.split(parcheSantiT02.split("/")[-1])
							if not os.path.exists( publishFolPath[0]  + publish_folder_alternativePB + parcheSantiT02 + publishFolPath[1]) :
								os.makedirs( publishFolPath[0]  + publish_folder_alternativePB + parcheSantiT02 + publishFolPath[1] )
							shutil.copy2( os.path.join( shotMainPublishPath , shotMainPubName + self.settin_list[5] ), os.path.join( publishFolPath[0] + publish_folder_alternativePB + parcheSantiT02 + publishFolPath[1] ,  shotMainPubName + self.settin_list [5] ) )
						self.tabAssManipLabOff()
						QMessageBox.information(None, u' ',  " Succes!! Scene Published!!!!  ")
						mensaje = "    Just Published :    " + shot + "_" + type_task + "  Assembly " + "    !!!!!! "
						self.slackBot( mensaje, self.settin_list[10] )

					elif actionSho04.text().startswith("create") or actionSho04.text().startswith("add"):
						id_list = self.getAllIDs(self.projectDataBase,"shots")
						id = len(id_list)
						if id in id_list:
							while id in id_list:
								id+= 1
						vacio = " "
						conn = sqlite3.connect ( self.projectDataBase)
						c = conn.cursor()
						if actionSho04.text() != "add subtask for reassign":
							taskk =  actionSho04.text().split(" ")[1]
							c.execute("INSERT INTO shots (id, shot_name, sequence_name, nice_name, comments, frames_cant, status, area, task_type,asignado, isPublished, lastPublishDate, isLocked, subtasked, blackListed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" ,(id,shot,seq,niceName,vacio,1, status_list[3],area_listt[0],taskk,"Set Artist",0," ",0,0,0))
						elif actionSho04.text() == "add subtask for reassign":
							sub_db_idx = sub_db_idx + 1
							taskk =  type_task + "_SUB" + str(sub_db_idx)
							# aca tengo que poner un update de la main task con 
							self.updateValueOnColumn( self.projectDataBase ,"shots" ,"subtasked",sub_db_idx, currentID)
							c.execute("INSERT INTO shots (id, shot_name, sequence_name, nice_name, comments, frames_cant, status, area, task_type,asignado, isPublished, lastPublishDate, isLocked, subtasked,blackListed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" ,(id,shot,seq,niceName,vacio,1, status_list[3],area_listt[0],taskk,"Set Artist",0," ",0,"-",0))
							self.subTask(id, shot, seq, type_task ,sub_db_idx)
						conn.commit()
						conn.close()
						self.refresh_shots_table()
			else:
				menuuu = QMenu()
				menuuu.setStyleSheet("background-color: rgb(200,190,160) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				acc = menuuu.addAction(" not available ")
				actionn = menuuu.exec_(self.tablaWidgAssets.mapToGlobal(position))
				
	def openSelectPLayB (self, lista , taskType):
		if len (lista) == 0:
			QMessageBox.information(None, u' Issue !', "No PlayBlast for: " + taskType + "  Task, please, Explore playBlast folder" )
		else:
			os.startfile( lista[0]) 	

	def subTask(self, id, shotName,sequ, task ,sub_db_idx):
		path =  str( win.root + "/" + win.projName + parchePB01 + parcheSantiT02 + "/" + sequ + "/" + shotName + "/" + task)
		wipPath = path + "/" + version_folder
		for fol in [publish_folder, version_folder]:
			subPath = path + "/" + "_SUB" + str(sub_db_idx) + "/" + fol
			if not os.path.exists(subPath):
				os.makedirs(subPath)
		mainTaskVerList =  glob.glob ( wipPath + "/" + shotName + "_" + task + "_v*" + self.settin_list[5] )
		shutil.copy2( os.path.join( wipPath , mainTaskVerList[-1].split("\\")[-1]) ,  os.path.join ( path + "/" + "_SUB" + str(sub_db_idx) + "/" + version_folder  ,   shotName + "_" + task + "_SUB" + str(sub_db_idx) + "_v000" + win.settin_list[5] ))

	def refreshShDB (self ):
		query ='SELECT * FROM shots'
		counter = 0
		if str(self.comboBfilterShotArea.currentText()) == "All":
			shArea = "%"
		else:
			shArea = str(self.comboBfilterShotArea.currentText())
			query = query + ' WHERE area LIKE "%s" ' %shArea
			counter = counter + 1 
		if self.comboBfilterShStatus.currentText() == "All":
			status = "%"
		else:
			status = str(self.comboBfilterShStatus.currentText())
			if counter > 0:
				query = query + ' AND status LIKE "%s" ' %status
				counter = counter + 1 
			else:
				query = query + ' WHERE status LIKE "%s" ' %status
				counter = counter + 1
		if self.comboBfilterShoTaskType.currentText() == "All":
			task = "%"
		else:
			task = str(self.comboBfilterShoTaskType.currentText()) + "%"
			if counter > 0:
				query = query + ' AND task_type LIKE "%s" ' %task
				counter = counter + 1 
			else:
				query = query + ' WHERE task_type LIKE "%s" ' %task
				counter = counter + 1 
		if self.comboBfilterShAsigned.currentText() == "All":
			userName = "%"
		else:
			userName =  str(self.comboBfilterShAsigned.currentText())
			if counter > 0:
				query = query + ' AND asignado LIKE "%s" ' %userName
				counter = counter + 1 
			else:
				query = query + ' WHERE asignado LIKE "%s" ' %userName
				counter = counter + 1 
		if self.comboBfilterShPublish.currentText() == "All":
			published = "%"
		else:
			published = str( self.comboBfilterShPublish.currentText())
			if published == "Published":
				bool = 1
			else:
				bool = 0
			if counter > 0:
				query = query + ' AND isPublished LIKE %s ' %bool
				counter = counter + 1 
			else:
				query = query + ' WHERE isPublished LIKE %s ' %bool
				counter = counter + 1
		if str(self.textEdFiltShot.toPlainText()) == "":
			shoName = "%"
		else:
			shoName = "%" + str(self.textEdFiltShot.toPlainText()) + "%"
			if counter > 0:
				query = query + ' AND shot_name LIKE "%s" ' %shoName
				counter = counter + 1
			else:
				query = query + ' WHERE shot_name LIKE "%s" ' %shoName
				counter = counter + 1	

		if not self.checkBShowShBlackList.isChecked ():
			if counter > 0:
				query = query + ' AND blackListed LIKE %s ' %0
			else:
				query = query + ' WHERE blackListed LIKE %s ' %0
		else:
			if counter > 0:
				query = query + ' AND blackListed LIKE %s' %1
			else:
				query = query + ' WHERE blackListed LIKE %s' %1

		query = query + ' ;'
		self.dbShInformLoaded = self.selectAllDB (self.projectDataBase,"shots" )
		conn = sqlite3.connect ( self.projectDataBase )
		c = conn.cursor()
		c.execute(query)
		self.dbShInformFiltered = c.fetchall()  # dbAsInformFiltered
		conn.close()

	def refresh_shots_table (self):
		self.refreshShDB ()
		self.tablaWidgShots.setRowCount(len(self.dbShInformFiltered))
		self.tablaWidgShots.setColumnCount(12)     #  setea la cantidad de columnas!!!!!
		for i, header in enumerate (['Thumbnail','Seq','Shot',"Nice_Name" ,'Area', 'Task_Type', 'Comments',"Frames", "Assigned", "ID","Status", "\n"]):
			locals()["item"+ str(i)] = QTableWidgetItem(header)
			locals()["item"+ str(i)].setBackground(QColor(180, 75, 65))
			self.tablaWidgShots.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )
			#self.tablaWidgShots.setStyleSheet(" border-radius: 15px;") 
		###############   columnas        0       1      2        3          4         5            6          7           8       9     10  
		
		###############  DB_column        1       3      2       13          4         5           6           7           9       0      8
		self.statusSh_column_idx = 10
		self.asignSh_column_idx = 8
		self.idSh_column_idx = 9
		self.shot_column_idx = 2
		self.seq_column_idx = 1
		self.thumnbSh_column_idx = 0
		self.area_column_idx = 4
		self.taskShType_column_idx = 5
		self.commentSh_column_idx = 6
		self.fpsCant_column_idx = 7
		self.priortySh_column_idx = 11
		self.niceShName_column_idx = 3
		self.tablaWidgShots.setColumnWidth(11, 1)
		self.tablaWidgShots.setColumnWidth(self.thumnbSh_column_idx, 145)
		self.tablaWidgShots.setColumnWidth(self.commentSh_column_idx, 281)   #  seteo el ancho en la columna de comentarios
		self.tablaWidgShots.setColumnWidth(self.fpsCant_column_idx, 50)
		self.tablaWidgShots.setColumnWidth(self.idSh_column_idx, 50)
		self.tablaWidgShots.setColumnWidth(self.taskShType_column_idx, 84)
		self.tablaWidgShots.setColumnWidth(self.area_column_idx, 60)
		self.tablaWidgShots.setColumnWidth(self.shot_column_idx, 110)
		self.tablaWidgShots.setColumnWidth(self.seq_column_idx, 45)
		self.tablaWidgShots.setColumnWidth(self.niceShName_column_idx, 105)
		self.tablaWidgShots.setColumnWidth(self.statusSh_column_idx, 93)
		self.rowsShLockedList = []
		self.rowsShBlackListed = []
		for i,dbShCellData in enumerate(self.dbShInformFiltered ):
			self.tablaWidgShots.setRowHeight(i, 90)
			id = str(dbShCellData[0]) #  es el index en la base de datos
			sName = str(dbShCellData[2])
			seqName = str(dbShCellData[3])
			niceName = str(dbShCellData[13])
			area = str(dbShCellData[4])
			task_type = str(dbShCellData[5])
			comentarios = str(dbShCellData[6])
			Frames = str(dbShCellData[7])
			artist = str(dbShCellData[9])
			status = str(dbShCellData[8])
			self.isLockedSh = str(dbShCellData[14])
			self.tablaWidgShots.setCellWidget(i, self.thumnbSh_column_idx, getThumbnClass(self, self.labRootProjectPath.text() + "/" + self.projName + parchePB01 + parcheSantiT02 + "/" + seqName + "/" + sName + "/" + sName  + "_thumbnail.jpg" ))
			dBidexList = [id ,sName ,seqName ,niceName ,area ,task_type,comentarios ,Frames ,artist ,status ]
			tableColumIndlist = [self.idSh_column_idx ,self.shot_column_idx ,self.seq_column_idx ,self.niceShName_column_idx ,self.area_column_idx ,self.taskShType_column_idx ,self.commentSh_column_idx ,self.fpsCant_column_idx ,self.asignSh_column_idx ,self.statusSh_column_idx ]
			for idx, column in enumerate (tableColumIndlist):
				item = QTableWidgetItem(dBidexList[idx])
				#labStatus.setFont(self.newfont)
				if i % 2 == 0:
					item.setBackground(QBrush(QColor(200, 200, 200)))
					#item.setStyleSheet("background-color: rgb(200,200,200); color: rgb(0,0,0);")
				else:
					item.setBackground(QBrush(QColor(180, 180, 190)))
					#item.setStyleSheet("background-color: rgb(180, 180, 190); color: rgb(0,0,0);")
					
				item.setForeground(QBrush(QColor(0, 0, 0)))
				if column == self.statusSh_column_idx:
					labStatus = QLabel(dBidexList[idx])
					labStatus.setGeometry(QtCore.QRect( 0 , 0, 100, 20))
					labStatus.setAlignment(QtCore.Qt.AlignCenter)
					
					if status_list[0] == item.text():
						#item.setBackground(QBrush(QColor(190, 90, 90)))
						labStatus.setStyleSheet("background-color: rgb(190, 90, 90); color: rgb(0,0,0); border-color: gray; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						
					if status_list[1] == item.text():
						#item.setBackground(QBrush(QColor(150, 215, 150)))
						labStatus.setStyleSheet("background-color: rgb(150, 215, 150); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						
					if status_list[2] == item.text():
						#item.setBackground(QBrush(QColor(210, 210, 120)))
						labStatus.setStyleSheet("background-color: rgb(210, 210, 120); color: rgb(0,0,0); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						
					if status_list[3] == item.text():
						#item.setBackground(QBrush(QColor(170, 205, 220)))   #  190, 150, 140
						#item.setForeground(QBrush(QColor(250, 250, 250)))
						labStatus.setStyleSheet("background-color: rgb(170, 205, 220); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
						
					if statusOnlySuperv_list [0] == item.text():
						#item.setBackground(QBrush(QColor(80, 190, 80)))
						#item.setForeground(QBrush(QColor(250, 250, 250)))
						labStatus.setStyleSheet("background-color: rgb(80, 190, 80); color: rgb(250,250,250); border-color: gray ; border-width: 3px; border-radius: 45px; padding: 5px; border-style: solid;")
					self.tablaWidgShots.setCellWidget(i ,column, labStatus)
						
				if column == self.shot_column_idx:
					item.setForeground(QBrush(QColor(180, 110, 45)))
				if column == self.asignSh_column_idx:
					if "Set Artist" != item.text():
						item.setForeground(QBrush(QColor(175, 50, 175)))
				if column == self.taskShType_column_idx:
					item.setFont(self.newfont2)
					try:
						if item.text() == self.settin_list[7][0]:
							item.setForeground(QBrush(QColor(70, 170, 145)))
							item.setFont(self.newfont2)
						elif item.text() == self.settin_list[7][1]:
							item.setForeground(QBrush(QColor(60, 90, 175)))
							item.setFont(self.newfont2)
						elif item.text() == self.settin_list[7][2]:
							item.setForeground(QBrush(QColor(175, 50, 175)))
							item.setFont(self.newfont2)
						elif item.text() == self.settin_list[7][3]:
							item.setForeground(QBrush(QColor(160, 50, 35)))
							item.setFont(self.newfont2)
					except:
						pass
				#if column != self.statusSh_column_idx:
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				self.tablaWidgShots.setItem(i ,column, item)
				if int(self.isLockedSh) == 1 and  self.userName != self.dbShInformFiltered[i][9] :
					self.rowsShLockedList.append(i)
					self.tablaWidgShots.item(i, column).setBackground(QColor(125,125,125))
					self.tablaWidgShots.item(i, column).setForeground(QColor(150,150,150))
				if self.dbShInformFiltered[i][16] == 1:
					self.rowsShBlackListed.append(i)
					self.tablaWidgShots.item(i, column).setBackground(QColor(45,45,43))
					self.tablaWidgShots.item(i, column).setForeground(QColor(125,125,125))

		curreRow = self.tablaWidgShots.currentRow()
		if curreRow == None or curreRow == -1:
			if 0 not in self.rowsShBlackListed:
				self.tablaWidgShots.setCurrentCell(0,11)
		else:
			if curreRow not in self.rowsShBlackListed:
				self.tablaWidgShots.setCurrentCell(curreRow,11)


		
	def load_shot_button(self): 
		self.refresh_shots_table()
		self.key_loadSh = True
		self.tablaWidgShots.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tablaWidgShots.customContextMenuRequested.connect(self.menuShotDespleg)
		self.tablaWidgShots.itemSelectionChanged.connect( lambda: self.changeSeletedShotRowColor ( self.tablaWidgShots, [1,2,3,4,5,6,7,8,9,10], self.rowsShBlackListed, self.rowsShLockedList))
		self.qButtRefreshShotT.setEnabled(True)
		self.qButtRefreshShotT.setStyleSheet("background-color: rgb(128,128,128); color: rgb(200,200,200) ;border-radius: 20px ; border-style: groove")
		
		shadow = QGraphicsDropShadowEffect(self)
		self.shadowButt ( shadow )	
		self.qButtRefreshShotT.setGraphicsEffect(shadow)		
		
		self.qButtLoadShots.setEnabled(False)
		self.qButtLoadShots.setStyleSheet("background-color: rgb(128,128,128); color: rgb(70,70,70) ;border-radius: 20px ; border-style: groove")
		
		shadow = QGraphicsDropShadowEffect(self)
		shadow.setEnabled(False)
		self.qButtLoadShots.setGraphicsEffect(shadow)
		
		
	# al crear la sequencia solo caracteres numericos
	def create_shot_button(self):
		listaTemplates = os.listdir(self.root  + self.projName + "/PIPELINE/TEMPLATES/SCENE/"	)
		if len(listaTemplates) != 0 :	
			winCreaShot = createShotWin()
			winCreaShot.WinCS.show()
			#try:
			if winCreaShot.exec_():
				print " "
			#except Exception:
			#	pass
		else:
			QMessageBox.information(None, u' No Templates', "                             Insert your asset template as \n              -- "+  animTamplate + self.settin_list[5] + " --       on this folder: \n" + self.root + self.projName + "/PIPELINE/TEMPLATES/SCENE/" )			

	def load_user_button(self):   #este metodo dispara  menuAssetDespleg()
		self.key_loadUse = True	
		self.refresh_user_table()
		self.tablaWidgUsers.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.tablaWidgUsers.customContextMenuRequested.connect(self.menuUserDespleg)
		self.tablaWidgUsers.itemSelectionChanged.connect( lambda: self.changeSeletedUserRowColor ( self.tablaWidgUsers, [0,1,2,3,4,5,6,7,8], self.rowsUsBlackListed))
		

	def refresh_user_table (self):
		query ='SELECT * FROM users;'
		self.dbAsInformLoaded = self.selectAllDB ( self.projectDataBase,"assets" )
		conn = sqlite3.connect ( self.projectDataBase )
		c = conn.cursor()
		c.execute(query)
		self.dbUsInform = c.fetchall()   #  en formato de lista de tuplas
		conn.close()
		self.tablaWidgUsers.setRowCount(len(self.dbUsInform ))
		self.tablaWidgUsers.setColumnCount(9)     #  setea la cantidad de columnas!!!!!
		for i, header in enumerate ([ "Black\nList",'\n Name \n','LastName','Password',"Email" , 'Area',"Lider\nSuperv.", 'Slack\nCode',"ID"]):
			locals()["item"+ str(i)] = QTableWidgetItem(header)
			if "Black\nList" == header:
				locals()["item"+ str(i)].setBackground(QColor(190,140,40))
			else:
				locals()["item"+ str(i)].setBackground(QColor(210,170,80))
			self.tablaWidgUsers.setHorizontalHeaderItem( i,locals()["item"+ str(i)] )		
		
		#self.tablaWidgUsers.setHorizontalHeaderLabels()
		#self.tablaWidgUsers.setHorizontalHeaderLabels.setBackground(QColor(0,0,0))
		#################################    columnas     0       1           2        3         4         5                 6              7        8     
		
		################################    DB_column     1       2           3        4         5         6                 7              8        0
		self.idUs_column_idx = 8
		self.usName_column_idx = 1
		self.usLastname_column_idx = 2
		self.usPassword_column_idx = 3
		self.usEmail_column_idx = 4
		self.usArea_column_idx = 5
		self.approver_column_idx = 6
		self.slackCode_column_idx = 7		
		self.blackList_column_idx = 0
		self.rowsUsBlackListed = []
		#self.tablaWidgUsers.setColumnWidth(self.commentAss_column_idx, 80)   #  seteo el ancho en la columna de comentarios
		for i,dbCellData in enumerate(self.dbUsInform ):
			self.tablaWidgUsers.setColumnWidth(self.idUs_column_idx, 35)
			self.tablaWidgUsers.setColumnWidth(self.blackList_column_idx, 45)
			self.tablaWidgUsers.setColumnWidth(self.approver_column_idx, 45)
			self.tablaWidgUsers.setColumnWidth(self.usArea_column_idx, 50)
			self.tablaWidgUsers.setColumnWidth(self.usEmail_column_idx, 130)
			self.tablaWidgUsers.setColumnWidth(self.slackCode_column_idx, 95)
			
			idUs = str(dbCellData[0]) #  es el index en la base de datos
			usName = str(dbCellData[1])
			usLastname = str(dbCellData[2])
			usPassword = str(dbCellData[3])
			usEmail = str(dbCellData[4])
			usArea = str(dbCellData[5])
			approver = str(dbCellData[6])
			slackCode = str(dbCellData[7])
			blackList = str(dbCellData[8])
			dBidexList = [ idUs,usName,usLastname,usPassword,usEmail,usArea,approver,slackCode,blackList ]
			tableColumIndlist = [self.idUs_column_idx, self.usName_column_idx, self.usLastname_column_idx, self.usPassword_column_idx, self.usEmail_column_idx, self.usArea_column_idx, self.approver_column_idx, self.slackCode_column_idx, self.blackList_column_idx]
			for idx, column in enumerate (tableColumIndlist):
				item = QTableWidgetItem(dBidexList[idx])
				
				if i % 2 == 0:
					item.setBackground(QBrush(QColor(210, 210, 195)))
				else:
					item.setBackground(QBrush(QColor(190, 190, 182)))
					
				item.setForeground(QBrush(QColor(0, 0, 0)))	
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				self.tablaWidgUsers.setItem(i ,column, item)
				if self.dbUsInform[i][8] == 1 :
					self.rowsUsBlackListed.append(i)
					self.tablaWidgUsers.item(i, column).setBackground(QColor(45,45,43))
					self.tablaWidgUsers.item(i, column).setForeground(QColor(125,125,125))

		curreRow = self.tablaWidgUsers.currentRow()
		if curreRow == None or curreRow == -1:
			if 0 not in self.rowsUsBlackListed:
				self.tablaWidgUsers.selectRow(0)
		else:
			if curreRow not in self.rowsUsBlackListed:
				self.tablaWidgUsers.selectRow(curreRow)



	def refresComboUs(self):
		tuplaList = self.selectAllDB_lessBlackL (self.projectDataBase,"users" )#  selectAllDB_lessBlackL	
		self.usuarios_list = []
		self.lideres_list = []
		self.productores_list = []
		self.diccUsSlack = {}
		for tupla in tuplaList:
			if tupla[5] == special_area_ls [0]:   #  [5] le corresponde a la columna de area
				self.productores_list.append(tupla[1])
				self.diccUsSlack [tupla[1]] = tupla[7]
			else:
				self.usuarios_list.append(tupla[1])
				self.diccUsSlack [tupla[1]] = tupla[7]
			if tupla[6] == 1:
				self.lideres_list.append(tupla[1])
				
		#self.tablaWidgUsers.clear()
		#self.getTableUser()					
		#self.comboBoxUsers.clear()
		#self.comboBoxUsers.addItems ( [ "     --- User Name ---"] + self.usuarios_list + self.productores_list )	

	def refreshUsertCombTable(self):
		self.refresComboUs()
		self.refresh_user_table()

	def menuUserDespleg(self, position):  # menu flotante que se despliega con clic derecho en las celdas
		if self.userName in self.productores_list or self.userName in self.lideres_list:
			key01 = True
		else:
			key01 = False
		items_list = self.tablaWidgUsers.selectedItems()
		selectedRow=[]
		for i in  items_list:
			selectedRow.append ( i.row())
		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Area':
			if key01:
				self.trueFalse_list = area_listt + special_area_ls
				menuUs02 = QMenu()
				menuUs02.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				for area in self.trueFalse_list:
					areaAction = menuUs02.addAction(area)			
				actionUs02 = menuUs02.exec_(self.tablaWidgUsers.mapToGlobal(position))
				if actionUs02 != None :  # es un objeto
					idtuple = [str(actionUs02.text())]
					query = "UPDATE users SET area=? WHERE id IN ("
					for i, curreRow in enumerate(selectedRow) :
						item = QTableWidgetItem(actionUs02.text())
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgUsers.setItem( curreRow,self.usArea_column_idx, item ) 
						currentID = self.tablaWidgUsers.item( curreRow, self.idUs_column_idx )  # saber el id
						currentID = currentID.text()
						if i < len(selectedRow) -1:
							query = query + " ?, "
						elif i == len(selectedRow) -1:
							query = query + " ? "
						idtuple.append (int (currentID))
					query = query + "); "
					idtuple = tuple( idtuple )
					conn = sqlite3.connect ( self.projectDataBase )
					c = conn.cursor()	
					c.execute( query, idtuple )
					conn.commit()
					conn.close()
					self.refreshUsertCombTable()
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))

		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Black\nList':
			if key01:
				menuBLUs02 = QMenu()
				menuBLUs02.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				areaAction = menuBLUs02.addAction("True")
				areaAction = menuBLUs02.addAction("False")
				actionBlLUs02 = menuBLUs02.exec_(self.tablaWidgUsers.mapToGlobal(position))
				if actionBlLUs02 != None :  # es un objeto
					if actionBlLUs02.text() == "True":
						bltuple = ["1"]
					elif actionBlLUs02.text() == "False":
						bltuple = ["0"]				
					query = "UPDATE users SET blackListed=? WHERE id IN ("
					for i, curreRow in enumerate(selectedRow) :
						if actionBlLUs02.text() == "True":
							item = QTableWidgetItem("1")
						elif actionBlLUs02.text() == "False":
							item = QTableWidgetItem("0")						
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgUsers.setItem( curreRow, self.blackList_column_idx, item )
						currentID = self.tablaWidgUsers.item( curreRow, self.idUs_column_idx )  # saber el id
						currentID = currentID.text()
						if i < len(selectedRow) -1:
							query = query + " ?, "
						elif i == len(selectedRow) -1:
							query = query + " ? "
						bltuple.append (int (currentID))
					query = query + "); "
					bltuple = tuple( bltuple )
					conn = sqlite3.connect ( self.projectDataBase )
					c = conn.cursor()	
					c.execute( query, bltuple )
					conn.commit()
					conn.close()
					self.refreshUsertCombTable()
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))
				


		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == '\n Name \n':
			if key01 == True :
				menuUs00 = QMenu()
				menuUs00.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				nameUsAction = menuUs00.addAction("                                    Done",lambda: self.textDone(self.tablaWidgUsers, "users","first_name", self.textEdNameUs, self.usName_column_idx, self.idUs_column_idx, [], self.rowsUsBlackListed ))
				self.textEdNameUs  = QTextEdit(menuUs00)
				self.textEdNameUs.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdNameUs.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionUs00 = menuUs00.exec_(self.tablaWidgUsers.mapToGlobal(position))
				self.refresComboUs()

			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))

		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'LastName':
			if key01 == True :
				menuUs01 = QMenu()
				menuUs01.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				lastNameUsAction = menuUs01.addAction("                                    Done",lambda: self.textDone(self.tablaWidgUsers, "users","last_name", self.textEdLastNameUs, self.usLastname_column_idx, self.idUs_column_idx, [], self.rowsUsBlackListed ))
				self.textEdLastNameUs  = QTextEdit(menuUs01)
				self.textEdLastNameUs.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdLastNameUs.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionUs01 = menuUs01.exec_(self.tablaWidgUsers.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))

		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Password':
			if key01 == True :
				menuUs02 = QMenu()
				menuUs02.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				passUsAction = menuUs02.addAction("                                    Done",lambda: self.textDone(self.tablaWidgUsers, "users","pass", self.textEdPassUs, self.usPassword_column_idx, self.idUs_column_idx, [], self.rowsUsBlackListed ))
				self.textEdPassUs  = QTextEdit(menuUs02)
				self.textEdPassUs.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdPassUs.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionUs02 = menuUs02.exec_(self.tablaWidgUsers.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))
				
		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Email':
			if key01 == True :
				menuUs03 = QMenu()
				menuUs03.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				emailUsAction = menuUs03.addAction("                                    Done",lambda: self.textDone(self.tablaWidgUsers, "users","email", self.textEdEmailUs, self.usEmail_column_idx, self.idUs_column_idx, [], self.rowsUsBlackListed ))
				self.textEdEmailUs  = QTextEdit(menuUs03)
				self.textEdEmailUs.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdEmailUs.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionUs03 = menuUs03.exec_(self.tablaWidgUsers.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))

		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Slack\nCode':
			if key01 == True :
				menuUs04 = QMenu()
				menuUs04.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				slackUsAction = menuUs04.addAction("                                    Done",lambda: self.textDone(self.tablaWidgUsers, "users","slack_code", self.textEdSlackUs, self.slackCode_column_idx, self.idUs_column_idx, [], self.rowsUsBlackListed ))
				self.textEdSlackUs  = QTextEdit(menuUs04)
				self.textEdSlackUs.setStyleSheet("background-color: rgb(190,190,190) ; color: rgb(0,0,0)")
				self.textEdSlackUs.setGeometry(QtCore.QRect(0, 0, 120, 30))
				actionUs04 = menuUs04.exec_(self.tablaWidgUsers.mapToGlobal(position))
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))

		if self.tablaWidgUsers.horizontalHeaderItem(self.tablaWidgUsers.currentColumn()).text() == 'Lider\nSuperv.':
			if key01:
				menuApprUs02 = QMenu()
				menuApprUs02.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				approveAction = menuApprUs02.addAction("True")
				approveAction = menuApprUs02.addAction("False")
				actionAPPRUs02 = menuApprUs02.exec_(self.tablaWidgUsers.mapToGlobal(position))
				if actionAPPRUs02 != None :  # es un objeto
					if actionAPPRUs02.text() == "True":
						bltuple = ["1"]
					elif actionAPPRUs02.text() == "False":
						bltuple = ["0"]				
					query = "UPDATE users SET approver=? WHERE id IN ("
					for i, curreRow in enumerate(selectedRow) :
						if actionAPPRUs02.text() == "True":
							item = QTableWidgetItem("1")
						elif actionAPPRUs02.text() == "False":
							item = QTableWidgetItem("0")						
						item.setTextAlignment(QtCore.Qt.AlignCenter)
						self.tablaWidgUsers.setItem( curreRow, self.approver_column_idx, item )
						currentID = self.tablaWidgUsers.item( curreRow, self.idUs_column_idx )  # saber el id
						currentID = currentID.text()
						if i < len(selectedRow) -1:
							query = query + " ?, "
						elif i == len(selectedRow) -1:
							query = query + " ? "
						bltuple.append (int (currentID))
					query = query + "); "
					bltuple = tuple( bltuple )
					conn = sqlite3.connect ( self.projectDataBase )
					c = conn.cursor()	
					c.execute( query, bltuple )
					conn.commit()
					conn.close()
					self.refreshUsertCombTable()
			else:
				menuu = QMenu()
				menuu.setStyleSheet("background-color: rgb(200,185,140) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 15px;")
				ac = menuu.addAction(" not available ")
				action = menuu.exec_(self.tablaWidgUsers.mapToGlobal(position))	
		#self.comboBoxUsers.clear()
		#self.comboBoxUsers.addItems ( [ "     --- User Name ---"] + self.usuarios_list + self.productores_list )				

class createAssetWin(QWidget):
	def __init__(self, parent=None):
		if len(str(excutSource).split("maya")) != 2:
			super(createAssetWin, self).__init__(parent)
			self.WinCA = QMainWindow()
			self.WinCA.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 15px;")			
		else:
			super(createAssetWin, self).__init__()
			parent = getWindow()
			self.WinCA = QMainWindow(parent)
			self.WinCA.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 15px;")			
		
		self.WinCA.setWindowIcon(win.iconPrg)
		
		self.WinCA.resize(300, 300)
		self.WinCA.setWindowTitle( " Asset Creation Panel")
		
		self.labassetName = QLabel(self.WinCA)
		self.labassetName.setText("Assets Name")
		self.labassetName.setGeometry(QtCore.QRect(20, 15, 100, 41))
		self.labassetName.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.textEdassetName = QTextEdit(self.WinCA)
		self.textEdassetName.setGeometry(QtCore.QRect(75, 55, 150, 30))
		self.textEdassetName.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px;")
		
		self.labSquen= QLabel(self.WinCA)
		self.labSquen.setText("Asset Type")
		self.labSquen.setGeometry(QtCore.QRect(20, 120, 180, 41))
		self.labSquen.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")		
		
		# combo box para seleccionar la variedad de proyectos
		self.comboBoxAssetType = QComboBox(self.WinCA)
		self.comboBoxAssetType.setGeometry(QtCore.QRect(100, 160, 100, 30)) 
		self.listAssTaskTypes = ["-default-"] + asset_type_list
		self.comboBoxAssetType.addItems(self.listAssTaskTypes)   
		self.comboBoxAssetType.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")

		self.btnDone = QPushButton(self.WinCA)
		self.btnDone.setText('Create Asset')
		self.btnDone.setGeometry(QtCore.QRect(100, 230, 100, 41))
		self.btnDone.clicked.connect(self.createNewAsset)
		self.btnDone.setStyleSheet(" background-color: rgb(210,135,20); color: rgb(200,200,200); border-width: 3px; border-style: groove; border-radius: 15px;")	

	def createNewAsset(self):
		self.assetFoldersList = win.settin_list[6]
		var_contador = 0
		try:
			self.assetName = str (self.textEdassetName.toPlainText())
		except UnicodeEncodeError:
			QMessageBox.warning(None, u' invalid parameter ', " No Special Character are allowed " )
		Boolean = win.AdvertSpecialChars(self.assetName )
		
		listaCaracteres = []
		for char in caracteresProhibidos:
			if len(self.assetName.split(char)) > 1:
				listaCaracteres.append(char)		
		if len (listaCaracteres ) > 0:
			QMessageBox.warning(None, u' invalid parameter ', "Forbidden Characters  :  " + str(listaCaracteres ) )
		else:
			var_contador+= 1

		if not Boolean or len (self.assetName) > 2 or self.assetName != "None" :
			if  len ( self.assetName.split(" ") ) < 2 :
				#self.assetName = self.assetName.upper()
				var_contador+= 1
			else:
				QMessageBox.warning(None, u' no spaces ', " No blank spaces are allowed" )
		else:
			QMessageBox.warning(None, u' invalid parameter ', " No Special Character are allowed " )
		self.assetType = str (self.comboBoxAssetType.currentText()) 
		if self.assetType != "-default-":
			var_contador+= 1
		else:
			QMessageBox.warning(None, u' no parameter ', " Choose Asset Type "  )
		if var_contador == 3:
			self.id_list = win.getAllIDs(win.projectDataBase,"assets")
			self.insertAsset()
			if win.key_loadAss:
				win.refresh_assets_table()
			else:
				win.load_asset_button()	
		self.WinCA.close()
	def insertAsset (self):
		path =  str( win.root + win.projName + assetMayaFol + self.assetType  + "/" + self.assetName + "/")
		id = 1
		if id in self.id_list:
			while id in self.id_list:
				id+= 1
			self.id_list.append (id)
			self.createAssFolderAndInsert(id," ",path)
		else:
			self.createAssFolderAndInsert(id," ",path)
		QMessageBox.information(None, u' Crack! ', "Asset Created !!!!!"  )
		os.startfile(path)


	def createAssFolderAndInsert(self,id,vacio, path):
		key = False
		for folder in self.assetFoldersList:# los seteos de la lista de tareas de assets
			projPath = win.root  + win.projName
			templatePath = projPath + "/PIPELINE/TEMPLATES/ASSET/"
			if self.assetType == char_folder or  self.assetType == props_folder:
				if folder == mod_folder:
					key = True
					tamplaName = modTemplate  + win.settin_list[5]     #  MOD TEMPLATES
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5] 
				elif folder == shad_folder:
					key = True
					tamplaName = emptyTempla  + win.settin_list[5]      #   empty
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5] 				
				elif folder == rig_folder:
					key = True
					tamplaName = rigCharPropTempl  + win.settin_list[5]
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5] 				
			elif self.assetType == sets_folder:  #set
				if folder == rig_folder:
					key = False
				elif folder == mod_folder:
					key = True
					tamplaName = escenarioTempl  + win.settin_list[5]
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5]
				elif folder == shad_folder:
					key = True
					tamplaName = emptyTempla  + win.settin_list[5]
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5]					
			elif self.assetType == module_folder:  #module
				if folder == rig_folder:
					key = False
				elif folder == mod_folder:
					key = True
					tamplaName = moduleTempl  + win.settin_list[5]
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5]
				elif folder == shad_folder:
					key = True
					tamplaName = emptyTempla  + win.settin_list[5]
					assetPath = path + folder + "/" + version_folder + "/"
					assName = self.assetName + "_" + folder + "_v000" + win.settin_list[5]
			print templatePath
			print assetPath					

			
			if key :
				if not os.path.exists( path + folder + "/"):
					for fol in [ version_folder, publish_folder]:
						os.makedirs(path + folder + "/" + fol + "/" )
			shutil.copy2( os.path.join( templatePath, tamplaName ) ,  os.path.join (assetPath , assName))
			#try:

			
			#except Exception:
			#	pass
			if folder == art_folder :
				if not os.path.exists( path + art_folder + "/" + Approved_fol + "/"	):
					os.makedirs( path + art_folder + "/" + Approved_fol + "/"	 )

			if folder == rsh_folder :
				if not os.path.exists( path + rsh_folder ):
					os.makedirs( path + rsh_folder + "/"  )

		conn = sqlite3.connect ( win.projectDataBase )
		c = conn.cursor()
		c.execute("INSERT INTO assets (id, asset_name, asset_type, nice_name, comments, status, task_type, asignado, priority, isPublished, lastPublishDate,isLocked, blackListed ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)" ,(id, self.assetName ,self.assetType, vacio, vacio, status_list[3], self.assetFoldersList[0] , "Set Artist",0,0,vacio,0,0))
		conn.commit()
		conn.close()

class createShotWin(QWidget):
	def __init__(self, parent=None):
		if len(str(excutSource).split("maya")) != 2:
			super(createShotWin, self).__init__(parent)
			self.WinCS = QMainWindow()
			self.WinCS.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 7px;")			
		else:
			super(createShotWin, self).__init__()
			parent = getWindow()
			self.WinCS = QMainWindow(parent)
			self.WinCS.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 7px;")	

		self.WinCS.setWindowIcon(win.iconPrg)		
		self.WinCS.resize(300, 300)
		self.WinCS.setWindowTitle( " Shot Creation Panel")
		
		self.labassetName = QLabel(self.WinCS)

		self.labShotCustomNa = QLabel(self.WinCS)
		#self.labShotCustomNa.setText("Shots amount")
		self.labShotCustomNa.setText("Custom Shot Prefix")
		self.labShotCustomNa.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labShotCustomNa.setGeometry(QtCore.QRect(40, 15, 100, 41))
		
		self.textEdShotCustomNa = QTextEdit(self.WinCS)
		self.textEdShotCustomNa.setGeometry(QtCore.QRect(40, 55, 100, 30))
		self.textEdShotCustomNa.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")
		#self.textEdShotCustomNa.setAlignment(scrollToAnchor (name) )
		self.textEdShotCustomNa.verticalScrollBar().setValue(0)

		self.labShotCant = QLabel(self.WinCS)
		self.labShotCant.setText("Shot Amount")
		self.labShotCant.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labShotCant.setGeometry(QtCore.QRect(192, 15, 100, 41))
		
		self.textEdShotCant = QTextEdit(self.WinCS)
		self.textEdShotCant.setGeometry(QtCore.QRect(200, 55, 50, 30))
		self.textEdShotCant.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0) ; border: 2px ridge gray; border-radius: 3px")
		self.textEdShotCant.verticalScrollBar().setValue(0)

		self.labSquen= QLabel(self.WinCS)
		self.labSquen.setText("Sequence Name Number ( new or existing )")
		self.labSquen.setStyleSheet("background-color: rgb(65,65,65); color: rgb(200,200,200)")
		self.labSquen.setGeometry(QtCore.QRect(20, 120, 240, 41))
		
		self.labPreEditTextShot = QLabel(self.WinCS)
		self.labPreEditTextShot.setText("SQ00")
		self.labPreEditTextShot.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labPreEditTextShot.setGeometry(QtCore.QRect(90, 157, 100, 30))
		
		self.textEdSquen = QTextEdit(self.WinCS)
		self.textEdSquen.setGeometry(QtCore.QRect(125, 160, 50, 30))
		self.textEdSquen.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")
		self.textEdSquen.verticalScrollBar().setValue(0)
	
		self.btnDone = QPushButton(self.WinCS)
		self.btnDone.setText('Create Shot/s')
		self.btnDone.setGeometry(QtCore.QRect(100, 230, 100, 41))
		self.btnDone.clicked.connect(self.createNewShotsSeq)
		self.btnDone.setStyleSheet(" background-color: rgb(210,135,20); color: rgb(200,200,200); border-width: 3px; border-style: groove; border-radius: 15px;")

	def createNewShotsSeq(self):
		var_contador = 0
		tuplaList = win.selectAllDB (win.projectDataBase,"shots" )
		self.shotCant = str (self.textEdShotCant.toPlainText())
		if self.shotCant != "":
			if self.shotCant.isdigit():
				int_shotName = []
				prefixList = []
				self.id_list = []
				digitChar = ""
				for tupla in tuplaList:
					for character in tupla[2]:
						if character.isdigit():
							digitChar = character
							break
					try:
						name = str(tupla[2])
						prefi = name.split(digitChar)[0]
						prefixList.append ( prefi )
					except ValueError:
						prefi = "----"
						prefixList.append ( name)
					int_shotName.append( name.split( prefi )[-1])
					self.id_list.append( tupla[0])
				if int_shotName == []:
					int_shotName = 0
				if int_shotName == 0:
					cont_var = 0
				elif int_shotName[ -1 ].isdigit():
					cont_var = int ( int_shotName [ -1 ] )
				else:
					cont_var = 0
				newShotsDigitsName = []
				for i in range (int (self.shotCant ) ):
					#i+= 1
					cont_var = cont_var + 10
					nameNum = str(cont_var)
					if len(nameNum) ==2:
						nameNum = "00" + nameNum
						newShotsDigitsName.append (nameNum)
					elif len(nameNum) ==3:
						nameNum = "0" + nameNum
						newShotsDigitsName.append (nameNum)
				var_contador+= 1
			else:
				QMessageBox.warning(None, u' invalid parameter ', " Insert Numeric Value on Shot input box"  )
		####################################
		try:
			prefix = str (self.textEdShotCustomNa.toPlainText())
		except UnicodeEncodeError:
			QMessageBox.warning(None, u' invalid parameter ', " No Special Character are allowed " )
		Boolean = win.AdvertSpecialChars(prefix )
		listaCaracteres = []

		if prefix == "":
			var_contador+= 2
		else:
			for char in caracteresProhibidos:
				if len(prefix.split(char)) > 1:
					listaCaracteres.append(char)
			if len (listaCaracteres ) > 0:
				QMessageBox.warning(None, u' invalid parameter ', "Forbidden Characters  :  " + str(listaCaracteres ) )
			else:
				var_contador+= 1
			if not Boolean  or prefix != "None" :
				if  len ( prefix.split(" ") ) < 2 :
					#prefix = self.prefix.upper()
					var_contador+= 1
				else:
					QMessageBox.warning(None, u' no spaces ', " No blank spaces are allowed" )
			else:
				QMessageBox.warning(None, u' invalid parameter ', " No Special Character are allowed " )
		sequ = self.textEdSquen.toPlainText()
		if sequ != "":
			if sequ.isdigit():
				sequ = int( sequ)
				var_contador+= 1
			else:
				QMessageBox.warning(None, u' invalid parameter ', " Insert Numeric Value on Sequence input box"  )
		else:
			QMessageBox.warning(None, u' no parameter ', " Insert Sequence numeric name "  )
		if var_contador > 3:
			shotNameList = []
			for digit in newShotsDigitsName:
				shotName = prefix + digit
				shotNameList.append(shotName)
				self.textEdShotCant.setText("")
				self.textEdShotCustomNa.setText("")
				self.textEdSquen.setText("")
				if len(str(sequ)) == 1:
					self.sequ = "SQ00" + str(sequ)
				elif len(str(sequ)) ==2:
					self.sequ = "SQ0" + str(sequ)
				elif len(str(sequ)) ==3:
					self.sequ = "SQ" + str(sequ)
				self.insertShots(shotName )
			if win.key_loadSh:
				win.refresh_shots_table()
			else:
				win.load_shot_button()
			QMessageBox.information(None, u' Done! ', str(self.sequ) + " - SH: " + str( shotNameList ) + "  Created!!!!" )
			self.WinCS.close()
			os.startfile( win.root  + win.projName + parchePB01  +  parcheSantiT02 + "/" + self.sequ + "/"  )
	def insertShots (self, shotName):
		id = len (self.id_list)
		while id in self.id_list:
			id+= 1
		self.id_list.append (id)
		self.createShFolderAndInsert(id, shotName , self.sequ," ")

	def createShFolderAndInsert(self, i, shotName, sequ, vacio):
		shotFoldersMayaList = win.settin_list[7]  # pEara crear los folders de cada carpeta	
		self.newShotList = []
		for folder in shotFoldersMayaList :
			for verPublFol in [ version_folder, publish_folder, playblaset_fol ] :
				path =  str( win.root  + win.projName + parchePB01  +  parcheSantiT02 + "/" + sequ + "/" + shotName + "/" + folder )

				if verPublFol == publish_folder:
					path = path + "/" + verPublFol + "/" + cache_folder + "/"
				elif verPublFol == version_folder or   verPublFol == playblaset_fol:
					path = path + "/" + verPublFol + "/"

				if not os.path.exists( path ):
					os.makedirs(path)
					self.newShotList.append( shotName )
				projPath = win.root + win.projName
				if folder == anim_fol or  folder == layout_fol or folder == lit_fol:
					if verPublFol ==  version_folder  :
						if folder == anim_fol or  folder == layout_fol:
							templPath = os.path.join( projPath + "/PIPELINE/TEMPLATES/SCENE/" , animTamplate + win.settin_list[5])
						elif folder == lit_fol :
							templPath = os.path.join( projPath + "/PIPELINE/TEMPLATES/SCENE/" , litTempla + win.settin_list[5])
						shutil.copy2( templPath ,  os.path.join ( path ,   shotName + "_" + folder + "_v000" + win.settin_list[5] ))

		shotFoldersNukeList = win.settin_list[8] 
		for folder in shotFoldersNukeList :
			if folder != compo_folder :
				if folder != assetsCompo_folder :
					print folder
					path =  str( win.root + win.projName + parchePB01  +  parcheSantiT02 + "/" + sequ + "/" + shotName + "/" + folder )
					path = path + "/" + verPublFol + "/"
					if not os.path.exists(path):
						os.makedirs(path)
						self.newShotList.append( shotName )
					projPath = win.root + win.projName
			try:	
				shutil.copytree( pipeline_root_path + "/TEMPLATES/nuke/" + compo_folder   ,   win.root  + win.projName + parchePB01  +  parcheSantiT02 + "/" + sequ + "/" + shotName + "/" + compo_folder   , symlinks=True)
			except Exception:
				pass
			try:
				shutil.copytree( pipeline_root_path + "/TEMPLATES/nuke/" + assetsCompo_folder   ,   win.root  + win.projName + parchePB01  +  parcheSantiT02 + "/" + sequ + "/" + shotName  + "/" + assetsCompo_folder     , symlinks=True)
			except Exception:
				pass


		conn = sqlite3.connect ( win.projectDataBase )
		c = conn.cursor()	
		c.execute("INSERT INTO shots (id, shot_name, sequence_name, nice_name, comments, frames_cant, status, area, task_type,asignado,thumbnail, priority, isPublished, lastPublishDate, isLocked, subtasked, blackListed) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)" ,(i,shotName,self.sequ,vacio,vacio,1, status_list[3],area_listt[0],win.settin_list[7][0],"Set Artist",vacio,0,0,vacio,0,0,0))
		conn.commit()
		conn.close()

class addUserWin(QWidget):
	def __init__(self, parent=None):
		super(addUserWin, self).__init__(parent)
		self.setStyleSheet(" background-color: rgb(65,65,65); border-style: groove;")
		self.resize(800, 200)
		self.setWindowIcon(win.iconPrg)
		self.setWindowTitle( " Add User ")

		tEAncho = 30		
		self.labUserNa = QLabel(self)
		self.labUserNa.setText("Name  *")
		self.labUserNa.setGeometry(QtCore.QRect(tEAncho + 42, 15, 110, 41))
		self.labUserNa.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.textEUserName = QTextEdit(self)
		self.textEUserName.setGeometry(QtCore.QRect(tEAncho, 55, 110, 30))
		self.textEUserName.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")

		self.labUserLastN = QLabel(self)
		self.labUserLastN.setText("LastName  *")
		self.labUserLastN.setGeometry(QtCore.QRect(tEAncho + 150, 15, 110, 41))
		self.labUserLastN.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.textEUserLastN = QTextEdit(self)
		self.textEUserLastN.setGeometry(QtCore.QRect(tEAncho + 120, 55, 110, 30))
		self.textEUserLastN.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")
		
		self.labUserPass = QLabel(self)
		self.labUserPass.setText("Password")
		self.labUserPass.setGeometry(QtCore.QRect(tEAncho + 270, 15, 100, 41))
		self.labUserPass.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.textEUserPass = QTextEdit(self)
		self.textEUserPass.setGeometry(QtCore.QRect(tEAncho +  240, 55, 110, 30))
		self.textEUserPass.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")

		self.labUserEmail = QLabel(self)
		self.labUserEmail.setText("Email")
		self.labUserEmail.setGeometry(QtCore.QRect(tEAncho + 430, 15, 200, 41))
		self.labUserEmail.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.textEUserEmail = QTextEdit(self)
		self.textEUserEmail.setGeometry(QtCore.QRect(tEAncho +  360, 55, 160, 30))
		self.textEUserEmail.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")

		self.labUserArea = QLabel(self)
		self.labUserArea.setText("Area  *")
		self.labUserArea.setGeometry(QtCore.QRect(tEAncho + 565, 15, 130, 41))
		self.labUserArea.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
			# combo box de artistas para setear
		self.comboUserArea = QComboBox(self)
		self.comboUserArea.setGeometry(QtCore.QRect(tEAncho +  530, 55, 100, 30))
		self.areaOptionsList = ["Choose Area", area_listt[1],area_listt[0], area_listt[2], special_area_ls [0]] # area_listt = ["3D", "CMP", "UNI"]
		self.comboUserArea.addItems ( self.areaOptionsList )
		self.comboUserArea.setStyleSheet(" background-color: rgb(40,40,40); color: rgb(210,135,20); border-radius: 5px;")  #(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")
		
			#self.comboUserArea.currentIndexChanged.connect(self.selectingUserArea)
		self.labUserAppr = QLabel(self)
		self.labUserAppr.setText(" Is Approver? \n(Suppervisor)  *")
		self.labUserAppr.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20);")
		self.labUserAppr.setGeometry(QtCore.QRect(tEAncho + 650, 15, 130, 41))
		
			# combo box de artistas para setear
		self.comboUserIsApr = QComboBox(self)
		self.comboUserIsApr.setGeometry(QtCore.QRect(tEAncho +  640, 55, 100, 30))
		self.trueFalseList = [ "False", "True"]
		self.comboUserIsApr.addItems ( self.trueFalseList ) 
		self.comboUserIsApr.setStyleSheet(" background-color: rgb(40,40,40); color: rgb(210,135,20); border-radius: 5px;")

		self.labUserAdded = QLabel(self)
		self.labUserAdded.setText( "")
		self.labUserAdded.setStyleSheet("background-color: rgb(65,65,65); color: rgb(10, 170, 160)")
		self.labUserAdded.setGeometry(QtCore.QRect(320, 122, 350, 41))
		self.labUserAdded.setFont(win.newfont)
		

		self.btnAddUserDone = QPushButton(self)
		self.btnAddUserDone.setText('Add User to DataBase')
		self.btnAddUserDone.setGeometry(QtCore.QRect(100, 120, 200, 41))
		self.btnAddUserDone.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-width: 3px; border-radius: 15px; border-style: groove;" )
		self.btnAddUserDone.clicked.connect(self.add_user_done)
		

	def add_user_done (self):
		uIsApprov = 0
		uName = self.textEUserName.toPlainText()
		win.comboBoxUsers.addItems ( [uName] )
		uLastNa = self.textEUserLastN.toPlainText()
		uPass = self.textEUserPass.toPlainText()
		uEmail = self.textEUserEmail.toPlainText()
		uArea = self.areaOptionsList [self.comboUserArea.currentIndex()]
		ilegalCharsList = []
		for names in [uName,uLastNa]:
			for char in caracteresProhibidos + [" "]:
				if len(uName.split(char)) > 1:
					ilegalCharsList.append (char)
		if len (ilegalCharsList ) > 0:
			QMessageBox.warning(None, u' invalid parameter ', "Forbidden Characters  :  " + str(ilegalCharsList ) )
		else:
			if self.trueFalseList [self.comboUserIsApr.currentIndex()] == "True":
				uIsApprov = 1
			else:
				uIsApprov = 0

			if uName == ""  or uLastNa == "" or uArea == "Choose Area" :
				print "Uncomplete fields"
			else:
				checkID_list = win.selectAllDB (win.projectDataBase,"users" )
				id_list = []
				for id in checkID_list:
					id_list.append (id[0])
				i = len(id_list)
				conn = sqlite3.connect ( win.projectDataBase )
				c = conn.cursor()
				if i in id_list:
					while i in id_list:
						i+= 1
					id_list.append (i)
					c.execute("INSERT INTO users ( id ,first_name , last_name, pass, email, area, approver, slack_code, blackListed ) VALUES (?,?,?,?,?,?,?,?,?)" ,(i, uName, uLastNa, uPass, uEmail, uArea, uIsApprov,"-",0 ))
				else:
					id_list.append (i)
					c.execute("INSERT INTO users ( id ,first_name , last_name, pass, email, area, approver ,slack_code, blackListed) VALUES (?,?,?,?,?,?,?,?,?)" ,(i, uName, uLastNa, uPass, uEmail, uArea, uIsApprov, "-",0 ))
				conn.commit()
				conn.close()
				if uArea == special_area_ls[0]:
					win.productores_list.append(uName)
				else:
					win.usuarios_list.append(uName)
				
			if uIsApprov == 1:
				win.lideres_list.append(uName)
			self.labUserAdded.setText( uName + " "+ uLastNa + " added to DataBase Project"  )
			self.labUserAdded.setFont(win.newfont2)
			self.close()

class creaSettingWin(QWidget):
	def __init__(self, parent=None):
		super(creaSettingWin, self).__init__(parent)
		self.setWindowIcon(win.iconPrg)
		self.setStyleSheet(" background-color: rgb(65,65,65)")
		self.resize(685, 505)
		self.setWindowTitle( " Projects Settings ")

		self.labFrameRate = QLabel(self)
		self.labFrameRate.setText(" Frame Rate")
		self.labFrameRate.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labFrameRate.setGeometry(QtCore.QRect(30 , 25, 100, 30))
		
		self.comboFrameRate = QComboBox(self)
		self.comboFrameRate.setGeometry(QtCore.QRect( 30, 55, 100, 30))
		self.comboFrameRate.addItems ( frameRateList ) 
		self.comboFrameRate.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	

		self.labProjResolut = QLabel(self)
		self.labProjResolut.setText(" Project Resolution ")
		self.labProjResolut.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labProjResolut.setGeometry(QtCore.QRect(160 , 25, 100, 30))

		self.comboProjResolut = QComboBox(self)
		self.comboProjResolut.setGeometry(QtCore.QRect( 160, 55, 100, 30))
		self.comboProjResolut.addItems ( projResolutList ) 
		self.comboProjResolut.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	


		self.labPreviewResolu = QLabel(self)
		self.labPreviewResolu.setText(" Preview Resolution ")
		self.labPreviewResolu.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labPreviewResolu.setGeometry(QtCore.QRect(290 , 25, 100, 30))
		
		self.combPreviewResolu = QComboBox(self)
		self.combPreviewResolu.setGeometry(QtCore.QRect( 290, 55, 100, 30))
		self.combPreviewResolu.addItems ( projResolutList ) 
		self.combPreviewResolu.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	
		
		self.labPreviewFormat = QLabel(self)
		self.labPreviewFormat.setText(" Preview Format ")
		self.labPreviewFormat.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labPreviewFormat.setGeometry(QtCore.QRect(420 , 25, 100, 30))
		
		self.combPreviewFormat = QComboBox(self)
		self.combPreviewFormat.setGeometry(QtCore.QRect( 420, 55, 100, 30))
		self.combPreviewFormat.addItems ( previewFormatList ) 
		self.combPreviewFormat.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	

		self.labColorManag = QLabel(self)
		self.labColorManag.setText(" Color Management ")
		self.labColorManag.setGeometry(QtCore.QRect(550 , 25, 100, 30))
		self.labColorManag.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		
		self.comboColorManag = QComboBox(self)
		self.comboColorManag.setGeometry(QtCore.QRect( 550, 55, 100, 30))
		self.comboColorManag.addItems ( colorManagList ) 
		self.comboColorManag.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	
		
		self.labMayaExtens = QLabel(self)
		self.labMayaExtens.setText(" Maya Extension ")
		self.labMayaExtens.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labMayaExtens.setGeometry(QtCore.QRect(30 , 95, 100, 30))
		
		self.comboMayaExtens = QComboBox(self)
		self.comboMayaExtens.setGeometry(QtCore.QRect( 30, 125, 100, 30))
		self.mayaExtensList = mayaExtenList
		self.comboMayaExtens.addItems ( self.mayaExtensList ) 
		self.comboMayaExtens.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	

		self.labMayaAsTasks = QLabel(self)
		self.labMayaAsTasks.setText(" Maya Assets Tasks ")
		self.labMayaAsTasks.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labMayaAsTasks.setGeometry(QtCore.QRect(160 , 95, 100, 30))
		
		self.comboMayaAsTasks = QComboBox(self)
		self.comboMayaAsTasks.setGeometry(QtCore.QRect( 160, 125, 100, 30))
		self.comboMayaAsTasks.addItems ( mayaAsTasksList ) 
		self.comboMayaAsTasks.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	

		self.lsWidMayaAsTasks = QListWidget(self)
		self.lsWidMayaAsTasks.setGeometry(QtCore.QRect( 160, 170, 100, 120))
		self.lsWidMayaAsTasks.setTextElideMode(QtCore.Qt.ElideMiddle)	
		self.lsWidMayaAsTasks.setStyleSheet("background-color: rgb(45,45,45) ; color: rgb(210,135,20)")		
		
		self.comboMayaAsTasks.currentIndexChanged.connect( lambda: self.getSelectedOption ( self.comboMayaAsTasks, mayaAsTasksList, self.lsWidMayaAsTasks))

		self.labMayaShTasks = QLabel(self)
		self.labMayaShTasks.setText(" Maya Shots Tasks  ")
		self.labMayaShTasks.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labMayaShTasks.setGeometry(QtCore.QRect(290 , 95, 100, 30))
		
		self.comboMayaShTasks = QComboBox(self)
		self.comboMayaShTasks.setGeometry(QtCore.QRect( 290, 125, 100, 30))
		self.comboMayaShTasks.addItems ( mayaShTasksList ) 
		self.comboMayaShTasks.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	


		self.lsWidMayaShTasks = QListWidget(self)
		self.lsWidMayaShTasks.setGeometry(QtCore.QRect( 290, 170, 100, 120))
		self.lsWidMayaShTasks.setTextElideMode(QtCore.Qt.ElideMiddle)
		self.lsWidMayaShTasks.setStyleSheet("background-color: rgb(45,45,45) ; color: rgb(210,135,20)")	

		self.comboMayaShTasks.currentIndexChanged.connect( lambda: self.getSelectedOption ( self.comboMayaShTasks, mayaShTasksList, self.lsWidMayaShTasks))

		self.labNukeShTasks = QLabel(self)
		self.labNukeShTasks.setText(" Nuke Type Tasks  ")
		self.labNukeShTasks.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labNukeShTasks.setGeometry(QtCore.QRect(420 , 95, 100, 30))
		
		self.comboNukeShTasks = QComboBox(self)
		self.comboNukeShTasks.setGeometry(QtCore.QRect( 420, 125, 100, 30))
		self.comboNukeShTasks.addItems ( nukeShTasksList ) 
		self.comboNukeShTasks.setStyleSheet(" background-color: rgb(40,40,40) ; color: rgb(210,135,20)")	

		self.lsWidNukeShTasks = QListWidget(self)
		self.lsWidNukeShTasks.setGeometry(QtCore.QRect( 420, 170, 100, 120))
		self.lsWidNukeShTasks.setTextElideMode(QtCore.Qt.ElideMiddle)
		self.lsWidNukeShTasks.setStyleSheet("background-color: rgb(45,45,45); color: rgb(210,135,20)")	

		self.comboNukeShTasks.currentIndexChanged.connect( lambda: self.getSelectedOption ( self.comboNukeShTasks, nukeShTasksList, self.lsWidNukeShTasks))

		self.labSlackCode = QLabel(self)
		self.labSlackCode.setText(" Slack Project code  ")
		self.labSlackCode.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labSlackCode.setGeometry(QtCore.QRect( 20, 320, 250, 20))

		self.labSlackIco = QLabel(self)
		self.labSlackIco.setGeometry(QtCore.QRect( 23, 347, 25, 25))

		icon = QPixmap(win.root + win.projName  + '/PIPELINE/slackLogo.png')
		self.labSlackIco.setPixmap (icon)


		self.labSlackHelp = QLabel(self)
		self.labSlackHelp.setText("     Go to   https://'your-project-name'.slack.com/apps/manage ")
		self.labSlackHelp.setStyleSheet("background-color: rgb(65,65,65); color: rgb(100,100,100)")
		self.labSlackHelp.setGeometry(QtCore.QRect( 135, 295, 315, 20))

		self.labSlackHelp2 = QLabel(self)
		self.labSlackHelp2.setText(" and   Look for   'Bots'   on the\n      top main 'searching Bar' \n    ...follow the steps...    then \n     Insert Slack Project Code")
		self.labSlackHelp2.setStyleSheet("background-color: rgb(65,65,65); color: rgb(100,100,100)")
		self.labSlackHelp2.setGeometry(QtCore.QRect( 498, 290, 250, 85))

		self.textEdSlackProjCode = QTextEdit(self)
		self.textEdSlackProjCode.setGeometry(QtCore.QRect( 121, 315, 352, 30))
		self.textEdSlackProjCode.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")

		self.labSlackChannel = QLabel(self)
		self.labSlackChannel.setText(" Slack Coord channel ")
		self.labSlackChannel.setStyleSheet("background-color: rgb(65,65,65); color: rgb(210,135,20)")
		self.labSlackChannel.setGeometry(QtCore.QRect( 20, 377, 250, 20))

		self.textEdSlackChannel = QTextEdit(self)
		self.textEdSlackChannel.setGeometry(QtCore.QRect( 140, 372, 120, 30))
		self.textEdSlackChannel.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0) ; border: 2px ridge gray; border-radius: 3px")

		self.btnSaveProjSettings = QPushButton(self)
		self.btnSaveProjSettings.setText('Save Settings')
		self.btnSaveProjSettings.setGeometry(QtCore.QRect(245, 430, 200, 41))
		self.btnSaveProjSettings.setStyleSheet(" background-color: rgb(210,135,20) ; color: rgb(200,200,200); border-width: 3px; border-radius: 15px ; border-style: groove")
		self.btnSaveProjSettings.clicked.connect(self.qButtsaveSetting)


	def getSelectedOption(self, combo_box, options_list, list_widg):
		selectedBeforeList =  [str(list_widg.item(i).text()) for i in range(list_widg.count())]
		_index = combo_box.currentIndex()
		if str( options_list[_index]) != "-default-" and str( options_list[_index]) not in selectedBeforeList:
			 list_widg.addItem(str( options_list[_index]))

	def qButtsaveSetting (self):
		self.fps = str( self.comboFrameRate.currentText() )
		self.resolu = str( self.comboProjResolut.currentText() )
		self.prev_resolu = str(self.combPreviewResolu.currentText() )
		self.prev_formatss = str(self.combPreviewFormat.currentText() )
		self.color_manag = str(self.comboColorManag.currentText() )
		self.maya_exen = str(self.comboMayaExtens.currentText() )
		
		self.listAssetsTask = [str(self.lsWidMayaAsTasks.item(i).text()) for i in range(self.lsWidMayaAsTasks.count())]
		self.listMayaShTask = [str(self.lsWidMayaShTasks.item(i).text()) for i in range(self.lsWidMayaShTasks.count())]
		self.listNukeShTask = [str(self.lsWidNukeShTasks.item(i).text()) for i in range(self.lsWidNukeShTasks.count())]
		
		if str(self.textEdSlackProjCode.toPlainText()) != "" :
			self.slackCode = str(self.textEdSlackProjCode.toPlainText())
		else:
			self.slackCode = '""'

		if str(self.textEdSlackChannel.toPlainText()) != "" :
			self.slackChannel = str(self.textEdSlackChannel.toPlainText())
		else:
			self.slackChannel = '""'

		if str(win.labRootRenderPath.setText) != "drive:/someFolders/Renders":
			self.renderRootPath = str(win.labRootRenderPath.setText)
		else:
			self.renderRootPath = '"drive:/someFolders/Renders"'
		win.pButtonCreateProjSettings.setText("Project Settings Done")
		win.pButtonCreateProjSettings.setStyleSheet("background-color: rgb(210,135,20);color: rgb(0,120,0) ; border-style: groove")

		self.close()

class sqlTableData():
	def createShotsTable(self, newDBpath):
		conn = sqlite3.connect (newDBpath )
		c = conn.cursor()
		c.execute("""CREATE TABLE shots (
			id INTEGER,  
			thumbnail text,
			shot_name text,
			sequence_name text,
			area text,
			task_type text,
			comments text,
			frames_cant text,
			status text,
			asignado text,
			priority INTEGER,
			isPublished INTEGER,
			lastPublishDate INTEGER,
			nice_name text,
			isLocked INTEGER,
			subtasked INTEGER,
			blackListed INTEGER
			)""" )
		conn.commit()
		conn.close()


	def createAssetTable(self, newDBpath):
		conn = sqlite3.connect (newDBpath)
		c = conn.cursor()
		c.execute("""CREATE TABLE assets (
			id INTEGER,  
			thumbnail text,
			asset_type text,
			asset_name text,
			nice_name text,
			task_type text,
			comments text,
			status text,
			asignado text,
			priority INTEGER,
			isPublished INTEGER,
			lastPublishDate INTEGER,
			isLocked INTEGER,
			blackListed INTEGER
			)""" )
		conn.commit()
		conn.close()



	def createUsersTable (self, newDBpath):
		conn = sqlite3.connect (newDBpath )
		c = conn.cursor()
		c.execute("""CREATE TABLE users (
			id INTEGER,
			first_name text,
			last_name text,
			pass text,
			email text,
			area text,
			approver INTEGER,
			slack_code text,
			blackListed INTEGER
			)""" )
		conn.commit()
		conn.close()

class masterPassWin(QWidget):
	def __init__(self, parent=None):
		if len(str(excutSource).split("maya")) != 2:
			super(masterPassWin, self).__init__(parent)
			self.WinMP = QMainWindow()
			self.WinMP.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 15px;")		
		else:
			super(masterPassWin, self).__init__()
			parent = getWindow()
			self.WinMP = QMainWindow(parent)
			self.WinMP.setStyleSheet(" background-color: rgb(65,65,65); border-radius: 15px;")	
		self.WinMP.setWindowIcon(win.iconPrg)
		self.WinMP.resize(440, 155)
		self.WinMP.setWindowTitle(" Set Master Password ")

		self.labNotice = QLabel(self.WinMP)
		self.labNotice.setText("Remember,  the first User you will create on this Project \n   must be Coordinator or Supervisor")
		self.labNotice.setStyleSheet("background-color: rgb(65,65,65); color: rgb(200,200,200)")
		self.labNotice.setGeometry(QtCore.QRect(113, 20, 400, 50))
		
		self.labUserNa = QLabel(self.WinMP)
		self.labUserNa.setText("Please, Set Master Pass")
		self.labUserNa.setStyleSheet("background-color: rgb(65,65,65); color: rgb(200,200,200)")
		self.labUserNa.setGeometry(QtCore.QRect(30, 80, 130, 41))
		
		self.textEdPass = QTextEdit(self.WinMP)
		self.textEdPass.setGeometry(QtCore.QRect(170, 90, 110, 30))
		self.textEdPass.setStyleSheet(" background-color: rgb(195,195,195) ; color: rgb(0,0,0); border: 2px ridge gray; border-radius: 3px")

		self.btnSetMasterPass = QPushButton(self.WinMP)
		self.btnSetMasterPass.setText(' Done ')
		self.btnSetMasterPass.setStyleSheet(" background-color: rgb(210,135,20) ; color: rgb(200,200,200); border-width: 3px; border-style: groove; border-radius: 15px")
		self.btnSetMasterPass.setGeometry(QtCore.QRect(310, 85, 100, 41))

class doVersionClass():
	def removeRogueModelPanelChangeEvents(self):
		try:
			EVIL_METHOD_NAMES = ['DCF_updateViewportList', 'CgAbBlastPanelOptChangeCallback']
			capitalEvilMethodNames = [name.upper() for name in EVIL_METHOD_NAMES]
			modelPanelLabel = mel.eval('localizedPanelLabel("ModelPanel")')
			processedPanelNames = []
			panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
			while panelName and panelName not in processedPanelNames:
				editorChangedValue = mc.modelEditor(panelName, query=True, editorChanged=True)
				parts = editorChangedValue.split(';')
				newParts = []
				changed = False
				for part in parts:
					for evilMethodName in capitalEvilMethodNames:
						if evilMethodName in part.upper():
							changed = True
							break
					else:
						newParts.append(part)
				if changed:
					mc.modelEditor(panelName, edit=True, editorChanged=';'.join(newParts))
				processedPanelNames.append(panelName)
				panelName = mc.sceneUIReplacement(getNextPanel=('modelPanel', modelPanelLabel))
		except Exception:
			pass

	def versionarFunc(self, path , name, exten):
		if path.endswith( "/" + version_folder + "/" ) and len (name.split("_v")) == 2 :
			numVersion = int(name.split("_v")[-1].split(exten)[0])
			numVersion+= 1
			if  len(str(numVersion)) == 1:
				self.numVersion =  "00" + str(numVersion)
			elif len(str(numVersion)) == 2:
				self.numVersion =  "0" + str(numVersion)
			elif len(str(numVersion)) == 3:
				self.numVersion = str(numVersion)
			name = name.split("_v")[0]
			#newName = name.upper() + "_v" + self.numVersion + exten    # upper
			newName = name + "_v" + self.numVersion + exten
			mc.file( rename = path + newName   )
			if exten == ".ma":
				mc.file( type='mayaAscii',s = True , force = True )
			elif exten == ".mb":
				mc.file( type='mayaBinary',s = True , force = True )
		else:
			QMessageBox.information(None, u' file issue ', "File Nomenclature or Placement Failiture")
	def execution(self, extension, curentPath, name):
		if len(name.split(extension)) < 2:
			QMessageBox.warning(None, u' extension issue ', " current scene extension is not the proper project extension")
		else:
			self.removeRogueModelPanelChangeEvents()
			self.versionarFunc(curentPath, name ,extension)
			return "_v" + self.numVersion

class publishShotClass():
# que no haya nada no referenciado en el grupo
# que los namespaces coincidan con el nombre del file
# hay que borrar las render layers
# listar constrains que esten llamando a fuentes fuera de anim group 
################### publicacion de assets ###########################
#####################################################################
	def __init__(self):
		#pregunta nombre y ruta de la current escena
		self.filepath_maya = mc.file(q=True, sn=True)
		# alerta que esten dentro de la estructura del template pertinente

	def AdvertTemplStructure(self):
		self.exportFolders = []
		for fol in win.ANIM_TEMPLATE:
			if fol !=  refeGrp :
				self.exportFolders.append (fol)
		list1 = []
		for fol in win.ANIM_TEMPLATE:
			#list1.append (fol)
			list1.append ( "*:*:*" + fol)
			list1.append ( "*:*:" + fol)
		list2 = []
		for fol in win.ANIM_TEMPLATE:
			list2.append ("*" + fol)
		nsOnRootGroup = mc.ls(list1)
		obj_template_list = mc.ls(list2, l = True )
		if obj_template_list == [] or len( nsOnRootGroup ) != 0 :
			QMessageBox.information(None, u' issue '," Doesn t found Asset Template Structure \n " + str (self.exportFolders) )
			return  True
		else:
			return False
	#  alertar de namespaces en la escena
	def AdvertDobleNameSpa (self):
		listaNSpace = mc.ls("*:*:*", "*:*:*:*")
		if listaNSpace !=[]:
			QMessageBox.information(None, u' 2 nm '," double Name detected")
			return True
		else:
			return False
	# detectar nombres repetidos
	def dupliNameDetectionFunc(self):
		duplicates = [f for f in mc.ls() if '|' in f]
		duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)
		if duplicates:
			for name in duplicates:
				m = re.compile("[^|]*$").search(name) 
				shortname = m.group(0)
				m2 = re.compile(".*[^0-9]").match(shortname) 
				if m2:
					stripSuffix = m2.group(0)
				else:
					stripSuffix = shortname
			QMessageBox.information(None, u' issue '," Duplicate Names: " + str (duplicates))
			return  True
		else:
			return False
	#  detectar nombres tipo locator o cosas sin namespace
	def AdvertDefaultNameObj (self):
		jointDefult = mc.ls ("joint*" )
		default_names = mc.ls ("nurbsSquare*", "locator*", "nurbsCircle*", "pCube*", "pCylinder*", "pSphere*", "nurbsSphere*" , "group*", "null*", type = "transform")
		for obj in default_names + jointDefult:
			if len ( obj.split("|")) > 1:
				obj = obj.split("|")[-1]
			if len (mc.ls (obj)) >1:
				QMessageBox.information(None, u' issue ',"duplicate names:" + obj)
				return  True
			else:
				try:
					rootObj = mc.listRelatives(obj,ap=True, f = True)[0]
					for fol in self.exportFolders:
						if rootObj.startswith( fol):
							QMessageBox.information(None, u' issue ',"Rename Default Object/s Name/s Objects:  " + obj )
							return  True
					else:
						return False
				except Exception:
					pass
	# dectectar caracteres especiales
	def AdvertSpecialChars(self):
		exportable_objs = []
		for folder in self.exportFolders:
			try:
				objsList = mc.listRelatives (folder , ad = True, s = False)
			except Exception:
				pass
			if  objsList == None:
				objsList = []
			for obj in objsList:
				exportable_objs.append(obj)
		if type(self.filepath_maya) == "string":
			all_list = exportable_objs + self.filepath_maya
		else:
			all_list = exportable_objs
		obj_con_ec = []
		for obj in all_list:
			if set(obj).difference(printable):
				obj_con_ec.append (obj)
		if obj_con_ec != []:
			QMessageBox.information(None, u' issue '," Specials Characters found: " + str(obj_con_ec))
			return  True
		else:
			return False

	def AdvertWrongExteralPath (self):
		externalFilesList =[]
		filesNodes = mc.ls(type='file')
		cache_node_list = []
		try:
			cache_node_list = mc.ls(type='ExocortexAlembicFile')
		except Exception:
			pass
		rootReference = mc.file(r = True, q = True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True )
			if subReferences != None:
				todasLasReferencias = todasLasReferencias + subReferences
		for f in filesNodes:
			t = mc.getAttr(f + '.fileTextureName')
			if os.path.isfile(t):
				externalFilesList.append(t)
		for ref in todasLasReferencias:
			ruta = mc.referenceQuery ( ref, filename = True )
			if os.path.isfile( ruta) :
				externalFilesList.append( ruta)
		for cache_node in cache_node_list:
			ruta_Ca = mc.getAttr(cache_node + '.fileName')
			externalFilesList.append(ruta_Ca)
		advertenceList = []
		for file in externalFilesList:
			win.root = win.root.replace("\\","/")
			if not file.startswith (win.root):
				advertenceList.append (file)
		if len(advertenceList) > 0 :
			QMessageBox.information(None, u' issue ', "Path/s Out of pipeline Root  \n " + str(advertenceList))
			return True
		else:
			return False

	def AdvertIfNotRef(self):
		listForReferenceCheck = []
		for folder in self.exportFolders:
			try:
				list = mc.listRelatives(folder,ad = True ,type = "transform", f =True)
			except Exception:
				pass
			if list == None:
				list = []
			for o in list:
				listForReferenceCheck.append(o)
		notReferenceObj_List = []
		for node in listForReferenceCheck:
			respuesta = mc.referenceQuery ( node, isNodeReferenced = True)
			if respuesta == False:
				notReferenceObj_List.append(node)
		if notReferenceObj_List != []:
			QMessageBox.information(None, u' issue ', " Object/s is not Reference: \n" + str (notReferenceObj_List) )
			return True
		else:
			return False



	def AdvertNaSpaNotMatchRefPath(self):
		rootReference = mc.file(r = True, q = True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True ) #
			if subReferences != None:
				if mc.referenceQuery (subReferences, il = True):
					todasLasReferencias = todasLasReferencias + subReferences
		nameSpaNotMatchinList = []
		for refNode in todasLasReferencias:
			nameSpa = mc.referenceQuery  (refNode , ns = True )
			if  len(refNode.split(":")) > 1:
				refNode = refNode.split(":")[-1]
			if refNode.split("RN")[0] !=  nameSpa.split(":")[-1] :
				nameSpaNotMatchinList.append (nameSpa.split(":")[-1])
			if nameSpaNotMatchinList != []:
				QMessageBox.information(None, u' issue ', "Reference Node Doesn t match with NameSpace\n" + str (nameSpaNotMatchinList) )
				return True
			else:
				return False


				
	def AdvertObjConstrOut (self):
		pConstraintNodes = mc.ls (type = "parentConstraint")
		for constr in pConstraintNodes:
			objs = mc.parentConstraint( constr, targetList = True ,q =True)
			#source = mc.parentConstraint( constr, weightAliasList = True ,q =True)
			for o in objs:
				try:
					for folder in self.exportFolders:
						try:
							root = mc.listRelatives(o, ap = True, f =True)[0]
						except Exception:
							pass
						if root != None:
							if root.startswith( "|" + folder) or root.startswith( folder):
								conections = mc.listConnections(constr)
								set_List_Conections = set(conections)
								for conect in set_List_Conections:
									if conect != o and conect != constr:
										try:
											sourceRoot = mc.listRelatives(conect, ap = True, f =True)[0]
										except Exception:
											pass
										if sourceRoot != None:
											if not sourceRoot.startswith( folder):
												QMessageBox.information(None, u' issue ', " insert object in to -" + folder + "- structure, with proper name \n  " + conect )
												return True
											else:
												return False
				except Exception:
					pass

					#################  y ahora voy a crear el publish   ####################
					########################################################

	def exportSelectionFunc(self, path, name, exten):
		full_path = os.path.join( path, name + exten)
		if exten == ".ma":
			tipo = 'mayaAscii'
		elif exten == ".mb":
			tipo = 'mayaBinary'
		if os.path.isfile(full_path):
			os.remove(full_path)
		mc.select (self.exportFolders)
		mc.file ( full_path, type=tipo , es = True  )
		win.scripJCounter1= win.scripJCounter1 + 1
		mc.file ( full_path ,o = True , force = True)
	# un vez abierto el publish
	#################### esto lo debe hacer en el fbx que export#######################
	##################################################################################
	# elimnar namespace del template
	def r_namespaces(self, node):   #  es parte de la siguiente funcion
		try:
			namespace, name = node.rsplit(":", 1)
		except:
			namespace, name = None, node
		if namespace:
			try:
				mc.rename(node, name)
			except RuntimeError:
				pass
	def removeNamesSpacesfromTemplate(self):
		transformRoot = self.exportFolders
		for node in transformRoot:
			try:
				nodeList = mc.listRelatives(node, allDescendents=True, typ="transform")
			except Exception:
				pass
			if nodeList != None:
				for descendent in nodeList:
					self.r_namespaces(descendent)
				self.r_namespaces(node)
 
	# eliminar namespace vacios
	def removeEmptyNameSpac (self):
		listaNSpace = mc.namespaceInfo( lon = True)
		listaNSpace.remove ('UI')
		listaNSpace.remove ('shared')
		for ns in listaNSpace:
			objNameSpList = mc.ls( ns + ":*" )
			if len (objNameSpList) == 0:
				mc.namespace (rm = ns) 



	# delete unknow nodes
	def deleteUnknowNodes(self):
		nodeList = mc.ls(type="unknown")
		for n in nodeList:
			try:
				mc.delete( n )
			except Exception:
				pass


	# borrar los display layers, esto depende de la etapa del asset
	def deleteDispLay(self):
		pathSplited = self.filepath_maya.split("/")
		etapaAsset = pathSplited[-3]
		if etapaAsset != rig_folder:
			layerList = mc.ls(type="displayLayer")
			for layer in layerList:
				try:
					if layer != "defaultLayer":
						mc.delete(layer)
				except Exception:
					pass


	def execution(self, path, name , exten):
		while True:
			if self.AdvertTemplStructure() == True: 
				break
			if self.dupliNameDetectionFunc() == True:     # este deberia ir pero seguramente ya es tarde
				break
			if self.AdvertDefaultNameObj() == True:
				break
			if self.AdvertSpecialChars() == True:
				break
			if self.AdvertWrongExteralPath() == True:
				break
			if self.AdvertNaSpaNotMatchRefPath() == True:
				break
			#if self.AdvertIfNotRef() == True:      #  este no va a ir a papper
			#	break
			
			self.deleteUnknowNodes()
			self.exportSelectionFunc(path, name , exten)
			#self.removeNamesSpacesfromTemplate()
			self.removeEmptyNameSpac ()
			self.deleteDispLay()
			mc.file ( s = True)
			return True

class publishAssetClass():
	################### publicacion de assets ######################
	def __init__(self):
		#pregunta nombre y ruta de la current escena
		self.filepath_maya = mc.file(q=True, sn=True)
		# alerta que esten dentro de la estructura del template pertinente
	
	def startVars(self):
		#templateTypeList = ["All_Grp", "SET","Render_Grp"]
		assetType = str(win.labSceneAssetName.text()).split("   ")[0]
		taskType = str(win.labSceneAssetName.text()).split("   ")[2]
		if assetType == char_folder or assetType == props_folder:  #  char  prop
			if taskType == mod_folder: #mod
				self.tempMainFolder = [ win.MOD_TEMPLATE[1] ]
			elif taskType == shad_folder: #shd
				self.tempMainFolder = [ win.MOD_TEMPLATE[1] ]  # # # # # # win.EMPTY_TEMPLATE
			elif taskType == rig_folder: #rig
				self.tempMainFolder = [win.RIGGEDASS_TEMPLATE[0] ]
		elif assetType == sets_folder or assetType == module_folder:  #  module  or scene
			self.tempMainFolder = []
			for fol in win.MODULE_TEMPLATE:
				if fol != refeGrp:
					self.tempMainFolder.append (fol)

	def AdvertDobleNameSpa (self):
		listaNSpace = mc.ls("*:*:*", "*:*:*:*")
		if listaNSpace !=[]:
			QMessageBox.information(None, u' 2 nm '," double Name detected")
			return True
		else:
			return False
	# detectar nombres repetidos
	def dupliNameDetectionFunc(self):
		duplicates = [f for f in mc.ls() if '|' in f]
		duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)
		if duplicates:
			for name in duplicates:
				m = re.compile("[^|]*$").search(name) 
				shortname = m.group(0)
				m2 = re.compile(".*[^0-9]").match(shortname) 
				if m2:
					stripSuffix = m2.group(0)
				else:
					stripSuffix = shortname
			QMessageBox.information(None, u' issue '," Duplicate Names: " + str (duplicates))
			return  True
		else:
			return False
	#  detectar nombres tipo locator o cosas sin namespace
	def AdvertDefaultNameObj (self):
		name_spaList = ["*:", "*:*:", "*:*:*:"]
		default = ["locator*", "nurbsCircle*", "pCube*", "pCylinder*", "pSphere*", "nurbsSphere*" , "group*", "null*"]
		new = []
		for defa in default:
			for ns in name_spaList:
				new.append( ns + defa)
		new = new + default	
		default_names = []
		for name in new:
			default_names = mc.ls (name, type = "transform") + default_names
		for obj in default_names:
			if len ( obj.split("|")) > 1:
				obj = obj.split("|")[-1]
			if len (mc.ls (obj)) >1:
				QMessageBox.information(None, u' issue ',"duplicate names:" + obj)
				return  True
			else:
				try:
					rootObj = mc.listRelatives(obj,ap=True, f = True)[0]
					if rootObj != None:
						for folder in self.tempMainFolder:
							if rootObj.startswith( folder)  or rootObj.startswith( "|" + folder):
								QMessageBox.information(None, u' issue ',"Rename Default Object/s Name/s Objects:  " + obj )
								return  True
						else:
							return False
				except Exception:
					pass

	# dectectar caracteres especiales
	def AdvertSpecialChars(self):
		exportable_objs = []
		for folder in self.tempMainFolder:
			try:
				objsList = mc.listRelatives (folder , ad = True, s = False)
			except ValueError:
				QMessageBox.information(None, u' issue '," Not -" + str (self.tempMainFolder) + "- folder founded ")
				return True
			if  objsList == None:
				objsList = []
			for obj in objsList:
				exportable_objs.append(obj)
		if type(self.filepath_maya) == "string":
			all_list = exportable_objs + self.filepath_maya
		else:
			all_list = exportable_objs
		obj_con_ec = []
		for obj in all_list:
			if set(obj).difference(printable):
				obj_con_ec.append (obj)
		if obj_con_ec != []:
			QMessageBox.information(None, u' issue '," Specials Characters found: " + str(obj_con_ec))
			return  True
		else:
			return False

	def AdvertWrongExteralPath (self):
		externalFilesList =[]
		filesNodes = mc.ls(type='file')
		cache_node_list = []
		try:
			cache_node_list = mc.ls(type='ExocortexAlembicFile')
		except Exception:
			pass
		rootReference = mc.file(r = True, q = True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True )
			if subReferences != None:
				todasLasReferencias = todasLasReferencias + subReferences
		for f in filesNodes:
			t = mc.getAttr(f + '.fileTextureName')
			if os.path.isfile(t):
				externalFilesList.append(t)
		for ref in todasLasReferencias:
			ruta = mc.referenceQuery ( ref, filename = True )
			if os.path.isfile( ruta) :
				externalFilesList.append( ruta)
		for cache_node in cache_node_list:
			ruta_Ca = mc.getAttr(cache_node + '.fileName')
			externalFilesList.append(ruta_Ca)
		advertenceList = []
		for file in externalFilesList:
			win.root = win.root.replace("\\","/")
			if not file.startswith (win.root):
				advertenceList.append (file)
		if len(advertenceList) > 0 :
			QMessageBox.information(None, u' issue ', "Path/s Out of pipeline Root  \n " + str(advertenceList))
			return True
		else:
			return False

	def AdvertIfNotRef(self):
		listForReferenceCheck = []
		for folder in self.tempMainFolder:
			try:
				list = mc.listRelatives(folder,ad = True ,type = "transform", f =True)
			except Exception:
				pass
			if list == None:
				list = []
			for o in list:
				listForReferenceCheck.append(o)
		notReferenceObj_List = []
		for node in listForReferenceCheck:
			respuesta = mc.referenceQuery ( node, isNodeReferenced = True)
			if respuesta == False:
				notReferenceObj_List.append(node)
		if notReferenceObj_List != []:
			QMessageBox.information(None, u' issue ', " Object/s is not Reference: \n" + str (notReferenceObj_List) )
			return True
		else:
			return False



	def AdvertNaSpaNotMatchRefPath(self):
		rootReference = mc.file(r = True, q = True)
		todasLasReferencias = []
		for re in rootReference:
			ref = mc.referenceQuery( re, referenceNode=True)
			todasLasReferencias.append (ref)
			subReferences = mc.referenceQuery ( ref, rfn = True ,child = True ) #
			if subReferences != None:
				if mc.referenceQuery (subReferences, il = True):
					todasLasReferencias = todasLasReferencias + subReferences
		nameSpaNotMatchinList = []
		for refNode in todasLasReferencias:
			nameSpa = mc.referenceQuery  (refNode , ns = True )
			if  len(refNode.split(":")) > 1:
				refNode = refNode.split(":")[-1]
			if refNode.split("RN")[0] !=  nameSpa.split(":")[-1] :
				nameSpaNotMatchinList.append (nameSpa.split(":")[-1])
			if nameSpaNotMatchinList != [] and nameSpaNotMatchinList != [u'']:
				QMessageBox.information(None, u' issue ', "Reference Node Doesn t match with NameSpace\n" + str (nameSpaNotMatchinList) )
				return True
			else:
				return False

	
	def AdvertObjConstrOut (self):
		pConstraintNodes = mc.ls (type = "parentConstraint")
		for constr in pConstraintNodes:
			objs = mc.parentConstraint( constr, targetList = True ,q =True)
			#source = mc.parentConstraint( constr, weightAliasList = True ,q =True)
			for o in objs:
				try:
					for folder in self.tempMainFolder:
						try:
							root = mc.listRelatives(o, ap = True, f =True)[0]
						except Exception:
							pass
						if root != None:
							if root.startswith( "|" + folder) or root.startswith( folder):
								conections = mc.listConnections(constr)
								set_List_Conections = set(conections)
								for conect in set_List_Conections:
									if conect != o and conect != constr:
										try:
											sourceRoot = mc.listRelatives(conect, ap = True, f =True)[0]
										except Exception:
											pass
										if not sourceRoot.startswith( folder):
											QMessageBox.information(None, u' issue ', " insert object in to -" + folder + "- structure, with proper name \n  " + conect )
											return True
										else:
											return False
				except Exception:
					pass

					#################  y ahora voy a crear el publish   ####################
					########################################################

	def exportSelectionFunc(self, path, name, exten):
		full_path = os.path.join( path, name + exten)
		if exten == ".ma":
			tipo = 'mayaAscii'
		elif exten == ".mb":
			tipo = 'mayaBinary'
		if os.path.isfile(full_path):
			os.remove(full_path)
		mc.select (self.tempMainFolder)
		mc.file ( full_path, type=tipo , es = True )
		win.scripJCounter1= win.scripJCounter1 + 1
		mc.file ( full_path,o = True , force = True )

	# un vez abierto el publish
	#################### esto lo debe hacer en el fbx que export#######################
	##################################################################################
	# elimnar namespace del template
	def r_namespaces(self, node):   #  es parte de la siguiente funcion
		try:
			namespace, name = node.rsplit(":", 1)
		except:
			namespace, name = None, node
		if namespace:
			try:
				mc.rename(node, name)
			except RuntimeError:
				pass
	def removeNamesSpacesfromTemplate(self):
		transformRoot = self.tempMainFolder
		for node in transformRoot:
			try:
				nodeList = mc.listRelatives(node, allDescendents=True, typ="transform")
			except Exception:
				pass
			if nodeList != None:
				for descendent in nodeList:
					self.r_namespaces(descendent)
				self.r_namespaces(node)
 
	# eliminar namespace vacios
	def removeEmptyNameSpac (self):
		listaNSpace = mc.namespaceInfo( lon = True)
		listaNSpace.remove ('UI')
		listaNSpace.remove ('shared')
		for ns in listaNSpace:
			objNameSpList = mc.ls( ns + ":*" )
			if len (objNameSpList) == 0:
				mc.namespace (rm = ns)
				print "deleted namepacecs:  " + ns

	# delete unknow nodes
	def deleteUnknowNodes(self):
		nodeList = mc.ls(type="unknown")
		for n in nodeList:
			try:
				mc.delete( n )
			except Exception:
				pass
	# borrar los display layers, esto depende de la etapa del asset
	def deleteDispLay(self):
		pathSplited = self.filepath_maya.split("/")
		etapaAsset = pathSplited[-3]
		if etapaAsset != rig_folder:
			layerList = mc.ls(type="displayLayer")
			for layer in layerList:
				try:
					if layer != "defaultLayer":
						mc.delete(layer)
				except Exception:
					pass

	def execution(self, path, name , exten):
		self.startVars()
		while True:
			if self.dupliNameDetectionFunc() == True:     # este deberia ir pero seguramente ya es tarde
				break
			if self.AdvertDefaultNameObj() == True:
				break
			if self.AdvertSpecialChars() == True:
				break
			if self.AdvertWrongExteralPath() == True:
				break
			if self.AdvertNaSpaNotMatchRefPath() == True:
				break
			self.deleteUnknowNodes()
			self.exportSelectionFunc(path, name , exten)
			self.removeNamesSpacesfromTemplate()
			self.removeEmptyNameSpac ()
			self.deleteDispLay()
			mc.file ( s = True)
			return True

class setTemplateWin(QWidget):
	def __init__(self, parent=None):
		super(setTemplateWin, self).__init__(parent)
		self.setStyleSheet(" background-color: rgb(65,65,65)")
		self.resize(500, 390)
		self.setWindowIcon(win.iconPrg)		
		self.setWindowTitle( " Set Templates ")

		texto = ("                             Insert your templates as: \n\n              -- " + animTamplate + win.settin_list[5] + " --       on this folder: \n\n" + win.root  + win.projName + "/PIPELINE/TEMPLATES/SCENE/" + "\n\n              -- " + rigCharPropTempl + win.settin_list[5] + " --\n              -- "+ modTemplate + win.settin_list[5] + " --\n              -- "+ emptyTempla + win.settin_list[5] + " --\n              -- " + escenarioTempl + win.settin_list[5] + " --\n              -- " + moduleTempl + win.settin_list[5] + " --      on this folder: \n\n" + win.root  + win.projName + "/PIPELINE/TEMPLATES/ASSET/" )

		self.labSetTemplates = QLabel(self)
		self.labSetTemplates.setGeometry(QtCore.QRect(63, -30, 500, 300))
		self.labSetTemplates.setText(texto)
		self.labSetTemplates.setStyleSheet("color: rgb(210,135,20)")
		#self.labSetTemplates.setFont(win.newfont)

		self.btnActivateTempl = QPushButton(self)
		self.btnActivateTempl.setText('Activate Copied Templates')
		self.btnActivateTempl.setGeometry(QtCore.QRect(135, 280, 230, 41))
		self.btnActivateTempl.setStyleSheet("background-color: rgb(210,135,20); color: rgb(200,200,200); border-radius: 20px; border-style: groove; border-width: 3px;")
		self.btnActivateTempl.clicked.connect( self.exceutingTempleActive )
		self.btnActivateTempl.setFont(win.newfont)
		
	def exceutingTempleActive(self):
		#mayaTemListNa = [ "ANIM_TEMPLATE", "MOD_TEMPLATE", "EMPTY_TEMPLATE", "RIGGEDASS_TEMPLATE", "SET_TEMPLATE", "MODULE_TEMPLATE" ]
		if len(str(excutSource).split("maya")) != 2:
			QMessageBox.information(None, u'', " Only Operating on Maya could activate templates " )
		else:
			main_list = []
			for temNa in mayaTemListNa:
				if temNa != animTamplate and temNa != litTempla:
					path = win.root + win.projName + "/PIPELINE/TEMPLATES/ASSET"
				else:
					path = win.root + win.projName + "/PIPELINE/TEMPLATES/SCENE"
				mc.file ( new = True, force = True )
				name = temNa + win.settin_list[5] 
				mc.file(  path + "/" + name ,o = True , force = True )
				RootTransforms = mc.ls("|*", type = "transform")
				for camNode in ['front', 'persp', 'side', 'top']:
					RootTransforms.remove(camNode)
				main_list.append ( RootTransforms )
			mc.file ( new = True, force = True )
			path = os.path.join( win.root + win.projName + "/PIPELINE/CONFIGURATION/", "project_tamplate_activation.json" )
			with open( path, "w") as file:
				file.write(   '{"templeVasData" :' + str (main_list) + '}')
				file.close()
			win.EMPTY_TEMPLATE= ["*"]
			win.MOD_TEMPLATE = main_list[1]
			win.MODULE_TEMPLATE = main_list[5]
			win.RIGGEDASS_TEMPLATE = main_list[3]
			win.SET_TEMPLATE = main_list[4]
			win.ANIM_TEMPLATE = main_list[0]
			win.LIT_TEMPLATE = main_list[6]
			self.btnActivateTempl.setText('Activated!')
			self.btnActivateTempl.setStyleSheet("background-color: rgb(210,135,20);color: rgb(0, 120, 0); border-style: groove")
			win.labTamplateActive.setText("Activated")
			win.labTamplateActive.setStyleSheet("background-color: rgb(65,65,65);color: rgb(10, 170, 160)")
			self.close()
			os.startfile(win.root + win.projName + "/PIPELINE/CONFIGURATION/")
		
class getThumbnClass(QLabel):

	def __init__(self, parent=None, path=None):
		super(getThumbnClass, self).__init__(parent)
		pic = QPixmap(path)
		self.setPixmap(pic)


if len(str(excutSource).split("maya")) != 2:
	if __name__ == '__main__':
		app = QApplication(sys.argv)
		#app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
		win = MainWindow()
		win.wind.show()
		sys.exit(app.exec_())
else:
	print " welcome!!!!!"
	win = MainWindow()
	mc.scriptJob(ka=True ,force=True)
	mc.scriptJob( runOnce=False,e= ["SceneOpened","validationsVarsReset()"], protected=True)
	#app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
	#win.wind.show()

#os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
#qapp = QApplication(sys.argv)
#qapp.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)