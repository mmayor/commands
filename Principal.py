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

        self.label = QLabel("Quality Control")

        layout = QGridLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowTitle("Quality Control")
        self.setFixedWidth(400)
        self.setFixedHeight(200)


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()