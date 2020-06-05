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

        principalLabel = QLabel("Principal:")
        self.principalSpinBox = QDoubleSpinBox()
        self.principalSpinBox.setRange(1, 1000000000)
        self.principalSpinBox.setValue(1000)
        self.principalSpinBox.setPrefix("$ ")
        rateLabel = QLabel("Rate:")
        self.rateSpinBox = QDoubleSpinBox()
        self.rateSpinBox.setRange(1, 100)
        self.rateSpinBox.setValue(5)
        self.rateSpinBox.setSuffix(" %")
        yearsLabel = QLabel("Years:")
        self.yearsComboBox = QComboBox()
        self.yearsComboBox.addItem("1 year")
        self.yearsComboBox.addItems(["{0} years".format(x) for x in range(2, 26)])
        amountLabel = QLabel("Amount")
        self.amountLabel = QLabel()

        grid = QGridLayout()
        grid.addWidget(principalLabel, 0, 0)
        grid.addWidget(self.principalSpinBox, 0, 1)
        grid.addWidget(rateLabel, 1, 0)
        grid.addWidget(self.rateSpinBox, 1, 1)
        grid.addWidget(yearsLabel, 2, 0)
        grid.addWidget(self.yearsComboBox, 2, 1)
        grid.addWidget(amountLabel, 3, 0)
        grid.addWidget(self.amountLabel, 3, 1)
        self.setLayout(grid)

        self.principalSpinBox.valueChanged.connect(self.updateUi)
        self.rateSpinBox.valueChanged.connect(self.updateUi)
        self.yearsComboBox.currentIndexChanged.connect(self.updateUi)

        self.setWindowTitle("Interest")
        self.updateUi()

    def updateUi(self):
        """Calculates compound interest"""
        principal = self.principalSpinBox.value()
        rate = self.rateSpinBox.value()
        years = self.yearsComboBox.currentIndex() + 1
        amount = principal * ((1 + (rate / 100.0)) ** years)
        self.amountLabel.setText("$ {0:.2f}".format(amount))


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()