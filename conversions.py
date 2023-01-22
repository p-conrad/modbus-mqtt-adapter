"""
This module contains everything that is necessary to convert the data obtained from
the Modbus device and restructure it in a usable format.
"""

import struct
from typing import List, Dict, Union, NamedTuple, Callable

ConversionResult = Dict[str, Union[float, List[float]]]
SensorList = List[Dict[str, Union[str, List[Dict[str, float]]]]]


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


class StructEntry(NamedTuple):
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


STRUCT_SIZE: int = 24
STRUCT_CONTENTS: List[StructEntry] = [
    StructEntry("timestamp", 0, 2, 1, convert_timestamp),
    StructEntry("busIndex", 2, 1, 1, lambda x: x[0]),
    StructEntry("voltage", 4, 2, 3, convert_real),
    StructEntry("current", 10, 2, 3, convert_real),
    StructEntry("power", 16, 2, 3, convert_real),
    StructEntry("energy", 22, 2, 1, convert_real),
]


def convert_single_struct(registers: List[int]) -> ConversionResult:
    """
    Converts a single structure from the Modbus response into a dictionary according
    to the description given by STRUCT_CONTENTS above.
    """
    result = {}
    for entry in STRUCT_CONTENTS:
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


def to_sensor_list(registers: List[int]) -> SensorList:
    """
    Takes a single structure from the Modbus response and turns it into a list of
    sensors as specified by the WDL JSON 0.1.0 specification, using the ConversionResult
    from convert_single_struct as an intermediary representation.
    """
    convResult = convert_single_struct(registers)
    sensorIds = [
        f"pm{convResult['busIndex']}-{suffix}"
        for suffix in ["phase1", "phase2", "phase3", "module"]
    ]
    result = [
        {"sensorId": sid, "energyvalues": [{"timestamp": convResult["timestamp"]}]}
        for sid in sensorIds
    ]

    # some assertion which are important for the correctness of the code below
    assert result[0]["sensorId"] == f"pm{convResult['busIndex']}-phase1"
    assert result[1]["sensorId"] == f"pm{convResult['busIndex']}-phase2"
    assert result[2]["sensorId"] == f"pm{convResult['busIndex']}-phase3"
    assert result[3]["sensorId"] == f"pm{convResult['busIndex']}-module"

    keys = convResult.keys()
    for key in keys:
        if key in ("timestamp", "busIndex"):
            continue

        value = convResult[key]
        # a rather simplistic approach: if we have one value we assume it is for the
        # module itself, otherwise they correspond to the 3 phases. The assumption
        # is that the 3 phases come first, then the module, as defined by the initial
        # result above
        if isinstance(value, float):
            result[3]["energyvalues"][0][key] = value
        elif isinstance(value, list) and len(value) == 3:
            for (index, num) in enumerate(value):
                result[index]["energyvalues"][0][key] = num
        else:
            raise TypeError(
                f"Unsupported data type '{type(value)}' for key '{key}'"
                + f" in the converted data: {value}"
            )

    return result


def merge_energy_values(target: SensorList, source: SensorList) -> SensorList:
    """
    Merges the energy values of one SensorList into another
    """
    for sourceEntry in source:
        targetEntry = next(
            (s for s in target if s["sensorId"] == sourceEntry["sensorId"]), None
        )
        if not targetEntry:
            target.append(sourceEntry)
        else:
            targetEntry["energyvalues"].append(  # type: ignore
                sourceEntry["energyvalues"][0]   # type: ignore
            )

    return target
