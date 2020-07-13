# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Gas\Desktop\gaston\scripts\exporterUI.ui'
#
# Created: Wed Apr 11 12:18:08 2018
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ExporterTool(object):
    def setupUi(self, ExporterTool):
        ExporterTool.setObjectName("ExporterTool")
        ExporterTool.setWindowModality(QtCore.Qt.NonModal)
        ExporterTool.setEnabled(True)
        ExporterTool.resize(700, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExporterTool.sizePolicy().hasHeightForWidth())
        ExporterTool.setSizePolicy(sizePolicy)
        ExporterTool.setMinimumSize(QtCore.QSize(700, 600))
        ExporterTool.setMaximumSize(QtCore.QSize(700, 600))
        ExporterTool.setSizeIncrement(QtCore.QSize(826, 673))
        ExporterTool.setBaseSize(QtCore.QSize(826, 673))
        ExporterTool.setAcceptDrops(False)
        ExporterTool.setStyleSheet("")
        ExporterTool.setModal(False)
        self.pushButtonDone = QtWidgets.QPushButton(ExporterTool)
        self.pushButtonDone.setGeometry(QtCore.QRect(470, 470, 101, 41))
        self.pushButtonDone.setObjectName("pushButtonDone")
        self.comboBoxNameSpaces = QtWidgets.QComboBox(ExporterTool)
        self.comboBoxNameSpaces.setGeometry(QtCore.QRect(70, 70, 141, 41))
        self.comboBoxNameSpaces.setObjectName("comboBoxNameSpaces")
        self.listWidgetSelectedNameSpaces = QtWidgets.QListWidget(ExporterTool)
        self.listWidgetSelectedNameSpaces.setGeometry(QtCore.QRect(440, 71, 131, 201))
        self.listWidgetSelectedNameSpaces.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.listWidgetSelectedNameSpaces.setObjectName("listWidgetSelectedNameSpaces")
        self.pushButton_arrow = QtWidgets.QPushButton(ExporterTool)
        self.pushButton_arrow.setGeometry(QtCore.QRect(270, 160, 111, 41))
        self.pushButton_arrow.setObjectName("pushButton_arrow")
        self.labelErrorStarD = QtWidgets.QLabel(ExporterTool)
        self.labelErrorStarD.setEnabled(False)
        self.labelErrorStarD.setGeometry(QtCore.QRect(410, 310, 221, 20))
        self.labelErrorStarD.setObjectName("labelErrorStarD")
        self.checkBoxExportMesh = QtWidgets.QCheckBox(ExporterTool)
        self.checkBoxExportMesh.setGeometry(QtCore.QRect(90, 330, 91, 17))
        self.checkBoxExportMesh.setObjectName("checkBoxExportMesh")
        self.checkBoxImproveBake = QtWidgets.QCheckBox(ExporterTool)
        self.checkBoxImproveBake.setGeometry(QtCore.QRect(90, 380, 141, 17))
        self.checkBoxImproveBake.setObjectName("checkBoxImproveBake")
        self.checkBoxBakeBlendShapes = QtWidgets.QCheckBox(ExporterTool)
        self.checkBoxBakeBlendShapes.setGeometry(QtCore.QRect(90, 430, 151, 17))
        self.checkBoxBakeBlendShapes.setObjectName("checkBoxBakeBlendShapes")
        self.labelSceneAssets = QtWidgets.QLabel(ExporterTool)
        self.labelSceneAssets.setGeometry(QtCore.QRect(110, 40, 131, 21))
        self.labelSceneAssets.setObjectName("labelSceneAssets")
        self.labelSelectedAssets = QtWidgets.QLabel(ExporterTool)
        self.labelSelectedAssets.setGeometry(QtCore.QRect(470, 50, 111, 16))
        self.labelSelectedAssets.setObjectName("labelSelectedAssets")
        
                # label imagen
        imagemap = QtGui.QPixmap ("C:/Users/Gas/Desktop/gaston/scripts/images32.png")

        label = QtWidgets.QLabel(ExporterTool)
        label.setGeometry(QtCore.QRect(270, 40, 125, 110))
        label.setMinimumSize(QtCore.QSize(125, 110))
        label.setMaximumSize(QtCore.QSize(125, 110))
        label.setObjectName("label")
        #label.setText(QtWidgets.QApplication.translate(window, "<html><head/><body><p><img src=\":/image perico/images32.png\"/></p></body></html>", None, -1))
        label.setPixmap (imagemap)
        

        self.retranslateUi(ExporterTool)
        QtCore.QMetaObject.connectSlotsByName(ExporterTool)

    def retranslateUi(self, ExporterTool):
        ExporterTool.setWindowTitle(QtWidgets.QApplication.translate("ExporterTool", "Perico Exporter Tool", None, -1))
        self.pushButtonDone.setText(QtWidgets.QApplication.translate("ExporterTool", "Done", None, -1))
        self.pushButton_arrow.setText(QtWidgets.QApplication.translate("ExporterTool", ">>>>>>>", None, -1))
        self.labelErrorStarD.setText(QtWidgets.QApplication.translate("ExporterTool", "Error, please check proper Star Distribution!", None, -1))
        self.checkBoxExportMesh.setText(QtWidgets.QApplication.translate("ExporterTool", "Export Mesh", None, -1))
        self.checkBoxImproveBake.setText(QtWidgets.QApplication.translate("ExporterTool", "Improve Bake Quality", None, -1))
        self.checkBoxBakeBlendShapes.setText(QtWidgets.QApplication.translate("ExporterTool", "Bake Blend Shapes Nodes", None, -1))
        self.labelSceneAssets.setText(QtWidgets.QApplication.translate("ExporterTool", "Scene Assets", None, -1))
        self.labelSelectedAssets.setText(QtWidgets.QApplication.translate("ExporterTool", "Selected Assets", None, -1))


#import imageTest_rc
#import imagePerico_rc
