"""
This module contains everything that is necessary to convert the data obtained from
the Modbus device and restructure it in a usable format.
"""

import pyModbusTCP.utils as utils
from typing import Dict, List, Union
from data_types import PlcDataType, DataEntry


def convert_value(
    responseData: List[int], type: PlcDataType, isBigEndian: bool
) -> Union[int, float]:
    """
    Converts a single value from the Modbus response according to the type
    definition and the given endianness. Rounds floating-point numbers
    to three fractional digits.
    """
    if type == PlcDataType.Int16:
        return responseData[0]
    elif type == PlcDataType.Uint16:
        return utils.get_2comp(responseData[0])

    longVal = utils.word_list_to_long(responseData[:2], isBigEndian)[0]
    if type == PlcDataType.Int32:
        return longVal
    elif type == PlcDataType.UInt32:
        return utils.get_2comp(longVal, val_size=32)
    elif type == PlcDataType.Float32:
        return round(utils.decode_ieee(longVal), 3)
    elif type == PlcDataType.Float64:
        return round(utils.decode_ieee(longVal, double=True), 3)


def convert_single_module(
    registers: List[int], layout: List[DataEntry], isBigEndian: bool
) -> Dict[str, Union[int, float, List[float]]]:
    """
    Converts a slice from the Modbus response into a dictionary according
    to the given data layout.
    """
    result = {}
    for entry in layout:
        if entry.count == 1:
            value = convert_value(
                registers[entry.position : entry.position + entry.wordsize],
                entry.type,
                isBigEndian,
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
            value = list(
                map(lambda v: convert_value(v, entry.type, isBigEndian), slices)
            )
        result[entry.name] = value
    return result
