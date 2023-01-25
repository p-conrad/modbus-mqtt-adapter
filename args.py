"""
This module contains the get_args function responsible for creating an ArgumentParser
instance and parsing all our supported command line arguments.
"""

from argparse import ArgumentParser


def get_args():
    """
    Creates and configures an ArgumentParser which parses the command line arguments,
    returning the results.
    """
    argParser = ArgumentParser(
        description="Reads PLC data points over Modbus/TCP, serializes them"
        + "and and sends the results to a MQTT broker."
    )
    argParser.add_argument(
        "-s",
        "--source",
        metavar="ADDRESS",
        type=str,
        default="localhost",
        help="The address of the PLC to connect to (default: localhost)",
    )
    argParser.add_argument(
        "-sp",
        "--sourceport",
        metavar="NUMBER",
        type=int,
        default=502,
        help="The port under which to connect to the PLC (default: 502)",
    )
    argParser.add_argument(
        "-t",
        "--target",
        metavar="ADDRESS",
        type=str,
        default="localhost",
        help="The address of the target MQTT broker (default: localhost)",
    )
    argParser.add_argument(
        "-tp",
        "--targetport",
        metavar="NUMBER",
        type=int,
        default=1883,
        help="The port under which to connect to the MQTT broker (default: 1883)",
    )
    argParser.add_argument(
        "-U",
        "--username",
        metavar="USER",
        type=str,
        default="",
        help="Username for the MQTT broker (default: none)",
    )
    argParser.add_argument(
        "-P",
        "--password",
        metavar="PASSWORD",
        type=str,
        default="",
        help="Password for the MQTT broker"
        + " (will be requested from the command line if empty and username is provided)",
    )
    argParser.add_argument(
        "-n",
        "--modules",
        metavar="NUMBER",
        type=int,
        default=1,
        help="The number of modules to read from on the bus (default: 1)",
    )
    argParser.add_argument(
        "-b",
        "--baseaddress",
        metavar="NUMBER",
        type=int,
        default=0,
        help="The starting address of the PLC input registers where the data is stored (default: 0)",
    )
    argParser.add_argument(
        "-i",
        "--interval",
        metavar="NUMBER",
        type=float,
        default=5,
        help="The interval to poll data from the PLC, in seconds"
        + " (can be a decimal number, default: 5)",
    )
    argParser.add_argument(
        "-d",
        "--device",
        metavar="NAME",
        type=str,
        default="plc",
        help="The name of the PLC device where the data is read from"
        + " (used as ID in the sent dataset and as part of the MQTT client ID, default: plc)",
    )
    argParser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        choices=["debug", "info", "warn", "warning", "error", "critical"],
        default="info",
        help="The logging level."
        + " Logging output at or above this level will be written to the log file (default: info)",
    )
    return argParser.parse_args()
