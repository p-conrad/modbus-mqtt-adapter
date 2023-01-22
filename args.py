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
        type=str,
        default="127.0.0.1",
        help="The address of the PLC to connect to",
    )
    argParser.add_argument(
        "-t",
        "--target",
        type=str,
        default="127.0.0.1",
        help="The address of the target MQTT broker",
    )
    argParser.add_argument(
        "-p", "--port", type=int, default=1883, help="The port of the MQTT broker"
    )
    argParser.add_argument(
        "-U",
        "--username",
        type=str,
        default="",
        help="Username for the MQTT broker",
    )
    argParser.add_argument(
        "-P",
        "--password",
        type=str,
        default="",
        help="Password for the MQTT broker"
        + " (will be requested from the command line if empty and username is provided)",
    )
    argParser.add_argument(
        "-n",
        "--modules",
        metavar="NUM",
        type=int,
        default=1,
        help="The number of modules to read from on the bus",
    )
    argParser.add_argument(
        "-b",
        "--baseaddress",
        metavar="NUM",
        type=int,
        default=0,
        help="The starting address of the PLC registers where the data is stored",
    )
    argParser.add_argument(
        "-i",
        "--interval",
        metavar="NUM",
        type=float,
        default=5,
        help="The interval to poll data from the PLC, in seconds"
        + " (can be a decimal number)",
    )
    argParser.add_argument(
        "-d",
        "--device",
        type=str,
        default="plc",
        help="The name of the PLC device where the data is read from"
        + " (used as ID in the sent dataset and as part of the MQTT client ID)",
    )
    argParser.add_argument(
        "-a",
        "--accumulate",
        type=int,
        default=10,
        help="How many results to accumulate before sending them to the broker",
    )
    argParser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        choices=["debug", "info", "warn", "warning", "error", "critical"],
        default="info",
        help="The logging level."
        + " Logging output at or above this level will be written to the log file",
    )
    return argParser.parse_args()
