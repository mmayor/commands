# -*- coding: utf-8 -*-

import threading, time, serial, struct, argparse, ezslib


class TextBinConsole():
    """ CONFIGURATION """

    displayPackets = True
    displayOutputStream = True
    displayInputStream = True
    dummyByteCount = 0
    platform = 'psoc4proc_ble'

    """ HELPER FUNCTIONS/VARIABLES """

    ser = serial.Serial()
    api = ezslib.API()

    def appRxPacketHandler(self, packet):
        if self.displayPackets:
            t = time.time()
            print("%.03f: <=RX" % t, packet)
            if packet.origin == ezslib.Packet.EZS_ORIGIN_BINARY:
                print("%.03f: <=RX [%s] (%s)" % (
                t, " ".join(['%02X' % b for b in packet.binaryByteArray]), repr(bytes(packet.binaryByteArray))))
            elif packet.origin == ezslib.Packet.EZS_ORIGIN_TEXT:
                print("%.03f: <=RX [%s] (%s)" % (
                t, " ".join(['%02X' % ord(b) for b in packet.textString]), repr(packet.textString)))
            print("")
        # if packet.type == ezslib.Packet.EZS_PACKET_TYPE_EVENT and packet.group == 0x02 and packet.method == 0x02:
        #    raise ezslib.SystemErrorException("EZ-Serial system error 0x%04X" % packet.payload["error"], packet)

    def appTxPacketHandler(self, packet):
        if self.displayPackets:
            print("%.03f: TX=>" % time.time(), packet)

    def appHardwareOutput(self, data):
        for x in range(self.dummyByteCount):
            data.insert(0, 0x00)
        if self.displayOutputStream:
            print("%.03f: TX=> [%s] (%s)" % (time.time(), " ".join(['%02X' % b for b in data]), repr(bytes(data))))
            print("")
        return (self.ser.write(data), ezslib.API.EZS_OUTPUT_RESULT_DATA_WRITTEN)

    def appHardwareInput(self, timeout):
        self.ser.timeout = timeout
        inBytes = self.ser.read()
        if len(inBytes) > 0:
            if self.displayInputStream:
                if type(inBytes) is str:
                    print(
                        "RX<=[%02X] ('%s'), lastParseResult=%s" % (ord(inBytes[0]), inBytes, self.api.lastParseResult))
                else:
                    print("RX<=[%02X] ('%s'), lastParseResult=%s" % (inBytes[0], inBytes, self.api.lastParseResult))
            return (inBytes[0], ezslib.API.EZS_INPUT_RESULT_BYTE_READ)
        elif timeout == 0:
            return (None, ezslib.API.EZS_INPUT_RESULT_NO_DATA)
        else:
            raise ezslib.TimeoutException("No data available")

    def __init__(self, port, baud):
        self.ser.port = port
        self.ser.baudrate = baud
        self.api.rxPacketHandler = self.appRxPacketHandler
        self.api.txPacketHandler = self.appTxPacketHandler
        self.api.hardwareOutput = self.appHardwareOutput
        self.api.hardwareInput = self.appHardwareInput
        self.api.defaults.rxtimeout = 1.5
        self.api.reset()

        # open and flush the serial port
        try:
            # Python 3.5
            if not self.ser.is_open: self.ser.open()
        except AttributeError as e:
            # Python 2.7
            if not self.ser.isOpen(): self.ser.open()
        self.ser.flushInput()
        self.ser.flushOutput()


class SerialInputThread(threading.Thread):
    def setConsole(self, console):
        self.console = console

    def run(self):
        while True:
            try:
                # self.console.api.waitPacket(platform="psoc4proc_ble", rxtimeout=None)
                # self.console.api.waitPacket(platform="wiced_ble", rxtimeout=None)
                self.console.api.waitPacket(platform=console.platform, rxtimeout=None)
            except ezslib.ParseException as e:
                print("ParseException:", e)
                self.console.api.reset()
            except ezslib.ProtocolException as e:
                print("ProtocolException:", e)
                self.console.api.reset()
            except ezslib.PacketException as e:
                print("PacketException:", e)
                self.console.api.reset()
            except struct.error as e:
                print("struct.error:", e)


if __name__ == '__main__':
    # parse all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Serial port", required=True)
    parser.add_argument("-b", "--baud", help="Baud rate", default=115200, type=int)
    parser.add_argument("-s", "--supress", help="Suppression list, e.g. 'input output packets' for all", nargs="+")
    parser.add_argument("-l", "--platform", help="Platform, e.g. 'psoc4proc_ble' or 'wiced_ble' or 'wiced_20706'",
                        default='psoc4proc_ble')
    args = parser.parse_args()

    if args.supress == None: args.supress = []
    console = TextBinConsole(args.port, args.baud)
    console.displayInputStream = False if 'input' in args.supress else True
    console.displayOutputStream = False if 'output' in args.supress else True
    console.displayPackets = False if 'packets' in args.supress else True
    console.platform = args.platform

    t1 = SerialInputThread()
    t1.setConsole(console)
    t1.daemon = True
    t1.start()

    while True:
        s = input()
        if s == "":
            console.api.reset()
            print("[API PARSER STATE RESET]")
        else:
            packet = ezslib.Packet()
            try:
                packet.buildOutgoingFromTextBuffer("%s\r\n" % s, platform=args.platform)
                console.api.sendPacket(packet, apiformat=ezslib.Packet.EZS_API_FORMAT_BINARY)
            except ezslib.ProtocolException as e:
                print("ProtocolException:", e)
            except ezslib.PacketException as e:
                print("PacketException:", e)
            except ValueError as e:
                print("ValueError:", e)

