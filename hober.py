from bluepy.btle import Scanner, DefaultDelegate
from bluepy import btle
import subprocess
import sys
import json

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)

    def scanHover(self):

        tempDevices = []
        tempCharacterist= []
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(10.0)
        # devices = subprocess.call(['sudo', scanner.scan(10.0)])

        for dev in devices:
            print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))

            for (adtype, desc, value) in dev.getScanData():
                # print(" Descipcion:  %s Value:  = %s  " % (desc, value))
                if (desc == 'Complete Local Name' and value == 'HOVER') or (dev.addr=='20:70:6A:20:01:54'):
                    tempCharacterist= []
                    try:
                        devConnect = btle.Peripheral(dev.addr, addrType=btle.ADDR_TYPE_RANDOM) ##AVRTAG DE:6E:23:90:AC:F9 ##
                        # devConnect = btle.Peripheral(dev.addr) ##AVRTAG DE:6E:23:90:AC:F9 ##
                        print('!!! CONNECTED')
                        print('!!!!Charact')
                        characteristics = devConnect.getCharacteristics()
                        for k in characteristics:
                            handleNew= k.getHandle()
                            uuidNew = k.uuid
                            tempCharacterist.append({
                            'handle': handleNew,
                            'uuid': uuidNew
                            })
                            # print(handleNew)
                            # print(uuidNew)

                        print('!!! DESCONNECT')
                        devConnect.disconnect()

                    except:

                        print("??? I cant not connect: Error... ")

                    tempDevices.append({

                            'addr': dev.addr,
                            'addrtype': dev.addrType,
                            'nivel': dev.rssi,
                            'name': value,
                            # 'characteristics': tempCharacterist

                            })

        #print(tempDevices)
        try:
            with open('data.json', 'w')  as file:
                json.dump(tempDevices, file)
                print("OK PRINTER")
        except ValueError as e:
            print(e)
        return tempDevices

# scanHover()