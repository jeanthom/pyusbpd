import abc
from dataclasses import dataclass
from pyusbpd.enum import *
from pyusbpd.helpers import get_bit_from_array

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

        # USB PD r3.1 6.2.1.1.8
        self.message_type = int(raw[0] & 0x1F)
        # USB PD r3.1 6.2.1.1.6
        self.port_data_role = PortDataRole(get_bit_from_array(raw, 5))
        # USB PD r3.1 6.2.1.1.5
        self.specification_revision = SpecificationRevision(int(raw[0] >> 6))
        # USB PD r3.1 6.2.1.1.7
        self.cable_plug = get_bit_from_array(raw, 8)
        # USB PD r3.1 6.2.1.1.4
        self.port_power_role = get_bit_from_array(raw, 8)
        # USB PD r3.1 6.2.1.1.3
        self.message_id = int((raw[1] & 0x0E) >> 1)
        # USB PD r3.1 6.2.1.1.2
        self.num_data_obj = int((raw[1] & 0x70) >> 4)
        # USB PD r3.1 6.2.1.1.1
        self.extended = get_bit_from_array(raw, 15)

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

        # USB PD r3.1 6.2.1.2.4
        self.data_size = int(raw[0] | ((raw[1] & 0x01) << 8))
        # USB PD r3.1 6.2.1.2.3
        self.request_chunk = get_bit_from_array(raw, 10)
        # USB PD r3.1 6.2.1.2.2
        self.chunk_number = int((raw[1] & 0x78) >> 3)
        # USB PD r3.1 6.2.1.2.1
        self.chunked = get_bit_from_array(raw, 15)

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

class Message:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.header = MessageHeader()

    @abc.abstractmethod
    def parse(self, raw: bytes):
        return

    @abc.abstractmethod
    def encode(self) -> bytes:
        return

class ControlMessage(Message):
    def parse(self, raw: bytes):
        self.header.parse(raw[0:2])

    def encode(self) -> bytes:
        return self.header.encode()

class DataMessage(Message):
    def __init__(self):
        super().__init__()
        self.data_objects = []

    def parse(self, raw: bytes):
        self.header.parse(raw[0:2])
        self._parse_data_objects(raw[2:])

    def _parse_data_objects(self, raw):
        self.data_objects = []
        for i in range(self.header.num_data_obj):
            self.data_objects.append(raw[i*4:(i+1)*4])

    def encode(self) -> bytes:
        self.header.num_data_obj = len(self.data_objects)

class ExtendedMessage(Message):
    def __init__(self):
        super().__init__()
        self.extended_header = ExtendedMessageHeader()

    def parse(self, raw: bytes):
        self.header.parse(raw[0:2])
        self.extended_header.parse(raw[2:4])

class GoodCRCMessage(ControlMessage):
    MESSAGE_TYPE = 0b00001

    def __init__(self):
        super().__init__()
        self.header.message_type = GoodCRCMessage.MESSAGE_TYPE

class AcceptMessage(ControlMessage):
    MESSAGE_TYPE = 0b00011

    def __init__(self):
        super().__init__()
        self.header.message_type = AcceptMessage.MESSAGE_TYPE

class RejectMessage(ControlMessage):
    MESSAGE_TYPE = 0b00100

    def __init__(self):
        super().__init__()
        self.header.message_type = RejectMessage.MESSAGE_TYPE

class PingMessage(ControlMessage):
    MESSAGE_TYPE = 0b00101

    def __init__(self):
        super().__init__()
        self.header.message_type = PingMessage.MESSAGE_TYPE

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

class Vendor_DefinedMessage(DataMessage):
    MESSAGE_TYPE = 0b01111

    def __init__(self):
        super().__init__()
        self.vdm_header = VDMHeader()

    def parse(self, raw: bytes):
        super().parse(self, raw)
        self.vdm_header.parse(self.data_objects[0])

@dataclass
class PowerData:
    type: PDOType = PDOType.FIXED_SUPPLY

    def parse(self, raw: bytes):
        assert len(raw) == 4
        self.type = PDOType((raw[3] & 0xC0) >> 6)

    def __repr__(self):
        return f"""Power data object
---
Type: {self.type}"""

class FixedSupplyPowerData(PowerData):
    def __init__(self):
        super().__init__()
        self.usb_suspend_supported = False
        self.unconstrained_power = False
        self.usb_communications_capable = False
        self.dualrole_data = False
        self.unchunked_extended_messages_supported = False
        self.epr_mode_capable = False
        self.voltage = 0
        self.maximum_current = 0

    def parse(self, raw: bytes):
        super().parse(raw)
        self.usb_suspend_supported = get_bit_from_array(raw, 28)
        self.unconstrained_power = get_bit_from_array(raw, 27)
        self.usb_communications_capable = get_bit_from_array(raw, 26)
        self.dualrole_data = get_bit_from_array(raw, 25)
        self.unchunked_extended_messages_supported = get_bit_from_array(raw, 24)
        self.epr_mode_capable = get_bit_from_array(raw, 23)
        self.voltage = (raw[1] >> 2) | ((raw[2] & 0xF) << 6)
        # Table 6-9
        self.maximum_current = raw[0] | (raw[1] & 0x3) << 8

    def __repr__(self):
        return super().__repr__() + "\n" + f"""Fixed supply power data object
---
USB suspend supported: {self.usb_suspend_supported}
Unconstrained power: {self.unconstrained_power}
USB communications capable: {self.usb_communications_capable}
Dual-role data: {self.dualrole_data}
Unchunked Extended Messages Supported: {self.unchunked_extended_messages_supported}
EPR Mode Capable: {self.epr_mode_capable}
Voltage: {self.voltage*50/1000} V
Maximum current: {self.maximum_current*10} mA"""

class Source_CapabilitiesMessage(DataMessage):
    MESSAGE_TYPE = 0b00001

    def __repr__(self):
        pd = FixedSupplyPowerData()
        pd.parse(self.data_objects[0])
        return str(pd)

def parse(raw: bytes) -> Message:
    msg = Message()
    msg.parse(raw)

    if msg.header.extended:
        msg = ExtendedMessage()
    else:
        if msg.header.num_data_obj > 0:
            if msg.header.message_type == Source_CapabilitiesMessage.MESSAGE_TYPE:
                msg = Source_CapabilitiesMessage()
            elif msg.header.message_type == Vendor_DefinedMessage.MESSAGE_TYPE:
                msg = Vendor_DefinedMessage()
            else:
                msg = DataMessage()
        else:
            if msg.header.message_type == GoodCRCMessage.MESSAGE_TYPE:
                msg = GoodCRCMessage()
            elif msg.header.message_type == AcceptMessage.MESSAGE_TYPE:
                msg = AcceptMessage()
            elif msg.header.message_type == RejectMessage.MESSAGE_TYPE:
                msg = RejectMessage()
            else:
                msg = ControlMessage()

    msg.parse(raw)
    return msg
