# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'graficNew.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Graphic(object):
    def setupUi(self, Graphic):
        Graphic.setObjectName("Graphic")
        Graphic.resize(843, 639)
        self.pushButton = QtWidgets.QPushButton(Graphic)
        self.pushButton.setGeometry(QtCore.QRect(90, 520, 691, 91))
        self.pushButton.setObjectName("pushButton")
        self.widget = MatplotlibWidget111_sin(Graphic)
        self.widget.setGeometry(QtCore.QRect(100, 50, 651, 451))
        self.widget.setObjectName("widget")

        self.retranslateUi(Graphic)
        QtCore.QMetaObject.connectSlotsByName(Graphic)

    def retranslateUi(self, Graphic):
        _translate = QtCore.QCoreApplication.translate
        Graphic.setWindowTitle(_translate("Graphic", "GraficNew"))
        self.pushButton.setText(_translate("Graphic", "Generar Grafico"))
from classgrafic import MatplotlibWidget111_sin
