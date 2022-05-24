def get_bit_from_array(arr, pos) -> bool:
    return bool(arr[pos//8] & (1 << (pos % 8)))
