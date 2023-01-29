#!/usr/bin/env python
"""
This is a simple script starting up a Modbus server with some test values,
to verify that values are read and interpreted correctly.
"""

import pyModbusTCP.utils as utils
from pyModbusTCP.server import ModbusServer

if __name__ == "__main__":
    originalValues = [
        230.03,
        229.87,
        230.15,
        3.03,
        0.63,
        0.19,
        697.87,
        144.21,
        43.62,
        21490440.0,
    ]
    encodedValues = list(map(utils.encode_ieee, originalValues))
    registerValues = utils.long_list_to_word(encodedValues, big_endian=False)

    server = ModbusServer(host="localhost", port=5020)
    server.data_bank.set_input_registers(0, registerValues)
    print("Server starting")
    server.start()
