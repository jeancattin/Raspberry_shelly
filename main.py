#!/usr/bin/python3

from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import time
import sys
from functions.shelly_util import get_3em_data, get_1pm_data
from functions.influxdb_util import write_to_influxdb

print(sys.version)

# Shelly Measurement Script Documentation
"""
This script collects data from Shelly 3EM and Shelly 1PM devices, calculates mean measurements over a specified time interval, and stores the data in an InfluxDB database.

Please refer to the accompanying README.md file for detailed instructions on setup and usage.
"""
# InfluxDB configuration
INFLUXDB_HOST = 'localhost'  # Replace with your InfluxDB host IP/hostname
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'shelly1'  # Replace with the desired database name

# Constants for Time Intervals
DATA_INTERVAL = timedelta(seconds=10)  # Time between datapoints in the DB
SLEEP_INTERVAL = 1  # Sampling rate for the average

def main():
    """
    Main function to collect and store data from Shelly devices.
    """

    # Connect to InfluxDB
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=INFLUXDB_DATABASE)

    # Initialize variables for mean power calculation
    mean_accumulated = {
        "3em": {
            "power": [0] * 3,
            "voltage": [0] * 3,
            "current": [0] * 3,
            "pf": [0] * 3
        },
        "1pm": {
            "power": 0,
            "voltage": 0,
            "current": 0
        }
    }

    samples_count = 0
    start_time = datetime.utcnow()

    while True:
        # Read data from Shelly 3EM ports and accumulate power
        for port in range(3):
            shelly_3em_data = get_3em_data(port=port)
            if shelly_3em_data:
                mean_accumulated["3em"]["power"][port] += shelly_3em_data["power"]
                mean_accumulated["3em"]["voltage"][port] += shelly_3em_data["voltage"]
                mean_accumulated["3em"]["current"][port] += shelly_3em_data["current"]
                mean_accumulated["3em"]["pf"][port] += shelly_3em_data["pf"]

        # Read data from Shelly Plus 1PM and accumulate power
        shelly_1pm_data = get_1pm_data()
        if shelly_1pm_data:
            mean_accumulated["1pm"]["power"] += shelly_1pm_data["apower"]
            mean_accumulated["1pm"]["voltage"] += shelly_1pm_data["voltage"]
            mean_accumulated["1pm"]["current"] += shelly_1pm_data["current"]

        samples_count += 1

        # Check if the time interval has passed
        current_time = datetime.utcnow()
        time_difference = current_time - start_time
        if time_difference >= DATA_INTERVAL:
            # Calculate mean measurements for each channel
            for port in range(3):
                measurement = "shelly_3em"
                tags = {
                    "port": port
                }
                fields = {
                    "power": mean_accumulated["3em"]["power"][port] / samples_count,
                    "voltage": mean_accumulated["3em"]["voltage"][port] / samples_count,
                    "current": mean_accumulated["3em"]["current"][port] / samples_count,
                    "pf": mean_accumulated["3em"]["pf"][port] / samples_count
                }
                write_to_influxdb(client, measurement, current_time, tags, fields)

            measurement = "shelly_1pm"
            tags = {
                "tag": "NA"
            }
            fields = {
                "power": mean_accumulated["1pm"]["power"] / samples_count,
                "voltage": mean_accumulated["1pm"]["voltage"] / samples_count,
                "current": mean_accumulated["1pm"]["current"] / samples_count,
            }
            write_to_influxdb(client, measurement, current_time, tags, fields)

            # Reset variables for the next 10-second interval
            for key in mean_accumulated:
                if isinstance(mean_accumulated[key], dict):
                    for subkey in mean_accumulated[key]:
                        if isinstance(mean_accumulated[key][subkey], list):
                            mean_accumulated[key][subkey] = [0] * len(mean_accumulated[key][subkey])
                        else:
                            mean_accumulated[key][subkey] = 0
                else:
                    mean_accumulated[key] = 0
            samples_count = 0
            start_time = datetime.utcnow()

        time.sleep(SLEEP_INTERVAL)  # Adjust the time interval based on your requirements

if __name__ == "__main__":
    main()
