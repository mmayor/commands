# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_server.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ServerListen(object):
    def setupUi(self, ServerListen):
        ServerListen.setObjectName("ServerListen")
        ServerListen.resize(400, 300)
        self.label = QtWidgets.QLabel(ServerListen)
        self.label.setGeometry(QtCore.QRect(30, 30, 61, 21))
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(ServerListen)
        self.pushButton.setGeometry(QtCore.QRect(90, 20, 94, 27))
        self.pushButton.setObjectName("pushButton")
        self.textEdit = QtWidgets.QTextEdit(ServerListen)
        self.textEdit.setGeometry(QtCore.QRect(30, 80, 341, 141))
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(ServerListen)
        QtCore.QMetaObject.connectSlotsByName(ServerListen)

    def retranslateUi(self, ServerListen):
        _translate = QtCore.QCoreApplication.translate
        ServerListen.setWindowTitle(_translate("ServerListen", "ServerListen"))
        self.label.setText(_translate("ServerListen", "Server"))
        self.pushButton.setText(_translate("ServerListen", "Run"))
