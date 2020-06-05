# import bluetooth

from bluepy import btle
# import serial
import time

# testing


class TestMotor(object):

    def __init__(self):

        super().__init__()
        # self.__text = str(text)
        self.__index = 0
        self.__data= ''
        self.__found= ''
        self.__foundFlag= False
        self.__powerMotor= 'POWER OFF'
        self.__voltaje= []
        self.__corriente = []
        self.__resistencia= []
        self.__frecuencia = []
        self.__frecuenciaTeorica = []
        self.__status= None
        self.__changeVoltaje= ''
        self.__ciclos= ''

        # self.textEdit.setText(self.__text
        # self.updateUi()


## FUNCTIONS

    def getCyclos(self):
        return self.__ciclos

    def getChangeVoltaje(self):
        return self.__changeVoltaje

    def getPower(self):
        return self.__powerMotor

    def getStatus(self):
        return self.__status

    def getFrecuenciaTeorica(self):
        return self.__frecuenciaTeorica

    def getFrecuencia(self):
        return self.__frecuencia
    
    def getResistencia(self):
        return self.__resistencia

    def getVoltaje(self):
        return self.__voltaje

    def getCorriente(self):
        return self.__corriente


    def envioCadenaBytes(self, number):
        bufTemp = bytearray(2)
        bufTemp = hex(number)
        bufNew = (number).to_bytes(2, byteorder='little')
        buf = self.to_bytes(bufTemp)
        # print(bufNew)
        return bufNew


    def envioCadenaBytesNew(self, number):
        bufTemp = bytearray(1)
        bufTemp = hex(number)
        bufNew = (number).to_bytes(1, byteorder='big')
        buf = self.to_bytes(bufTemp)
        print(bufNew)
        return bufNew


    def to_bytes(self, bytes_or_str):
        if isinstance(bytes_or_str, str):
            value = bytes_or_str.encode('utf-8')

        else:
            value = bytes_or_str
        return value


    def to_str(self, bytes_or_str):
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')

        else:
            value = bytes_or_str
        return value


    def changeRadio(self, value):
        print("Connecting...")
        print('Value: ', value)

        # HOBBER C3:A6:5B:E9:2B:84
        # ROBERT RADIO
        # dev = btle.Peripheral("34:81:F4:06:E2:90") ##ROBERTO 80:1F:12:B6:E6:E6 ## ADRIANO
        try:
            dev = btle.Peripheral("C3:A6:5B:E9:2B:84",
                                  addrType=btle.ADDR_TYPE_RANDOM)  ##ROBERTO 80:1F:12:B6:E6:E6 ## ADRIANO
        except EOFError as e:
            print('ERROR: ', e)

            # temServices = dev.getServices()

        # dev = btle.Peripheral("D8:80:39:FE:2F:44") ##AVRTAG DE:6E:23:90:AC:F9 ## RADIO:::34:81:F4:06:E2:90
        # dev = btle.Peripheral("F6:A5:49:E1:07:07", addrType=btle.ADDR_TYPE_RANDOM) ##AVRTAG DE:6E:23:90:AC:F9 ##
        # dev = btle.Peripheral("CB:B0:2C:E9:E5:76", addrType=btle.ADDR_TYPE_RANDOM) ##AVRTAG DE:6E:23:90:AC:F9 ## CB:B0:2C:E9:E5:76 NORDI
        # dev = btle.Peripheral("DE:6E:23:90:AC:F9", addrType=btle.ADDR_TYPE_RANDOM) ##NEW

        print("Services...")

        try:

            for svc in dev.services:
                print(svc)

        except ValueError as e:
            print(e)

        print('characteristics')

        try:
            characteristics = dev.getCharacteristics()


        except:
            print('error')

        print(characteristics)

        hexNew = self.envioCadenaBytesNew(int(value))
        # dev.writeCharacteristic(51, hexNew, withResponse=True)

        # for i in range(6) :

        # hexNew = envioCadenaBytesNew(1)
        # dev.writeCharacteristic(16, hexNew, withResponse=True)

        # notiTemp= dev.waitForNotifications(10)
        # print(notiTemp)

        # time.sleep(10)
        # notiTemp= dev.handleNotification(16)
        # print(notiTemp)
        # hexNew = envioCadenaBytesNew(2)
        # dev.writeCharacteristic(16, hexNew, withResponse=True)

        for k in characteristics:

            handleNew = k.getHandle()
            uuidNew = k.uuid

            print(handleNew)
            print(uuidNew)

            try:
                redCH = dev.readCharacteristic(handleNew)
                print(redCH)
            except:
                pass

        #     i = i+1

        dev.disconnect()
        return 'OK INSERT'


    def cadenaBytes(self, bytesCadena):
        # ser = serial.Serial('COM14', 115200)
        # ser.flushInput()
        buf = bytearray(16)

        rx_raw = bytesCadena
        print("raw:  ")
        print(rx_raw)
        print(bytesCadena)
        print("\n")

        mystring = ""
        myInteger = ''
        h = 0
        temp0 = ''
        temp1 = ''
        temp2 = ''
        temp3Corriente = ''
        temp4Corriente = ''
        tempCorrienteFinalNew = 0

        for c in rx_raw:

            if h == 0:
                temp0 = hex(c)
            if h == 1:
                temp1 = hex(c)

            if h == 2:
                temp3Corriente = hex(c)
            if h == 3:
                temp4Corriente = hex(c)

            mystring = mystring + " " + hex(c)
            myInteger = myInteger + "__" + str(int(hex(c), 16))
            if h == 4:
                temp2 = str(int(hex(c), 16))

            h = h + 1
        print("hexed: ")
        print(mystring)
        # print("\n")
        # b'\xf0\xf1\xf2'.hex()
        # print(temp2)
        tempVoltaje = temp1 + temp0

        if temp3Corriente is not "":
            tempCorriente = temp4Corriente + temp3Corriente
            tempCorrienteFinal = tempCorriente.replace('0x', '')
            tempCorrienteFinalNew = int(tempCorrienteFinal, 16)

        # print("Corriente:::::::::")
        # print(tempCorriente)
        tempVoltajeFinal = tempVoltaje.replace('0x', '')

        tempVoltajeFinalNew = int(tempVoltajeFinal, 16)

        tempFrecuenciaFinalNew = temp2
        # tempVoltaje =   tempVoltaje.hex()
        # tempVoltaje = int(tempVoltaje)
        return mystring, myInteger, tempVoltajeFinalNew, temp2, tempCorrienteFinalNew

    ## SIMULAR RANDOM GOOD-BAD
    def ranDOM(self):
        tempCorriente = []
        tempVoltaje = []
        tempVoltajeOther = []
        tempFrecuenciaOther = []
        tempFrecuenciaTeoricaOther = []
        tempCorrienteOther = []
        tempResistenciaOther = []
        tempRuido = []
        tempVibracion = []
        stCorriente = ""
        stVoltaje = ""
        stRuido = ""
        stVibracion = ""

        tempALL = self.Principal()
        tempVoltajeOther = tempALL[0]
        tempFrecuenciaOther = tempALL[1]
        tempCorrienteOther = tempALL[2]
        tempResistenciaOther = tempALL[3]
        tempFrecuenciaTeoricaOther = tempALL[4]

        if (float(tempCorrienteOther[6]) >= 0.01 and float(tempCorrienteOther[6]) <= 0.03) or (
                float(tempCorrienteOther[7]) >= 0.01 and float(tempCorrienteOther[7]) <= 0.03):
            statusCorriente = "GOOD"
        else:
            statusCorriente = "BAD"

        if (float(tempResistenciaOther[6]) >= 4.0 and float(tempResistenciaOther[6]) <= 5.0) or (
                float(tempResistenciaOther[7]) >= 4.0 and float(tempResistenciaOther[7]) <= 5.0):
            statusRuido = "GOOD"
        else:
            statusRuido = "BAD"


        statusVoltaje = "GOOD"
        # statusRuido = validarStatus(tempRuido, 1)
        statusVibracion = "GOOD"
        statusVibracionTeorica = "GOOD"

        if statusVoltaje == "GOOD" and statusCorriente == "GOOD" \
                and statusRuido == "GOOD" and statusVibracion == "GOOD":
            status = "GOOD"
        else:
            status = "BAD"

        stCorriente = ','.join(tempCorriente)
        stVoltaje = ','.join(tempVoltaje)
        stRuido = ','.join(tempRuido)
        stVibracion = ','.join(tempVibracion)

        stVoltajeOther = ','.join(tempVoltajeOther)
        stFrecuenciaOther = ','.join(tempFrecuenciaOther)
        stFrecuenciaTeoricaOther = ','.join(tempFrecuenciaTeoricaOther)
        stCorrienteOther = ','.join(tempCorrienteOther)
        stResistenciaOther = ','.join(tempResistenciaOther)

        print(tempCorrienteOther)
        print(tempALL)

        return tempCorriente, tempVoltaje, tempVibracion, tempVoltaje, status, stCorrienteOther, stVoltajeOther, \
               stResistenciaOther, stFrecuenciaOther, status, statusCorriente, statusVoltaje, statusRuido, \
               statusVibracion, stFrecuenciaTeoricaOther, statusVibracionTeorica


    def Principal(self):
        print("Connecting...")
        dev = btle.Peripheral("C3:A6:5B:E9:2B:84", addrType=btle.ADDR_TYPE_RANDOM)
        print('Characteristics.....................')
        characteristics = dev.getCharacteristics()
        tempUUIDVoltaje = '4851'  # VOLTAJE
        tempUUIDPower = '4853'  # POWER
        tempUUIDALL = '4854'  # ALL
        valueUUIDVoltaje = 0
        valueUUIDPower = 0
        valueUUIDALL = 0
        valueUUIDVoltajeFinal = 0
        valueUUIDPowerFinal = 0
        valueUUIDALLFinal = 0

        for k in characteristics:

            handleNew = k.getHandle()
            uuidNew = k.uuid
            # print(handleNew)
            # print(uuidNew)
            strNewTemp = str(uuidNew)
            valueUUIDVoltaje = strNewTemp.find(tempUUIDVoltaje, 0, 9)
            valueUUIDPower = strNewTemp.find(tempUUIDPower, 0, 9)
            valueUUIDALL = strNewTemp.find(tempUUIDALL, 0, 9)

            if (valueUUIDVoltaje != -1):
                valueUUIDVoltajeFinal = handleNew
                # print("FIND VOLTAJE")

            if (valueUUIDPower != -1):
                valueUUIDPowerFinal = handleNew
                self.__powerMotor = self.to_str(dev.readCharacteristic(valueUUIDPowerFinal))
                # print('Power', valueUUIDPower)
                # print('Power_final', valueUUIDPowerFinal)
                print("Encendido...")
                hexNewEncendido = self.envioCadenaBytesNew(1)
                dev.writeCharacteristic(valueUUIDPowerFinal, hexNewEncendido, withResponse=True)
                self.__powerMotor= 'POWER ON'


                # print('TEMP_ENCENDIDO', tempEncendido)
                # print("FIND POWER")

            if (valueUUIDALL != -1):
                valueUUIDALLFinal = handleNew
                # print(ALL)

        resultFinalVoltaje = []
        resultFinalFrecuencia = []
        resultFinalFrecuenciaTeorica = []
        resultFinalCorriente = []
        resultFinalResistencia = []
        value = 5000
        hexNew = self.envioCadenaBytes(value)
        ## INIT VOLYAJE 5000
        dev.writeCharacteristic(valueUUIDVoltajeFinal, hexNew, withResponse=True)

        for i in range(1, 11):
            # print("CICLO: " + str(i))
            self.__ciclos = 'CYCLE: ', str(i)
            temp = ''

            value = 6000 + (i * 500)
            # value = 9000
            hexNew = self.envioCadenaBytes(value)
            dev.writeCharacteristic(valueUUIDVoltajeFinal, hexNew, withResponse=True)
            self.__changeVoltaje= 'Voltaje: ' + str(value)
            time.sleep(1.5)

            tempRedCH = 0
            valueNewNew = [0, 0, 0, 0, 0]
            valueNewNewCorr = 0
            valueNewNewVolt = 0
            valueNewNewFre = 0
            for j in range(0, 2):
                print("SUB_CICLO: " + str(j))

                tempRedCH = dev.readCharacteristic(valueUUIDALLFinal)
                # print("HEX...")
                # print(tempRedCH)
                valueTemp = self.cadenaBytes(tempRedCH)
                time.sleep(0.5)

                print("READ TESTING ......")
                # print(tempRedCH)
                print(int(valueTemp[2]))

                voltajeTemp = 0

                while int(valueTemp[2]) > 15000 or int(valueTemp[2]) < 5000:
                    tempRedCH = dev.readCharacteristic(valueUUIDALLFinal)
                    # print("HEX...")
                    # print(tempRedCH)
                    valueTemp = self.cadenaBytes(tempRedCH)
                    time.sleep(0.5)

                valueNewNew[2] = valueNewNew[2] + int(valueTemp[2])
                valueNewNew[3] = valueNewNew[3] + int(valueTemp[3])
                valueNewNew[4] = valueNewNew[4] + int(valueTemp[4])

            valueNewNew[2] = round(valueNewNew[2] / 2)
            valueNewNew[3] = round(valueNewNew[3] / 2)
            valueNewNew[4] = round(valueNewNew[4] / 2)

            valueNew = valueNewNew
            # print(valueNew)

            resultFinalVoltaje.append(str(valueNew[2]))
            self.__voltaje.append(str(valueNew[2]))
            resultFinalFrecuencia.append(str(valueNew[3]))
            self.__frecuencia.append(str(valueNew[3]))
            resultFinalCorriente.append(str(round(valueNew[4] / 100, 2)))
            self.__corriente.append(str(round(valueNew[4] / 100, 2)))
            if valueNew[4] == 0:
                resultFinalResistencia.append(str(0))
                self.__resistencia.append(str(0))
                resultFinalFrecuenciaTeorica.append(str(0))
                self.__frecuenciaTeorica.append(str(0))

            else:

                resultFinalResistencia.append(str(round(valueNew[2] / (valueNew[4]) / 1000, 2)))
                self.__resistencia.append(str(round(valueNew[2] / (valueNew[4]) / 1000, 2)))
                resultFinalFrecuenciaTeorica.append(
                    str(round(valueNew[4] * (valueNew[2] / (valueNew[4]) / 1000) / 1.21, 2)))
            print("CORRIENTE....")
            # print(valueNew)

        # print(resultFinalVoltaje)
        # print(resultFinalCorriente)
        # print(resultFinalResistencia)
        # print(resultFinalFrecuencia)
        # print(resultFinalFrecuenciaTeorica)

        value = 5000
        hexNew = self.envioCadenaBytes(value)
        dev.writeCharacteristic(valueUUIDVoltajeFinal, hexNew, withResponse=True)
        hexNew = self.envioCadenaBytesNew(2)
        dev.writeCharacteristic(valueUUIDPowerFinal, hexNew, withResponse=True)
        self.__powerMotor= 'POWER OFF'

        dev.disconnect()

        return resultFinalVoltaje, resultFinalFrecuencia, resultFinalCorriente, resultFinalResistencia, resultFinalFrecuenciaTeorica


# Principal()


# changeRadio(10)


