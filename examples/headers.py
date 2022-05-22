#!/usr/bin/env python

from pyusbpd.message import *

hdr = MessageHeader(b"\x41\x0C")
print(hdr)

msg = GoodCRCMessage(sop=0, raw=b"\x41\x0C")
print(msg.message_header)

msg = Message(sop=0, raw=b"\x6F\x2D\x01\x01\xAC\x05\x00\x00\x00\x00").decode()
print(msg.vdm_header)
