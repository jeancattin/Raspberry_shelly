# Shelly Measurement Script Documentation

## Introduction
This documentation provides information on setting up and using the Shelly Measurement Script. The script is designed to read data from one Shelly 3em device and store it in an InfluxDB database for monitoring (through Grafana) and analysis.

## Prerequisites
Before using this script, ensure you have the following:

- Raspberry Pi running Raspbian or a compatible OS
- InfluxDB installed and configured
- Python 3 installed
- Git installed (for easy script retrieval)
- 3em Shelly device connected on the same local network
- Knowledge of your Shelly devices' IP addresses

## Overview
The Shelly Measurement Script collects the measured energy data (on the 3 phases) from the Shelly 3EM device, and stores the data in an InfluxDB database. 

## Script Configuration and setup
The step by step terminal command list for raspberry configuration is given in the file "Installation_clone".
Before running the script, configure the following variables in the script:

- `INFLUXDB_HOST`: The IP or hostname of your InfluxDB server.
- `INFLUXDB_PORT`: The InfluxDB server port.
- `INFLUXDB_DATABASE`: The desired InfluxDB database name.
- `SHELLY_3EM_IP`: IP address of the Shelly 3EM.

## Running the Script
Execute the script using Python 3. Use the following command:

```bash
python3 main.py
```

## Export the data to csv
Execute the data export script "influxDB_ExportData.py":
```bash
python3 influxDB_ExportData.py
```

## Hardware list
- Raspberry pi
- Raspberry power supply
- USB mouse and keyboard
- Micro-HDMI to HDMI cable for raspberry screen connection
- Shelly 3em

## Conclusion
Initial realease by Jean Cattin

## Version History
 **Version 1.0 (28.09.2023)
  - Initial release.
 **Version 1.2 (05.10.2023)
  - Code simplification for a single device