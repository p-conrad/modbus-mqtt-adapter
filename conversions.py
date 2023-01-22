"""
This module contains everything that is necessary to convert the data obtained from
the Modbus device and restructure it in a usable format.
"""

import struct
from typing import List, Dict, Union, NamedTuple, Callable

ConversionResult = Dict[str, Union[float, List[float]]]


def convert_timestamp(responseData: List[int]) -> int:
    """
    Converts two words from the Modbus response to a datetime object.
    """
    return responseData[1] << 16 | responseData[0]


def convert_real(responseData: List[int]) -> float:
    """
    Converts two words (integers) from the Modbus response to a floating-point number.
    """
    # Explanation: The REAL data type consists of two 16-bits words, of which the more
    # significant one comes second in the Modbus response. As they are being stored as
    # integers, the bits need to be assembled and reinterpreted as a floating-point
    # number. After bit-shifting and ORing the words together, we first obtain the hex
    # string, which then needs to be converted to a byte string using the bytes.fromhex
    # function. However, bytes.fromhex will complain about the '0x' part of the hex
    # string, so we need to cut it off using [2:] first. Furthermore, bytes.fromhex
    # needs to have at least 4 bytes, so we need to fill the string up in case the
    # number is shorter (e.g. 'f' -> '0000000f'). Then finally, we can use
    # struct.unpack to interpret these bytes as a big-endian floating-point value,
    # which returns a tuple, the first value of which is our desired number.
    # This is probably to the most clunky way of converting between number formats in any
    # programming language, ever.
    hexStr = hex(responseData[1] << 16 | responseData[0])[2:]
    if len(hexStr) < 8:
        hexStr = "0" * (8 - len(hexStr)) + hexStr

    return struct.unpack(">f", bytes.fromhex(hexStr))[0]


def convert_word(responseData: List[int]) -> int:
    """
    Takes a single word from the Modbus response and returns it as-is.
    """
    return responseData[0]


class DataEntry(NamedTuple):
    """
    A structure describing one entry in the memory layout of the Modbus response:
    How it is called, at which position it resides in the array, how many words
    a single value consists of, how many values there are, and a function doing
    the appropriate conversion.
    """

    name: str
    position: int
    wordsize: int
    count: int
    converter: Callable[[List[int]], float]


DATA_SIZE: int = 24
DATA_DESCRIPTION: List[DataEntry] = [
    DataEntry("timestamp", 0, 2, 1, convert_timestamp),
    DataEntry("busIndex", 2, 1, 1, convert_word),
    DataEntry("voltage", 4, 2, 3, convert_real),
    DataEntry("current", 10, 2, 3, convert_real),
    DataEntry("power", 16, 2, 3, convert_real),
    DataEntry("energy", 22, 2, 1, convert_real),
]


def convert_single_module(registers: List[int]) -> ConversionResult:
    """
    Converts a slice from the Modbus response into a dictionary according
    to the description given by STRUCT_CONTENTS above.
    """
    result = {}
    for entry in DATA_DESCRIPTION:
        if entry.count == 1:
            value = entry.converter(
                registers[entry.position : entry.position + entry.wordsize]
            )
        else:
            slices = [
                registers[i : i + entry.wordsize]
                for i in range(
                    entry.position,
                    entry.position + entry.wordsize * entry.count,
                    entry.wordsize,
                )
            ]
            value = list(map(entry.converter, slices))
        result[entry.name] = value
    return result