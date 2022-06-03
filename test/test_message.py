#!/usr/bin/env python

from pyusbpd.message import *
from pyusbpd.enum import *

def test_source_capabilitiesmessage_parse():
    msg = parse(b"\x61\x11\x96\x90\x01\x36\x3e\x61\x73\x9c")
    assert isinstance(msg, Source_CapabilitiesMessage)

def test_goodcrcmessage_parse():
    msg = parse(b"\x41\x0C")
    assert isinstance(msg, GoodCRCMessage)

def test_goodcrcmessage_encode():
    reference = b"\x41\x0C"
    msg = GoodCRCMessage()
    msg.parse(reference)
    encoded = msg.encode()
    assert encoded == reference
