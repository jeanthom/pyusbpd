from dataclasses import dataclass
from pyusbpd.enum import *
from pyusbpd.helpers import get_bit_from_array, get_int_from_array

__all__ = [
    "MessageHeader",
    "ExtendedMessageHeader",
    "VDMHeader",
]

@dataclass
class MessageHeader:
    """USB Power Delivery Message Header (6.2.1.1)"""
    message_type: int = 0
    port_data_role: PortDataRole = PortDataRole.UFP
    port_power_role: bool = False
    specification_revision: SpecificationRevision = SpecificationRevision.REV10
    cable_plug: bool = False
    message_id: int = 0
    num_data_obj: int = 0
    extended: bool = False

    def parse(self, raw: bytes):
        assert len(raw) == 2

        # USB PD r3.1 section numbers
        self.message_type = get_int_from_array(raw, width=5, offset=0) # 6.2.1.1.8
        self.port_data_role = PortDataRole(get_bit_from_array(raw, 5)) # 6.2.1.1.6
        self.specification_revision = SpecificationRevision(int(raw[0] >> 6)) # 6.2.1.1.5
        self.cable_plug = get_bit_from_array(raw, 8) # 6.2.1.1.7
        self.port_power_role = get_bit_from_array(raw, 8) # 6.2.1.1.4
        self.message_id = get_int_from_array(raw, width=3, offset=9) # 6.2.1.1.3
        self.num_data_obj = get_int_from_array(raw, width=3, offset=12) # 6.2.1.1.2
        self.extended = get_bit_from_array(raw, 15) # 6.2.1.1.1

    def encode(self) -> bytes:
        pass

    def __repr__(self):
        """Returns a string representation"""
        return f"""USB Power Delivery Message Header
---
Extended: {self.extended}
Number of Data Objects: {self.num_data_obj}
MessageID: {self.message_id}
Port Power Role: {self.port_power_role}
Cable Plug: {self.cable_plug}
Specification Revision: {self.specification_revision}
Port Data Role: {self.port_data_role}
Message Type: {self.message_type}"""

@dataclass
class ExtendedMessageHeader:
    """USB Power Delivery Extended Message Header (6.2.1.2)"""
    data_size: int = 0
    request_chunk: bool = False
    chunk_number: int = 0
    chunked: bool = False

    def parse(self, raw: bytes):
        assert len(raw) == 2

        # USB PD r3.1 section numbers
        self.data_size = get_int_from_array(raw, width=9, offset=0) # 6.2.1.2.4
        self.request_chunk = get_bit_from_array(raw, 10) # 6.2.1.2.3
        self.chunk_number = get_int_from_array(raw, width=4, offset=11) # 6.2.1.2.2
        self.chunked = get_bit_from_array(raw, 15) # 6.2.1.2.1

    def encode(self) -> bytes:
        pass

    def __repr__(self):
        """Returns a string representation"""
        return f"""USB Power Delivery Extended Message Header
---
Chunked: {self.chunked}
Chunk Number: {self.chunk_number}
Request Chunk: {self.request_chunk}
Data Size: {self.data_size}"""

@dataclass
class VDMHeader:
    vendor_id: int = 0
    vdm_type: bool = False
    structured_vdm_version: StructuredVDMVersion = StructuredVDMVersion.REV10
    vendor_use: int = 0
    object_position: int = 0
    command_type: VDMCommandType = VDMCommandType.REQ
    command: VDMCommand = VDMCommand.DISCOVER_IDENTITY

    def parse(self, raw: bytes):
        assert len(raw) == 4
        self.vendor_id = int(raw[3] << 8 | raw[2])
        self.vdm_type = bool(raw[1] & 0x80)
        if self.vdm_type:
            self.structured_vdm_version = StructuredVDMVersion((raw[1] & 0x60) >> 5)
            self.object_position = int(raw[1] & 0x07)
            self.command_type = VDMCommandType(raw[0] & 0xC0 >> 5)
            self.command = VDMCommand(raw[0] & 0x1F)
        else:
            self.vendor_use = int((raw[1] & 0x7F) << 8 | raw[0])

    def __repr__(self):
        if self.vdm_type: # Structured VDM
            return f"""Standard or Vendor ID: {self.vendor_id}
VDM Type: {self.vdm_type}
Structured VDM version: {self.structured_vdm_version}
Object Position: {self.object_position}
Command Type: {self.command_type}
Command: {self.command}"""
        if not self.vdm_type:
            return f"""Vendor ID: {self.vendor_id}
VDM Type: {self.vdm_type}
Vendor Use: {self.vendor_use}"""
