import abc
from dataclasses import dataclass
import bitstring
from pyusbpd.enum import *
from pyusbpd.helpers import get_bit_from_array, get_int_from_array
from pyusbpd.header import VDMHeader

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
    "RevisionMessage",
    "parse"
]

class Message:
    __metaclass__ = abc.ABCMeta

    @dataclass
    class Header:
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
            self.specification_revision = SpecificationRevision(get_int_from_array(raw, width=2, offset=6)) # 6.2.1.1.5
            self.cable_plug = get_bit_from_array(raw, 8) # 6.2.1.1.7
            self.port_power_role = get_bit_from_array(raw, 8) # 6.2.1.1.4
            self.message_id = get_int_from_array(raw, width=3, offset=9) # 6.2.1.1.3
            self.num_data_obj = get_int_from_array(raw, width=3, offset=12) # 6.2.1.1.2
            self.extended = get_bit_from_array(raw, 15) # 6.2.1.1.1

        def encode(self) -> bytes:
            sop_only_fmt = """
                bool=extended,
                uint:3=num_data_obj,
                uint:3=message_id,
                bool=port_power_role,
                uint:2=specification_revision,
                bool=port_data_role,
                uint:5=message_type,
            """
            val = {
                'message_type': self.message_type,
                'port_data_role': bool(self.port_data_role),
                'specification_revision': self.specification_revision,
                'port_power_role': self.port_power_role,
                'message_id': self.message_id,
                'num_data_obj': self.num_data_obj,
                'extended': self.extended,
            }
            s = bitstring.pack(sop_only_fmt, **val)
            s.byteswap()
            return s.bytes

    def __init__(self):
        self.header = Message.Header()

    @abc.abstractmethod
    def parse(self, raw: bytes):
        self.header.parse(raw[0:2])

    @abc.abstractmethod
    def encode(self) -> bytes:
        return

class ControlMessage(Message):
    """Control Message (6.3)"""

    def parse(self, raw: bytes):
        super().parse(raw)

    def encode(self) -> bytes:
        return self.header.encode()

class DataMessage(Message):
    """Data Message (6.4)"""

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
        return self.header.encode() + b''.join(self.data_objects)

class ExtendedMessage(Message):
    """Extended Message (6.5)"""

    @dataclass
    class Header:
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
            fmt = """
                bool=chunked,
                uint:4=chunk_number,
                bool=request_chunk,
                bool=0,
                uint:9=data_size,
            """
            val = {
                'chunked': self.chunked,
                'chunk_number': self.chunk_number,
                'request_chunk': self.request_chunk,
                'data_size': self.data_size,
            }
            s = bitstring.pack(fmt, **val)
            s.byteswap()
            return s

    def __init__(self):
        super().__init__()
        self.extended_header = ExtendedMessage.Header()

    def parse(self, raw: bytes):
        super().parse(raw)
        self.extended_header.parse(raw[2:4])

class GoodCRCMessage(ControlMessage):
    """Good CRC Message (6.3.1)"""
    MESSAGE_TYPE = 0b00001

    def __init__(self):
        super().__init__()
        self.header.message_type = GoodCRCMessage.MESSAGE_TYPE

class AcceptMessage(ControlMessage):
    """Accept Message (6.3.3)"""
    MESSAGE_TYPE = 0b00011

    def __init__(self):
        super().__init__()
        self.header.message_type = AcceptMessage.MESSAGE_TYPE

class RejectMessage(ControlMessage):
    """Reject Message (6.3.4)"""
    MESSAGE_TYPE = 0b00100

    def __init__(self):
        super().__init__()
        self.header.message_type = RejectMessage.MESSAGE_TYPE

class PingMessage(ControlMessage):
    """Ping Message (6.3.5)"""
    MESSAGE_TYPE = 0b00101

    def __init__(self):
        super().__init__()
        self.header.message_type = PingMessage.MESSAGE_TYPE

class Vendor_DefinedMessage(DataMessage):
    """Vendor Defined Message (6.4.4)"""
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
    """Fixed Supply Power Data Object (6.4.1.2.2)"""
    dualrole_power: bool = False
    usb_suspend_supported: bool = False
    unconstrained_power: bool = False
    usb_communications_capable: bool = False
    dualrole_data: bool = False
    unchunked_extended_messages_supported: bool = False
    epr_mode_capable: bool = False
    peak_current: int = 0
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
        self.peak_current = get_int_from_array(raw, offset=20, width=2)
        self.voltage = get_int_from_array(raw, offset=10, width=10)
        # Table 6-9
        self.maximum_current = get_int_from_array(raw, offset=0, width=10)

    def encode(self) -> bytes:
        fmt = """
            uint:2=0,
            bool=dualrole_power,
            bool=usb_suspend_supported,
            bool=unconstrained_power,
            bool=usb_communications_capable,
            bool=dualrole_data,
            bool=unchunked_extended_messages_supported,
            bool=epr_mode_capable,
            bool=0,
            uint:2=peak_current,
            uint:10=voltage,
            uint:10=maximum_current,
        """
        val = {
            'dualrole_power': self.dualrole_power,
            'usb_suspend_supported': self.usb_suspend_supported,
            'unconstrained_power': self.unconstrained_power,
            'usb_communications_capable': self.usb_communications_capable,
            'dualrole_data': self.dualrole_data,
            'unchunked_extended_messages_supported': self.unchunked_extended_messages_supported,
            'epr_mode_capable': self.epr_mode_capable,
            'peak_current': self.peak_current,
            'voltage': self.voltage,
            'maximum_current': self.maximum_current,
        }
        s = bitstring.pack(fmt, **val)
        s.byteswap()
        return s.bytes

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
Maximum current: {self.maximum_current*10} mA\n"""

@dataclass(kw_only=True)
class VariableSupplyPowerData(PowerData):
    """Variable Supply (non-Battery) Power Data Object (6.4.1.2.3)"""
    maximum_voltage: int = 0
    minimum_voltage: int = 0
    maximum_current: int = 0

    def parse(self, raw: bytes):
        super().parse(raw)
        # Table 6-11
        self.maximum_voltage = get_int_from_array(raw, offset=20, width=10)
        self.minimum_voltage = get_int_from_array(raw, offset=10, width=10)
        self.maximum_current = get_int_from_array(raw, offset=0, width=10)

@dataclass(kw_only=True)
class BatterySupplyPowerData(PowerData):
    """Battery Supply Power Data Object (6.4.1.2.4)"""
    maximum_voltage: int = 0
    minimum_voltage: int = 0
    maximum_allowable_power: int = 0

    def parse(self, raw: bytes):
        super().parse(raw)
        # Table 6-12
        self.maximum_voltage = get_int_from_array(raw, offset=20, width=10)
        self.minimum_voltage = get_int_from_array(raw, offset=10, width=10)
        self.maximum_allowable_power = get_int_from_array(raw, offset=0, width=10)

class Source_CapabilitiesMessage(DataMessage):
    MESSAGE_TYPE = 0b00001

    def __init__(self):
        super().__init__()
        self.power_data_objects = list()

    def parse(self, raw: bytes):
        super().parse(raw)
        self._parse_power_data_objects()

    def encode(self) -> bytes:
        self.data_objects = map(lambda x: x.encode(), self.power_data_objects)
        return super().encode()

    def _parse_power_data_objects(self):
        self.power_data_objects = list()
        for data_object in self.data_objects:
            power_data = PowerData()
            power_data.parse(data_object)
            if power_data.type == PDOType.FIXED_SUPPLY:
                power_data = FixedSupplyPowerData()
            elif power_data.type == PDOType.BATTERY:
                power_data = BatterySupplyPowerData()
            elif power_data.type == PDOType.VARIABLE_SUPPLY:
                power_data = VariableSupplyPowerData()
            elif power_data.type == PDOType.AUGMENTED_POWER_DATA_OBJECT:
                raise NotImplementedError
            power_data.parse(data_object)
            self.power_data_objects.append(power_data)

    def __repr__(self) -> str:
        representation = ""
        for idx, power_data in enumerate(self.power_data_objects):
            representation += f"#{idx}: {str(power_data)}"
        return representation

class RevisionMessage(DataMessage):
    MESSAGE_TYPE = 0b01100

    @dataclass
    class RevisionMessageDataObject:
        """Revision Message Data Object (RMDO)"""
        revision_major: int = 0
        revision_minor: int = 0
        version_major: int = 0
        version_minor: int = 0

        def parse(self, raw: bytes):
            # Table 6-52
            self.revision_major = get_int_from_array(raw, offset=28, width=4)
            self.revision_minor = get_int_from_array(raw, offset=24, width=4)
            self.version_major = get_int_from_array(raw, offset=20, width=4)
            self.version_minor = get_int_from_array(raw, offset=16, width=4)

        def encode(self) -> bytes:
            fmt = """
                uint:4=revision_major
                uint:4=revision_minor
                uint:4=version_major
                uint:4=version_minor
                uint:32=0
            """
            val = {
                'revision_major': self.revision_major,
                'revision_minor': self.revision_minor,
                'version_major': self.version_major,
                'version_minor': self.version_minor,
            }
            s = bitstring.pack(fmt, **val)
            s.byteswap()
            return s.bytes

        def __str__(self):
            return f"Revision {self.revision_major}.{self.revision_minor}, Version {self.version_major}.{self.verison_minor}"

    def __init__(self):
        super().__init__()
        self.rmdo = RevisionMessage.RevisionMessageDataObject()

    def parse(self, raw: bytes):
        super().parse(raw)
        self.rmdo.parse(self.data_objects[0])

    def encode(self) -> bytes:
        self.data_objects = [self.rmdo.encode()]
        return super.encode()

def parse(raw: bytes) -> Message:
    msg = Message()
    msg.parse(raw)

    if msg.header.extended:
        msg = ExtendedMessage()
    else:
        print(msg.header.num_data_obj)
        if msg.header.num_data_obj > 0:
            if msg.header.message_type == Source_CapabilitiesMessage.MESSAGE_TYPE:
                msg = Source_CapabilitiesMessage()
            elif msg.header.message_type == Vendor_DefinedMessage.MESSAGE_TYPE:
                msg = Vendor_DefinedMessage()
            elif msg.header.message_type == RevisionMessage.MESSAGE_TYPE:
                msg = RevisionMessage()
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
