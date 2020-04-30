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


class ScanDlg(QDialog, ui_scan.Ui_Dialog):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ScanDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        # self.textEdit.setText(self.__text
        # self.updateUi()

    @pyqtSlot()
    def on_pushButton_clicked(self):

        self.tempScan.camIdMotor()
        print(self.tempScan.__found)
        while  self.tempScan.__found:
            print('temp WAIT')
            print(self.tempScan.__data)
        # print(otroTemp)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = ScanDlg()
    form.show()
    app.exec_()
    # print(form.result())