import socket
import struct
import numpy as np
# from PyQt5 import QtGui
from PySide2.QtWidgets import QPushButton
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import json
import time
from sys import exit

# Widget condiguration
app = QtGui.QApplication([])
w = QtGui.QWidget()
layout = QtGui.QGridLayout()
# button1= QPushButton('One')
# layout.addWidget(button1)
w.setLayout(layout)
w.setWindowTitle("Procesado de señal de audio")
w.setFixedSize(1400, 1000)
p = w.palette()
p.setColor(w.backgroundRole(), pg.mkColor('k'))
w.setPalette(p)
a_np_array = np.array([])
temp = np.array([])
pg.setConfigOptions(antialias=True)
dataExample = np.loadtxt('data1.csv', delimiter=',')
dataExampleNew= np.loadtxt('dataExamp.csv', delimiter=',')
dataFrec = np.loadtxt('data.csv', delimiter=',')



class AudioServer():
    HOST = '127.0.0.1'

    def __init__(self, port, layout, w):
        self.port = port

        # Initialize socket connections
        self.socketCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketCon.bind((self.HOST, self.port))
        print("Socket creado:", self.socketCon.getsockname)
        self.handshaked = None
        # Initialize Widget layout
        self.lay = layout
        self.labelFps = QtGui.QLabel()
        self.labelFps.setText('Frames per second: 0')
        self.labelFps.setStyleSheet('color: yellow')
        self.plt1 = pg.PlotWidget()
        self.plt2 = pg.PlotWidget()
        self.plt3 = pg.PlotWidget()
        self.lay.addWidget(self.labelFps, 0, 0)
        self.lay.addWidget(self.plt1, 1, 0)
        self.lay.addWidget(self.plt2, 1, 1)
        self.lay.addWidget(self.plt3, 2, 0)

        self.fps = 0
        self.timeAnt = 0
        self.timeTcpAnt = 0
        self.w = w


    def listen(self):

        self.socketCon.listen(1)
        print("Escoltant connexions...")
        self.conn, self.addr = self.socketCon.accept()
        print("Connexió acceptada de: ", self.conn.getpeername())
        print(type(self.conn))

    def readblob(self, size):
        buffer = ""
        while len(buffer) != size:
            print("longitud buffer: ", len(buffer))
            ret = self.conn.recv(size - len(buffer))
            print(ret)
            if not ret:
                raise Exception("Socket closed")
            buffer += ret
        return buffer

    def myreceive(self, size):
        chunks = []
        bytes_recd = 0
        while bytes_recd < size:
            chunk = self.conn.recv(min(size - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

    def readlong(self):
        size = struct.calcsize("L")
        print(size)
        data = self.myreceive(size)
        print(data)
        print(struct.unpack("L", data))
        return struct.unpack("L", data)

    def checkParam(self, jdata):
        if 'N' in jdata:
            self.N = jdata['N']
        else:
            raise Exception("Incorrect param N in handshake")
        if 'rate' in jdata:
            self.rate = jdata['rate']
        else:
            raise Exception("Incorrect param rate in handshake")
        if 'T' in jdata:
            self.T = jdata['T']
        else:
            raise Exception("Incorrect param T in handshake")

        return True

    def handshake(self):
        longitud = self.readlong()
        print("Longitud....", longitud[0])
        if longitud:
            print("Fent handshake")
            print("Longitud header: ", longitud[0])
            print("LLegint params...")
            data = self.myreceive(longitud[0])
            jdata = json.loads(data.decode('utf-8'))
            print(jdata)
            if self.checkParam(jdata):

                # Enviamos ACK
                ack = 'ACK'
                long = struct.pack("L", len(ack))
                self.conn.sendall(long)
                self.conn.sendall(bytes(ack, 'utf-8'))
                print("Handshake finished correctly")
                self.handshaked = True

            else:
                self.handshaked = False
        else:
            print("No handshake")
            self.handshaked = False

    def initPlot(self):

        self.plt1.setYRange(-20000, 20000)
        self.plt1.getPlotItem().setTitle(title="Representación temporal")
        self.plt1.getAxis('bottom').setLabel('Tiempo')
        self.plt1.getAxis('left').setLabel('Nivel')
        self.plt2.setYRange(0, 2000)
        self.plt2.getPlotItem().setTitle(title="Representación frecuencial (FFT)")
        self.plt2.getAxis('bottom').setLabel('Frecuencia', units='Hz')
        self.plt2.getAxis('bottom').enableAutoSIPrefix(enable=True)
        self.plt2.getAxis('left').setLabel('Nivel')
        self.plt3.setYRange(0, 400)
        self.plt3.getPlotItem().setTitle('Mathematical study of a sound analyzer spectrum in Engines')
        self.plt3.getAxis('bottom').setLabel('Frecuencia', units='Hz')
        # self.plt3.getAxis('bottom').enableAutoSIPrefix(enable=True)
        self.plt3.getAxis('left').setLabel('Nivel')
        # legend = self.plt3.getPlotItem.setlegend(loc='upper right', shadow=True, fontsize='small')
        # Put a nicer background color on the legend.
        # legend.get_frame().set_facecolor('C0')
        self.w.show()

    def ajustarARRAY(self, dataArray, dataArrayValue, dataArrayValue1):
        dataFinal = np.array([])
        dataFinalValue = np.array([])
        for i in range(23):
            dataFinal = np.append(dataFinal, i)

        dataFinalValue = np.array([])
        dataFinalValue1 = np.array([])
        # dataFinalValue2 = np.array([])


        for i in range(23):
            count = 0
            sum = 0
            sum1 = 0


            for j in range(2048):
                # print(dataArray[j], j)

                if (dataArray[j] < ((i + 1) * (1000))):
                    count = count + 1
                    sum = sum + dataArrayValue[j]
                    sum1 = sum1 + dataArrayValue1[j]


            dataFinalValue = np.append(dataFinalValue, sum / count)
            dataFinalValue1 = np.append(dataFinalValue1, sum1 / count)


        return dataFinal, dataFinalValue, dataFinalValue1



    def receive(self):


        global  temp
        # print(a_np_array)
        timeTcpAct = time.time()
        print("Temps entre crides receive Tcp: ", (timeTcpAct - self.timeTcpAnt) * 1000)
        self.timeTcpAnt = timeTcpAct
        data = self.conn.recv(2 * self.N)
        # print(data)
        print("Temps per rebre packets: ", (time.time() - timeTcpAct) * 1000)
        if not data:
            print("no data")
        else:
            # Señal temporal

            count = len(data) / 2
            format = "%dh" % (count)
            shorts = struct.unpack(format, data)
            # print(len(shorts))
            npshorts = np.asarray(shorts)
            xaxis_t = np.linspace(0.0, self.N * self.T, self.N)
            # print(xaxis_t)
            self.plt1.plot(xaxis_t, npshorts, pen=(255, 0, 0), clear=True)

            # Frecuencia
            timeFact = time.time()
            print('FRECUENCIA ')
            freq = np.fft.rfft(npshorts)
            # freqNew = np.fft.irfft(freq)
            for f in freq:
               # print(f.real)
               # print(abs(f))
              pass


            tempArrayAXI= []
            tempArrayFRE= []
            tempArrayMIX = [[]]
            print("Durada FFT: ", (time.time() - timeFact) * 1000)
            print('SELFT: ')
            tempT= 1.0 / (2.0 * self.T)
            tempN= self.N // 2
            x2 = np.linspace(0, 10, 8)
            # print(tempT, tempN, x2)
            xaxis_f = np.linspace(0.0, 1.0 / (2.0 * self.T), self.N // 2)    # 0 to 22050 with 2048 values   (eje x)
            
            # print('xaxisF: ')
            # print(xaxis_f)

            n = int(len(npshorts) / 2)
            tempOther = np.abs(freq[range(n)])
            tempY = (2.0 / self.N) * np.abs(freq[range(n)])

            print(len(temp))
            temp= np.concatenate([temp, tempY])


            self.plt2.plot(xaxis_f, (2.0 / self.N) * np.abs(freq[range(n)]), pen=(255, 0, 0), clear=True)

            # Label fps
            timeAct = time.time()
            fps = 1 / (timeAct - self.timeAnt)
            self.timeAnt = timeAct
            self.labelFps.setText('Frames per second: {:2.1f}'.format(fps))

            plt3Data, plt3Data1, plt3DataY= self.ajustarARRAY(dataFrec, dataExampleNew, tempY)
            ## DESVIACION RESPECTO MEDIA
            mediAritDatay= np.mean(plt3DataY)
            mediAritData1 = np.mean(plt3Data1)
            print("MEDIA_DATAy", mediAritDatay)
            print("MEDIA_DATA1", mediAritData1)

            ## PLT3
            ## Ajustar ARRAY
            # print('DATA PLT3: ', plt3Data, plt3Data1, plt3DataY)
            self.plt3.plot(plt3Data, plt3DataY, pen=('r'), symbol='o', symbolPen='r', symbolBrush=0.2, clear=True)
            self.plt3.plot(plt3Data, plt3Data1, pen=('g'),  symbol='x', symbolPen='b', symbolBrush=0.2)



        # np.savetxt('data1.csv', temp, delimiter=',')


    def printCVS(self):
        global temp
        np.savetxt('data1.csv', temp, delimiter=',')

    def gethandshaked(self):
        return self.handshaked

myServer = AudioServer(50007, layout, w)

myServer.listen()
myServer.handshake()
print('had: ', myServer.gethandshaked())
if myServer.handshaked:
    myServer.initPlot()
    timer = QtCore.QTimer()
    timer.timeout.connect(myServer.receive)
    timer.start(0)
else:
    print("No  esta possible el handshake")
    exit(0)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
