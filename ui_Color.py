# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_Color.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Color(object):
    def setupUi(self, Color):
        Color.setObjectName("Color")
        Color.resize(1444, 1145)
        self.label_7 = QtWidgets.QLabel(Color)
        self.label_7.setGeometry(QtCore.QRect(110, 50, 511, 31))
        self.label_7.setStyleSheet("color:rgb(85, 170, 0);\n"
"font: 75 20pt \"Cantarell\";")
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.pushButton = QtWidgets.QPushButton(Color)
        self.pushButton.setGeometry(QtCore.QRect(20, 30, 1361, 41))
        self.pushButton.setStyleSheet("font: 75 20pt \"Bitstream Charter\";")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("fileopen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(28, 28))
        self.pushButton.setObjectName("pushButton")
        self.dockWidget = QtWidgets.QDockWidget(Color)
        self.dockWidget.setGeometry(QtCore.QRect(20, 130, 441, 971))
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockWidget.setWidget(self.dockWidgetContents)
        self.dockWidget_2 = QtWidgets.QDockWidget(Color)
        self.dockWidget_2.setGeometry(QtCore.QRect(490, 130, 431, 971))
        self.dockWidget_2.setObjectName("dockWidget_2")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        self.dockWidget_3 = QtWidgets.QDockWidget(Color)
        self.dockWidget_3.setGeometry(QtCore.QRect(970, 130, 411, 971))
        self.dockWidget_3.setObjectName("dockWidget_3")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        self.progressBar = QtWidgets.QProgressBar(Color)
        self.progressBar.setGeometry(QtCore.QRect(20, 90, 1361, 23))
        self.progressBar.setStyleSheet("")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(Color)
        QtCore.QMetaObject.connectSlotsByName(Color)

    def retranslateUi(self, Color):
        _translate = QtCore.QCoreApplication.translate
        Color.setWindowTitle(_translate("Color", "Color"))
        self.pushButton.setText(_translate("Color", "Load Data"))
        self.dockWidget.setWindowTitle(_translate("Color", "POS 1"))
        self.dockWidget_2.setWindowTitle(_translate("Color", "POS3"))
        self.dockWidget_3.setWindowTitle(_translate("Color", "POS5"))
