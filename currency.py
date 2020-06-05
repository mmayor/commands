import sys
import time
from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request

from pyparsing import unicode


class Form(QDialog):
     def __init__(self, parent=None):
         super(Form, self).__init__(parent)
         date = self.getdata()
         rates = sorted(self.rates.keys())
         dateLabel = QLabel(date)
         self.fromComboBox = QComboBox()
         self.fromComboBox.addItems(rates)
         self.fromSpinBox = QDoubleSpinBox()
         self.fromSpinBox.setRange(0.01, 10000000.00)
         self.fromSpinBox.setValue(1.00)
         self.toComboBox = QComboBox()
         self.toComboBox.addItems(rates)
         self.toLabel = QLabel("1.00")

         grid = QGridLayout()
         grid.addWidget(dateLabel, 0, 0)
         grid.addWidget(self.fromComboBox, 1, 0)
         grid.addWidget(self.fromSpinBox, 1, 1)
         grid.addWidget(self.toComboBox, 2, 0)
         grid.addWidget(self.toLabel, 2, 1)
         self.setLayout(grid)

         # self.connect(self.fromComboBox, SIGNAL("currentIndexChanged(int)"), self.updateUi)
         # self.connect(self.toComboBox,   SIGNAL("currentIndexChanged(int)"), self.updateUi)
         # self.connect(self.fromSpinBox,  SIGNAL("valueChanged(double)"), self.updateUi)

         self.fromComboBox.currentIndexChanged.connect(self.updateUi)
         self.toComboBox.currentIndexChanged.connect(self.updateUi)
         self.fromSpinBox.valueChanged.connect(self.updateUi)

         self.setWindowTitle("Currency")

     def updateUi(self):
         to = unicode(self.toComboBox.currentText())
         from_ = unicode(self.fromComboBox.currentText())
         amount = (self.rates[from_] / self.rates[to]) * self.fromSpinBox.value()
         self.toLabel.setText("%0.2f" % amount)

     def getdata(self):  # Idea taken from the Python Cookbook
         self.rates = {}
         try:
             date = "Unknown"
             fh = urllib.request.urlopen("https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/csv?start_date=2017-01-03")
             print(fh.read())
             #  print(type(fh.read))
             # fh= urllib.("https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/csv?start_date=2017-01-03")


             openFile= open('FX_RATES_DAILY-sd-2017-01-03.csv', 'r')

             for line in openFile:

                if not line or line.startswith("#") or line.startswith("Closing "):

                     continue


                fields = line.split(",")

                # print('Line: ', line)
                # print('Campos: ', fields)


                if line.startswith('"date"'):
                    dateTemp = fields


                if line.startswith('"2020-04-13"'):

                     date = fields[0]
                     # print('DATE: ', date)
                     lineTemp= line

                     try:
                         # fields = line.split(",")

                         for field in fields:
                             pass
                         try:

                             count= 0
                             for temp in fields:

                                field= temp.replace('"', "")
                                if field not in '2020-04-13' and field not in '' and field not in '\n':
                                    # print("Type Field", type(field))
                                    # print('FIELD: ', field)


                                    count= count+1
                                    value = float(field)
                                    self.rates[unicode(dateTemp[count])] = value


                         except ValueError as g:
                             print('G', g)

                     except ValueError as f:
                         print('F', f)
                         pass


                '''

                else:
                    try:
                        print('Fields -1: ', value)
                        value = float(fields[-1])
                        
                        self.rates[unicode(fields[0])] = value
                    except ValueError as f:
                        print(f)
                        pass
                 '''

             return "Exchange Rates Date: " + date
         except Exception as e:
            return "Failed to download:\n%s" % e


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()