import functools
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

        button1 = QPushButton("One")
        button2 = QPushButton("Two")
        button3 = QPushButton("Three")
        button4 = QPushButton("Four")
        button5 = QPushButton("Five")
        self.label = QLabel("Click a button...")

        layout = QHBoxLayout()
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(button4)
        layout.addWidget(button5)
        layout.addStretch()
        layout.addWidget(self.label)
        self.setLayout(layout)

        button1.clicked.connect(self.one)
        self.button2callback = functools.partial(self.anyButton, "Two")
        button2.clicked.connect(self.button2callback)
        self.button3callback = lambda whoTemp='Three' : self.anyButton('Three')
        button3.clicked.connect(self.button3callback)
        button4.clicked.connect(self.clicked)
        button5.clicked.connect(self.clicked)

        self.setWindowTitle("Connections")


    def one(self):
        self.label.setText("You clicked button 'One'")


    def anyButton(self, who):
        self.label.setText("You clicked button '{0}'".format(who))


    def clicked(self):
        button = self.sender()
        if button is None or not isinstance(button, QPushButton):
            return
        self.label.setText("You clicked button '{0}'".format(
                           button.text()))


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()