#!/usr/bin/env python
"""
The main module, responsible for doing the initialization and running the read loop.
"""
from getpass import getpass
from time import time, sleep
import json
import logging
import logging.handlers
import os
import sys
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from args import get_args
from config import DATA_LAYOUT, DATA_SIZE
from conversions import convert_single_module
from mqtt import create_mqtt_client


def wait_next_cycle(start: float, duration: float) -> None:
    """
    Sleeps until one measurement cycle is completed.
    """
    elapsed = time() - start
    remaining = max(0, duration - elapsed)
    logging.debug("Sleeping for %s seconds", remaining)
    sleep(remaining)


if __name__ == "__main__":
    args = get_args()

    MQTT_TOPIC = f"modbus-mqtt/{args.device}"
    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "main.log")

    # set up logging with outputs on the console and to a logfile with different levels
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    fileHandler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE, maxBytes=1048576, backupCount=4
    )
    fileHandler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=args.loglevel.upper(),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[consoleHandler, fileHandler],
    )

    print("=== Modbus MQTT Adapter ===")
    print(f"Data Source  : {args.source}")
    print(f"MQTT Broker  : {args.target}:{args.port}")
    print(f"MQTT Topic   : {MQTT_TOPIC}")
    print(f"# of Modules : {args.modules}")
    print(f"Base Address : {args.baseaddress}")
    print(f"Poll Interval: {args.interval}s")
    print("")

    logging.info("Interface started with arguments: %s", args)

    # Modbus/TCP connection setup
    modbusClient = ModbusTcpClient(args.source)
    if not modbusClient.connect():
        logging.error("Connection to the PLC failed.")
        sys.exit(1)
    logging.info("Modbus connection to %s successful", args.source)

    # this helps with tracking the PLC connection state
    modbusConnected = True

    # MQTT connection setup
    if args.username and not args.password:
        args.password = getpass("MQTT Password: ")

    mqttClient = create_mqtt_client(args)
    mqttClient.connect_async(args.target, args.port)
    mqttClient.loop_start()

    # preparing the initial empty data set
    dataset = {
        "device": args.device,
        "results": []
    }

    try:
        while True:
            startTime = time()

            if not modbusConnected and modbusClient.connect():
                logging.info("Reconnection to the PLC successful")
                modbusConnected = True


            try:
                for i in range(0, 2):
                    # Pymodbus has a strange habit where every second request fails
                    # if the polling interval is too big (roughly equal to or above
                    # 2 seconds). Trying once more should fix it in most cases.
                    response = modbusClient.read_input_registers(
                        args.baseaddress, DATA_SIZE * args.modules
                    )
                    if not response.isError():
                        break

                if response.isError():
                        logging.warning(
                            "Modbus response is an error: %s. Skipping this cycle",
                            response,
                        )
                        wait_next_cycle(startTime, args.interval)
                        continue
            except ConnectionException:
                if modbusConnected:
                    logging.error("Connection to the PLC lost, trying to reconnect...")
                    modbusConnected = False
                wait_next_cycle(startTime, args.interval)
                continue

            for i in range(0, args.modules):
                moduleSlice = response.registers[i * DATA_SIZE : (i + 1) * DATA_SIZE]
                dataset["results"].append(
                    convert_single_module(moduleSlice, DATA_LAYOUT)
                )

            jsonStr = json.dumps(dataset, separators=(",", ":"))
            messageInfo = mqttClient.publish(MQTT_TOPIC, jsonStr, qos=2)
            logging.debug(
                "Publish requested for message with ID %s: %s",
                messageInfo.mid,
                jsonStr,
            )
            dataset["results"].clear()

            wait_next_cycle(startTime, args.interval)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, closing application")
        modbusClient.close()
        mqttClient.loop_stop()
        mqttClient.disconnect()
        sys.exit(0)
