"""
This module contains some type information, particularly for the configuration
objects and the conversion function.
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

DataDescription = List[DataEntry]
ConversionResult = Dict[str, Union[int, float, List[float]]]