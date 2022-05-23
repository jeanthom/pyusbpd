from pyusbpd.enum import SpecificationRevision

class MessageHeader:
    """USB Power Delivery Message Header (6.2.1.1)"""

    def __init__(self, raw=bytes(2)):
        assert isinstance(raw, (bytearray, bytes))
        assert len(raw) == 2
        self.raw = raw

    @property
    def message_type(self) -> int:
        """Returns Message Type field (USB PD r3.1 6.2.1.1.8)"""
        return int(self.raw[0] & 0x1F)

    @message_type.setter
    def message_type(self, value: int):
        """Sets Message Type field (USB PD r3.1 6.2.1.1.8)"""
        self.raw[0] = (self.raw[0] & 0xE0) | (value & 0x1F)

    @property
    def port_data_role(self) -> bool:
        """Returns Port Data Role field (USB PD r3.1 6.2.1.1.6)"""
        return bool(self.raw[0] & 0x20)

    @property
    def specification_revision(self):
        """Returns Specification Revision field (USB PD r3.1 6.2.1.1.5)"""
        return SpecificationRevision(int(self.raw[0] >> 6))

    @property
    def cable_plug(self):
        """Returns Cable Plug field (USB PD r3.1 6.2.1.1.7)"""
        return bool(self.raw[1] & 0x01)

    @property
    def port_power_role(self):
        """Returns Port Power Role field (USB PD r3.1 6.2.1.1.4)"""
        return bool(self.raw[1] & 0x01)

    @property
    def message_id(self):
        """Returns MessageID field (USB PD r3.1 6.2.1.1.3)"""
        return int((self.raw[1] & 0x0E) >> 1)

    @property
    def num_data_obj(self):
        """Returns Number of Data Objects field (USB PD r3.1 6.2.1.1.2)"""
        return int((self.raw[1] & 0x70) >> 4)

    @property
    def extended(self):
        """Returns Extended field (USB PD r3.1 6.2.1.1.1)"""
        return bool(self.raw[1] & 0x80)

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

class ExtendedMessageHeader:
    """USB Power Delivery Extended Message Header (6.2.1.2)"""

    def __init__(self, raw=bytes(2)):
        assert isinstance(raw, (bytes, bytearray))
        assert len(raw) == 2
        self.raw = raw

    @property
    def data_size(self):
        """Returns Data Size field (USB PD r3.1 6.2.1.2.4)"""
        return int(self.raw[0] | ((self.raw[1] & 0x01) << 8))

    @property
    def request_chunk(self):
        """Returns Request Chunk field (USB PD r3.1 6.2.1.2.3)"""
        return bool(self.raw[1] & 0x04)

    @property
    def chunk_number(self):
        """Returns Chunk Number field (USB PD r3.1 6.2.1.2.2)"""
        return int((self.raw[1] & 0x78) >> 3)

    @property
    def chunked(self):
        """Returns Chunked field (USB PD r3.1 6.2.1.2.1)"""
        return bool(self.raw[1] & 0x80)

    def validate(self):
        """Validates all field, returns exception on error"""
        if self.chunked:
            assert self.chunk_number == 0, "USB PD r3.1 6.2.1.2.2 violation"

    def __repr__(self):
        """Returns a string representation"""
        return f"""USB Power Delivery Extended Message Header
---
Chunked: {self.chunked}
Chunk Number: {self.chunk_number}
Request Chunk: {self.request_chunk}
Data Size: {self.data_size}"""

class Message:
    def __init__(self, sop, raw):
        self.sop = sop
        self.raw = raw

    @property
    def message_header(self):
        return MessageHeader(self.raw[0:2])

    def decode(self):
        """Decode a message into its appropriate subclass"""
        if not self.message_header.extended:
            if self.message_header.num_data_obj > 0:
                return DataMessage(self.sop, self.raw).decode()
            if self.message_header.num_data_obj == 0:
                return ControlMessage(self.sop, self.raw).decode()
        else:
            return ExtendedMessage(self.sop, self.raw).decode()

class ControlMessage(Message):
    def __init__(self, sop, raw=b"\x00\x00"):
        super().__init__(sop, raw)
        assert self.message_header.num_data_obj == 0
        assert not self.message_header.extended

    def decode(self):
        if self.message_header.message_type == GoodCRCMessage.MESSAGE_TYPE:
            return GoodCRCMessage(self.sop, self.raw)
        else:
            return self

class DataMessage(Message):
    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.num_data_obj > 0
        assert len(self.raw) == 2 + self.message_header.num_data_obj*4
        assert not self.message_header.extended

    @property
    def data_objects(self):
        res = []
        for i in range(self.message_header.num_data_obj):
            res.append(self.raw[2+i*4:2+(i+1)*4])
        return res

    def decode(self):
        if self.message_header.message_type == Vendor_DefinedMessage.MESSAGE_TYPE:
            return Vendor_DefinedMessage(self.sop, self.raw)
        else:
            return self

class ExtendedMessage(Message):
    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.extended

    @property
    def extended_message_header(self):
        assert self.message_header.extended, "Message Header has extended bit deasserted"
        return ExtendedMessageHeader(self.raw[2:4])

    def decode(self):
        return self

class GoodCRCMessage(ControlMessage):
    MESSAGE_TYPE = 0b00001

    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.message_type == GoodCRCMessage.MESSAGE_TYPE

class AcceptMessage(ControlMessage):
    MESSAGE_TYPE = 0b00011

    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.message_type == AcceptMessage.MESSAGE_TYPE

class RejectMessage(ControlMessage):
    MESSAGE_TYPE = 0b00100

    def __init(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.message_type == RejectMessage.MESSAGE_TYPE

class PingMessage(ControlMessage):
    MESSAGE_TYPE = 0b00101

    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.message_type == PingMessage.MESSAGE_TYPE

class VDMHeader:
    def __init__(self, raw):
        assert len(raw) == 4
        self.raw = raw

    @property
    def vendor_id(self):
        return self.raw[3] << 8 | self.raw[2]

    @property
    def vdm_type(self):
        return bool(self.raw[1] & 0x80)

    @property
    def structured_vdm_version(self):
        print(self.raw[1])
        return StructuredVDMVersion((self.raw[1] & 0x60) >> 5)

    @property
    def vendor_use(self):
        return (self.raw[1] & 0x7F) << 8 | self.raw[0]

    @property
    def object_position(self):
        raise NotImplementedError

    @property
    def command_type(self):
        return VDMCommandType(self.raw[0] & 0xC0 >> 5)

    @property
    def command(self):
        return VDMCommand(self.raw[0] & 0x1F)

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

    def __init__(self, sop, raw):
        super().__init__(sop, raw)
        assert self.message_header.message_type == Vendor_DefinedMessage.MESSAGE_TYPE

    @property
    def vdm_header(self):
        return VDMHeader(self.data_objects[0])

    @property
    def objects(self):
        return self.data_objects[1:]

    def decode(self):
        return self
