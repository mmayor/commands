import time

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
import os
import pygame
import testMotor
import classInsertar


class Scanning(QThread, object):

    def __init__(self):
        super().__init__()
        # self._url = url
        # self._filename = filename
        # self.tempScan = classCam.ScanComplete()
        self.__tempSTR = None
        self.__dadaEND= None

    # self.signal = pyqtSignal(QStringListModel)
    # signalChange = pyqtSignal()
        self.tempScan = classCam.ScanComplete()


    def __del__(self):
        print("DELETE OBJ")

    def getDataEND(self):
        return self.__dadaEND

    def setTempSTR(self, dataStr):
        self.__tempSTR = dataStr

    def getTempSTR(self):
        return self.__tempSTR

    def emitChange(self):

        self.signalChange.emit()


    def chequingScanning(self):

        while not self.tempScan.getFoundFlag():
            # print(tempScan.getData())

            QCoreApplication.processEvents()
            self.__tempSTR = ''
            for ele in self.tempScan.getData():
                if ele == '':
                    ele = 'Scanning... \n'
                self.__tempSTR += ele

            self.emitChange()
            print("self.__tempSTR")



    def run(self):

        # d = threading.Thread(target=self.tempScan.camIdMotor, name='daemon')
        # d.start()
        self.__dadaEND= self.tempScan.camIdMotor()
        # self.chequingScanning()
        '''
        while not self.tempScan.getFoundFlag():
            # print(tempScan.getData())

            self.__tempSTR= ''
            for ele in self.tempScan.getData():
                if ele == '':
                    ele = 'Scanning... \n'
                self.__tempSTR += ele

    
            self.emitChange()
            print("self.__tempSTR")
        
        '''

class ScanDlg(QDialog, ui_scan.Ui_Dialog, classCam.ScanComplete):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ScanDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.tempScan = classCam.ScanComplete()
        self.__data= ''
        self.__found= ''
        # self.textEdit.setText('')
        self.label_4.setVisible(False)
        self.dockWidget.setEnabled(False)
        self.dockWidget.setWidget(QTextEdit())
        self.pushButton.pressed.connect(self.pushButtonScan)
        self.__testTEmp= None


        # self.lineEdit_2.textEdited.connect()
        # self.li
        # self.pu

        # self.updateUi('')
        self.__list= QTextEdit()
        # self.show()

    @pyqtSlot()
    def on_pushButton_3_clicked(self):

        # print("PEPE")
        self.scanning.tempScan.setStopScan(True)
        self.pushButton.setText('StartScan')
        self.pushButton.setEnabled(True)
        self.pushButton.repaint()
        self.scanning.quit()
        self.scanning.exit()
        print("ID_OBJ", id(self.scanning))
        time.sleep(1)

        # self.scanning.terminate()
        tempReturn= self.scanning.isFinished()
        print("RETURN", tempReturn)
        print("DATA_END", self.scanning.getDataEND())

        # self.scanning.terminate()
        # self.scanning.tempScan.s



    def chequingScanning(self):
        while not self.scanning.tempScan.getFoundFlag():
            # print(tempScan.getData())
            QCoreApplication.processEvents()
            tempStr= ''
            for ele in self.scanning.tempScan.getData():
                if ele == '':
                    ele = 'Scanning... \n'
                tempStr += ele

                # print(tempStr)

            self.updateUi(tempStr)
            # self.textEdit.repaint()
            self.dockWidget.repaint()
            # self.updateUi('pepe')


    # @pyqtSlot()
    def pushButtonScan(self):


        self.__list.clear()
        self.lineEdit_2.clear()
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton.setText('Scanning...')
        self.label.setText('SCANNING')
        self.label_4.setVisible(False)
        self.scanning= Scanning()
        # self.scanning.finished.connect(self.finishScan)
        # self.scanning.signalChange.connect(self.updateDataScan)
        self.scanning.start()
        # if self.scanning:
        # self.chequingScanning()
        # self.scanning.chequingScanning()
        # self.scanning.chequingScanning()
        # self.updateUi('BEGIN SCANNING...')
        # d= threading.Thread(target=self.scanning.chequingScanning(), name='daemon')
        # d.start()

        while not self.scanning.tempScan.getFoundFlag() and not self.scanning.tempScan.getStopScan():

            # print(tempScan.getData())
            QCoreApplication.processEvents()
            tempStr= ''
            for ele in self.scanning.tempScan.getData():
                if ele == '':
                    ele = 'Scanning... \n'
                tempStr += ele

                # print(tempStr)

            self.updateUi(tempStr)
            # self.textEdit.repaint()
            self.dockWidget.repaint()
            # self.updateUi('pepe')

        if self.scanning.tempScan.getFoundFlag():

            pygame.mixer.init()
            sound = pygame.mixer.Sound('scanner-beep-checkout.ogg')
            sound.play()
            self.__found= self.scanning.tempScan.getFound()
            self.updateUi('<p style="color:#07870F"><b>ID DETECTED: "'+self.scanning.tempScan.getFound()+'"<b></p>')
            self.lineEdit_2.setText(self.scanning.tempScan.getFound())
            self.label_4.setVisible(True)
            self.label_4.repaint()

            # self.pushButton.repaint()self.pushButton.setEnabled(True)
            # print('Value Found: ', tempScan.getFound())
            self.__testTemp= testMotor.TestMotor()
            h = threading.Thread(target=self.__testTemp.Principal, name='testing')
            # tempDataMotor= testTemp.ranDOM()
            h.start()

            while h.isAlive():

                # print(testTemp.getVoltaje())
                # tempDstring=
                self.label.setText(str(self.__testTemp.getPower() + " "  +  self.__testTemp.getChangeVoltaje()) + " " + str(self.__testTemp.getCyclos()))
                self.label.repaint()
                print(self.__testTemp.getPower())
                dataVoltaje = [self.num(i) for i in self.__testTemp.getVoltaje()]
                dataCorriente = [self.num(i) for i in self.__testTemp.getCorriente()]
                dataResistencia = [self.num(i) for i in self.__testTemp.getResistencia()]
                dataFrecuencia = [self.num(i) for i in self.__testTemp.getFrecuencia()]

                X = [i for i in range(len(dataCorriente))]
                self.widget.canvas.ax1.clear()
                self.widget.canvas.ax1.set_xlim(1, 10)
                # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
                self.widget.canvas.ax1.set_xticks(X)
                self.widget.canvas.ax1.set_xticklabels(X, fontsize=8, color='red')
                self.widget.canvas.ax1.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
                self.widget.canvas.ax1.grid(axis='both', color='0.7', linestyle='-')
                self.widget.canvas.ax1.set_title('Corriente')
                self.widget.canvas.ax1.plot(X, dataCorriente, color='black')

                X = [i for i in range(len(dataVoltaje))]
                self.widget.canvas.ax2.clear()
                self.widget.canvas.ax2.set_xlim(1, 10)
                # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
                self.widget.canvas.ax2.set_xticks(X)
                self.widget.canvas.ax2.set_xticklabels(X, fontsize=8, color='red')
                self.widget.canvas.ax2.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
                self.widget.canvas.ax2.grid(axis='both', color='0.7', linestyle='-')
                self.widget.canvas.ax2.set_title('Voltaje')
                self.widget.canvas.ax2.plot(X, dataVoltaje, color='blue')

                X = [i for i in range(len(dataResistencia))]
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
                self.widget.repaint()

            self.label.setText('FINISHED...')
            self.pushButton.setText('StartScan')
            self.pushButton.setEnabled(True)
            self.pushButton.repaint()
            self.pushButton_2.setEnabled((True))
            self.pushButton_2.repaint()

        self.label.setText('SAVING DATA WAIT..')
        tempCode= self.insertData()
        if tempCode == 200:
            self.label.setText('SAVED OK')
        else:
            self.label.setText('Something went wrong saving BAD...')

    @pyqtSlot()
    def updateDataScan(self):

        print("PEPE")
        self.updateUi(self.scanning.getTempSTR())
        # self.textEdit.repaint()
        self.dockWidget.repaint()
        # self.updateUi('pepe')
        pass

    def insertData(self):
        dataTemp= []
        dataTemp.append(self.__testTemp.getVoltaje())
        dataTemp.append(self.__testTemp.getFrecuencia())
        dataTemp.append(self.__testTemp.getCorriente())
        dataTemp.append(self.__testTemp.getResistencia())
        dataTemp.append(self.__testTemp.getFrecuenciaTeorica())
        print("ENCONTRADO", self.__found)
        tempInsert= classInsertar.ConsultaInsert('MIguel', self.__found, dataTemp)
        tempInsert.insertData()
        return tempInsert.getStatusCode()

    def finishScan(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound('scanner-beep-checkout.ogg')
        sound.play()
        self.updateUi('<p style="color:#07870F"><b>ID DETECTED: "' + self.scanning.tempScan.getFound() + '"<b></p>')
        self.lineEdit_2.setText(self.scanning.tempScan.getFound())
        self.label_4.setVisible(True)
        self.label_4.repaint()

        # self.pushButton.repaint()self.pushButton.setEnabled(True)
        # print('Value Found: ', tempScan.getFound())
        testTemp = testMotor.TestMotor()
        h = threading.Thread(target=testTemp.Principal, name='testing')
        # tempDataMotor= testTemp.ranDOM()
        h.start()

        while h.isAlive():
            # print(testTemp.getVoltaje())
            # tempDstring=
            self.label.setText(
                str(testTemp.getPower() + " " + testTemp.getChangeVoltaje()) + " " + str(testTemp.getCyclos()))
            self.label.repaint()
            print(testTemp.getPower())
            dataVoltaje = [self.num(i) for i in testTemp.getVoltaje()]
            dataCorriente = [self.num(i) for i in testTemp.getCorriente()]
            dataResistencia = [self.num(i) for i in testTemp.getResistencia()]

            X = [i for i in range(len(dataCorriente))]
            self.widget.canvas.ax1.clear()
            self.widget.canvas.ax1.set_xlim(1, 10)
            # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
            self.widget.canvas.ax1.set_xticks(X)
            self.widget.canvas.ax1.set_xticklabels(X, fontsize=8, color='red')
            self.widget.canvas.ax1.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
            self.widget.canvas.ax1.grid(axis='both', color='0.7', linestyle='-')
            self.widget.canvas.ax1.set_title('Corriente')
            self.widget.canvas.ax1.plot(X, dataCorriente, color='black')

            X = [i for i in range(len(dataVoltaje))]
            self.widget.canvas.ax2.clear()
            self.widget.canvas.ax2.set_xlim(1, 10)
            # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
            self.widget.canvas.ax2.set_xticks(X)
            self.widget.canvas.ax2.set_xticklabels(X, fontsize=8, color='red')
            self.widget.canvas.ax2.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
            self.widget.canvas.ax2.grid(axis='both', color='0.7', linestyle='-')
            self.widget.canvas.ax2.set_title('Voltaje')
            self.widget.canvas.ax2.plot(X, dataVoltaje, color='blue')

            X = [i for i in range(len(dataResistencia))]
            self.widget.canvas.ax3.clear()
            self.widget.canvas.ax3.set_xlim(1, 10)
            # self.widget.canvas.ax.set_ylim(0, max(int(dataCorriente))*1.1)
            self.widget.canvas.ax3.set_xticks(X)
            self.widget.canvas.ax3.set_xticklabels(X, fontsize=8, color='red')
            self.widget.canvas.ax3.yaxis.set_tick_params(labelsize=8, labelcolor='blue')
            self.widget.canvas.ax3.grid(axis='both', color='0.7', linestyle='-')
            self.widget.canvas.ax3.set_title('Resistencia')
            self.widget.canvas.ax3.plot(X, dataResistencia, color='green')

            self.widget.canvas.draw()
            self.widget.repaint()

        self.label.setText('FINISHED...')
        self.pushButton.setText('StartScan')
        self.pushButton.setEnabled(True)
        self.pushButton.repaint()
        self.pushButton_2.setEnabled((True))
        self.pushButton_2.repaint()


    def cube(self, x):
        return x*x*x

    def mapping(self):
        print(map(self.cube, range(1, 10)))



    def num(self, s):
        try:
            return int(s)
        except ValueError:
            return float(s)

    def updateUi(self, text):

        # self.textEdit.append(text)
        self.__index= 10
        self.__list.append(text)
        self.dockWidget.setWidget(self.__list)


'''
    def main(self):
        import sys

        app = QApplication(sys.argv)
        form = ScanDlg()
        form.show()
        app.exec_()
'''
'''
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = ScanDlg()
    form.show()
    app.exec_()
    # print(form.result())
'''