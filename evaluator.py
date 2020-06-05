from __future__ import division
from math import *
import sys
import time
from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PySide2.QtCore import SIGNAL
from numpy import unicode


class Form(QDialog):
     def __init__(self, parent=None):
         super(Form, self).__init__(parent)
         self.browser = QTextBrowser()
         self.button=QPushButton("Click")
         self.button1 = QPushButton("Clear")
         self.lineedit = QLineEdit("Type an expression and press Enter")
         self.lineedit.selectAll()
         layout = QVBoxLayout()
         layout.addWidget(self.browser)
         layout.addWidget(self.lineedit)
         # layout.addWidget(self.button)
         # layout.addWidget(self.button1)
         self.setLayout(layout)
         self.lineedit.setFocus()
         # self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)
         # self.button.clicked.connect(self.updateUi)
         self.lineedit.returnPressed.connect(self.updateUi)
         # self.button1.clicked.connect(self.clear)
         self.setWindowTitle("Calculate")


     def clear(self):
         self.lineedit.clear()
         self.browser.clear()

     def updateUi(self):
         try:
             text = unicode(self.lineedit.text())
             self.browser.append("%s = <b>%s</b>" % (text, eval(text)))
             self.lineedit.clear()
         except:
            self.browser.append("<font color=red>%s is invalid!</font>" % (text))




app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()