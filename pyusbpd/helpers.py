from bitstring import BitArray

def get_bit_from_array(arr: bytes, pos: int) -> bool:
    return bool(arr[pos//8] & (1 << (pos % 8)))

def get_int_from_array(arr: bytes, width: int, offset: int = 0):
    source = BitArray(arr)
    source.byteswap()
    source.reverse()
    extracted = source[offset:offset+width]
    extracted.reverse()
    return extracted.uint
