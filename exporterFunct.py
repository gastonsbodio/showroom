# Author: Gaston Sbodio (gastonsbodio@gmail.com)

from PySide2 import QtCore, QtGui, QtWidgets
import exporterUI as customUI
reload(customUI)
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as mc
import pymel.core as pm



def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ControlMainWindow(QtWidgets.QDialog):


    listaNSpace = mc.namespaceInfo( lon = True)
    listaNSpace.remove ('UI')
    listaNSpace.remove ('shared')
    for o in listaNSpace:
        consul = mc.ls ( o + ":DeformSet")
        if consul == []:
            listaNSpace.remove (o)

###########    Interface y Ejecusion  #############
    def __init__(self, parent=None):
 
        super(ControlMainWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui =  customUI.Ui_ExporterTool()
        self.ui.setupUi(self)
        self.ui.comboBoxNameSpaces.addItems(self.listaNSpace)        
        self.ui.pushButton_arrow.clicked.connect(self.ArrowButton)
        self.ui.pushButtonDone.clicked.connect(self.DoneButton)
        self.ui.labelErrorStarD.hide() 


###########   Funcionalidad  ######################


    def ArrowButton(self):
        global charNameS
        global listaAssetsSelects
        charNameS = self.ui.comboBoxNameSpaces.currentIndex()
        listaAssetsSelects = [i.text() for i in self.ui.listWidgetSelectedNameSpaces.findItems("", QtCore.Qt.MatchContains)]
        if listaAssetsSelects == []:
            self.ui.listWidgetSelectedNameSpaces.addItem(self.listaNSpace[charNameS])
            listaAssetsSelects = [i.text() for i in self.ui.listWidgetSelectedNameSpaces.findItems("", QtCore.Qt.MatchContains)]
        else:
            if self.listaNSpace[charNameS] not in listaAssetsSelects:
                self.ui.listWidgetSelectedNameSpaces.addItem(self.listaNSpace[charNameS])
                listaAssetsSelects = [i.text() for i in self.ui.listWidgetSelectedNameSpaces.findItems("", QtCore.Qt.MatchContains)]
                print "            la      lista       de          Assets          es           :" + str(listaAssetsSelects)


    def importRefer(self):
        global granFather
        refNMatching = "nada"

        todasLasReferencias = mc.ls ( "*RN", type = "reference")
        print "  todas las referencias       ssssssssssssssss     son    " + str (  todasLasReferencias  )
        for obj in todasLasReferencias:
            print obj + "    la la la aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa                   aaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            try:
                nameSRef = str (mc.referenceQuery ( obj, ns = True ))
                print nameSRef + "       name space ssssssssssssssssssssssssssssssssssssss"
            except Exception: 
                pass            
            if nameSRef  == ":" + nomNSSelected:
                refNMatching = obj
        ruta = mc.referenceQuery ( refNMatching, filename = True )
        mc.file (ruta,ir = True )
        try :
            rootUnity = mc.ls (nomNSSelected + ":Rootunity")
        except Exception: 
            pass
        if rootUnity == []:
            mc.createNode('joint', n = nomNSSelected + ":Rootunity")
            children = mc.listRelatives( nomNSSelected + ":DeformationSystem",c = True, type = "joint")
            father = mc.listRelatives ( nomNSSelected + ":DeformationSystem", p = True)
            granFather = mc.listRelatives ( father[0], p = True)
            mc.parent (nomNSSelected + ":DeformationSystem", nomNSSelected + ":Rootunity")
            mc.sets ( nomNSSelected + ":Rootunity", add = nomNSSelected + ":DeformSet" )
        print ("okkkk")

    def exportSoloJoints(self):
               
        mc.parent (nomNSSelected + ":Geometry", w = True)
        mc.delete (granFather)
        mc.select ( setSel )
        mc.file ( rutaSeteada, force=True, exportSelected = True, type="FBX export" )
        print ("okkk")

    def exportMeshJoints(self):
        mc.parent (nomNSSelected + ":Geometry", w = True)
        selObjMesh = mc.listRelatives( nomNSSelected + ":Geometry", ad = True, type = "mesh")
        mc.delete (granFather)
        mc.select ( setSel, selObjMesh )
        mc.file ( rutaSeteada, force=True, exportSelected = True, type="FBX export" )
        print ("okk")

    def bakeJoints(self):
        global start
        global end
        start = mc.playbackOptions( minTime = True, q = True )
        end = mc.playbackOptions( maxTime = True, q = True )   
        global setSel
        mc.select( nomNSSelected + ":DeformSet" )
        setSel = mc.ls ( sl = True )
        mc.playbackOptions( minTime = start, maxTime=end, e = True )
        mc.bakeResults( setSel, t = (start , end), simulation=True )
        check2 = self.ui.checkBoxImproveBake.isChecked()       
        
        if check2 == True :
            atributosRot = mc.ls  (nomNSSelected + ":*.rotateX", nomNSSelected + ":*.rotateY", nomNSSelected +":*.rotateZ")
            mc.filterCurve( atributosRot )
        childrens = mc.listRelatives ( granFather[0] , c = True)
        for obj in childrens:
            if obj != nomNSSelected + ":Rootunity" and obj != nomNSSelected + ":Geometry":
                mc.delete (obj)
        mc.select (setSel)
        lsJointExport = mc.ls (sl = True)
        for obj in lsJointExport:
            mc.setAttr (obj+'.drawStyle',0)
            mc.setAttr (obj+'.radius',0.01)
        print ("ok")



    def bakeGeoBS(self):
        check3 = self.ui.checkBoxBakeBlendShapes.isChecked() 
        if check3 == True :
            selObjM = mc.listRelatives( nomNSSelected + ":Geometry", ad = True, type = "mesh")
            for obj in selObjM:
                nodosBlendShapes = mc.ls (type = "blendShape")
                for bs in nodosBlendShapes:
                    nomGeoConectadaAbs = mc.blendShape ( bs, g = True, q = True )[0]
                    if nomGeoConectadaAbs == obj :
                        mc.playbackOptions( minTime=start, maxTime=end, e = True )
                        mc.bakeResults( bs, t = (start , end), simulation=True )

        print ("okkkkk")

    def borrarJointsEnd(self):
        lista = ["R","L","M","C"]
        for side in lista:
            try:
                mc.delete ("*:*End_" + side)
            except Exception: 
                pass


    def advertenciaStarJoints(self):
        global textoText01
        global nomNSSelected
        nomNSSelected = turnoAsset
        print "el nombre del asset de turno essssssss         ssssss           " + turnoAsset

        rigJoints = mc.listRelatives ( nomNSSelected + ":Root_M", ad = True, type = "joint" )
        cantidad01 = len ( rigJoints )

        rigJointsOnlyChildren = mc.listRelatives ( nomNSSelected + ":Root_M", c = True, type = "joint" )
        cantidad02 = len ( rigJointsOnlyChildren )

        if cantidad01 != cantidad02:
            textoText01 = " error    "
            self.ui.labelErrorStarD.setEnabled(True)
            self.ui.labelErrorStarD.setStyleSheet("background-color:red;")
            self.ui.labelErrorStarD.show() 
 
        else:
            textoText01 = " "
            

    
    def DoneButton(self):
        global turnoAsset
        turnoAsset = "nada"
        if listaAssetsSelects == []:
            pass
        else:
            for i in listaAssetsSelects:
                turnoAsset = i
                global rutaSeteada
                estado = self.ui.checkBoxExportMesh.isChecked()
                if estado == True :
                    self.advertenciaStarJoints()
                    if textoText01 == " ":
                        rutaSeteada = pm.fileDialog2( caption = 'Seve Path', fileMode = 0, fileFilter = "FBX File (*.fbx);;All Files (*.*))", spe = True)[0]
                        self.importRefer()
                        self.bakeJoints()
                        self.bakeGeoBS()
                        self.exportMeshJoints()
                        self.borrarJointsEnd()
                        myWin.hide()
                    else:
                        print ("mostrar el error")
                        
                else:
                    self.advertenciaStarJoints()
                    if textoText01 == " ":
                        rutaSeteada = pm.fileDialog2( caption = 'Seve Path', fileMode = 0, fileFilter = "FBX File (*.fbx);;All Files (*.*))", spe = True)[0]
                        self.importRefer()
                        self.bakeJoints()
                        self.exportSoloJoints()
                        self.borrarJointsEnd()
                        myWin.hide()
                    else:
                        print ("mostrar el error")


myWin = ControlMainWindow(parent=maya_main_window())

myWin.show()











