from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request
import ui_scan
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import cam
import classCam
from threading import Thread
import threading


class ScanDlg(QDialog, ui_scan.Ui_Dialog, classCam.ScanComplete):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ScanDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        self.textEdit.setText('')
        self.updateUi('')

    @pyqtSlot()
    def on_pushButton_clicked(self):

        self.textEdit.clear()
        self.lineEdit_2.clear()
        self.pushButton.setEnabled(False)
        self.pushButton.setText('Scanning...')
        tempScan = classCam.ScanComplete()
        d= threading.Thread(target=tempScan.camIdMotor, name='daemon')
        d.start()

        # self.updateUi('pepe')
        # for i in range(50):
        #     self.updateUi(str(i))

        while not tempScan.getFoundFlag():
            # print(tempScan.getData())
            tempStr= ''
            for ele in tempScan.getData():
                tempStr += ele

            # print(tempStr)
            self.updateUi(tempStr)
            self.textEdit.repaint()
            # self.updateUi('pepe')
        self.lineEdit_2.setText(tempScan.getFound())

        # self.setupUi(self)
        self.pushButton.setText('StartScan')
        self.pushButton.setEnabled(True)
        # self.pushButton.repaint()self.pushButton.setEnabled(True)
        # print('Value Found: ', tempScan.getFound())

    def updateUi(self, text):

        self.textEdit.append(text)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = ScanDlg()
    form.show()
    app.exec_()
    # print(form.result())