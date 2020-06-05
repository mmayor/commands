#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-20 10:20:23
# @Author  : Your Name (you@example.org)
# @Link    : link
# @Version : 1.0.0

import os
import sys
# print("HELLOORLD")
print(sys.version_info, sys.version)

def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value # Instance of str



def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value # Instance of bytes


