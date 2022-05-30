import abc
from dataclasses import dataclass
from pyusbpd.enum import *
from pyusbpd.helpers import get_bit_from_array
from pyusbpd.header import MessageHeader, ExtendedMessageHeader, VDMHeader

__all__ = [
    "ControlMessage",
    "DataMessage",
    "ExtendedMessage",
    "GoodCRCMessage",
    "AcceptMessage",
    "RejectMessage",
    "Vendor_DefinedMessage",
    "PowerData",
    "FixedSupplyPowerData",
    "Source_CapabilitiesMessage",
    "parse"
]

class Message:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.header = MessageHeader()

    @abc.abstractmethod
    def parse(self, raw: bytes):
        self.header.parse(raw[0:2])

    @abc.abstractmethod
    def encode(self) -> bytes:
        return

class ControlMessage(Message):
    def parse(self, raw: bytes):
        super().parse(raw)

    def encode(self) -> bytes:
        return self.header.encode()

class DataMessage(Message):
    def __init__(self):
        super().__init__()
        self.data_objects = []

    def parse(self, raw: bytes):
        super().parse(raw)
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
        super().parse(raw)
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

class Vendor_DefinedMessage(DataMessage):
    MESSAGE_TYPE = 0b01111

    def __init__(self):
        super().__init__()
        self.vdm_header = VDMHeader()

    def parse(self, raw: bytes):
        super().parse(self, raw)
        self.vdm_header.parse(self.data_objects[0])

@dataclass(kw_only=True)
class PowerData:
    type: PDOType = PDOType.FIXED_SUPPLY

    def parse(self, raw: bytes):
        assert len(raw) == 4
        self.type = PDOType((raw[3] & 0xC0) >> 6)

    def __repr__(self):
        return f"""Power data object
---
Type: {self.type}"""

@dataclass(kw_only=True)
class FixedSupplyPowerData(PowerData):
    usb_suspend_supported: bool = False
    unconstrained_power: bool = False
    usb_communications_capable: bool = False
    dualrole_data: bool = False
    unchunked_extended_messages_supported: bool = False
    epr_mode_capable: bool = False
    voltage: int = 0
    maximum_current: int = 0

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

    def __init__(self):
        super().__init__()
        self.power_data_objects = list()

    def parse(self, raw: bytes):
        super().parse(raw)
        self._parse_power_data_objects()

    def _parse_power_data_objects(self):
        self.power_data_objects = list()
        for data_object in self.data_objects:
            power_data = PowerData()
            power_data.parse(data_object)
            if power_data.type == PDOType.FIXED_SUPPLY:
                power_data = FixedSupplyPowerData()
            elif power_data.type == PDOType.BATTERY:
                pass
            elif power_data.type == PDOType.VARIABLE_SUPPLY:
                pass
            elif power_data.type == PDOType.AUGMENTED_POWER_DATA_OBJECT:
                pass
            power_data.parse(data_object)
            self.power_data_objects.append(power_data)

    def __repr__(self) -> str:
        representation = ""
        for idx, power_data in enumerate(self.power_data_objects):
            representation += f"#{idx}: {str(power_data)}"
        return representation

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
