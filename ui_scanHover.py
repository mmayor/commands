# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanHover.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_scanHover(object):
    def setupUi(self, scanHover):
        scanHover.setObjectName("scanHover")
        scanHover.resize(713, 344)
        self.pushButton = QtWidgets.QPushButton(scanHover)
        self.pushButton.setGeometry(QtCore.QRect(10, 50, 94, 27))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(scanHover)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 260, 94, 27))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("delete_close_stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setObjectName("pushButton_2")
        self.tableWidget = QtWidgets.QTableWidget(scanHover)
        self.tableWidget.setGeometry(QtCore.QRect(120, 21, 561, 291))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.retranslateUi(scanHover)
        self.pushButton_2.clicked.connect(scanHover.close)
        QtCore.QMetaObject.connectSlotsByName(scanHover)

    def retranslateUi(self, scanHover):
        _translate = QtCore.QCoreApplication.translate
        scanHover.setWindowTitle(_translate("scanHover", "Scan Hover"))
        self.pushButton.setText(_translate("scanHover", "Scan"))
        self.pushButton_2.setText(_translate("scanHover", "Close"))
