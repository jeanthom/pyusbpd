import enum

class PortDataRole(enum.Flag):
    """Port Data Role (USB PD r3.1 6.2.1.1.6)"""
    UFP = False
    DFP = True

class PortPowerRole(enum.Flag):
    """Port Power Role (USB PD r3.1 6.2.1.1.4)"""
    SINK = False
    SOURCE = True

class SpecificationRevision(enum.IntEnum):
    """USB Power Delivery Specification Revision
    enumeration from the Message Header struct"""
    REV10 = 0b00
    REV20 = 0b01
    REV30 = 0b10
    RESERVED = 0b11

    def __str__(self):
        if self.value == 0b00:
            return "Revision 1.0"
        if self.value == 0b01:
            return "Revision 2.0"
        if self.value == 0b10:
            return "Revision 3.0"
        return "Reserved, Shall Not be used"

class SOP(enum.Enum):
    """Enum of all Start of Packet sequences (5.6.1.2)"""
    UNKNOWN = "Unknown"
    SOP = "SOP"
    SOP_PRIME = "SOP'"
    SOP_DOUBLEPRIME = "SOP''"
    SOP_PRIME_DEBUG = "SOP'_Debug"
    SOP_DOUBLEPRIME_DEBUG = "SOP''_Debug"

class StructuredVDMVersion(enum.IntEnum):
    REV10 = 0b00
    REV20 = 0b01

    def __str__(self):
        if self.value == 0b00:
            return "Version 1.0"
        if self.value == 0b01:
            return "Version 2.0"

class VDMCommandType(enum.IntEnum):
    """Enum of all structured VDM Header Command Types (Table 6-29)"""
    REQ = 0b00
    ACK = 0b01
    NAK = 0b10
    BUSY = 0b11

class VDMCommand(enum.IntEnum):
    """Enum of all available VDM Header Commands (Table 6-29)"""
    DISCOVER_IDENTITY = 1
    DISCOVER_SVID = 2
    DISCOVER_MODES = 3
    ENTER_MODE = 4
    EXIT_MODE = 5
    ATTENTION = 6
    SVID_SPECIFIC_0 = 16
    SVID_SPECIFIC_1 = 17
    SVID_SPECIFIC_2 = 18
    SVID_SPECIFIC_3 = 19
    SVID_SPECIFIC_4 = 20
    SVID_SPECIFIC_5 = 21
    SVID_SPECIFIC_6 = 22
    SVID_SPECIFIC_7 = 23
    SVID_SPECIFIC_8 = 24
    SVID_SPECIFIC_9 = 25
    SVID_SPECIFIC_10 = 26
    SVID_SPECIFIC_11 = 27
    SVID_SPECIFIC_12 = 28
    SVID_SPECIFIC_13 = 29
    SVID_SPECIFIC_14 = 30
    SVID_SPECIFIC_15 = 31

class PDOType(enum.IntEnum):
    """Power Data Object type (Table 6-7)"""
    FIXED_SUPPLY = 0b00
    BATTERY = 0b01
    VARIABLE_SUPPLY = 0b10
    AUGMENTED_POWER_DATA_OBJECT = 0b11
