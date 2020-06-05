# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_searchMotors.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SearchMotors(object):
    def setupUi(self, SearchMotors):
        SearchMotors.setObjectName("SearchMotors")
        SearchMotors.resize(1177, 919)
        self.pushButton = QtWidgets.QPushButton(SearchMotors)
        self.pushButton.setGeometry(QtCore.QRect(10, 180, 211, 31))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.tableWidget = QtWidgets.QTableWidget(SearchMotors)
        self.tableWidget.setGeometry(QtCore.QRect(240, 20, 911, 241))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.radioButton = QtWidgets.QRadioButton(SearchMotors)
        self.radioButton.setGeometry(QtCore.QRect(10, 40, 112, 24))
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(SearchMotors)
        self.radioButton_2.setGeometry(QtCore.QRect(10, 80, 112, 24))
        self.radioButton_2.setObjectName("radioButton_2")
        self.lineEdit = QtWidgets.QLineEdit(SearchMotors)
        self.lineEdit.setGeometry(QtCore.QRect(40, 130, 171, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(SearchMotors)
        self.label.setGeometry(QtCore.QRect(10, 140, 31, 19))
        self.label.setObjectName("label")
        self.pushButton_2 = QtWidgets.QPushButton(SearchMotors)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 230, 201, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("filequit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setObjectName("pushButton_2")
        self.widget = MatplotlibWidget22_sin(SearchMotors)
        self.widget.setGeometry(QtCore.QRect(10, 290, 1141, 611))
        self.widget.setObjectName("widget")

        self.retranslateUi(SearchMotors)
        self.pushButton_2.clicked.connect(SearchMotors.close)
        QtCore.QMetaObject.connectSlotsByName(SearchMotors)

    def retranslateUi(self, SearchMotors):
        _translate = QtCore.QCoreApplication.translate
        SearchMotors.setWindowTitle(_translate("SearchMotors", "Search Motors"))
        self.pushButton.setText(_translate("SearchMotors", "Search"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("SearchMotors", "ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("SearchMotors", "Serial"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("SearchMotors", "Status"))
        self.radioButton.setText(_translate("SearchMotors", "Motors"))
        self.radioButton_2.setText(_translate("SearchMotors", "Test"))
        self.label.setText(_translate("SearchMotors", "Id:"))
        self.pushButton_2.setText(_translate("SearchMotors", "Close"))
from classgrafic import MatplotlibWidget22_sin
