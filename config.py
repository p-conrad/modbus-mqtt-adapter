"""
This file contains the configuration of the program, namely information on how
the data is laid out in the Modbus response for the given use case, and what
the data size of it is.
"""

from data_types import PlcDataType, DataEntry
from typing import List

DATA_IS_BIG_ENDIAN: bool = False
DATA_SIZE: int = 20
DATA_LAYOUT: List[DataEntry] = [
    DataEntry("voltage", 0, 2, 3, PlcDataType.Float32),
    DataEntry("current", 6, 2, 3, PlcDataType.Float32),
    DataEntry("power", 12, 2, 3, PlcDataType.Float32),
    DataEntry("energy", 18, 2, 1, PlcDataType.Float32),
]
