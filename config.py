"""
This file contains the configuration of the program, namely information on how
the data is laid out in the Modbus response for the given use case, and what
the data size of it is.
"""

from conversions import convert_timestamp, convert_real, convert_word
from data_entry import DataEntry
from typing import List

DATA_SIZE: int = 24
DATA_LAYOUT: List[DataEntry] = [
    DataEntry("timestamp", 0, 2, 1, convert_timestamp),
    DataEntry("busIndex", 2, 1, 1, convert_word),
    DataEntry("voltage", 4, 2, 3, convert_real),
    DataEntry("current", 10, 2, 3, convert_real),
    DataEntry("power", 16, 2, 3, convert_real),
    DataEntry("energy", 22, 2, 1, convert_real),
]