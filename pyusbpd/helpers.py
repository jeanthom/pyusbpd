from bitarray import bitarray
from bitarray.util import ba2int, zeros

def get_bit_from_array(arr: bytes, pos: int) -> bool:
    return bool(arr[pos//8] & (1 << (pos % 8)))

def get_int_from_array(arr: bytes, width: int, offset: int = 0):
    source = bitarray()
    source.frombytes(arr)
    source.bytereverse()
    x = source[offset:offset+width]
    x.reverse()
    return ba2int(x)
