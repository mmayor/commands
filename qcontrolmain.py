from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request
import recursos_1_qrc
from numpy.f2py import __version__
import ui_scan
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
# import cam
import classCam
from threading import Thread
import threading
import ui_QControl
import scan
import scanHover
import searchMotors
import ui_scan
# import servidor
# import audioRecord
# import datetime
from time import gmtime, strftime
import classgrafic
import graficNew
import color

class QualityControlMain(QMainWindow, ui_QControl.Ui_QControl):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(QualityControlMain, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        # self.textEdit.setText('')
        # self.label_4.setVisible(False)
        # self.updateUi('')
        self.actionScan.triggered.connect(lambda:  self.openScan())
        self.actionScan_2.triggered.connect(lambda: self.hoverScan())
        self.actionAbout.triggered.connect(lambda: self.helpAbout())
        self.actionMotors.triggered.connect(lambda: self.searchMotors())
        self.actionNew.triggered.connect(lambda: self.grapficNew())
        self.actionClose.triggered.connect(self.close)
        self.actionLigntninbolt.triggered.connect(lambda : self.lightninbolt())
        self.statusbar.addWidget(self.label_2)
        self.label_2.setText(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

        # self.statusbar.showMessage(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

    @pyqtSlot()
    def on_actionMotors_clicked(self):

        # print('pepe')
        pass


    def printText(self, text):
        print(text)

    def openScan(self):
        scanNew= scan.ScanDlg(self)
        scanNew.show()

    def hoverScan(self):
        scanNew= scanHover.ScanHoverDlg(self)
        scanNew.show()


    def lightninbolt(self):
        lightNew= color.ColoreDlg(self)
        lightNew.show()


    def searchMotors(self):
        tempMotors= searchMotors.SearchMotors(self)
        tempMotors.show()

    def grapficNew(self):
        # tempGrafic= classgrafic.MatplotlibWidget111()
        # tempGrafic.grafico()
        tempGrafic= graficNew.MiFormulario(self)
        # X = list(range(50))
        # Y1 = [1 / (x + 5) for x in X]
        # tempGrafic.canvas.ax.plot(X, Y1)
        tempGrafic.show()


    def helpAbout(self):
        QMessageBox.about(self, "Quaility Control",
                          "<b>FKIRONS Quality Control</b>"
                          "<p>Copyright &copy; 2008-10 Qtrac Ltd."
                          "All rights reserved."
                          "<p>This application allows to improve"
                          "the quality control system.")

def main():
    import sys

    app = QApplication(sys.argv)
    form = QualityControlMain()
    form.show()
    app.exec_()

main()

