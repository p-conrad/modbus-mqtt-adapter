# Modbus MQTT Adapter

This is a program to read a contiguous number of Modbus registers and transform them into a JSON
object according to a given configuration. The result is then forwarded via MQTT. This can be useful
if you have a PLC sharing some data (e.g. measurement values) and want to redirect them for central
processing or storing.


## Example

Consider the following list of registers:
```python
# as integers:
[1966, 17254, 57016, 17253, 9830, 17254, 60293, 16449, 18350, 16161, 36700, 15938, 30638, 17454, 13763, 17168, 31457, 16942, 62852, 19363]
# as hex:
['0x07ae', '0x4366', '0xdeb8', '0x4365', '0x2666', '0x4366', '0xeb85', '0x4041', '0x47ae', '0x3f21', '0x8f5c', '0x3e42', '0x77ae', '0x442e', '0x35c3', '0x4310', '0x7ae1', '0x422e', '0xf584', '0x4ba3']
```

Given the following configuration:
```python
DATA_IS_BIG_ENDIAN: bool = False
DATA_SIZE: int = 20
DATA_LAYOUT: List[DataEntry] = [
    DataEntry("voltage", 0, 2, 3, PlcDataType.Float32),
    DataEntry("current", 6, 2, 3, PlcDataType.Float32),
    DataEntry("power", 12, 2, 3, PlcDataType.Float32),
    DataEntry("energy", 18, 2, 1, PlcDataType.Float32),
]
```

The register values will be transformed into this kind of object:
```json
{
  "device": "plc",
  "timestamp": 1675015833,
  "results": [
    {
      "voltage": [
        230.03,
        229.87,
        230.15
      ],
      "current": [
        3.03,
        0.63,
        0.19
      ],
      "power": [
        697.87,
        144.21,
        43.62
      ],
      "energy": 21490440,
      "index": 0
    }
  ]
}
```


# Features

* Supports most of the common PLC data types. Missing types can be easily added.
* Supports big endian as well as little endian register orders.
* Multiple values of the same type (e.g. energy values for multiple phases) can be grouped into an
  array without having to assign a name and configuration to each of them.
* Reading values of multiple modules is supported given that the memory layout of each one is the
  same.
* Uses the asynchronous MQTT client from the
  [Eclipse Paho Python library](https://github.com/eclipse/paho.mqtt.python). Sending of messages
  happens independently from the main cycle, thus not affecting the run time even in case of a bad
  connection.
* All relevant settings can be set with command-line arguments
  (using Python's [argparse](https://docs.python.org/3/library/argparse.html) library).
* Uses Pythons [logging framework](https://docs.python.org/3/library/logging.html) with
  a configurable log level. Messages are printed to the console and also saved to a log file. Log
  files are automatically rotated after reaching a certain size, with older files getting deleted
  automatically.


# Limitations

* Data shared by the PLC over Modbus must be in one contiguous array, though the base address can be
  defined freely.
* Currently, only reading the input registers is supported (function code 4).
* Data can be read from one device only.
* Configuration of the data layout is currently static and needs to be done by modifying the
  `config.py` file.
* The logging directory is currently hard-coded and cannot be changed by configuration.


# Installation

To create a reproducible environment, installation using [pipenv](https://pypi.org/project/pipenv/)
is recommended: After checking out the repository, the `pipenv install` command creates a new Python
environment with the dependencies necessary for the script. This environment can be made available
in the terminal using `pipenv shell` or, alternatively, the script can be executed directly with
`pipenv run ./main.py`.

Alternatively, the script can be launched without pipenv if the dependencies specified in the
`Pipfile` (currently paho-mqtt and pyModbusTCP) are installed and available in the system.


## As a systemd Unit

This script can be set up as a systemd unit and automatically started as a service together with the
system. After the script with its dependencies has been installed, a file
`modbus-mqtt-adapter.service` with the following content (adapting the user name, paths, and
parameters as needed) must first be created under `/etc/systemd/system` or copied from this
repository:
```
[Unit]
Description=Modbus->MQTT Adapter
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
WorkingDirectory=/home/user/modbus-mqtt-adapter
ExecStart=/usr/bin/pipenv run ./main.py --loglevel info
StandardInput=tty-force
User=user

[Install]
WantedBy=multi-user.target
```

The service can then be loaded and activated with the following commands:
```
$ systemctl daemon-reload
$ systemctl enable --now modbus-mqtt-adapter
```

No the service can be managed with systemd in the usual manner, e.g.:
```
$ systemctl stop modbus-mqtt-adapter
$ systemctl start modbus-mqtt-adapter
$ systemctl restart modbus-mqtt-adapter
$ systemctl status modbus-mqtt-adapter
```

An important limitation is that the log outputs are not processed and stored by the systemd journal.
Checking the logs is explained in the next section.


## Monitoring the Operation

By default, the service saves log files named `main.log` in the `logs` folder during operation.  The
latest output can be viewed with the command `tail logs/main.log` command. Live output with a higher
number of lines is possible via the parameters `-f` and `-n`, e.g.: `tail -n 30 -f logs/main.log`


# Usage

First of all, program your PLC to share your desired data points over Modbus and adapt the
configuration file (`config.py`) to reflect your setup. You may then run the script from the
command line with `./main.py [PARAMETERS]`. Use `./main.py --help` to get an overview of the
available settings.
