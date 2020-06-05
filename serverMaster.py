import json
import struct

import numpy as np
from PyQt5 import QtCore
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
# import classCam
from threading import Thread
import threading
import ui_server
import classServer
import time
import socket


class ServerListenDlg(QDialog, ui_server.Ui_ServerListen, classServer.AudioServer):
    found = pyqtSignal(int)
    notfound = pyqtSignal()


    def __init__(self, parent=None):

        super(ServerListenDlg, self).__init__(parent)
        # self.__text = str(text)
        self.__index = 0
        self.setupUi(self)
        # self.updateUi('')

    @pyqtSlot()
    def on_pushButton_clicked(self):

        myServer = classServer.AudioServer(50007)

        # d = threading.Thread(target=myServer.listen, name='daemon')
        # e = threading.Thread(target=myServer.handshake, name='daemonNew')
        # d.start()
        # e.start()
        myServer.listen()
        myServer.handshake()
        # self.textEdit.setText(str(myServer.getStatus()))
        # print('HAN: ', myServer.gethandshaked())
        if myServer.gethandshaked():
            # myServer.initPlot()
            timer = QtCore.QTimer()
            timer.timeout.connect(myServer.receive)
            timer.start(0)
        else:
            print("No ha esta possible el handshake")
            exit(0)

        pass
        


    def updateUi(self):
        pass


if __name__ == "__main__":
    import sys


    app = QApplication(sys.argv)
    form = ServerListenDlg()
    form.show()
    app.exec_()