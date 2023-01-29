"""
This module contains definitions of data types shared over Modbus
as well as the DataEntry type describing the nature of a single
value in the Modbus response.
"""

from enum import Enum, auto
from typing import NamedTuple


class PlcDataType(Enum):
    Uint16 = auto()  # aka WORD, UINT
    Int16 = auto()  # aka INT
    UInt32 = auto()  # aka UDINT
    Int32 = auto()  # aka DWORD, DINT
    Float32 = auto()  # aka REAL
    Float64 = auto()  # aka LREAL


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
    type: PlcDataType
