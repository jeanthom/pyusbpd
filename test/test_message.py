#!/usr/bin/env python

from pyusbpd.message import *
from pyusbpd.enum import *

def test_vdmheader_get_set():
    hdr = VDMHeader(bytearray(b"\x11\x81\x01\xFF"))
    assert hdr.vendor_id == 0xFF01
    assert hdr.vdm_type
    assert hdr.structured_vdm_version == StructuredVDMVersion.REV10
    assert hdr.command_type == VDMCommandType.REQ

def test_parse():
    msg = parse(b"\x61\x11\x96\x90\x01\x36\x3e\x61\x73\x9c")
    assert isinstance(msg, Source_CapabilitiesMessage)

    msg = parse(b"\x41\x0C")
    assert isinstance(msg, GoodCRCMessage)
