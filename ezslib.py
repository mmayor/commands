# -*- coding: utf-8 -*-

import sys, re, struct


class dotdict(dict):
    # dot.notation access to dictionary attributes
    # http://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# custom cases for cleaner exception handling
class EZSerialException(Exception):
    pass


class TimeoutException(EZSerialException):
    pass


class ProtocolException(EZSerialException):
    pass


class PacketException(EZSerialException):
    def __init__(self, msg, packet):
        super(PacketException, self).__init__(msg)
        self.packet = packet


class ParseException(EZSerialException):
    pass


class Protocol():
    dataTypeMap = {
        "uint8": "B",
        "uint16": "H",
        "uint32": "L",
        "int8": "b",
        "int16": "h",
        "int32": "l",
        "macaddr": "6s",
        "uint8a": "B",
        "string": "B",
        "longuint8a": "H",
        "longstring": "H"
    }

    dataTypeWidth = {
        "uint8": 1,
        "uint16": 2,
        "uint32": 4,
        "int8": 1,
        "int16": 2,
        "int32": 4,
        "macaddr": 6,
        "uint8a": 1,
        "string": 1,
        "longuint8a": 2,
        "longstring": 2
    }

    commands = {
        "psoc4proc_ble": {
            1: {
                "name": "protocol",
                1: {"name": "set_parse_mode", "textname": "SPPM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                2: {"name": "get_parse_mode", "textname": "GPPM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
                3: {"name": "set_echo_mode", "textname": "SPEM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                4: {"name": "get_echo_mode", "textname": "GPEM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
            },
            2: {
                "name": "system",
                1: {"name": "ping", "textname": "/PING", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "runtime", "textname": "R"},
                                {"type": "uint16", "name": "fraction", "textname": "F"}]},
                2: {"name": "reboot", "textname": "/RBT", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "dump", "textname": "/DUMP", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3}],
                    "returns": [{"type": "uint16", "name": "length", "textname": "L"}]},
                4: {"name": "store_config", "textname": "/SCFG", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "factory_reset", "textname": "/RFAC", "flashopt": 0, "parameters": [], "returns": []},
                6: {"name": "query_firmware_version", "textname": "/QFV", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "app", "textname": "E"},
                                {"type": "uint32", "name": "stack", "textname": "S"},
                                {"type": "uint16", "name": "protocol", "textname": "P"},
                                {"type": "uint8", "name": "hardware", "textname": "H"}]},
                7: {"name": "query_unique_id", "textname": "/QUID", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "id", "textname": "U"}]},
                8: {"name": "query_random_number", "textname": "/QRND", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                9: {"name": "aes_encrypt", "textname": "/AESE", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                    "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                10: {"name": "aes_decrypt", "textname": "/AESD", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                     "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                11: {"name": "write_user_data", "textname": "/WUD", "flashopt": 0,
                     "parameters": [{"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 255},
                                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                     "maxlength": 32}], "returns": []},
                12: {"name": "read_user_data", "textname": "/RUD", "flashopt": 0,
                     "parameters": [{"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 255},
                                    {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 32}],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                13: {"name": "set_bluetooth_address", "textname": "SBA", "flashopt": 1,
                     "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}], "returns": []},
                14: {"name": "get_bluetooth_address", "textname": "GBA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                15: {"name": "set_eco_parameters", "textname": "SECO", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "trim", "textname": "T", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                16: {"name": "get_eco_parameters", "textname": "GECO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "trim", "textname": "T"}]},
                17: {"name": "set_wco_parameters", "textname": "SWCO", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "accuracy", "textname": "A", "minimum": 0, "maximum": 7}],
                     "returns": []},
                18: {"name": "get_wco_parameters", "textname": "GWCO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "accuracy", "textname": "A"}]},
                19: {"name": "set_sleep_parameters", "textname": "SSLP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "level", "textname": "L", "minimum": 0, "maximum": 2}],
                     "returns": []},
                20: {"name": "get_sleep_parameters", "textname": "GSLP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "level", "textname": "L"}]},
                21: {"name": "set_tx_power", "textname": "STXP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "power", "textname": "P", "minimum": 1, "maximum": 8}],
                     "returns": []},
                22: {"name": "get_tx_power", "textname": "GTXP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "power", "textname": "P"}]},
                23: {"name": "set_transport", "textname": "ST", "flashopt": 1, "parameters": [
                    {"type": "uint8", "name": "interface", "textname": "I", "minimum": 1, "maximum": 1}],
                     "returns": []},
                24: {"name": "get_transport", "textname": "GT", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "interface", "textname": "I"}]},
                25: {"name": "set_uart_parameters", "textname": "STU", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "baud", "textname": "B", "minimum": 300, "maximum": 2000000},
                    {"type": "uint8", "name": "autobaud", "textname": "A", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "autocorrect", "textname": "C", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "flow", "textname": "F", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "databits", "textname": "D", "minimum": 7, "maximum": 9},
                    {"type": "uint8", "name": "parity", "textname": "P", "minimum": 0, "maximum": 2},
                    {"type": "uint8", "name": "stopbits", "textname": "S", "minimum": 1, "maximum": 7}], "returns": []},
                26: {"name": "get_uart_parameters", "textname": "GTU", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "baud", "textname": "B"},
                                 {"type": "uint8", "name": "autobaud", "textname": "A"},
                                 {"type": "uint8", "name": "autocorrect", "textname": "C"},
                                 {"type": "uint8", "name": "flow", "textname": "F"},
                                 {"type": "uint8", "name": "databits", "textname": "D"},
                                 {"type": "uint8", "name": "parity", "textname": "P"},
                                 {"type": "uint8", "name": "stopbits", "textname": "S"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "reboot", "textname": "/RDFU", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2}],
                    "returns": []},
            },
            4: {
                "name": "gap",
                1: {"name": "connect", "textname": "/C", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                2: {"name": "cancel_connection", "textname": "/CX", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "update_conn_parameters", "textname": "/UCP", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200}],
                    "returns": []},
                4: {"name": "send_connupdate_response", "textname": "/CUR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 1}], "returns": []},
                5: {"name": "disconnect", "textname": "/DIS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                6: {"name": "add_whitelist_entry", "textname": "/WLA", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                7: {"name": "delete_whitelist_entry", "textname": "/WLD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                8: {"name": "start_adv", "textname": "/A", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 32,
                                    "maximum": 16384},
                                   {"type": "uint8", "name": "channels", "textname": "C", "minimum": 1, "maximum": 7},
                                   {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                    "maximum": 65535}], "returns": []},
                9: {"name": "stop_adv", "textname": "/AX", "flashopt": 0, "parameters": [], "returns": []},
                10: {"name": "start_scan", "textname": "/S", "flashopt": 0,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                11: {"name": "stop_scan", "textname": "/SX", "flashopt": 0, "parameters": [], "returns": []},
                12: {"name": "query_peer_address", "textname": "/QPA", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"},
                                 {"type": "uint8", "name": "address_type", "textname": "T"}]},
                13: {"name": "query_rssi", "textname": "/QSS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "int8", "name": "rssi", "textname": "R"}]},
                14: {"name": "query_whitelist", "textname": "/QWL", "flashopt": 0, "parameters": [],
                     "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                15: {"name": "set_device_name", "textname": "SDN", "flashopt": 1, "parameters": [
                    {"type": "string", "name": "name", "textname": "N", "minlength": 0, "maxlength": 64}],
                     "returns": []},
                16: {"name": "get_device_name", "textname": "GDN", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "string", "name": "name", "textname": "N"}]},
                17: {"name": "set_device_appearance", "textname": "SDA", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "appearance", "textname": "A", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                18: {"name": "get_device_appearance", "textname": "GDA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "appearance", "textname": "A"}]},
                19: {"name": "set_adv_data", "textname": "SAD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                20: {"name": "get_adv_data", "textname": "GAD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                21: {"name": "set_sr_data", "textname": "SSRD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                22: {"name": "get_sr_data", "textname": "GSRD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                23: {"name": "set_adv_parameters", "textname": "SAP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 32,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "channels", "textname": "C", "minimum": 1, "maximum": 7},
                                    {"type": "uint8", "name": "filter", "textname": "L", "minimum": 0, "maximum": 3},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}],
                     "returns": []},
                24: {"name": "get_adv_parameters", "textname": "GAP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "type", "textname": "T"},
                                 {"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint8", "name": "channels", "textname": "C"},
                                 {"type": "uint8", "name": "filter", "textname": "L"},
                                 {"type": "uint16", "name": "timeout", "textname": "O"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                25: {"name": "set_scan_parameters", "textname": "SSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                26: {"name": "get_scan_parameters", "textname": "GSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "window", "textname": "W"},
                                 {"type": "uint8", "name": "active", "textname": "A"},
                                 {"type": "uint8", "name": "filter", "textname": "F"},
                                 {"type": "uint8", "name": "nodupe", "textname": "D"},
                                 {"type": "uint16", "name": "timeout", "textname": "O"}]},
                27: {"name": "set_conn_parameters", "textname": "SCP", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 3200},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200},
                    {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                28: {"name": "get_conn_parameters", "textname": "GCP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                 {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                 {"type": "uint16", "name": "scan_interval", "textname": "V"},
                                 {"type": "uint16", "name": "scan_window", "textname": "W"},
                                 {"type": "uint16", "name": "scan_timeout", "textname": "M"}]},
            },
            5: {
                "name": "gatts",
                # UNIQUE TO PSOC4/PROC
                1: {"name": "create_attr", "textname": "/CAC", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "type", "textname": "T", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8", "name": "read_permissions", "textname": "R", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "write_permissions", "textname": "W", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "char_properties", "textname": "C", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint16", "name": "length", "textname": "L", "minimum": 0, "maximum": 512},
                                   {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0,
                                    "maxlength": 512}],
                    "returns": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                2: {"name": "delete_attr", "textname": "/CAD", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"},
                                {"type": "uint16", "name": "next_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                3: {"name": "validate_db", "textname": "/VGDB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint16", "name": "valid", "textname": "V"}]},
                4: {"name": "store_db", "textname": "/SGDB", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "dump_db", "textname": "/DGDB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "include_fixed", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                6: {"name": "discover_services", "textname": "/DLS", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                7: {"name": "discover_characteristics", "textname": "/DLC", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                8: {"name": "discover_descriptors", "textname": "/DLD", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "characteristic", "textname": "C", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                9: {"name": "read_handle", "textname": "/RLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "longuint8a", "name": "data", "textname": "D"}]},
                10: {"name": "write_handle", "textname": "/WLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                11: {"name": "notify_handle", "textname": "/NH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                12: {"name": "indicate_handle", "textname": "/IH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                13: {"name": "send_writereq_response", "textname": "/WRR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 255}],
                     "returns": []},
                14: {"name": "set_parameters", "textname": "SGSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                     "returns": []},
                15: {"name": "get_parameters", "textname": "GGSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_services", "textname": "/DRS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535}], "returns": []},
                2: {"name": "discover_characteristics", "textname": "/DRC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "discover_descriptors", "textname": "/DRD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "characteristic", "textname": "T", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "read_handle", "textname": "/RRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": []},
                5: {"name": "write_handle", "textname": "/WRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 2},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
                6: {"name": "confirm_indication", "textname": "/CI", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                7: {"name": "set_parameters", "textname": "SGCP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": []},
                8: {"name": "get_parameters", "textname": "GGCP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "query_bonds", "textname": "/QB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                2: {"name": "delete_bond", "textname": "/BD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                3: {"name": "pair", "textname": "/P", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "mode", "textname": "M", "minimum": 16, "maximum": 35},
                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1}], "returns": []},
                4: {"name": "query_random_address", "textname": "/QRA", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                5: {"name": "send_pairreq_response", "textname": "/PR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_passkeyreq_response", "textname": "/PE", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                    "returns": []},
                7: {"name": "generate_oob_data", "textname": "/GOOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8a", "name": "key", "textname": "K", "minlength": 16, "maxlength": 16}],
                    "returns": []},
                8: {"name": "clear_oob_data", "textname": "/COOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                9: {"name": "set_privacy_mode", "textname": "SPRV", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 1,
                                    "maximum": 65535}], "returns": []},
                10: {"name": "get_privacy_mode", "textname": "GPRV", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"}]},
                11: {"name": "set_security_parameters", "textname": "SSBP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 16, "maximum": 35},
                                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "io", "textname": "I", "minimum": 0, "maximum": 4},
                                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}],
                     "returns": []},
                12: {"name": "get_security_parameters", "textname": "GSBP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "bonding", "textname": "B"},
                                 {"type": "uint8", "name": "keysize", "textname": "K"},
                                 {"type": "uint8", "name": "pairprop", "textname": "P"},
                                 {"type": "uint8", "name": "io", "textname": "I"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                13: {"name": "set_fixed_passkey", "textname": "SFPK", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                     "returns": []},
                14: {"name": "get_fixed_passkey", "textname": "GFPK", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "passkey", "textname": "P"}]},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connect", "textname": "/LC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "remote", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "local", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "T", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                2: {"name": "disconnect", "textname": "/LDIS", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "register_psm", "textname": "/LRP", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "watermark", "textname": "W", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "send_connreq_response", "textname": "/LCR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "M", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                5: {"name": "send_credits", "textname": "/LSC", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_data", "textname": "/LD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
            },
            9: {
                "name": "gpio",
                1: {"name": "query_logic", "textname": "/QIOL", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                2: {"name": "query_adc", "textname": "/QADC", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 0},
                                   {"type": "uint8", "name": "reference", "textname": "R", "minimum": 0, "maximum": 0}],
                    "returns": [{"type": "uint16", "name": "value", "textname": "A"},
                                {"type": "uint32", "name": "uvolts", "textname": "U"}]},
                3: {"name": "set_function", "textname": "SIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "drive", "textname": "D", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                4: {"name": "get_function", "textname": "GIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "drive", "textname": "D"}]},
                5: {"name": "set_drive", "textname": "SIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "direction", "textname": "D", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_down", "textname": "W", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_up", "textname": "U", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "analog", "textname": "A", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                6: {"name": "get_drive", "textname": "GIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "direction", "textname": "D"},
                                {"type": "uint8", "name": "pulldrive_down", "textname": "W"},
                                {"type": "uint8", "name": "pulldrive_up", "textname": "U"},
                                {"type": "uint8", "name": "analog", "textname": "A"}]},
                7: {"name": "set_logic", "textname": "SIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "logic", "textname": "L", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                8: {"name": "get_logic", "textname": "GIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                9: {"name": "set_interrupt_mode", "textname": "SIOI", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "rising", "textname": "R", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "falling", "textname": "F", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                10: {"name": "get_interrupt_mode", "textname": "GIOI", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                     "returns": [{"type": "uint8", "name": "rising", "textname": "R"},
                                 {"type": "uint8", "name": "falling", "textname": "F"}]},
                11: {"name": "set_pwm_mode", "textname": "SPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "divider", "textname": "D", "minimum": 0, "maximum": 255},
                                    {"type": "uint8", "name": "prescaler", "textname": "S", "minimum": 0, "maximum": 7},
                                    {"type": "uint16", "name": "period", "textname": "P", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint16", "name": "compare", "textname": "C", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                12: {"name": "get_pwm_mode", "textname": "GPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3}],
                     "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                 {"type": "uint8", "name": "divider", "textname": "D"},
                                 {"type": "uint8", "name": "prescaler", "textname": "S"},
                                 {"type": "uint16", "name": "period", "textname": "P"},
                                 {"type": "uint16", "name": "compare", "textname": "C"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "check", "textname": ".CYSPPCHECK", "flashopt": 0, "parameters": [], "returns": []},
                2: {"name": "start", "textname": ".CYSPPSTART", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "set_parameters", "textname": ".CYSPPSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "role", "textname": "G", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint32", "name": "local_key", "textname": "L", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_key", "textname": "R", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_mask", "textname": "M", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint8", "name": "sleep_level", "textname": "P", "minimum": 0,
                                    "maximum": 2},
                                   {"type": "uint8", "name": "server_security", "textname": "S", "minimum": 0,
                                    "maximum": 3},
                                   {"type": "uint8", "name": "client_flags", "textname": "F", "minimum": 0,
                                    "maximum": 3}], "returns": []},
                4: {"name": "get_parameters", "textname": ".CYSPPGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "role", "textname": "G"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint32", "name": "local_key", "textname": "L"},
                                {"type": "uint32", "name": "remote_key", "textname": "R"},
                                {"type": "uint32", "name": "remote_mask", "textname": "M"},
                                {"type": "uint8", "name": "sleep_level", "textname": "P"},
                                {"type": "uint8", "name": "server_security", "textname": "S"},
                                {"type": "uint8", "name": "client_flags", "textname": "F"}]},
                5: {"name": "set_client_handles", "textname": ".CYSPPSH", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "data_value_handle", "textname": "A", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "data_cccd_handle", "textname": "B", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_value_handle", "textname": "C", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "get_client_handles", "textname": ".CYSPPGH", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint16", "name": "data_value_handle", "textname": "A"},
                                {"type": "uint16", "name": "data_cccd_handle", "textname": "B"},
                                {"type": "uint16", "name": "rxflow_value_handle", "textname": "C"},
                                {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D"}]},
                7: {"name": "set_packetization", "textname": ".CYSPPSK", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 4},
                                   {"type": "uint8", "name": "wait", "textname": "W", "minimum": 1, "maximum": 255},
                                   {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 128},
                                   {"type": "uint8", "name": "eop", "textname": "E", "minimum": 0, "maximum": 255}],
                    "returns": []},
                8: {"name": "get_packetization", "textname": ".CYSPPGK", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                {"type": "uint8", "name": "wait", "textname": "W"},
                                {"type": "uint8", "name": "length", "textname": "L"},
                                {"type": "uint8", "name": "eop", "textname": "E"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "set_parameters", "textname": ".CYCOMSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "hostout", "textname": "H", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "timeout", "textname": "T", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint8", "name": "safemode", "textname": "F", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "challenge", "textname": "C", "minimum": 0, "maximum": 3},
                                   {"type": "uint8", "name": "security", "textname": "S", "minimum": 0, "maximum": 3},
                                   {"type": "uint8a", "name": "secret", "textname": "R", "minlength": 0,
                                    "maxlength": 20}], "returns": []},
                2: {"name": "get_parameters", "textname": ".CYCOMGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "hostout", "textname": "H"},
                                {"type": "uint16", "name": "timeout", "textname": "T"},
                                {"type": "uint8", "name": "safemode", "textname": "F"},
                                {"type": "uint8", "name": "challenge", "textname": "C"},
                                {"type": "uint8", "name": "security", "textname": "S"},
                                {"type": "uint8a", "name": "secret", "textname": "R"}]},
            },
            12: {
                "name": "p_ibeacon",
                1: {"name": "set_parameters", "textname": ".IBSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "major", "textname": "J", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "minor", "textname": "N", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8a", "name": "uuid", "textname": "U", "minlength": 16,
                                    "maxlength": 16}], "returns": []},
                2: {"name": "get_parameters", "textname": ".IBGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint16", "name": "major", "textname": "J"},
                                {"type": "uint16", "name": "minor", "textname": "N"},
                                {"type": "uint8a", "name": "uuid", "textname": "U"}]},
            },
            13: {
                "name": "p_eddystone",
                1: {"name": "set_parameters", "textname": ".EDDYSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 255},
                                   {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                    "maxlength": 19}], "returns": []},
                2: {"name": "get_parameters", "textname": ".EDDYGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint8", "name": "type", "textname": "T"},
                                {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
        },
        "wiced_ble": {
            1: {
                "name": "protocol",
                1: {"name": "set_parse_mode", "textname": "SPPM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                2: {"name": "get_parse_mode", "textname": "GPPM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
                3: {"name": "set_echo_mode", "textname": "SPEM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                4: {"name": "get_echo_mode", "textname": "GPEM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
            },
            2: {
                "name": "system",
                1: {"name": "ping", "textname": "/PING", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "runtime", "textname": "R"},
                                {"type": "uint16", "name": "fraction", "textname": "F"}]},
                2: {"name": "reboot", "textname": "/RBT", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "dump", "textname": "/DUMP", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3}],
                    "returns": [{"type": "uint16", "name": "length", "textname": "L"}]},
                4: {"name": "store_config", "textname": "/SCFG", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "factory_reset", "textname": "/RFAC", "flashopt": 0, "parameters": [], "returns": []},
                6: {"name": "query_firmware_version", "textname": "/QFV", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "app", "textname": "E"},
                                {"type": "uint32", "name": "stack", "textname": "S"},
                                {"type": "uint16", "name": "protocol", "textname": "P"},
                                {"type": "uint8", "name": "hardware", "textname": "H"}]},
                7: {"name": "query_unique_id", "textname": "/QUID", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "id", "textname": "U"}]},
                8: {"name": "query_random_number", "textname": "/QRND", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                9: {"name": "aes_encrypt", "textname": "/AESE", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                    "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                10: {"name": "aes_decrypt", "textname": "/AESD", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                     "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                11: {"name": "write_user_data", "textname": "/WUD", "flashopt": 0,
                     "parameters": [{"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 255},
                                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                     "maxlength": 32}], "returns": []},
                12: {"name": "read_user_data", "textname": "/RUD", "flashopt": 0,
                     "parameters": [{"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 255},
                                    {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 32}],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                13: {"name": "set_bluetooth_address", "textname": "SBA", "flashopt": 1,
                     "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}], "returns": []},
                14: {"name": "get_bluetooth_address", "textname": "GBA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                15: {"name": "set_eco_parameters", "textname": "SECO", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "trim", "textname": "T", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                16: {"name": "get_eco_parameters", "textname": "GECO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "trim", "textname": "T"}]},
                17: {"name": "set_wco_parameters", "textname": "SWCO", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "accuracy", "textname": "A", "minimum": 0, "maximum": 7}],
                     "returns": []},
                18: {"name": "get_wco_parameters", "textname": "GWCO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "accuracy", "textname": "A"}]},
                19: {"name": "set_sleep_parameters", "textname": "SSLP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "level", "textname": "L", "minimum": 0, "maximum": 1}],
                     "returns": []},
                20: {"name": "get_sleep_parameters", "textname": "GSLP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "level", "textname": "L"}]},
                21: {"name": "set_tx_power", "textname": "STXP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "power", "textname": "P", "minimum": 1, "maximum": 8}],
                     "returns": []},
                22: {"name": "get_tx_power", "textname": "GTXP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "power", "textname": "P"}]},
                23: {"name": "set_transport", "textname": "ST", "flashopt": 1, "parameters": [
                    {"type": "uint8", "name": "interface", "textname": "I", "minimum": 1, "maximum": 1}],
                     "returns": []},
                24: {"name": "get_transport", "textname": "GT", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "interface", "textname": "I"}]},
                25: {"name": "set_uart_parameters", "textname": "STU", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "baud", "textname": "B", "minimum": 300, "maximum": 2000000},
                    {"type": "uint8", "name": "autobaud", "textname": "A", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "autocorrect", "textname": "C", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "flow", "textname": "F", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "databits", "textname": "D", "minimum": 7, "maximum": 9},
                    {"type": "uint8", "name": "parity", "textname": "P", "minimum": 0, "maximum": 2},
                    {"type": "uint8", "name": "stopbits", "textname": "S", "minimum": 1, "maximum": 7}], "returns": []},
                26: {"name": "get_uart_parameters", "textname": "GTU", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "baud", "textname": "B"},
                                 {"type": "uint8", "name": "autobaud", "textname": "A"},
                                 {"type": "uint8", "name": "autocorrect", "textname": "C"},
                                 {"type": "uint8", "name": "flow", "textname": "F"},
                                 {"type": "uint8", "name": "databits", "textname": "D"},
                                 {"type": "uint8", "name": "parity", "textname": "P"},
                                 {"type": "uint8", "name": "stopbits", "textname": "S"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "reboot", "textname": "/RDFU", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2}],
                    "returns": []},
            },
            4: {
                "name": "gap",
                1: {"name": "connect", "textname": "/C", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                2: {"name": "cancel_connection", "textname": "/CX", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "update_conn_parameters", "textname": "/UCP", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200}],
                    "returns": []},
                4: {"name": "send_connupdate_response", "textname": "/CUR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 1}], "returns": []},
                5: {"name": "disconnect", "textname": "/DIS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                6: {"name": "add_whitelist_entry", "textname": "/WLA", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                7: {"name": "delete_whitelist_entry", "textname": "/WLD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                8: {"name": "start_adv", "textname": "/A", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 32,
                                    "maximum": 16384},
                                   {"type": "uint8", "name": "channels", "textname": "C", "minimum": 1, "maximum": 7},
                                   {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                    "maximum": 65535}], "returns": []},
                9: {"name": "stop_adv", "textname": "/AX", "flashopt": 0, "parameters": [], "returns": []},
                10: {"name": "start_scan", "textname": "/S", "flashopt": 0,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                11: {"name": "stop_scan", "textname": "/SX", "flashopt": 0, "parameters": [], "returns": []},
                12: {"name": "query_peer_address", "textname": "/QPA", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"},
                                 {"type": "uint8", "name": "address_type", "textname": "T"}]},
                13: {"name": "query_rssi", "textname": "/QSS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "int8", "name": "rssi", "textname": "R"}]},
                14: {"name": "query_whitelist", "textname": "/QWL", "flashopt": 0, "parameters": [],
                     "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                15: {"name": "set_device_name", "textname": "SDN", "flashopt": 1, "parameters": [
                    {"type": "string", "name": "name", "textname": "N", "minlength": 0, "maxlength": 64}],
                     "returns": []},
                16: {"name": "get_device_name", "textname": "GDN", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "string", "name": "name", "textname": "N"}]},
                17: {"name": "set_device_appearance", "textname": "SDA", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "appearance", "textname": "A", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                18: {"name": "get_device_appearance", "textname": "GDA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "appearance", "textname": "A"}]},
                19: {"name": "set_adv_data", "textname": "SAD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                20: {"name": "get_adv_data", "textname": "GAD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                21: {"name": "set_sr_data", "textname": "SSRD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                22: {"name": "get_sr_data", "textname": "GSRD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                23: {"name": "set_adv_parameters", "textname": "SAP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 32,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "channels", "textname": "C", "minimum": 1, "maximum": 7},
                                    {"type": "uint8", "name": "filter", "textname": "L", "minimum": 0, "maximum": 3},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}],
                     "returns": []},
                24: {"name": "get_adv_parameters", "textname": "GAP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "type", "textname": "T"},
                                 {"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint8", "name": "channels", "textname": "C"},
                                 {"type": "uint8", "name": "filter", "textname": "L"},
                                 {"type": "uint16", "name": "timeout", "textname": "O"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                25: {"name": "set_scan_parameters", "textname": "SSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                26: {"name": "get_scan_parameters", "textname": "GSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "window", "textname": "W"},
                                 {"type": "uint8", "name": "active", "textname": "A"},
                                 {"type": "uint8", "name": "filter", "textname": "F"},
                                 {"type": "uint8", "name": "nodupe", "textname": "D"},
                                 {"type": "uint16", "name": "timeout", "textname": "O"}]},
                27: {"name": "set_conn_parameters", "textname": "SCP", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 3200},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200},
                    {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                28: {"name": "get_conn_parameters", "textname": "GCP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                 {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                 {"type": "uint16", "name": "scan_interval", "textname": "V"},
                                 {"type": "uint16", "name": "scan_window", "textname": "W"},
                                 {"type": "uint16", "name": "scan_timeout", "textname": "M"}]},
            },
            5: {
                "name": "gatts",
                # UNIQUE TO WICED BLE
                1: {"name": "create_attr", "textname": "/CAC", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8", "name": "permissions", "textname": "P", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint16", "name": "length", "textname": "L", "minimum": 0, "maximum": 512},
                                   {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0,
                                    "maxlength": 512}],
                    "returns": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                2: {"name": "delete_attr", "textname": "/CAD", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"},
                                {"type": "uint16", "name": "next_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                3: {"name": "validate_db", "textname": "/VGDB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint16", "name": "valid", "textname": "V"}]},
                4: {"name": "store_db", "textname": "/SGDB", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "dump_db", "textname": "/DGDB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "include_fixed", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                6: {"name": "discover_services", "textname": "/DLS", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                7: {"name": "discover_characteristics", "textname": "/DLC", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                8: {"name": "discover_descriptors", "textname": "/DLD", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "characteristic", "textname": "C", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                9: {"name": "read_handle", "textname": "/RLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "longuint8a", "name": "data", "textname": "D"}]},
                10: {"name": "write_handle", "textname": "/WLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                11: {"name": "notify_handle", "textname": "/NH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                12: {"name": "indicate_handle", "textname": "/IH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                13: {"name": "send_writereq_response", "textname": "/WRR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 255}],
                     "returns": []},
                14: {"name": "set_parameters", "textname": "SGSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                     "returns": []},
                15: {"name": "get_parameters", "textname": "GGSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_services", "textname": "/DRS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535}], "returns": []},
                2: {"name": "discover_characteristics", "textname": "/DRC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "discover_descriptors", "textname": "/DRD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "characteristic", "textname": "T", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "read_handle", "textname": "/RRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": []},
                5: {"name": "write_handle", "textname": "/WRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 2},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
                6: {"name": "confirm_indication", "textname": "/CI", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                7: {"name": "set_parameters", "textname": "SGCP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": []},
                8: {"name": "get_parameters", "textname": "GGCP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "query_bonds", "textname": "/QB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                2: {"name": "delete_bond", "textname": "/BD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                3: {"name": "pair", "textname": "/P", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "mode", "textname": "M", "minimum": 16, "maximum": 35},
                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1}], "returns": []},
                4: {"name": "query_random_address", "textname": "/QRA", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                5: {"name": "send_pairreq_response", "textname": "/PR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_passkeyreq_response", "textname": "/PE", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                    "returns": []},
                7: {"name": "generate_oob_data", "textname": "/GOOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8a", "name": "key", "textname": "K", "minlength": 16, "maxlength": 16}],
                    "returns": []},
                8: {"name": "clear_oob_data", "textname": "/COOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                9: {"name": "set_privacy_mode", "textname": "SPRV", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 1,
                                    "maximum": 65535}], "returns": []},
                10: {"name": "get_privacy_mode", "textname": "GPRV", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"}]},
                11: {"name": "set_security_parameters", "textname": "SSBP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 16, "maximum": 35},
                                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "io", "textname": "I", "minimum": 0, "maximum": 4},
                                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}],
                     "returns": []},
                12: {"name": "get_security_parameters", "textname": "GSBP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "bonding", "textname": "B"},
                                 {"type": "uint8", "name": "keysize", "textname": "K"},
                                 {"type": "uint8", "name": "pairprop", "textname": "P"},
                                 {"type": "uint8", "name": "io", "textname": "I"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                13: {"name": "set_fixed_passkey", "textname": "SFPK", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                     "returns": []},
                14: {"name": "get_fixed_passkey", "textname": "GFPK", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "passkey", "textname": "P"}]},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connect", "textname": "/LC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "remote", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "local", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "T", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                2: {"name": "disconnect", "textname": "/LDIS", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "register_psm", "textname": "/LRP", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "watermark", "textname": "W", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "send_connreq_response", "textname": "/LCR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "M", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                5: {"name": "send_credits", "textname": "/LSC", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_data", "textname": "/LD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
            },
            9: {
                "name": "gpio",
                1: {"name": "query_logic", "textname": "/QIOL", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                2: {"name": "query_adc", "textname": "/QADC", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 0},
                                   {"type": "uint8", "name": "reference", "textname": "R", "minimum": 0, "maximum": 0}],
                    "returns": [{"type": "uint16", "name": "value", "textname": "A"},
                                {"type": "uint32", "name": "uvolts", "textname": "U"}]},
                3: {"name": "set_function", "textname": "SIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "drive", "textname": "D", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                4: {"name": "get_function", "textname": "GIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "drive", "textname": "D"}]},
                5: {"name": "set_drive", "textname": "SIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "direction", "textname": "D", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_down", "textname": "W", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_up", "textname": "U", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "analog", "textname": "A", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                6: {"name": "get_drive", "textname": "GIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "direction", "textname": "D"},
                                {"type": "uint8", "name": "pulldrive_down", "textname": "W"},
                                {"type": "uint8", "name": "pulldrive_up", "textname": "U"},
                                {"type": "uint8", "name": "analog", "textname": "A"}]},
                7: {"name": "set_logic", "textname": "SIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "logic", "textname": "L", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                8: {"name": "get_logic", "textname": "GIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                9: {"name": "set_interrupt_mode", "textname": "SIOI", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "rising", "textname": "R", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "falling", "textname": "F", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                10: {"name": "get_interrupt_mode", "textname": "GIOI", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                     "returns": [{"type": "uint8", "name": "rising", "textname": "R"},
                                 {"type": "uint8", "name": "falling", "textname": "F"}]},
                11: {"name": "set_pwm_mode", "textname": "SPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "divider", "textname": "D", "minimum": 0, "maximum": 255},
                                    {"type": "uint8", "name": "prescaler", "textname": "S", "minimum": 0, "maximum": 7},
                                    {"type": "uint16", "name": "period", "textname": "P", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint16", "name": "compare", "textname": "C", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                12: {"name": "get_pwm_mode", "textname": "GPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3}],
                     "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                 {"type": "uint8", "name": "divider", "textname": "D"},
                                 {"type": "uint8", "name": "prescaler", "textname": "S"},
                                 {"type": "uint16", "name": "period", "textname": "P"},
                                 {"type": "uint16", "name": "compare", "textname": "C"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "check", "textname": ".CYSPPCHECK", "flashopt": 0, "parameters": [], "returns": []},
                2: {"name": "start", "textname": ".CYSPPSTART", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "set_parameters", "textname": ".CYSPPSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "role", "textname": "G", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint32", "name": "local_key", "textname": "L", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_key", "textname": "R", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_mask", "textname": "M", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint8", "name": "sleep_level", "textname": "P", "minimum": 0,
                                    "maximum": 2},
                                   {"type": "uint8", "name": "server_security", "textname": "S", "minimum": 0,
                                    "maximum": 3},
                                   {"type": "uint8", "name": "client_flags", "textname": "F", "minimum": 0,
                                    "maximum": 3}], "returns": []},
                4: {"name": "get_parameters", "textname": ".CYSPPGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "role", "textname": "G"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint32", "name": "local_key", "textname": "L"},
                                {"type": "uint32", "name": "remote_key", "textname": "R"},
                                {"type": "uint32", "name": "remote_mask", "textname": "M"},
                                {"type": "uint8", "name": "sleep_level", "textname": "P"},
                                {"type": "uint8", "name": "server_security", "textname": "S"},
                                {"type": "uint8", "name": "client_flags", "textname": "F"}]},
                5: {"name": "set_client_handles", "textname": ".CYSPPSH", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "data_value_handle", "textname": "A", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "data_cccd_handle", "textname": "B", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_value_handle", "textname": "C", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "get_client_handles", "textname": ".CYSPPGH", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint16", "name": "data_value_handle", "textname": "A"},
                                {"type": "uint16", "name": "data_cccd_handle", "textname": "B"},
                                {"type": "uint16", "name": "rxflow_value_handle", "textname": "C"},
                                {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D"}]},
                7: {"name": "set_packetization", "textname": ".CYSPPSK", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 4},
                                   {"type": "uint8", "name": "wait", "textname": "W", "minimum": 1, "maximum": 255},
                                   {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 128},
                                   {"type": "uint8", "name": "eop", "textname": "E", "minimum": 0, "maximum": 255}],
                    "returns": []},
                8: {"name": "get_packetization", "textname": ".CYSPPGK", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                {"type": "uint8", "name": "wait", "textname": "W"},
                                {"type": "uint8", "name": "length", "textname": "L"},
                                {"type": "uint8", "name": "eop", "textname": "E"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "set_parameters", "textname": ".CYCOMSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "hostout", "textname": "H", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "timeout", "textname": "T", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint8", "name": "safemode", "textname": "F", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "challenge", "textname": "C", "minimum": 0, "maximum": 3},
                                   {"type": "uint8", "name": "security", "textname": "S", "minimum": 0, "maximum": 3},
                                   {"type": "uint8a", "name": "secret", "textname": "R", "minlength": 0,
                                    "maxlength": 20}], "returns": []},
                2: {"name": "get_parameters", "textname": ".CYCOMGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "hostout", "textname": "H"},
                                {"type": "uint16", "name": "timeout", "textname": "T"},
                                {"type": "uint8", "name": "safemode", "textname": "F"},
                                {"type": "uint8", "name": "challenge", "textname": "C"},
                                {"type": "uint8", "name": "security", "textname": "S"},
                                {"type": "uint8a", "name": "secret", "textname": "R"}]},
            },
            12: {
                "name": "p_ibeacon",
                1: {"name": "set_parameters", "textname": ".IBSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "major", "textname": "J", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "minor", "textname": "N", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8a", "name": "uuid", "textname": "U", "minlength": 16,
                                    "maxlength": 16}], "returns": []},
                2: {"name": "get_parameters", "textname": ".IBGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint16", "name": "major", "textname": "J"},
                                {"type": "uint16", "name": "minor", "textname": "N"},
                                {"type": "uint8a", "name": "uuid", "textname": "U"}]},
            },
            13: {
                "name": "p_eddystone",
                1: {"name": "set_parameters", "textname": ".EDDYSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 255},
                                   {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                    "maxlength": 19}], "returns": []},
                2: {"name": "get_parameters", "textname": ".EDDYGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint8", "name": "type", "textname": "T"},
                                {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
        },
        "wiced_20706": {
            1: {
                "name": "protocol",
                1: {"name": "set_parse_mode", "textname": "SPPM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                2: {"name": "get_parse_mode", "textname": "GPPM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
                3: {"name": "set_echo_mode", "textname": "SPEM", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 1}],
                    "returns": []},
                4: {"name": "get_echo_mode", "textname": "GPEM", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"}]},
            },
            2: {
                "name": "system",
                1: {"name": "ping", "textname": "/PING", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "runtime", "textname": "R"},
                                {"type": "uint16", "name": "fraction", "textname": "F"}]},
                2: {"name": "reboot", "textname": "/RBT", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "dump", "textname": "/DUMP", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3}],
                    "returns": [{"type": "uint16", "name": "length", "textname": "L"}]},
                4: {"name": "store_config", "textname": "/SCFG", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "factory_reset", "textname": "/RFAC", "flashopt": 0, "parameters": [], "returns": []},
                6: {"name": "query_firmware_version", "textname": "/QFV", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint32", "name": "app", "textname": "E"},
                                {"type": "uint32", "name": "stack", "textname": "S"},
                                {"type": "uint16", "name": "protocol", "textname": "P"},
                                {"type": "uint8", "name": "hardware", "textname": "H"}]},
                7: {"name": "query_unique_id", "textname": "/QUID", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "id", "textname": "U"}]},
                8: {"name": "query_random_number", "textname": "/QRND", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                9: {"name": "aes_encrypt", "textname": "/AESE", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                    "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                10: {"name": "aes_decrypt", "textname": "/AESD", "flashopt": 0, "parameters": [
                    {"type": "uint8a", "name": "in_struct", "textname": "I", "minlength": 30, "maxlength": 56}],
                     "returns": [{"type": "uint8a", "name": "out", "textname": "O"}]},
                11: {"name": "write_user_data", "textname": "/WUD", "flashopt": 0,
                     "parameters": [{"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 255},
                                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                     "maxlength": 32}], "returns": []},
                12: {"name": "read_user_data", "textname": "/RUD", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "offset", "textname": "O", "minimum": 0, "maximum": 65535},
                    {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 32}],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                13: {"name": "set_bluetooth_address", "textname": "SBA", "flashopt": 1,
                     "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}], "returns": []},
                14: {"name": "get_bluetooth_address", "textname": "GBA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                15: {"name": "set_eco_parameters", "textname": "SECO", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "trim", "textname": "T", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                16: {"name": "get_eco_parameters", "textname": "GECO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "trim", "textname": "T"}]},
                17: {"name": "set_wco_parameters", "textname": "SWCO", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "accuracy", "textname": "A", "minimum": 0, "maximum": 7}],
                     "returns": []},
                18: {"name": "get_wco_parameters", "textname": "GWCO", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "accuracy", "textname": "A"}]},
                19: {"name": "set_sleep_parameters", "textname": "SSLP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "level", "textname": "L", "minimum": 0, "maximum": 1}],
                     "returns": []},
                20: {"name": "get_sleep_parameters", "textname": "GSLP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "level", "textname": "L"}]},
                21: {"name": "set_tx_power", "textname": "STXP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "power", "textname": "P", "minimum": 1, "maximum": 8}],
                     "returns": []},
                22: {"name": "get_tx_power", "textname": "GTXP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "power", "textname": "P"}]},
                23: {"name": "set_transport", "textname": "ST", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "interface", "textname": "I", "minimum": 1, "maximum": 1},
                                    {"type": "uint8", "name": "cmd_channel", "textname": "N", "minimum": 1,
                                     "maximum": 51},
                                    {"type": "uint8", "name": "spp_route", "textname": "S", "minimum": 0,
                                     "maximum": 51},
                                    {"type": "uint32", "name": "cyspp_route", "textname": "C", "minimum": 0,
                                     "maximum": 51},
                                    {"type": "uint8", "name": "bt_flag", "textname": "T", "minimum": 0, "maximum": 146},
                                    {"type": "uint8", "name": "ble_flag", "textname": "L", "minimum": 0,
                                     "maximum": 136}], "returns": []},
                24: {"name": "get_transport", "textname": "GT", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "interface", "textname": "I"},
                                 {"type": "uint8", "name": "cmd_channel", "textname": "N"},
                                 {"type": "uint8", "name": "spp_route", "textname": "S"},
                                 {"type": "uint32", "name": "cyspp_route", "textname": "C"},
                                 {"type": "uint8", "name": "bt_flag", "textname": "T"},
                                 {"type": "uint8", "name": "ble_flag", "textname": "L"}]},
                25: {"name": "set_uart_parameters", "textname": "STU", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "baud", "textname": "B", "minimum": 300, "maximum": 3000000},
                    {"type": "uint8", "name": "autobaud", "textname": "A", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "autocorrect", "textname": "C", "minimum": 0, "maximum": 0},
                    {"type": "uint8", "name": "flow", "textname": "F", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "databits", "textname": "D", "minimum": 7, "maximum": 9},
                    {"type": "uint8", "name": "parity", "textname": "P", "minimum": 0, "maximum": 2},
                    {"type": "uint8", "name": "stopbits", "textname": "S", "minimum": 1, "maximum": 7}], "returns": []},
                26: {"name": "get_uart_parameters", "textname": "GTU", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "baud", "textname": "B"},
                                 {"type": "uint8", "name": "autobaud", "textname": "A"},
                                 {"type": "uint8", "name": "autocorrect", "textname": "C"},
                                 {"type": "uint8", "name": "flow", "textname": "F"},
                                 {"type": "uint8", "name": "databits", "textname": "D"},
                                 {"type": "uint8", "name": "parity", "textname": "P"},
                                 {"type": "uint8", "name": "stopbits", "textname": "S"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "reboot", "textname": "/RDFU", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2}],
                    "returns": []},
            },
            4: {
                "name": "gap",
                1: {"name": "connect", "textname": "/C", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10,
                                    "maximum": 3200},
                                   {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                2: {"name": "cancel_connection", "textname": "/CX", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "update_conn_parameters", "textname": "/UCP", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200}],
                    "returns": []},
                4: {"name": "send_connupdate_response", "textname": "/CUR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 1}], "returns": []},
                5: {"name": "disconnect", "textname": "/DIS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                6: {"name": "add_whitelist_entry", "textname": "/WLA", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                7: {"name": "delete_whitelist_entry", "textname": "/WLD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                8: {"name": "start_adv", "textname": "/A", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                   {"type": "uint8", "name": "channel", "textname": "C", "minimum": 1, "maximum": 7},
                                   {"type": "uint16", "name": "high_duty_interval", "textname": "H", "minimum": 32,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "high_duty_duration", "textname": "D", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "low_duty_interval", "textname": "L", "minimum": 32,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "low_duty_duration", "textname": "O", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint8", "name": "adv_flags", "textname": "F", "minimum": 0, "maximum": 3}],
                    "returns": []},
                9: {"name": "stop_adv", "textname": "/AX", "flashopt": 0, "parameters": [], "returns": []},
                10: {"name": "start_scan", "textname": "/S", "flashopt": 0,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0,
                                     "maximum": 65565},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                11: {"name": "stop_scan", "textname": "/SX", "flashopt": 0, "parameters": [], "returns": []},
                12: {"name": "query_peer_address", "textname": "/QPA", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "macaddr", "name": "address", "textname": "A"},
                                 {"type": "uint8", "name": "address_type", "textname": "T"}]},
                13: {"name": "query_rssi", "textname": "/QSS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                     "returns": [{"type": "int8", "name": "rssi", "textname": "R"}]},
                14: {"name": "query_whitelist", "textname": "/QWL", "flashopt": 0, "parameters": [],
                     "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                15: {"name": "set_device_name", "textname": "SDN", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minlength": 0, "maxlength": 1},
                                    {"type": "string", "name": "name", "textname": "N", "minlength": 0,
                                     "maxlength": 64}], "returns": []},
                16: {"name": "get_device_name", "textname": "GDN", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minlength": 0, "maxlength": 1}],
                     "returns": [{"type": "string", "name": "name", "textname": "N"}]},
                17: {"name": "set_device_appearance", "textname": "SDA", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "appearance", "textname": "A", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                18: {"name": "get_device_appearance", "textname": "GDA", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "appearance", "textname": "A"}]},
                19: {"name": "set_adv_data", "textname": "SAD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                20: {"name": "get_adv_data", "textname": "GAD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                21: {"name": "set_sr_data", "textname": "SSRD", "flashopt": 1, "parameters": [
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 31}],
                     "returns": []},
                22: {"name": "get_sr_data", "textname": "GSRD", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8a", "name": "data", "textname": "D"}]},
                23: {"name": "set_adv_parameters", "textname": "SAP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "channel", "textname": "C", "minimum": 1, "maximum": 7},
                                    {"type": "uint16", "name": "high_duty_interval", "textname": "H", "minimum": 32,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "high_duty_duration", "textname": "D", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint16", "name": "low_duty_interval", "textname": "L", "minimum": 32,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "low_duty_duration", "textname": "O", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint8", "name": "adv_flags", "textname": "F", "minimum": 0,
                                     "maximum": 3}], "returns": []},
                24: {"name": "get_adv_parameters", "textname": "GAP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "type", "textname": "T"},
                                 {"type": "uint8", "name": "channel", "textname": "C"},
                                 {"type": "uint16", "name": "high_duty_interval", "textname": "H"},
                                 {"type": "uint16", "name": "high_duty_duration", "textname": "D"},
                                 {"type": "uint16", "name": "low_duty_interval", "textname": "L"},
                                 {"type": "uint16", "name": "low_duty_duration", "textname": "O"},
                                 {"type": "uint8", "name": "adv_flags", "textname": "F"}]},
                25: {"name": "set_scan_parameters", "textname": "SSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 2},
                                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint16", "name": "window", "textname": "W", "minimum": 4,
                                     "maximum": 16384},
                                    {"type": "uint8", "name": "active", "textname": "A", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "filter", "textname": "F", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "nodupe", "textname": "D", "minimum": 0, "maximum": 1},
                                    {"type": "uint16", "name": "timeout", "textname": "O", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                26: {"name": "get_scan_parameters", "textname": "GSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "window", "textname": "W"},
                                 {"type": "uint8", "name": "active", "textname": "A"},
                                 {"type": "uint8", "name": "filter", "textname": "F"},
                                 {"type": "uint8", "name": "nodupe", "textname": "D"},
                                 {"type": "uint16", "name": "timeout", "textname": "O"}]},
                27: {"name": "set_conn_parameters", "textname": "SCP", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "interval", "textname": "I", "minimum": 6, "maximum": 3200},
                    {"type": "uint16", "name": "slave_latency", "textname": "L", "minimum": 0, "maximum": 3200},
                    {"type": "uint16", "name": "supervision_timeout", "textname": "O", "minimum": 10, "maximum": 3200},
                    {"type": "uint16", "name": "scan_interval", "textname": "V", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_window", "textname": "W", "minimum": 4, "maximum": 16384},
                    {"type": "uint16", "name": "scan_timeout", "textname": "M", "minimum": 0, "maximum": 65535}],
                     "returns": []},
                28: {"name": "get_conn_parameters", "textname": "GCP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "interval", "textname": "I"},
                                 {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                 {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                 {"type": "uint16", "name": "scan_interval", "textname": "V"},
                                 {"type": "uint16", "name": "scan_window", "textname": "W"},
                                 {"type": "uint16", "name": "scan_timeout", "textname": "M"}]},
            },
            5: {
                "name": "gatts",
                # UNIQUE TO WICED BLE
                1: {"name": "create_attr", "textname": "/CAC", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8", "name": "permissions", "textname": "P", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint16", "name": "length", "textname": "L", "minimum": 0, "maximum": 512},
                                   {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0,
                                    "maxlength": 512}],
                    "returns": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                2: {"name": "delete_attr", "textname": "/CAD", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"},
                                {"type": "uint16", "name": "next_handle", "textname": "H"},
                                {"type": "uint16", "name": "valid", "textname": "V"}]},
                3: {"name": "validate_db", "textname": "/VGDB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint16", "name": "valid", "textname": "V"}]},
                4: {"name": "store_db", "textname": "/SGDB", "flashopt": 0, "parameters": [], "returns": []},
                5: {"name": "dump_db", "textname": "/DGDB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "include_fixed", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                6: {"name": "discover_services", "textname": "/DLS", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                7: {"name": "discover_characteristics", "textname": "/DLC", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                8: {"name": "discover_descriptors", "textname": "/DLD", "flashopt": 0,
                    "parameters": [{"type": "uint16", "name": "begin", "textname": "B", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "end", "textname": "E", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "service", "textname": "S", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "characteristic", "textname": "C", "minimum": 0,
                                    "maximum": 65535}],
                    "returns": [{"type": "uint16", "name": "count", "textname": "C"}]},
                9: {"name": "read_handle", "textname": "/RLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": [{"type": "longuint8a", "name": "data", "textname": "D"}]},
                10: {"name": "write_handle", "textname": "/WLH", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                11: {"name": "notify_handle", "textname": "/NH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                12: {"name": "indicate_handle", "textname": "/IH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                     "returns": []},
                13: {"name": "send_writereq_response", "textname": "/WRR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "response", "textname": "R", "minimum": 0, "maximum": 255}],
                     "returns": []},
                14: {"name": "set_parameters", "textname": "SGSP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                     "returns": []},
                15: {"name": "get_parameters", "textname": "GGSP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_services", "textname": "/DRS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535}], "returns": []},
                2: {"name": "discover_characteristics", "textname": "/DRC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "discover_descriptors", "textname": "/DRD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "begin", "textname": "B", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "end", "textname": "E", "minimum": 1, "maximum": 65535},
                    {"type": "uint16", "name": "service", "textname": "S", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "characteristic", "textname": "T", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "read_handle", "textname": "/RRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535}],
                    "returns": []},
                5: {"name": "write_handle", "textname": "/WRH", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "attr_handle", "textname": "H", "minimum": 1, "maximum": 65535},
                    {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 2},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
                6: {"name": "confirm_indication", "textname": "/CI", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                7: {"name": "set_parameters", "textname": "SGCP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 1}],
                    "returns": []},
                8: {"name": "get_parameters", "textname": "GGCP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "flags", "textname": "F"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "query_bonds", "textname": "/QB", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                2: {"name": "delete_bond", "textname": "/BD", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 1}],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                3: {"name": "pair", "textname": "/P", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8", "name": "mode", "textname": "M", "minimum": 16, "maximum": 35},
                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1}], "returns": []},
                4: {"name": "query_random_address", "textname": "/QRA", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "macaddr", "name": "address", "textname": "A"}]},
                5: {"name": "send_pairreq_response", "textname": "/PR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_passkeyreq_response", "textname": "/PE", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                    "returns": []},
                7: {"name": "generate_oob_data", "textname": "/GOOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint8a", "name": "key", "textname": "K", "minlength": 16, "maxlength": 16}],
                    "returns": []},
                8: {"name": "clear_oob_data", "textname": "/COOB", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4}],
                    "returns": []},
                9: {"name": "set_privacy_mode", "textname": "SPRV", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 1,
                                    "maximum": 65535}], "returns": []},
                10: {"name": "get_privacy_mode", "textname": "GPRV", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint16", "name": "interval", "textname": "I"}]},
                11: {"name": "set_security_parameters", "textname": "SSBP", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 00, "maximum": 93},
                                    {"type": "uint8", "name": "bonding", "textname": "B", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "keysize", "textname": "K", "minimum": 7, "maximum": 16},
                                    {"type": "uint8", "name": "pairprop", "textname": "P", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "io", "textname": "I", "minimum": 0, "maximum": 4},
                                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}],
                     "returns": []},
                12: {"name": "get_security_parameters", "textname": "GSBP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                 {"type": "uint8", "name": "bonding", "textname": "B"},
                                 {"type": "uint8", "name": "keysize", "textname": "K"},
                                 {"type": "uint8", "name": "pairprop", "textname": "P"},
                                 {"type": "uint8", "name": "io", "textname": "I"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                13: {"name": "set_fixed_passkey", "textname": "SFPK", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "passkey", "textname": "P", "minimum": 0, "maximum": 999999}],
                     "returns": []},
                14: {"name": "get_fixed_passkey", "textname": "GFPK", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "passkey", "textname": "P"}]},
                15: {"name": "set_pin_code", "textname": "SBTPIN", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "pin_code", "textname": "P", "minimum": 0, "maximum": 9999}],
                     "returns": []},
                16: {"name": "get_pin_code", "textname": "GBTPIN", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint16", "name": "pin_code", "textname": "A"}]},
                17: {"name": "send_pinreq_response", "textname": "/BTPIN", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255},
                    {"type": "uint32", "name": "pin_code", "textname": "P", "minimum": 0, "maximum": 999999}],
                     "returns": []},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connect", "textname": "/LC", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "remote", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "local", "textname": "L", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "T", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                2: {"name": "disconnect", "textname": "/LDIS", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                3: {"name": "register_psm", "textname": "/LRP", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "watermark", "textname": "W", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                4: {"name": "send_connreq_response", "textname": "/LCR", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "response", "textname": "R", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "mtu", "textname": "M", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "mps", "textname": "P", "minimum": 23, "maximum": 512},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                5: {"name": "send_credits", "textname": "/LSC", "flashopt": 0, "parameters": [
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "credits", "textname": "Z", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "send_data", "textname": "/LD", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 4},
                    {"type": "uint16", "name": "channel", "textname": "N", "minimum": 0, "maximum": 65535},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 0, "maxlength": 512}],
                    "returns": []},
            },
            9: {
                "name": "gpio",
                1: {"name": "query_logic", "textname": "/QIOL", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                2: {"name": "query_adc", "textname": "/QADC", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 0},
                                   {"type": "uint8", "name": "reference", "textname": "R", "minimum": 0, "maximum": 0}],
                    "returns": [{"type": "uint16", "name": "value", "textname": "A"},
                                {"type": "uint32", "name": "uvolts", "textname": "U"}]},
                3: {"name": "set_function", "textname": "SIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "drive", "textname": "D", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                4: {"name": "get_function", "textname": "GIOF", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "drive", "textname": "D"}]},
                5: {"name": "set_drive", "textname": "SIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "direction", "textname": "D", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_down", "textname": "W", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "pulldrive_up", "textname": "U", "minimum": 0,
                                    "maximum": 255},
                                   {"type": "uint8", "name": "analog", "textname": "A", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                6: {"name": "get_drive", "textname": "GIOD", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "direction", "textname": "D"},
                                {"type": "uint8", "name": "pulldrive_down", "textname": "W"},
                                {"type": "uint8", "name": "pulldrive_up", "textname": "U"},
                                {"type": "uint8", "name": "analog", "textname": "A"}]},
                7: {"name": "set_logic", "textname": "SIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "logic", "textname": "L", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                8: {"name": "get_logic", "textname": "GIOL", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                    "returns": [{"type": "uint8", "name": "logic", "textname": "L"}]},
                9: {"name": "set_interrupt_mode", "textname": "SIOI", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5},
                                   {"type": "uint8", "name": "mask", "textname": "M", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "rising", "textname": "R", "minimum": 0, "maximum": 255},
                                   {"type": "uint8", "name": "falling", "textname": "F", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "affected", "textname": "A"}]},
                10: {"name": "get_interrupt_mode", "textname": "GIOI", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "port", "textname": "P", "minimum": 0, "maximum": 5}],
                     "returns": [{"type": "uint8", "name": "rising", "textname": "R"},
                                 {"type": "uint8", "name": "falling", "textname": "F"}]},
                11: {"name": "set_pwm_mode", "textname": "SPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3},
                                    {"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                    {"type": "uint8", "name": "divider", "textname": "D", "minimum": 0, "maximum": 255},
                                    {"type": "uint8", "name": "prescaler", "textname": "S", "minimum": 0, "maximum": 7},
                                    {"type": "uint16", "name": "period", "textname": "P", "minimum": 0,
                                     "maximum": 65535},
                                    {"type": "uint16", "name": "compare", "textname": "C", "minimum": 0,
                                     "maximum": 65535}], "returns": []},
                12: {"name": "get_pwm_mode", "textname": "GPWM", "flashopt": 1,
                     "parameters": [{"type": "uint8", "name": "channel", "textname": "N", "minimum": 0, "maximum": 3}],
                     "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                 {"type": "uint8", "name": "divider", "textname": "D"},
                                 {"type": "uint8", "name": "prescaler", "textname": "S"},
                                 {"type": "uint16", "name": "period", "textname": "P"},
                                 {"type": "uint16", "name": "compare", "textname": "C"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "check", "textname": ".CYSPPCHECK", "flashopt": 0, "parameters": [], "returns": []},
                2: {"name": "start", "textname": ".CYSPPSTART", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "set_parameters", "textname": ".CYSPPSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint8", "name": "role", "textname": "G", "minimum": 0, "maximum": 1},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint32", "name": "local_key", "textname": "L", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_key", "textname": "R", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint32", "name": "remote_mask", "textname": "M", "minimum": 0,
                                    "maximum": 4294967295},
                                   {"type": "uint8", "name": "sleep_level", "textname": "P", "minimum": 0,
                                    "maximum": 2},
                                   {"type": "uint8", "name": "server_security", "textname": "S", "minimum": 0,
                                    "maximum": 3},
                                   {"type": "uint8", "name": "client_flags", "textname": "F", "minimum": 0,
                                    "maximum": 3}], "returns": []},
                4: {"name": "get_parameters", "textname": ".CYSPPGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "role", "textname": "G"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint32", "name": "local_key", "textname": "L"},
                                {"type": "uint32", "name": "remote_key", "textname": "R"},
                                {"type": "uint32", "name": "remote_mask", "textname": "M"},
                                {"type": "uint8", "name": "sleep_level", "textname": "P"},
                                {"type": "uint8", "name": "server_security", "textname": "S"},
                                {"type": "uint8", "name": "client_flags", "textname": "F"}]},
                5: {"name": "set_client_handles", "textname": ".CYSPPSH", "flashopt": 1, "parameters": [
                    {"type": "uint16", "name": "data_value_handle", "textname": "A", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "data_cccd_handle", "textname": "B", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_value_handle", "textname": "C", "minimum": 0, "maximum": 65535},
                    {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D", "minimum": 0, "maximum": 65535}],
                    "returns": []},
                6: {"name": "get_client_handles", "textname": ".CYSPPGH", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint16", "name": "data_value_handle", "textname": "A"},
                                {"type": "uint16", "name": "data_cccd_handle", "textname": "B"},
                                {"type": "uint16", "name": "rxflow_value_handle", "textname": "C"},
                                {"type": "uint16", "name": "rxflow_cccd_handle", "textname": "D"}]},
                7: {"name": "set_packetization", "textname": ".CYSPPSK", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M", "minimum": 0, "maximum": 4},
                                   {"type": "uint8", "name": "wait", "textname": "W", "minimum": 1, "maximum": 255},
                                   {"type": "uint8", "name": "length", "textname": "L", "minimum": 1, "maximum": 128},
                                   {"type": "uint8", "name": "eop", "textname": "E", "minimum": 0, "maximum": 255}],
                    "returns": []},
                8: {"name": "get_packetization", "textname": ".CYSPPGK", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "mode", "textname": "M"},
                                {"type": "uint8", "name": "wait", "textname": "W"},
                                {"type": "uint8", "name": "length", "textname": "L"},
                                {"type": "uint8", "name": "eop", "textname": "E"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "set_parameters", "textname": ".CYCOMSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "hostout", "textname": "H", "minimum": 0, "maximum": 3},
                                   {"type": "uint16", "name": "timeout", "textname": "T", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint8", "name": "safemode", "textname": "F", "minimum": 0, "maximum": 1},
                                   {"type": "uint8", "name": "challenge", "textname": "C", "minimum": 0, "maximum": 3},
                                   {"type": "uint8", "name": "security", "textname": "S", "minimum": 0, "maximum": 3},
                                   {"type": "uint8a", "name": "secret", "textname": "R", "minlength": 0,
                                    "maxlength": 20}], "returns": []},
                2: {"name": "get_parameters", "textname": ".CYCOMGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint8", "name": "hostout", "textname": "H"},
                                {"type": "uint16", "name": "timeout", "textname": "T"},
                                {"type": "uint8", "name": "safemode", "textname": "F"},
                                {"type": "uint8", "name": "challenge", "textname": "C"},
                                {"type": "uint8", "name": "security", "textname": "S"},
                                {"type": "uint8a", "name": "secret", "textname": "R"}]},
            },
            12: {
                "name": "p_ibeacon",
                1: {"name": "set_parameters", "textname": ".IBSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint16", "name": "company", "textname": "C", "minimum": 0,
                                    "maximum": 65535},
                                   {"type": "uint16", "name": "major", "textname": "J", "minimum": 0, "maximum": 65535},
                                   {"type": "uint16", "name": "minor", "textname": "N", "minimum": 0, "maximum": 65535},
                                   {"type": "uint8a", "name": "uuid", "textname": "U", "minlength": 16,
                                    "maxlength": 16}], "returns": []},
                2: {"name": "get_parameters", "textname": ".IBGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint16", "name": "company", "textname": "C"},
                                {"type": "uint16", "name": "major", "textname": "J"},
                                {"type": "uint16", "name": "minor", "textname": "N"},
                                {"type": "uint8a", "name": "uuid", "textname": "U"}]},
            },
            13: {
                "name": "p_eddystone",
                1: {"name": "set_parameters", "textname": ".EDDYSP", "flashopt": 1,
                    "parameters": [{"type": "uint8", "name": "enable", "textname": "E", "minimum": 0, "maximum": 2},
                                   {"type": "uint16", "name": "interval", "textname": "I", "minimum": 160,
                                    "maximum": 16384},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 255},
                                   {"type": "uint8a", "name": "data", "textname": "D", "minlength": 1,
                                    "maxlength": 19}], "returns": []},
                2: {"name": "get_parameters", "textname": ".EDDYGP", "flashopt": 1, "parameters": [],
                    "returns": [{"type": "uint8", "name": "enable", "textname": "E"},
                                {"type": "uint16", "name": "interval", "textname": "I"},
                                {"type": "uint8", "name": "type", "textname": "T"},
                                {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
            14: {
                "name": "bt",
                1: {"name": "start_inquiry", "textname": "/BTI", "flashopt": 0,
                    "parameters": [{"type": "uint8", "name": "duration", "textname": "D", "minimum": 3, "maximum": 30},
                                   {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 2}],
                    "returns": []},
                2: {"name": "cancel_inquiry", "textname": "/BTIX", "flashopt": 0, "parameters": [], "returns": []},
                3: {"name": "query_name", "textname": "/BTQN", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}], "returns": []},
                4: {"name": "connect", "textname": "/BTC", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                5: {"name": "cancel_connection", "textname": "/BTCX", "flashopt": 0, "parameters": [], "returns": []},
                6: {"name": "disconnect", "textname": "/BTDIS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255}],
                    "returns": []},
                7: {"name": "query_connections", "textname": "/BTQC", "flashopt": 0, "parameters": [],
                    "returns": [{"type": "uint8", "name": "count", "textname": "C"}]},
                8: {"name": "query_peer_address", "textname": "/BTQPA", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255}],
                    "returns": [{"type": "macaddr", "name": "address", "textname": "A"},
                                {"type": "uint8", "name": "address_type", "textname": "T"}]},
                9: {"name": "query_rssi", "textname": "/BTQSS", "flashopt": 0,
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}],
                    "returns": [{"type": "int8", "name": "rssi", "textname": "R"}]},
                10: {"name": "set_parameters", "textname": "SBTP", "flashopt": 1, "parameters": [
                    {"type": "uint8", "name": "discoverable", "textname": "D", "minimum": 0, "maximum": 2},
                    {"type": "uint8", "name": "connectable", "textname": "C", "minimum": 0, "maximum": 1},
                    {"type": "uint8", "name": "flags", "textname": "F", "minimum": 0, "maximum": 3}], "returns": []},
                11: {"name": "get_parameters", "textname": "GBTP", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint8", "name": "discoverable", "textname": "D"},
                                 {"type": "uint8", "name": "connectable", "textname": "C"},
                                 {"type": "uint8", "name": "flags", "textname": "F"}]},
                12: {"name": "set_device_class", "textname": "SBTDC", "flashopt": 1, "parameters": [
                    {"type": "uint32", "name": "cod", "textname": "C", "minimum": 0, "maximum": 16777215}],
                     "returns": []},
                13: {"name": "get_device_class", "textname": "GBTDC", "flashopt": 1, "parameters": [],
                     "returns": [{"type": "uint32", "name": "cod", "textname": "C"}]},
            },
            15: {
                "name": "p_rfcomm",
                1: {"name": "send_data", "textname": ".RFS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 1, "maxlength": 512}],
                    "returns": []},
            },
            16: {
                "name": "p_a2dp",
                1: {"name": "start_stream", "textname": ".A2DPSTART", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255}],
                    "returns": []},
                2: {"name": "stop_stream", "textname": ".A2DPSTOP", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255}],
                    "returns": []},
                3: {"name": "mute_stream", "textname": ".A2DPMUTE", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255},
                    {"type": "uint8", "name": "mute", "textname": "M", "minimum": 0, "maximum": 1}], "returns": []},
            },
            17: {
                "name": "p_avrcp",
                1: {"name": "send_command", "textname": ".AVRCPS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 1, "maxlength": 512}],
                    "returns": []},
            },
            18: {
                "name": "p_hfp",
                1: {"name": "send_command", "textname": ".HFPS", "flashopt": 0, "parameters": [
                    {"type": "uint8", "name": "conn_handle", "textname": "C", "minimum": 0, "maximum": 255},
                    {"type": "longuint8a", "name": "data", "textname": "D", "minlength": 1, "maxlength": 512}],
                    "returns": []},
            },
        }
    }

    events = {
        "psoc4proc_ble": {
            1: {
                "name": "protocol",
            },
            2: {
                "name": "system",
                1: {"name": "boot", "textname": "BOOT",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"}]},
                2: {"name": "error", "textname": "ERR",
                    "parameters": [{"type": "uint16", "name": "error", "textname": "E"}]},
                3: {"name": "factory_reset_complete", "textname": "RFAC", "parameters": []},
                4: {"name": "factory_test_entered", "textname": "TFAC",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"}]},
                5: {"name": "dump_blob", "textname": "DBLOB",
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "offset", "textname": "O"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "boot", "textname": "BDFU",
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "valid", "textname": "V"},
                                   {"type": "uint8", "name": "bootloader", "textname": "B"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"}]},
            },
            4: {
                "name": "gap",
                1: {"name": "whitelist_entry", "textname": "WL",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "adv_state_changed", "textname": "ASC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                3: {"name": "scan_state_changed", "textname": "SSC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                4: {"name": "scan_result", "textname": "S",
                    "parameters": [{"type": "uint8", "name": "result_type", "textname": "R"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "address_type", "textname": "T"},
                                   {"type": "int8", "name": "rssi", "textname": "S"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
                5: {"name": "connected", "textname": "C",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                   {"type": "uint8", "name": "bond", "textname": "B"}]},
                6: {"name": "disconnected", "textname": "DIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                7: {"name": "connection_update_requested", "textname": "UCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval_min", "textname": "I"},
                                   {"type": "uint16", "name": "interval_max", "textname": "X"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
                8: {"name": "connection_updated", "textname": "CU",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
            },
            5: {
                "name": "gatts",
                1: {"name": "discover_result", "textname": "DL",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "data_written", "textname": "W",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                3: {"name": "indication_confirmed", "textname": "IC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"}]},
                4: {"name": "db_entry_blob", "textname": "DGATT",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "read_permissions", "textname": "R"},
                                   {"type": "uint8", "name": "write_permissions", "textname": "W"},
                                   {"type": "uint8", "name": "char_properties", "textname": "C"},
                                   {"type": "uint16", "name": "length", "textname": "L"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_result", "textname": "DR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "remote_procedure_complete", "textname": "RPC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                3: {"name": "data_received", "textname": "D",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "source", "textname": "S"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "write_response", "textname": "WRR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "bond_entry", "textname": "B",
                    "parameters": [{"type": "uint8", "name": "handle", "textname": "B"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "pairing_requested", "textname": "P",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "bonding", "textname": "B"},
                                   {"type": "uint8", "name": "keysize", "textname": "K"},
                                   {"type": "uint8", "name": "pairprop", "textname": "P"}]},
                3: {"name": "pairing_result", "textname": "PR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                4: {"name": "encryption_status", "textname": "ENC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "status", "textname": "S"}]},
                5: {"name": "passkey_display_requested", "textname": "PKD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint32", "name": "passkey", "textname": "P"}]},
                6: {"name": "passkey_entry_requested", "textname": "PKE",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connection_requested", "textname": "LCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "local", "textname": "L"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                2: {"name": "connection_response", "textname": "LC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "response", "textname": "R"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                3: {"name": "data_received", "textname": "LD",
                    "parameters": [{"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "disconnected", "textname": "LDIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                5: {"name": "rx_credits_low", "textname": "LRCL",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                6: {"name": "tx_credits_received", "textname": "LTCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                7: {"name": "command_rejected", "textname": "LREJ",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
            },
            9: {
                "name": "gpio",
                1: {"name": "interrupt", "textname": "INT",
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P"},
                                   {"type": "uint8", "name": "trigger", "textname": "T"},
                                   {"type": "uint8", "name": "logic", "textname": "L"},
                                   {"type": "uint32", "name": "runtime", "textname": "R"},
                                   {"type": "uint16", "name": "fraction", "textname": "F"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "status", "textname": ".CYSPP",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "status", "textname": ".CYCOM",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            12: {
                "name": "p_ibeacon",
            },
            13: {
                "name": "p_eddystone",
            },
        },
        "wiced_ble": {
            1: {
                "name": "protocol",
            },
            2: {
                "name": "system",
                1: {"name": "boot", "textname": "BOOT",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"}]},
                2: {"name": "error", "textname": "ERR",
                    "parameters": [{"type": "uint16", "name": "error", "textname": "E"}]},
                3: {"name": "factory_reset_complete", "textname": "RFAC", "parameters": []},
                4: {"name": "factory_test_entered", "textname": "TFAC",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"}]},
                5: {"name": "dump_blob", "textname": "DBLOB",
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "offset", "textname": "O"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "boot", "textname": "BDFU",
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "valid", "textname": "V"},
                                   {"type": "uint8", "name": "bootloader", "textname": "B"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"}]},
            },
            4: {
                "name": "gap",
                1: {"name": "whitelist_entry", "textname": "WL",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "adv_state_changed", "textname": "ASC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                3: {"name": "scan_state_changed", "textname": "SSC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                4: {"name": "scan_result", "textname": "S",
                    "parameters": [{"type": "uint8", "name": "result_type", "textname": "R"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "address_type", "textname": "T"},
                                   {"type": "int8", "name": "rssi", "textname": "S"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
                5: {"name": "connected", "textname": "C",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                   {"type": "uint8", "name": "bond", "textname": "B"}]},
                6: {"name": "disconnected", "textname": "DIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                7: {"name": "connection_update_requested", "textname": "UCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval_min", "textname": "I"},
                                   {"type": "uint16", "name": "interval_max", "textname": "X"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
                8: {"name": "connection_updated", "textname": "CU",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
            },
            5: {
                "name": "gatts",
                1: {"name": "discover_result", "textname": "DL",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "data_written", "textname": "W",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                3: {"name": "indication_confirmed", "textname": "IC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"}]},
                4: {"name": "db_entry_blob", "textname": "DGATT",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "permissions", "textname": "P"},
                                   {"type": "uint16", "name": "length", "textname": "L"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_result", "textname": "DR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "remote_procedure_complete", "textname": "RPC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                3: {"name": "data_received", "textname": "D",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "source", "textname": "S"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "write_response", "textname": "WRR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "bond_entry", "textname": "B",
                    "parameters": [{"type": "uint8", "name": "handle", "textname": "B"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "pairing_requested", "textname": "P",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "bonding", "textname": "B"},
                                   {"type": "uint8", "name": "keysize", "textname": "K"},
                                   {"type": "uint8", "name": "pairprop", "textname": "P"}]},
                3: {"name": "pairing_result", "textname": "PR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                4: {"name": "encryption_status", "textname": "ENC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "status", "textname": "S"}]},
                5: {"name": "passkey_display_requested", "textname": "PKD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint32", "name": "passkey", "textname": "P"}]},
                6: {"name": "passkey_entry_requested", "textname": "PKE",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connection_requested", "textname": "LCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "local", "textname": "L"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                2: {"name": "connection_response", "textname": "LC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "response", "textname": "R"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                3: {"name": "data_received", "textname": "LD",
                    "parameters": [{"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "disconnected", "textname": "LDIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                5: {"name": "rx_credits_low", "textname": "LRCL",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                6: {"name": "tx_credits_received", "textname": "LTCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                7: {"name": "command_rejected", "textname": "LREJ",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
            },
            9: {
                "name": "gpio",
                1: {"name": "interrupt", "textname": "INT",
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P"},
                                   {"type": "uint8", "name": "trigger", "textname": "T"},
                                   {"type": "uint8", "name": "logic", "textname": "L"},
                                   {"type": "uint32", "name": "runtime", "textname": "R"},
                                   {"type": "uint16", "name": "fraction", "textname": "F"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "status", "textname": ".CYSPP",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "status", "textname": ".CYCOM",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            12: {
                "name": "p_ibeacon",
            },
            13: {
                "name": "p_eddystone",
            },
        },
        "wiced_20706": {
            1: {
                "name": "protocol",
            },
            2: {
                "name": "system",
                1: {"name": "boot", "textname": "BOOT",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"}]},
                2: {"name": "error", "textname": "ERR",
                    "parameters": [{"type": "uint16", "name": "error", "textname": "E"}]},
                3: {"name": "factory_reset_complete", "textname": "RFAC", "parameters": []},
                4: {"name": "factory_test_entered", "textname": "TFAC",
                    "parameters": [{"type": "uint32", "name": "app", "textname": "E"},
                                   {"type": "uint32", "name": "stack", "textname": "S"},
                                   {"type": "uint16", "name": "protocol", "textname": "P"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"},
                                   {"type": "uint8", "name": "cause", "textname": "C"}]},
                5: {"name": "dump_blob", "textname": "DBLOB",
                    "parameters": [{"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "offset", "textname": "O"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
            },
            3: {
                "name": "dfu",
                1: {"name": "boot", "textname": "BDFU",
                    "parameters": [{"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "valid", "textname": "V"},
                                   {"type": "uint8", "name": "bootloader", "textname": "B"},
                                   {"type": "uint8", "name": "hardware", "textname": "H"}]},
            },
            4: {
                "name": "gap",
                1: {"name": "whitelist_entry", "textname": "WL",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "adv_state_changed", "textname": "ASC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                3: {"name": "scan_state_changed", "textname": "SSC",
                    "parameters": [{"type": "uint8", "name": "state", "textname": "S"},
                                   {"type": "uint8", "name": "reason", "textname": "R"}]},
                4: {"name": "scan_result", "textname": "S",
                    "parameters": [{"type": "uint8", "name": "result_type", "textname": "R"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "address_type", "textname": "T"},
                                   {"type": "int8", "name": "rssi", "textname": "S"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "uint8a", "name": "data", "textname": "D"}]},
                5: {"name": "connected", "textname": "C",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"},
                                   {"type": "uint8", "name": "bond", "textname": "B"}]},
                6: {"name": "disconnected", "textname": "DIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                7: {"name": "connection_update_requested", "textname": "UCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval_min", "textname": "I"},
                                   {"type": "uint16", "name": "interval_max", "textname": "X"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
                8: {"name": "connection_updated", "textname": "CU",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "interval", "textname": "I"},
                                   {"type": "uint16", "name": "slave_latency", "textname": "L"},
                                   {"type": "uint16", "name": "supervision_timeout", "textname": "O"}]},
            },
            5: {
                "name": "gatts",
                1: {"name": "discover_result", "textname": "DL",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "data_written", "textname": "W",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                3: {"name": "indication_confirmed", "textname": "IC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"}]},
                4: {"name": "db_entry_blob", "textname": "DGATT",
                    "parameters": [{"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "permissions", "textname": "P"},
                                   {"type": "uint16", "name": "length", "textname": "L"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            },
            6: {
                "name": "gattc",
                1: {"name": "discover_result", "textname": "DR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "attr_handle_rel", "textname": "R"},
                                   {"type": "uint16", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "properties", "textname": "P"},
                                   {"type": "uint8a", "name": "uuid", "textname": "U"}]},
                2: {"name": "remote_procedure_complete", "textname": "RPC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                3: {"name": "data_received", "textname": "D",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint8", "name": "source", "textname": "S"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "write_response", "textname": "WRR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "attr_handle", "textname": "H"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
            },
            7: {
                "name": "smp",
                1: {"name": "bond_entry", "textname": "B",
                    "parameters": [{"type": "uint8", "name": "handle", "textname": "B"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"}]},
                2: {"name": "pairing_requested", "textname": "P",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "mode", "textname": "M"},
                                   {"type": "uint8", "name": "bonding", "textname": "B"},
                                   {"type": "uint8", "name": "keysize", "textname": "K"},
                                   {"type": "uint8", "name": "pairprop", "textname": "P"}]},
                3: {"name": "pairing_result", "textname": "PR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "result", "textname": "R"}]},
                4: {"name": "encryption_status", "textname": "ENC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "status", "textname": "S"}]},
                5: {"name": "passkey_display_requested", "textname": "PKD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint32", "name": "passkey", "textname": "P"}]},
                6: {"name": "passkey_entry_requested", "textname": "PKE",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                7: {"name": "pin_entry_requested", "textname": "BTPIN",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"}]},
            },
            8: {
                "name": "l2cap",
                1: {"name": "connection_requested", "textname": "LCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "local", "textname": "L"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                2: {"name": "connection_response", "textname": "LC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "response", "textname": "R"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "mtu", "textname": "M"},
                                   {"type": "uint16", "name": "mps", "textname": "P"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                3: {"name": "data_received", "textname": "LD",
                    "parameters": [{"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                4: {"name": "disconnected", "textname": "LDIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                5: {"name": "rx_credits_low", "textname": "LRCL",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                6: {"name": "tx_credits_received", "textname": "LTCR",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "credits", "textname": "Z"}]},
                7: {"name": "command_rejected", "textname": "LREJ",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "channel", "textname": "N"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
            },
            9: {
                "name": "gpio",
                1: {"name": "interrupt", "textname": "INT",
                    "parameters": [{"type": "uint8", "name": "port", "textname": "P"},
                                   {"type": "uint8", "name": "trigger", "textname": "T"},
                                   {"type": "uint8", "name": "logic", "textname": "L"},
                                   {"type": "uint32", "name": "runtime", "textname": "R"},
                                   {"type": "uint16", "name": "fraction", "textname": "F"}]},
            },
            10: {
                "name": "p_cyspp",
                1: {"name": "status", "textname": ".CYSPP",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            11: {
                "name": "p_cycommand",
                1: {"name": "status", "textname": ".CYCOM",
                    "parameters": [{"type": "uint8", "name": "status", "textname": "S"}]},
            },
            12: {
                "name": "p_ibeacon",
            },
            13: {
                "name": "p_eddystone",
            },
            14: {
                "name": "bt",
                1: {"name": "inquiry_result", "textname": "BTIR",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "uint32", "name": "cod", "textname": "C"}]},
                2: {"name": "name_result", "textname": "BTINR",
                    "parameters": [{"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "string", "name": "name", "textname": "N"}]},
                3: {"name": "inquiry_complete", "textname": "BTIC", "parameters": []},
                4: {"name": "connected", "textname": "BTCON",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "bond", "textname": "B"}]},
                5: {"name": "connection_status", "textname": "BTCS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "macaddr", "name": "address", "textname": "A"},
                                   {"type": "uint8", "name": "type", "textname": "T"},
                                   {"type": "uint8", "name": "bond", "textname": "B"},
                                   {"type": "uint8", "name": "role", "textname": "R"},
                                   {"type": "uint8", "name": "sniff", "textname": "S"}]},
                6: {"name": "connection_failed", "textname": "BTCF",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
                7: {"name": "disconnected", "textname": "BTDIS",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint16", "name": "reason", "textname": "R"}]},
            },
            15: {
                "name": "p_rfcomm",
                1: {"name": "data_received", "textname": ".RFD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                2: {"name": "modem_status", "textname": ".RFM",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            },
            16: {
                "name": "p_a2dp",
                1: {"name": "data_received", "textname": ".A2DPD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
                2: {"name": "stream_started", "textname": ".A2DPSTART",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                3: {"name": "stream_stopped", "textname": ".A2DPSTOP",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"}]},
                4: {"name": "codec_config", "textname": ".A2DPCODEC",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "uint8", "name": "codec_id", "textname": "I"},
                                   {"type": "uint8a", "name": "cie_data", "textname": "D"}]},
            },
            17: {
                "name": "p_avrcp",
                1: {"name": "data_received", "textname": ".AVRCPD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            },
            18: {
                "name": "p_hfp",
                1: {"name": "data_received", "textname": ".HFPD",
                    "parameters": [{"type": "uint8", "name": "conn_handle", "textname": "C"},
                                   {"type": "longuint8a", "name": "data", "textname": "D"}]},
            }
        }
    }

    @classmethod
    def getMethodByName(cls, platform, name):
        parts = name.split('_', 2)
        if len(parts) < 3:
            raise ProtocolException(
                "Invalid method name '%s' specified, format must be similar to 'cmd_system_ping'" % name)

        if platform not in Protocol.commands:
            raise ProtocolException("Unknown platform '%s'" % platform)

        if parts[0] in ["cmd", "rsp"]:
            search = Protocol.commands[platform]
        elif parts[0] == "evt":
            search = Protocol.events[platform]
        else:
            raise ProtocolException("Invalid method type '%s' specified, must be 'cmd', 'rsp', or 'evt'" % parts[0])

        # group is "p_cyspp" or "p_ibeacon" or similar, adjust name
        if parts[1] == "p":
            temp = parts[2].split('_', 1)
            parts[1] += "_" + temp[0]
            parts[2] = temp[1]

        for group in search:
            if type(group) != int: continue
            if search[group]["name"] == parts[1]:
                for method in search[group]:
                    if type(method) != int: continue
                    if search[group][method]["name"] == parts[2]:
                        search[group][method]["group"] = group
                        search[group][method]["method"] = method
                        return search[group][method]

        # not found in table
        raise ProtocolException("Method with name '%s' not found" % name)

    @classmethod
    def getCommandByName(cls, platform, name):
        return Protocol.getMethodByName(platform, "cmd_%s" % name)

    @classmethod
    def getEventByName(cls, platform, name):
        return Protocol.getMethodByName(platform, "evt_%s" % name)

    @classmethod
    def getCommandByTextName(cls, platform, name):
        if platform not in Protocol.commands:
            raise ProtocolException("Unknown platform '%s'" % platform)
        for group in Protocol.commands[platform]:
            if type(group) != int: continue
            for method in Protocol.commands[platform][group]:
                if type(method) != int: continue
                if Protocol.commands[platform][group][method]["textname"] == name.upper():
                    Protocol.commands[platform][group][method]["group"] = group
                    Protocol.commands[platform][group][method]["method"] = method
                    return Protocol.commands[platform][group][method]

        # not found in table
        raise ProtocolException("Command method with text name '%s' not found" % name)

    @classmethod
    def getEventByTextName(cls, platform, name):
        if platform not in Protocol.events:
            raise ProtocolException("Unknown platform '%s'" % platform)
        for group in Protocol.events[platform]:
            if type(group) != int: continue
            for method in Protocol.events[platform][group]:
                if type(method) != int: continue
                if Protocol.events[platform][group][method]["textname"] == name.upper():
                    Protocol.events[platform][group][method]["group"] = group
                    Protocol.events[platform][group][method]["method"] = method
                    return Protocol.events[platform][group][method]

        # not found in table
        raise ProtocolException("Event method with text name '%s' not found" % name)

    @classmethod
    def getCommandByIds(cls, platform, group, method):
        if platform not in Protocol.commands:
            raise ProtocolException("Unknown platform '%s'" % platform)
        if group in Protocol.commands[platform] and method in Protocol.commands[platform][group]:
            Protocol.commands[platform][group][method]["group"] = group
            Protocol.commands[platform][group][method]["method"] = method
            return Protocol.commands[platform][group][method]

        # not found in table
        raise ProtocolException("Command method with IDs %d/%d not found" % (group, method))

    @classmethod
    def getEventByIds(cls, platform, group, method):
        if platform not in Protocol.events:
            raise ProtocolException("Unknown platform '%s'" % platform)
        if group in Protocol.events[platform] and method in Protocol.events[platform][group]:
            Protocol.events[platform][group][method]["group"] = group
            Protocol.events[platform][group][method]["method"] = method
            return Protocol.events[platform][group][method]

        # not found in table
        raise ProtocolException("Event method with IDs %d/%d not found" % (group, method))


class Packet():
    EZS_PACKET_TYPE_COMMAND = 0
    EZS_PACKET_TYPE_RESPONSE = 1
    EZS_PACKET_TYPE_EVENT = 2
    EZS_PACKET_TYPE_NAMES = ["command", "response", "event"]
    EZS_PACKET_TYPE_PREFIXES = ["cmd", "rsp", "evt"]

    EZS_API_FORMAT_TEXT = 0
    EZS_API_FORMAT_BINARY = 1

    EZS_MEMORY_SCOPE_RAM = 0
    EZS_MEMORY_SCOPE_FLASH = 1
    EZS_MEMORY_SCOPE_NAMES = ["ram", "flash"]

    EZS_ORIGIN_ASSEMBLY = 0
    EZS_ORIGIN_BINARY = 1
    EZS_ORIGIN_TEXT = 2
    EZS_ORIGIN_NAMES = ["assembly", "binary", "text"]

    def __getitem__(self, i):
        return self.payload[i]

    def __init__(self, command=None, memscope=EZS_MEMORY_SCOPE_RAM, platform="psoc4proc_ble", **kwargs):
        self.entry = None
        self.type = None
        self.scope = None
        self.payloadLength = None
        self.group = None
        self.method = None
        self.payload = dotdict()

        self.platform = None
        self.origin = None
        self.binaryByteArray = None
        self.textString = None
        self.textSublength = None
        self.textName = None
        self.textPayload = dotdict()

        if command != None:
            self.buildOutgoingFromArgs(command, memscope, platform, **kwargs)

    def __repr__(self):
        argList = None
        if self.type == self.EZS_PACKET_TYPE_COMMAND or self.type == self.EZS_PACKET_TYPE_RESPONSE:
            if self.platform == None:
                buf = "[%s packet, uninitialized platform" % self.EZS_PACKET_TYPE_NAMES[self.type]
            elif self.group == None:
                buf = "[%s %s packet, uninitialized group ID" % (self.platform, self.EZS_PACKET_TYPE_NAMES[self.type])
            elif self.group not in Protocol.commands[self.platform]:
                buf = "[%s %s packet, unknown group ID %d" % (
                self.platform, self.EZS_PACKET_TYPE_NAMES[self.type], self.group)
            elif self.method == None:
                buf = "[%s %s packet in group %d, uninitialized method ID" % (
                self.platform, self.EZS_PACKET_TYPE_NAMES[self.type], self.group)
            elif self.method not in Protocol.commands[self.platform][self.group]:
                buf = "[%s %s packet in group %d, unknown method ID %d" % (
                self.platform, self.EZS_PACKET_TYPE_NAMES[self.type], self.group, self.method)
            else:
                buf = "[%s.%s_%s_%s (%d/%d) from %s (scope=%s)" % ( \
                    self.platform, \
                    self.EZS_PACKET_TYPE_PREFIXES[self.type], \
                    Protocol.commands[self.platform][self.group]["name"], \
                    Protocol.commands[self.platform][self.group][self.method]["name"], \
                    self.group, self.method, self.EZS_ORIGIN_NAMES[self.origin],
                    self.EZS_MEMORY_SCOPE_NAMES[self.scope])
                if self.type == self.EZS_PACKET_TYPE_COMMAND:
                    # copy (not directly assign!) parameter list definition to working argument list
                    argList = list(Protocol.commands[self.platform][self.group][self.method]["parameters"])
                else:
                    # copy (not directly assign!) parameter list definition to working argument list
                    argList = list(Protocol.commands[self.platform][self.group][self.method]["returns"])
                    argList.insert(0, {"type": 'uint16', "name": 'result', "textname": '_'})

        elif self.type == self.EZS_PACKET_TYPE_EVENT:
            if self.platform == None:
                buf = "[event packet, uninitialized platform"
            elif self.group == None:
                buf = "[%s event packet, uninitialized group ID" % self.platform
            elif self.group not in Protocol.events[self.platform]:
                buf = "[%s event packet, unknown group ID %d" % (self.platform, self.group)
            elif self.method == None:
                buf = "[%s event packet, uninitialized method ID"
            elif self.method not in Protocol.events[self.platform][self.group]:
                buf = "[%s event packet in group %d, unknown method ID %d" % (self.platform, self.group, self.method)
            else:
                buf = "[%s.evt_%s_%s (%d/%d) from %s" % ( \
                    self.platform, \
                    Protocol.events[self.platform][self.group]["name"], \
                    Protocol.events[self.platform][self.group][self.method]["name"], \
                    self.group, self.method, self.EZS_ORIGIN_NAMES[self.origin])
                # copy (not directly assign!) parameter list definition to working argument list
                argList = list(Protocol.events[self.platform][self.group][self.method]["parameters"])

        else:
            buf = "[uninitialized packet"

        if argList != None:
            for x in argList:
                if x["name"] not in self.payload:
                    buf += ", %s: MISSING" % x["name"]
                else:
                    if x["type"] == "macaddr":
                        buf += ", %s: %s" % (
                        x["name"], ":".join(['%02X' % b for b in reversed(self.payload[x["name"]])]))
                    elif x["type"] in ['uint8a', 'longuint8a']:
                        if type(self.payload[x["name"]]) == str:
                            buf += ", %s: %s" % (x["name"], "".join(['%02X' % ord(b) for b in self.payload[x["name"]]]))
                        else:
                            buf += ", %s: %s" % (x["name"], "".join(['%02X' % b for b in self.payload[x["name"]]]))
                    elif x["type"] in ['string', 'longstring']:
                        buf += ", %s: %s" % (x["name"], self.payload[x["name"]])
                    else:
                        buf += ", %s: 0x%X" % (x["name"], self.payload[x["name"]])

        buf += "]"
        return buf

    def getPayloadLengthFromBinaryBuffer(self, buf):
        # all valid packets must be at least 5 bytes (4 header + 1 checksum)
        if len(buf) < 5:
            raise PacketException("Binary packet buffer is not properly initialized with header data", self)

        # packet length is 11-bit field spread across two
        return ((buf[0] & 0x7) << 8) + buf[1]

    def buildOutgoingFromArgs(self, command, memscope=EZS_MEMORY_SCOPE_RAM, platform="psoc4proc_ble", **kwargs):
        self.entry = Protocol.getCommandByName(platform, command)
        argList = self.entry["parameters"]
        packFormat = '<%s' % ''.join([Protocol.dataTypeMap[z["type"]] for z in argList])
        self.type = Packet.EZS_PACKET_TYPE_COMMAND
        self.payloadLength = struct.calcsize(packFormat)
        self.group = self.entry["group"]
        self.method = self.entry["method"]
        self.origin = Packet.EZS_ORIGIN_ASSEMBLY
        self.scope = memscope
        self.platform = platform

        byteList = [0xC0, self.payloadLength, self.group, self.method]
        packValues = []
        suffix = None

        # start text string with command name
        self.textString = self.entry["textname"]

        # apply correct memory scope if flash is specified
        if memscope == Packet.EZS_MEMORY_SCOPE_FLASH:
            byteList[0] = 0xD0
            self.textString = self.textString + '$'

        for arg in argList:
            if arg["name"] not in kwargs:
                raise PacketException("Missing required command argument '%s' (type=%s)" % (arg["name"], arg["type"]),
                                      self)
            if arg["type"] in ['uint8a', 'string', 'longuint8a', 'longstring']:
                packValues.append(len(kwargs[arg["name"]]))
                if sys.version_info < (3, 0):
                    # Python 2.x
                    if arg["type"] in ['string', 'longstring']:
                        suffix = kwargs[arg["name"]].encode('ascii', 'ignore')
                    else:
                        suffix = kwargs[arg["name"]]
                else:
                    # Python 3.x
                    suffix = kwargs[arg["name"]]
                self.payloadLength += len(kwargs[arg["name"]])
                byteList[0] += self.payloadLength >> 8
                byteList[1] = self.payloadLength % 256
                if arg["type"] in ["string", "longstring"]:
                    # raw data copy for these special datatypes
                    self.textPayload[arg["textname"]] = kwargs[arg["name"]]
                else:
                    # byte to ASCII hex conversion for normal data blobs
                    self.textPayload[arg["textname"]] = ''.join(['%02X' % b for b in bytearray(kwargs[arg["name"]])])
            else:
                if arg["type"] == "macaddr":
                    self.textPayload[arg["textname"]] = ''.join(
                        reversed(['%02X' % b for b in bytearray(kwargs[arg["name"]])]))
                    if sys.version_info < (3, 0):
                        # Python 2.x
                        packValues.append("".join(map(chr, kwargs[arg["name"]])))
                    else:
                        # Python 3.x
                        packValues.append(bytes(kwargs[arg["name"]]))
                else:
                    self.textPayload[arg["textname"]] = ('{:0%dX}' % (Protocol.dataTypeWidth[arg["type"]] * 2)).format(
                        kwargs[arg["name"]], "x")
                    packValues.append(kwargs[arg["name"]])

            # append this argument to the literal argument list
            self.payload[arg["name"]] = kwargs[arg["name"]]

            # append this argument to the text string
            self.textString = self.textString + (",%s=%s" % (arg["textname"], self.textPayload[arg["textname"]]))

        # end text string
        self.textString = self.textString + "\r\n"

        # assemble binary byte array
        self.binaryByteArray = byteList
        self.binaryByteArray += bytearray(struct.pack(packFormat, *packValues))
        if suffix != None:
            if type(suffix) is str:
                if sys.version_info < (3, 0):
                    # Python 2.x
                    self.binaryByteArray += bytearray(suffix)
                else:
                    # Python 3.x
                    self.binaryByteArray += bytearray(suffix, "utf-8")
            else:
                self.binaryByteArray += suffix

        # calculate and append checksum
        checksum = 0x99
        for b in self.binaryByteArray:
            checksum += b
        self.binaryByteArray.append(checksum % 256)

    def buildOutgoingFromTextBuffer(self, buf, platform="psoc4proc_ble"):
        if type(buf) == str:
            self.textString = buf
        else:
            self.textString = "".join(map(chr, buf))
        self.origin = Packet.EZS_ORIGIN_TEXT
        self.scope = Packet.EZS_MEMORY_SCOPE_RAM
        self.platform = platform
        rePacket = re.compile('^([a-zA-Z0-9\\$\\.\\/]+)([^\r\n]*)\r\n$')
        reMatch = rePacket.match(self.textString)

        if not reMatch:
            raise PacketException("Malformed text command packet: '%s'" % self.textString, self)
        self.textName = reMatch.group(1).upper()
        if self.textName[-1] == '$':
            self.scope = Packet.EZS_MEMORY_SCOPE_FLASH
            self.textName = self.textName[:-1]

        # command packet
        self.type = self.EZS_PACKET_TYPE_COMMAND
        rePayload = re.compile('^,*(.*)$')
        payloadMatch = rePayload.match(reMatch.group(2))
        if not payloadMatch:
            raise PacketException("Malformed text command packet: '%s'" % self.textString, self)
        argText = payloadMatch.group(1)

        # attempt to find this packet in the API definition
        self.entry = Protocol.getCommandByTextName(self.platform, self.textName)
        self.group = self.entry["group"]
        self.method = self.entry["method"]

        # parse all text parameters from this packet
        reArgs = re.compile('([a-zA-Z])=([^,]*)');
        for argMatch in reArgs.finditer(argText):
            argName = argMatch.group(1).upper()
            if argName in self.textPayload:
                raise PacketException("Text argument '%s' already encountered in payload '%s'" % (argName, argText),
                                      self)
            if argName not in [x["textname"] for x in self.entry["parameters"]]:
                raise PacketException(
                    "Text argument '%s' from payload '%s' not expected for this command" % (argName, argText), self)
            self.textPayload[argMatch.group(1).upper()] = argMatch.group(2)

        # convert to binary based on API definition
        missing = []
        for x in self.entry["parameters"]:
            if x["textname"] in self.textPayload:
                if x["type"] in ["uint8a", "longuint8a"]:
                    self.payload[x["name"]] = bytearray.fromhex(self.textPayload[x["textname"]])
                elif x["type"] in ["string", "longstring"]:
                    self.payload[x["name"]] = self.textPayload[x["textname"]]
                elif x["type"] == "macaddr":
                    self.payload[x["name"]] = list(reversed(bytearray.fromhex(self.textPayload[x["textname"]])))
                else:
                    self.payload[x["name"]] = int(self.textPayload[x["textname"]], 16)
            else:
                # some argument is missing, can't safely convert from text to binary
                missing.append(x)

        if len(missing) > 0:
            raise PacketException(
                "Missing text arguments: %s" % ", ".join(["%s (%s)" % (x["name"], x["textname"]) for x in missing]),
                self)

        # reuse other method to do the legwork of filling in the rest of the packet details
        self.buildOutgoingFromArgs(Protocol.commands[self.platform][self.group]["name"] + "_" +
                                   Protocol.commands[self.platform][self.group][self.method]["name"],
                                   platform=self.platform, memscope=self.scope, **self.payload)

    def buildIncomingFromBinaryBuffer(self, buf, platform="psoc4proc_ble"):
        self.binaryByteArray = bytearray(buf)
        self.origin = Packet.EZS_ORIGIN_BINARY
        self.platform = platform
        payloadLength = self.getPayloadLengthFromBinaryBuffer(buf)

        if len(buf) != payloadLength + 5:
            raise PacketException("Malformed binary packet, invalid length", self)

        # assign known packet metadata from header
        self.payloadLength = payloadLength
        self.group = buf[2]
        self.method = buf[3]

        # determine packet type (response/event) and identify it
        argList = None
        textSub = ""
        if (buf[0] & 0xC0) == 0xC0:
            # response packet has first 2 MSB's set (0xC0)
            self.type = self.EZS_PACKET_TYPE_RESPONSE

            # assume RAM scope as default
            self.scope = self.EZS_MEMORY_SCOPE_RAM

            # check for flash memory scope bit
            if buf[0] & 0x30 == 0x10:
                self.scope = self.EZS_MEMORY_SCOPE_FLASH

            # store API definition entry reference in packet
            self.entry = Protocol.getCommandByIds(self.platform, buf[2], buf[3])

            # begin text string
            self.textString = "@R,"
            textSub = "," + self.entry["textname"]

            if self.scope == self.EZS_MEMORY_SCOPE_FLASH:
                textSub = textSub + "$"

            # copy (not directly assign!) parameter list definition to working argument list
            argList = list(self.entry["returns"])
            argList.insert(0, {"type": 'uint16', "name": 'result', "textname": '_'})

        elif (buf[0] & 0xC0) == 0x80:
            # event packet has only first MSB set and second MSB clear (0x80)
            self.type = self.EZS_PACKET_TYPE_EVENT

            # store API definition entry reference in packet
            self.entry = Protocol.getEventByIds(self.platform, buf[2], buf[3])

            # begin text string
            self.textString = "@E,"
            textSub = "," + self.entry["textname"]

            # copy (not directly assign!) parameter list definition to working argument list
            argList = list(self.entry["parameters"])

        else:
            # packet has neither of first two MSB's set, which is invalid
            raise PacketException("Unidentifiable packet type, SOF byte=0x%02X" % buf[0], self)

        # proceed if argument list is known
        if argList != None:
            unpackFormat = '<%s' % ''.join([Protocol.dataTypeMap[z["type"]] for z in argList])
            argValues = struct.unpack_from(unpackFormat, self.binaryByteArray[4:])
            for x in range(len(argList)):
                if argList[x]["type"] in ["uint8a", "longuint8a", "string", "longstring"]:
                    start = 4 + struct.calcsize(unpackFormat)
                    if start + argValues[x] != self.payloadLength + 4:
                        # variable-length array does not fit properly within header-specified payload length
                        raise PacketException("Variable-length argument '%s' claims %d bytes but actually has %d" % (
                        argList[x]["name"], argValues[x], self.payloadLength - start + 4), self)
                    if argList[x]["type"] in ["string", "longstring"]:
                        # raw data copy and conversion to decoded string (NOT bytearray) for these special data types
                        self.payload[argList[x]["name"]] = self.binaryByteArray[start:start + argValues[x]].decode()
                        self.textPayload[argList[x]["textname"]] = self.binaryByteArray[
                                                                   start:start + argValues[x]].decode()
                    else:
                        # raw byte array slice for binary payload of normal data blob
                        self.payload[argList[x]["name"]] = self.binaryByteArray[start:start + argValues[x]]

                        # byte to ASCII hex conversion for normal data blobs
                        self.textPayload[argList[x]["textname"]] = ''.join(
                            ['%02X' % b for b in self.binaryByteArray[start:start + argValues[x]]])
                elif argList[x]["type"] == "macaddr":
                    self.payload[argList[x]["name"]] = list(bytearray(argValues[x]))
                    self.textPayload[argList[x]["textname"]] = ''.join(
                        ['%02X' % b for b in reversed(bytearray(argValues[x]))])
                else:
                    self.payload[argList[x]["name"]] = argValues[x]
                    self.textPayload[argList[x]["textname"]] = (
                                '{:0%dX}' % (Protocol.dataTypeWidth[argList[x]["type"]] * 2)).format(argValues[x], "x")

                # append this argument to the text string
                if argList[x]["textname"] == "_":
                    # result in a response, no name prefix
                    textSub = textSub + (",%s" % self.textPayload[argList[x]["textname"]])
                else:
                    textSub = textSub + (",%s=%s" % (argList[x]["textname"], self.textPayload[argList[x]["textname"]]))

        # calculate text string payload length value and end it
        self.textString = self.textString + ("%04X" % len(textSub)) + textSub + "\r\n"

    def buildIncomingFromTextBuffer(self, buf, platform="psoc4proc_ble"):
        self.textString = "".join(map(chr, buf))
        self.origin = Packet.EZS_ORIGIN_TEXT
        self.platform = platform
        rePacket = re.compile('^@([RE]),([0-9A-F]{4}),([A-Z0-9\\$\\.\\/]+)([^\r\n]*)\r\n$')
        reMatch = rePacket.match(self.textString)

        if not reMatch:
            raise PacketException("Malformed text packet: '%s'" % self.textString, self)

        self.textSublength = int(reMatch.group(2), 16)
        self.textName = reMatch.group(3)
        argList = None

        if self.textSublength != (len(reMatch.group(3)) + len(reMatch.group(4)) + 1):
            raise PacketException("Text length specified %d payload bytes but %d found, detail: %s" % \
                                  (self.textSublength, len(reMatch.group(3)) + len(reMatch.group(4)) + 1,
                                   self.textString), self)

        if reMatch.group(1) == "R":
            # response packet
            self.type = self.EZS_PACKET_TYPE_RESPONSE
            rePayload = re.compile('^,([0-9A-F]{4}),*(.*)$')
            payloadMatch = rePayload.match(reMatch.group(4))
            if not payloadMatch:
                raise PacketException("Malformed text response packet: '%s'" % self.textString, self)
            self.textPayload['_'] = payloadMatch.group(1)
            argText = payloadMatch.group(2)

            # assume RAM scope as default
            self.scope = self.EZS_MEMORY_SCOPE_RAM

            # check for flash scope character
            if self.textName[-1] == '$':
                self.scope = self.EZS_MEMORY_SCOPE_FLASH
                self.textName = self.textName[0:-1]

            # attempt to get method details based on text name
            self.entry = Protocol.getCommandByTextName(self.platform, self.textName)
            self.group = self.entry["group"]
            self.method = self.entry["method"]

            # copy (not directly assign!) parameter list definition to working argument list
            argList = list(self.entry["returns"])
            argList.insert(0, {"type": 'uint16', "name": 'result', "textname": '_'})

        elif reMatch.group(1) == "E":
            # event packet
            self.type = self.EZS_PACKET_TYPE_EVENT
            rePayload = re.compile('^,*(.*)$')
            payloadMatch = rePayload.match(reMatch.group(4))
            if not payloadMatch:
                raise PacketException("Malformed text event packet: '%s'" % self.textString, self)
            argText = payloadMatch.group(1)

            # attempt to find this packet in the API definition
            self.entry = Protocol.getEventByTextName(self.platform, self.textName)
            self.group = self.entry["group"]
            self.method = self.entry["method"]

            # copy (not directly assign!) parameter list definition to working argument list
            argList = list(self.entry["parameters"])

        else:
            raise PacketException("Invalid incoming text packet type, SOF match='%s'" % reMatch.group(1), self)

        # parse all text parameters from this packet
        reArgs = re.compile('([A-Z])=([^,]*)');
        for argMatch in reArgs.finditer(argText):
            if argMatch.group(1) in self.textPayload:
                raise PacketException(
                    "Text argument '%s' already encountered in payload '%s'" % (argMatch.group(1), argText), self)
            else:
                self.textPayload[argMatch.group(1)] = argMatch.group(2)

        # convert to binary based on API definition
        if argList != None:
            for x in argList:
                if x["textname"] in self.textPayload:
                    if x["type"] in ["uint8a", "longuint8a"]:
                        self.payload[x["name"]] = bytearray.fromhex(self.textPayload[x["textname"]])
                    elif x["type"] in ["string", "longstring"]:
                        self.payload[x["name"]] = self.textPayload[x["textname"]]
                    elif x["type"] == "macaddr":
                        self.payload[x["name"]] = list(reversed(bytearray.fromhex(self.textPayload[x["textname"]])))
                    else:
                        self.payload[x["name"]] = int(self.textPayload[x["textname"]], 16)


class API():
    EZS_BINARY_SOF_MASK = 0x80
    EZS_TEXT_SOF_CHAR = 0x40
    EZS_BINARY_CHECKSUM_INITIAL_VALUE = 0x99

    EZS_OUTPUT_RESULT_DATA_WRITTEN = 0
    EZS_OUTPUT_RESULT_RESPONSE_PENDING = 1

    EZS_INPUT_RESULT_BYTE_READ = 2
    EZS_INPUT_RESULT_NO_DATA = 3

    EZS_PARSE_RESULT_BYTE_IGNORED = 4
    EZS_PARSE_RESULT_IN_PROGRESS = 5
    EZS_PARSE_RESULT_PACKET_COMPLETE = 6

    def __init__(self, rxPacketHandler=None, txPacketHandler=None, hardwareOutput=None, hardwareInput=None):
        self.rxPacketHandler = rxPacketHandler
        self.txPacketHandler = txPacketHandler
        self.hardwareOutput = hardwareOutput
        self.hardwareInput = hardwareInput

        self.lastTxPacket = None
        self.lastRxPacket = None

        self.defaults = dotdict()
        self.defaults.memscope = Packet.EZS_MEMORY_SCOPE_RAM  # used if argument=None
        self.defaults.platform = "psoc4proc_ble"
        self.defaults.rxtimeout = None  # wait forever, used if argument=False
        self.defaults.apiformat = Packet.EZS_API_FORMAT_BINARY  # used if argument=None
        self.defaults.consumeecho = 1  # enabled, used if argument=None

        self.reset()

    def reset(self):
        self.inBinaryPacket = False
        self.inTextPacket = False
        self.rxPacketBuffer = []
        self.rxPacketLengthExpected = 0
        self.rxPacketChecksum = 0
        self.lastOutputResult = None
        self.lastInputResult = None
        self.lastParseResult = None

    def parse(self, b, platform=None):
        if platform == None: platform = self.defaults.platform
        if type(b) is str:
            b = ord(b)

        # assume correct parsing
        result = self.EZS_PARSE_RESULT_IN_PROGRESS

        if self.inBinaryPacket or (b & self.EZS_BINARY_SOF_MASK) != 0:
            # print("B:%02X" % b)
            if not self.inBinaryPacket:
                # start of new binary packet
                self.inBinaryPacket = True
                self.rxPacketChecksum = self.EZS_BINARY_CHECKSUM_INITIAL_VALUE

                # reset packet and clear text packet status to be safe
                self.inTextPacket = False
                self.rxPacketBuffer[:] = []

            elif len(self.rxPacketBuffer) == 1:
                # length byte in binary packet header
                self.rxPacketLengthExpected = 5 + b + ((self.rxPacketBuffer[0] & 0x7) << 8)

            # append incoming binary byte to packet buffer
            self.rxPacketBuffer.append(b)

            if len(self.rxPacketBuffer) == self.rxPacketLengthExpected:
                # verify checksum
                if self.rxPacketChecksum != b:
                    raise ParseException("Invalid checksum byte 0x%02X, expecting 0x%02X" % (self.rxPacketChecksum, b))
                else:
                    self.lastRxPacket = Packet()
                    self.lastRxPacket.buildIncomingFromBinaryBuffer(self.rxPacketBuffer, platform)
                    if self.rxPacketHandler != None:
                        self.rxPacketHandler(self.lastRxPacket)
                    result = self.EZS_PARSE_RESULT_PACKET_COMPLETE;

                    # reset packet
                    self.inBinaryPacket = False
                    self.rxPacketBuffer[:] = []

            else:
                # compute running checksum
                self.rxPacketChecksum += b
                self.rxPacketChecksum %= 256

        elif self.inTextPacket or b == self.EZS_TEXT_SOF_CHAR:
            # print("T:%02X,%c" % (b, b))
            if not self.inTextPacket:
                # start of new text packet
                self.inTextPacket = True
                self.rxPacketBuffer[:] = []

            # append incoming text byte to packet buffer
            self.rxPacketBuffer.append(b)

            if b == 0x0A:
                # end of text packet in progress
                self.lastRxPacket = Packet()
                self.lastRxPacket.buildIncomingFromTextBuffer(self.rxPacketBuffer, platform)
                if self.rxPacketHandler != None:
                    self.rxPacketHandler(self.lastRxPacket)
                result = self.EZS_PARSE_RESULT_PACKET_COMPLETE

                # reset packet
                self.inTextPacket = False
                self.rxPacketBuffer[:] = []

        else:
            result = self.EZS_PARSE_RESULT_BYTE_IGNORED

        self.lastParseResult = result
        return result

    def sendCommand(self, command, memscope=None, platform=None, apiformat=None, **kwargs):
        if memscope == None: memscope = self.defaults.memscope
        if platform == None: platform = self.defaults.platform
        self.lastTxPacket = Packet(command, memscope, platform, **kwargs)
        if apiformat == None: apiformat = self.defaults.apiformat
        if self.txPacketHandler != None:
            self.txPacketHandler(self.lastTxPacket)
        if apiformat == Packet.EZS_API_FORMAT_BINARY:
            outputTuple = self.hardwareOutput(self.lastTxPacket.binaryByteArray)
        else:
            outputTuple = self.hardwareOutput(bytearray(self.lastTxPacket.textString, "utf-8"))
        self.lastOutputResult = outputTuple[1]
        return outputTuple

    def sendPacket(self, packet, apiformat=None):
        self.lastTxPacket = packet
        if apiformat == None: apiformat = self.defaults.apiformat
        if self.txPacketHandler != None:
            self.txPacketHandler(self.lastTxPacket)
        if apiformat == Packet.EZS_API_FORMAT_BINARY:
            outputTuple = self.hardwareOutput(self.lastTxPacket.binaryByteArray)
        else:
            outputTuple = self.hardwareOutput(bytearray(self.lastTxPacket.textString, "utf-8"))
        self.lastOutputResult = outputTuple[1]
        return outputTuple

    def consumeEcho(self, data, rxtimeout=False):
        read = 0
        readResult = self.EZS_INPUT_RESULT_NO_DATA
        readData = bytearray()
        if rxtimeout is False: rxtimeout = self.defaults.rxtimeout
        while read < len(data):
            (b, readResult) = self.hardwareInput(rxtimeout)
            if b == None:
                # no data available to read
                raise ParseException("Incoming echo data after '%s' is not available as expected in '%s'" % (
                readData, bytearray(data, "utf-8")))
            if type(b) is str:
                # Python 2.x compatibility
                b = ord(b)
            readData.append(b)
            self.lastInputResult = readResult
            if readResult == self.EZS_INPUT_RESULT_BYTE_READ:
                if b == ord(data[read]):
                    read = read + 1
                else:
                    # incoming data doesn't match expected data
                    raise ParseException(
                        "Incoming echo data 0x%02X in '%s' does not match expected byte 0x%02X in '%s'" % (
                        b, readData, ord(data[read]), bytearray(data, "utf-8")))

        # send back the count of bytes actually read
        return read

    def waitPacket(self, platform=None, rxtimeout=False):
        readResult = self.EZS_INPUT_RESULT_NO_DATA
        parseResult = None
        if platform == None: platform = self.defaults.platform
        if rxtimeout is False: rxtimeout = self.defaults.rxtimeout
        if rxtimeout == 0:
            (b, readResult) = self.hardwareInput(rxtimeout)
            self.lastInputResult = readResult
            if readResult == self.EZS_INPUT_RESULT_BYTE_READ:
                parseResult = self.parse(b, platform)
        else:
            while parseResult != self.EZS_PARSE_RESULT_PACKET_COMPLETE:
                (b, readResult) = self.hardwareInput(rxtimeout)
                self.lastInputResult = readResult
                if readResult == self.EZS_INPUT_RESULT_BYTE_READ:
                    parseResult = self.parse(b, platform)

        # send back results
        if parseResult == self.EZS_PARSE_RESULT_PACKET_COMPLETE:
            return (self.lastRxPacket, readResult, parseResult)
        else:
            return (None, readResult, parseResult)

    def waitResponse(self, response, platform=None, rxtimeout=False):
        # initialize to unique value (not valid waitPacket() return value)
        packet = False
        if platform == None: platform = self.defaults.platform

        # identify target response to wait for
        entry = Protocol.getCommandByName(platform, response)

        # keep polling for packets until we time out (None) or find a match
        while packet == False:
            (packet, readResult, parseResult) = self.waitPacket(platform, rxtimeout)
            if packet != None and not packet.entry is entry: packet = False

        # send back results
        return (packet, readResult, parseResult)

    def waitEvent(self, event, platform=None, rxtimeout=False):
        # initialize to unique value (not valid waitPacket() return value)
        packet = False
        if platform == None: platform = self.defaults.platform

        # identify target response to wait for
        entry = Protocol.getEventByName(platform, event)

        # keep polling for packets until we time out (None) or find a match
        while packet == False:
            (packet, readResult, parseResult) = self.waitPacket(platform=platform, rxtimeout=rxtimeout)
            if packet != None and not packet.entry is entry: packet = False

        return (packet, readResult, parseResult)

    def sendAndWait(self, command, memscope=None, platform=None, apiformat=None, consumeecho=None, rxtimeout=False,
                    **kwargs):
        if memscope == None: memscope = self.defaults.memscope
        if platform == None: platform = self.defaults.platform
        if apiformat == None: apiformat = self.defaults.apiformat
        if consumeecho == None: consumeecho = self.defaults.consumeecho
        if rxtimeout is False: rxtimeout = self.defaults.rxtimeout
        self.sendCommand(command, memscope, platform, apiformat, **kwargs)
        if apiformat == Packet.EZS_API_FORMAT_TEXT and consumeecho != 0:
            self.consumeEcho(self.lastTxPacket.textString, rxtimeout)
        return self.waitResponse(command, platform, rxtimeout)