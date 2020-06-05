import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from matplotlib.figure import  Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class Mp1Canvas11(FigureCanvas):
    def __init__(self):
        self.fig= Figure()
        self.ax= self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)


class Mp1Canvas22(FigureCanvas):
    def __init__(self):
        self.fig= Figure(facecolor='0.94')
        self.ax1= self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        FigureCanvas.__init__(self, self.fig)

class MatplotlibWidget111(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas= Mp1Canvas11()
        self.vb1= QVBoxLayout()
        self.vb1.addWidget(self.canvas)
        self.toolbar= NavigationToolbar(self.canvas, self)
        self.vb1.addWidget(self.toolbar)
        self.setLayout(self.vb1)

class MatplotlibWidget111_sin(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = Mp1Canvas11()
        self.vb1 = QVBoxLayout()
        self.vb1.addWidget(self.canvas)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        # self.vb1.addWidget(self.toolbar)
        self.setLayout(self.vb1)

class MatplotlibWidget22(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = Mp1Canvas22()
        self.vb1 = QVBoxLayout()
        self.vb1.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vb1.addWidget(self.toolbar)
        self.setLayout(self.vb1)

class MatplotlibWidget22_sin(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = Mp1Canvas22()
        self.vb1 = QVBoxLayout()
        self.vb1.addWidget(self.canvas)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        # self.vb1.addWidget(self.toolbar)
        self.setLayout(self.vb1)





    '''
    def grafico(self):
        X= list(range(50))
        Y1= [1/(x+5) for x in X]
        self.canvas.ax.plot(X, Y1)
    '''



        
