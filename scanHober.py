import json
import subprocess

from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request

import ui_hober
import ui_scan
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import cam
import hober
from threading import Thread
import threading
import ui_hober
# import bluScan


class ScanHoberDlg(QDialog, ui_hober.Ui_scanHober, hober.ScanDelegate):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ScanHoberDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        # self.textEdit.setText('')
        self.updateUi('')
        self.__list = QTextEdit()

    @pyqtSlot()
    def on_pushButton_clicked(self):

        # self.textEdit.clear()
        # self.lineEdit_2.clear()
        self.pushButton.setEnabled(False)
        self.pushButton.setText('Scanning...')
        # tempScanHober = hober.ScanDelegate()
        # d= threading.Thread(target=tempScanHober.scanHover, name='daemon')
        # d.start()

        tempScan = subprocess.call(['sudo', sys.executable, 'bluScan.py'])

        with open('data.json') as file:
            data = json.load(file)

        # self.lineEdit_2.setText(tempScan.getFound())

        # self.setupUi(self)
        self.pushButton.setText('Start Scan')
        self.pushButton.setEnabled(True)
        # self.pushButton.repaint()self.pushButton.setEnabled(True)
        # print('Value Found: ', tempScan.getFound())

    def updateUi(self, text):

        self.__list.append(text)
        self.dockWidget.setWidget(self.__list)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = ScanHoberDlg()
    form.show()
    app.exec_()
    # print(form.result())