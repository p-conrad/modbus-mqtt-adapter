"""
This module contains everything that is necessary to convert the data obtained from
the Modbus device and restructure it in a usable format.
"""

import struct
from typing import List
from datatypes import DataDescription, ConversionResult

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


def convert_single_module(registers: List[int], layout: DataDescription) -> ConversionResult:
    """
    Converts a slice from the Modbus response into a dictionary according
    to the given DataDescription instance.
    """
    result = {}
    for entry in layout:
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