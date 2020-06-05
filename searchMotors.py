from random import randrange

from PyQt5.QtCore import *
# from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request
import ui_scan
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
# import cam
import classCam
from threading import Thread
import threading
import ui_searchMotors
import classConsulta

class MiDataGraphic(QDialog, ui_searchMotors.Ui_SearchMotors):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setupUi(self)
        # self.tableWidget.clicked.connect(lambda: self.printData())


    def printData(self):
        print('pepe')

    @pyqtSlot()
    def on_tableWidget_cellClicked(self):

        print('pepe')
        pass


    def graficarFunction(self):
        meses= ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGS', 'SEP', 'OCT', 'NOV', 'DIC']
        X = [i for i in range(12)]
        Y1 = [1 / (x + 5) for x in X]
        data= []
        for i in range(12):
            data.append(randrange(100))

class SearchMotors(QDialog, ui_searchMotors.Ui_SearchMotors, classConsulta.ConsultaMotors):

    def __init__(self, parent=None):

        super(SearchMotors, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        self.__data= ''
        self.__found= ''
        self.tempData= None
        # self.tableWidget.setEnabled()
        # self.dataTemp= MiDataGraphic()
        self.tableWidget.cellClicked.connect(self.printData)
        # self.tableWidget.clicked.connect(lambda:  self.printData())

    def num(self, s):
        try:
            return int(s)
        except ValueError:
            return float(s)



    def printData(self, a, b):
        print('DATA', a, b)
        print(self.tableWidget.item(a,b).text())
        

        for data in self.tempData[0]['testTemp']:

            if str(data['id']) == self.tableWidget.item(a, b).text():
                # print('Corriente: ', data['corriente'])
                # print('Ruido: ', data['ruido'])
                # print('Vibracion: ', data['vibracion'])
                # print('Voltaje: ', data['voltaje'])

                dataCorriente= data['corriente'].split(',')
                dataVoltaje = data['voltaje'].split(',')
                dataResistencia = data['ruido'].split(',')
                dataFrecuencia = data['vibracion'].split(',')



        dataCorriente= [self.num(i)  for i in dataCorriente]
        dataVoltaje = [self.num(i) for i in dataVoltaje]
        dataResistencia = [self.num(i) for i in dataResistencia]
        dataFrecuencia = [self.num(i) for i in dataFrecuencia]



        X= [i for i in range(1, 11)]
        self.widget.canvas.ax1.clear()
        self.widget.canvas.ax1.set_xlim(1, 10)
        # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
        self.widget.canvas.ax1.set_xticks(X)
        self.widget.canvas.ax1.set_xticklabels(X, fontsize=8, color='red')
        self.widget.canvas.ax1.yaxis.set_tick_params(labelsize= 8, labelcolor='blue')
        self.widget.canvas.ax1.grid(axis= 'both', color='0.7', linestyle='-')
        self.widget.canvas.ax1.set_title('Corriente')
        self.widget.canvas.ax1.plot(X, dataCorriente, color='black')

        X = [i for i in range(1, 11)]
        self.widget.canvas.ax2.clear()
        self.widget.canvas.ax2.set_xlim(1, 10)
        # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
        self.widget.canvas.ax2.set_xticks(X)
        self.widget.canvas.ax2.set_xticklabels(X, fontsize=8, color='red')
        self.widget.canvas.ax2.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
        self.widget.canvas.ax2.grid(axis='both', color='0.7', linestyle='-')
        self.widget.canvas.ax2.set_title('Voltaje')
        self.widget.canvas.ax2.plot(X, dataVoltaje, color='blue')

        X = [i for i in range(1, 11)]
        self.widget.canvas.ax3.clear()
        self.widget.canvas.ax3.set_xlim(1, 10)
        # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
        self.widget.canvas.ax3.set_xticks(X)
        self.widget.canvas.ax3.set_xticklabels(X, fontsize=8, color='red')
        self.widget.canvas.ax3.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
        self.widget.canvas.ax3.grid(axis='both', color='0.7', linestyle='-')
        self.widget.canvas.ax3.set_title('Resistencia')
        self.widget.canvas.ax3.plot(X, dataResistencia, color='green')

        X = [i for i in range(len(dataFrecuencia))]
        self.widget.canvas.ax4.clear()
        self.widget.canvas.ax4.set_xlim(1, 10)
        # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
        self.widget.canvas.ax4.set_xticks(X)
        self.widget.canvas.ax4.set_xticklabels(X, fontsize=8, color='red')
        self.widget.canvas.ax4.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
        self.widget.canvas.ax4.grid(axis='both', color='0.7', linestyle='-')
        self.widget.canvas.ax4.set_title('Frecuencia')
        self.widget.canvas.ax4.plot(X, dataFrecuencia, color='red')

        self.widget.canvas.draw()

        # self.widget.canvas.draw()


    @pyqtSlot()
    def on_pushButton_clicked(self):

        self.pushButton.setEnabled(False)
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.pushButton.repaint()
        self.tableWidget.repaint()
        temConsulta= classConsulta.ConsultaMotors()

        if self.radioButton.isChecked():

            self.tempData= temConsulta.consultaMotors(self.lineEdit.text())
            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['Id', 'Serial', 'Status'])
            row = 0
            col = 0
            count = 0
            for data in self.tempData:
                count = count + 1
                # print(data['id'], data['serial'], data['status'])
                self.tableWidget.setRowCount(count)
                item_tabla = QTableWidgetItem(str(data['id']))
                item_tabla.setTextAlignment(0x0084)
                self.tableWidget.setItem(row, col, item_tabla)
                item_tabla = QTableWidgetItem(str(data['serial']))
                item_tabla.setTextAlignment(0x0084)
                self.tableWidget.setItem(row, col + 1, item_tabla)
                item_tabla = QTableWidgetItem(str(data['status']))
                item_tabla.setTextAlignment(0x0084)
                self.tableWidget.setItem(row, col + 2, item_tabla)
                row = row + 1

        else:
            self.tempData= temConsulta.consultaTests(self.lineEdit.text())
            self.tableWidget.setColumnCount(3)
            if self.lineEdit.text() == '':

                self.tableWidget.setHorizontalHeaderLabels(['Id', 'Motor ID', 'Status'])
                row = 0
                col = 0
                count = 0
                # print(tempData)
                for data in self.tempData:
                    count = count + 1
                    self.tableWidget.setRowCount(count)
                    item_tabla = QTableWidgetItem(str(data['id']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['motor_id']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 1, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['status']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 2, item_tabla)
                    row = row + 1
            else:
                self.tableWidget.setColumnCount(6)
                self.tableWidget.setHorizontalHeaderLabels(['Id TEST',  'Serial Motor', 'Status GEN', 'Id Motor',   'Status Test', 'Date'])
                row = 0
                col = 0
                count = 0
                print(self.tempData[0])

                for data in self.tempData[0]['testTemp']:
                    count= count+1
                    self.tableWidget.setRowCount(count)
                    item_tabla = QTableWidgetItem(str(self.tempData[0]['id']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col+3, item_tabla)
                    item_tabla = QTableWidgetItem(str(self.tempData[0]['serial']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col+1, item_tabla)
                    item_tabla = QTableWidgetItem(str(self.tempData[0]['status']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col+2, item_tabla)
                    item_tabla= QTableWidgetItem(str(data['id']))
                    item_tabla.setTextAlignment(0x0084)
                    # item_tabla.setBackground()
                    self.tableWidget.setItem(row, col, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['status']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 4, item_tabla)
                    item_tabla = QTableWidgetItem(str(data['dateNew']))
                    item_tabla.setTextAlignment(0x0084)
                    self.tableWidget.setItem(row, col + 5, item_tabla)
                    row = row + 1


        # self.tableWidget.repaint()
        self.pushButton.setEnabled(True)

    def updateUi(self):
        pass
'''
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = SearchMotors()
    form.show()
    app.exec_()
    
'''