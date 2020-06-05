import sys
import time
from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request



class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        dial = QDial()
        dial.setNotchesVisible(True)
        spinbox = QSpinBox()
        layout = QHBoxLayout()
        layout.addWidget(dial)
        layout.addWidget(spinbox)
        self.setLayout(layout)
        dial.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(dial.setValue)
        self.setWindowTitle("Signals and Slots")

class ZeroSpinBox(QSpinBox):
    zeros = 0
    def __init__(self, parent=None):
        super(ZeroSpinBox, self).__init__(parent)
        self.valueChanged().connect(self.checkzero)
    def checkzero(self):
        if self.value() == 0:
            self.zeros += 1
            self.atzero.emit(self.zeros)

class TaxRate(QObject):
    rateChanged = pyqtSignal(int)
    def __init__(self):
        super(TaxRate, self).__init__()
        self.__rate = 17.5


    def rate(self):
        return self.__rate
    def setRate(self, rate):

        if rate != self.__rate:
            self.__rate = rate
            self.rateChanged.emit(self.__rate)

def rateChanged(value):
    print("TaxRate changed to %.2f%%" % value)

app = QApplication(sys.argv)
form = None
form = Form()
if form is not None:
    form.show()
    app.exec_()




'''
vat = TaxRate()
# data= vat.rate()
vat.rateChanged.connect(rateChanged)
vat.setRate(17.5)
# No change will occur (new rate is the same)
vat.setRate(8.5)
# A change will occur (new rate is different)
'''