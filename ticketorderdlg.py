#!/usr/bin/env python3
# Copyright (c) 2008-9 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import random
# from PyQt4.QtCore import (QDate, Qt, SIGNAL, pyqtSignature)
# from PyQt4.QtGui import (QApplication, QDialog, QDialogButtonBox)
from PyQt5.QtWidgets import *
# import urllib2
import urllib.request
import ui_findandreplacedlg
import re
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QDate
import ui_ticketorderdlg1


'''
if random.choice((1, 2)) == 1:
    import ui_ticketorderdlg1 as ui_ticketorderdlg
else:
    import ui_ticketorderdlg2 as ui_ticketorderdlg
'''

class TicketOrderDlg(QDialog,  ui_ticketorderdlg1.Ui_TicketOrderDlg):

    def __init__(self, parent=None):
        super(TicketOrderDlg, self).__init__(parent)
        self.setupUi(self)
        today = QDate.currentDate()
        self.whenDateTimeEdit.setDateRange(today.addDays(1),
                                           today.addYears(1))
        self.updateUi()
        self.customerLineEdit.setFocus()


    @pyqtSlot("QString")
    def on_customerLineEdit_textEdited(self, text):
        self.updateUi()


    @pyqtSlot("double")
    def on_priceSpinBox_valueChanged(self, value):
        self.updateUi()


    @pyqtSlot("int")
    def on_quantitySpinBox_valueChanged(self, value):
        self.updateUi()


    def updateUi(self):
        amount = (self.priceSpinBox.value() *
                  self.quantitySpinBox.value())
        enable = not self.customerLineEdit.text() == '' and amount
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)
        self.amountLabel.setText("$ {0:.2f}".format(amount))


    def result(self):
        when = self.whenDateTimeEdit.dateTime().toPyDateTime()
        return (str(self.customerLineEdit.text()), when, self.priceSpinBox.value(), self.quantitySpinBox.value())


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = TicketOrderDlg()
    form.show()
    app.exec_()
    print(form.result())

