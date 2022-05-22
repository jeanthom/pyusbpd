import enum

class SpecificationRevision(enum.Enum):
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
