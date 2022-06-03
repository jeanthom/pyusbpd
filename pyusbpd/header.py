from dataclasses import dataclass
from pyusbpd.enum import *
from pyusbpd.helpers import get_bit_from_array, get_int_from_array

__all__ = [
    "VDMHeader",
]

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

    def encode(self) -> bytes:
        pass

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
