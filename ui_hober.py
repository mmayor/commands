# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_Hober.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_scanHober(object):
    def setupUi(self, scanHober):
        scanHober.setObjectName("scanHober")
        scanHober.resize(497, 309)
        self.label = QtWidgets.QLabel(scanHober)
        self.label.setGeometry(QtCore.QRect(20, 30, 81, 31))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(scanHober)
        self.pushButton.setGeometry(QtCore.QRect(100, 30, 94, 27))
        self.pushButton.setObjectName("pushButton")
        self.tableWidget = QtWidgets.QTableWidget(scanHober)
        self.tableWidget.setGeometry(QtCore.QRect(30, 90, 391, 192))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.label.setBuddy(self.pushButton)

        self.retranslateUi(scanHober)
        QtCore.QMetaObject.connectSlotsByName(scanHober)

    def retranslateUi(self, scanHober):
        _translate = QtCore.QCoreApplication.translate
        scanHober.setWindowTitle(_translate("scanHober", "Dialog"))
        self.label.setText(_translate("scanHober", "Scan Hober"))
        self.pushButton.setText(_translate("scanHober", "Scan"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("scanHober", "Addr"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("scanHober", "Name"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("scanHober", "Nivel"))
