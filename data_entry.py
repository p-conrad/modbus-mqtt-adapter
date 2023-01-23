"""
This module contains information for the data entry type
used to describe a single entry the Modbus response layout.
"""

from typing import List, Dict, Union, NamedTuple, Callable

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