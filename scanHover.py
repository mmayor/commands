import subprocess
import sys
import json
# import bluScan
from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request
import ui_scan
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
# import cam
import scanHover
import ui_scanHover
from threading import Thread
import threading
import os
import pygame


class ScanHoverDlg(QDialog, ui_scanHover.Ui_scanHover):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ScanHoverDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        # self.dockWidget.setEnabled(False)
        # self.dockWidget.setWidget(QTextEdit())
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['Address', 'Addrtype', 'Nivel', 'Name'])
        self.tableWidget.setColumnWidth(0, 142)
        # self.textEdit.setText('')
        # self.updateUi('')
        # self.__list= QTextEdit()
        # self.show()


    def scanHover(self):

        row = 0
        col = 0
        count = 0
        try:
            tempScan = subprocess.call(['sudo', sys.executable, 'blueScan.py'])
        except:
            print("ERROR SCAN HOVER")

        try:
            with open('data.json') as file:
                datas = json.load(file)
                print(datas)

                for data in datas:
                    # print(data['addr'])
                    count = count + 1
                    # print(data['id'], data['serial'], data['status'])
                    self.tableWidget.setRowCount(count)
                    item_tabla = QTableWidgetItem(str(data['addr']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['addrtype']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 1, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['nivel']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 2, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['name']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 3, item_tabla)

                    row = row + 1



        except:
            print("ERROR LOAD JSON")





    @pyqtSlot()
    def on_pushButton_clicked(self):

        self.pushButton.setEnabled(False)
        self.pushButton.setText('Scanning...')
        self.pushButton.repaint()
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.repaint()

        self.scanHover()

        self.pushButton.setText('Scan')
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled((True))


    def updateUi(self, text):

        # self.textEdit.append(text)
        self.__index = 10
        # self.__list.append(text)
        # self.dockWidget.setWidget(self.__list)

