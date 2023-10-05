#!/usr/bin/python3

from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import time
import sys
from functions.shelly_util import get_3em_data
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
DATA_INTERVAL = 60  # Time between readings

def main():
    """
    Main function to collect and store data from Shelly devices.
    """

    # Connect to InfluxDB
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=INFLUXDB_DATABASE)

    while True:
        # Read shelly data from the 3 phases
        for port in range(3):
            shelly_3em_data = get_3em_data(port=port)
            current_time = datetime.utcnow()
            energy_in = shelly_3em_data["total"]
            energy_out = shelly_3em_data["total_returned"]

            measurement = "shelly_3em"
            tags = {
                "port": port
            }
            fields = {
                "energy_in": energy_in,
                "energy_out": energy_out
            }
            write_to_influxdb(client, measurement, current_time, tags, fields)
        
        time.sleep(DATA_INTERVAL)

if __name__ == "__main__":
    main()
