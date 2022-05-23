#!/usr/bin/env python

from pyusbpd.message import *
from pyusbpd.enum import *

def test_vdmheader_get_set():
    hdr = VDMHeader(bytearray(b"\x11\x81\x01\xFF"))
    assert hdr.vendor_id == 0xFF01
    assert hdr.vdm_type
    assert hdr.structured_vdm_version == StructuredVDMVersion.REV10
    assert hdr.command_type == VDMCommandType.REQ
