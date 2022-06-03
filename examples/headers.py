#!/usr/bin/env python

from pyusbpd.message import *

msg = GoodCRCMessage()
msg.parse(b"\x41\x0C")
print(msg.header)

msg = Source_CapabilitiesMessage()
msg.parse(b"\x61\x11\x96\x90\x01\x36\x3e\x61\x73\x9c")
print(msg)

msg = Source_CapabilitiesMessage()
msg.parse(b"\x61\x21\xF0\x90\x01\x08\xC8\xA0\x04\x00")
print(msg)
