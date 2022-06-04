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

def test_reference_vdm_1():
    # Example from Table C-1, port power role = 0, MessageID = 0
    reference = b"\x8F\x10\x01\xa0\x00\xFF"

    msg = parse(reference)
    assert isinstance(msg, Vendor_DefinedMessage)

    # Message header checks
    assert msg.header.num_data_obj == 1
    assert msg.header.message_id == 0
    assert msg.header.port_power_role == 0
    assert msg.header.specification_revision == SpecificationRevision.REV30
    assert msg.header.message_type == 0b1111

    # VDM header checks
    assert msg.vdm_header.vendor_id == 0xFF00
    assert msg.vdm_header.vdm_type == 1
    assert msg.vdm_header.structured_vdm_version == StructuredVDMVersion.REV20
    assert msg.vdm_header.object_position == 0
    assert msg.vdm_header.command_type == VDMCommandType.REQ
    assert msg.vdm_header.command == VDMCommand.DISCOVER_IDENTITY

    assert msg.encode() == reference
