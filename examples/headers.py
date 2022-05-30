#!/usr/bin/env python

from pyusbpd.message import *
from pyusbpd.header import MessageHeader

hdr = MessageHeader()
hdr.parse(b"\x41\x0C")
print(hdr)

msg = GoodCRCMessage()
msg.parse(b"\x41\x0C")
print(msg.header)

msg = Source_CapabilitiesMessage()
msg.parse(b"\x61\x11\x96\x90\x01\x36\x3e\x61\x73\x9c")
print(msg)
