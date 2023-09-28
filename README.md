# Shelly Measurement Script Documentation

## Introduction
This documentation provides information on setting up and using the Shelly Measurement Script. The script is designed to read data from Shelly devices and store it in an InfluxDB database for monitoring (through Grafana) and analysis.

## Prerequisites
Before using this script, ensure you have the following:

- Raspberry Pi running Raspbian or a compatible OS
- InfluxDB installed and configured
- Python 3 installed
- Git installed (for easy script retrieval)
- Shelly devices (Shelly 3EM and/or Shelly 1PM) connected on the same local network
- Knowledge of your Shelly devices' IP addresses

## Overview
The Shelly Measurement Script collects data from Shelly 3EM and Shelly 1PM devices, calculates mean measurements over a specified time interval, and stores the data in an InfluxDB database. It periodically retrieves data and resets accumulated values for accurate measurements.

## Script Configuration and setup
The step by step terminal command list for raspberry configuration is given in the file "Installation_clone".
Before running the script, configure the following variables in the script:

- `INFLUXDB_HOST`: The IP or hostname of your InfluxDB server.
- `INFLUXDB_PORT`: The InfluxDB server port.
- `INFLUXDB_DATABASE`: The desired InfluxDB database name.
- `SHELLY_3EM_IP`: IP address of Shelly 3EM.
- `SHELLY_1PM_IP`: IP address of Shelly 1PM.

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
- Shelly 3em and/or Shelly plus 1pm

## Conclusion
Initial realease by Jean Cattin

## Version History
 **Version 1.1 (28.09.2023)
  - Initial release.
