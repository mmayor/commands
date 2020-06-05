import sys
from random import random, randrange
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QDialog, QWidget
# from PyQt5.QtGui import QWi
from ui_graficNew import *
import matplotlib.ticker as ticker

class MiFormulario(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.ui= Ui_Graphic()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.graficarFunction)


    def graficarFunction(self):
        meses= ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGS', 'SEP', 'OCT', 'NOV', 'DIC']
        X = [i for i in range(12)]
        Y1 = [1 / (x + 5) for x in X]
        data= []
        for i in range(12):
            data.append(randrange(100))


        self.ui.widget.canvas.ax.clear()
        self.ui.widget.canvas.ax.axis([-0.5, 11.5, 0, max(data)+10])
        self.ui.widget.canvas.ax.xaxis.set_major_locator(ticker.FixedLocator((X)))
        self.ui.widget.canvas.ax.xaxis.set_major_formatter(ticker.FixedFormatter((meses)))
        self.ui.widget.canvas.ax.bar(X, data, align='center', width=1, color='r', linewidth=0, edgecolor='black')





        self.ui.widget.canvas.draw()

        # tempGrafic.canvas.ax.plot(X, Y1)
        # tempGrafic.show()






