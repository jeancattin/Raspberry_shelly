#!/usr/bin/python3

from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import requests
import time
import sys
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

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"
SHELLY_1PM_IP = "192.168.0.12"

# Constants for Time Intervals
DATA_INTERVAL = timedelta(seconds=10) # Time between datapoints in the DB
SLEEP_INTERVAL = 1  # Sampling rate for the average


def write_to_influxdb(client, measurement, meas_time, tags, fields):
    """
    Writes data to InfluxDB.

    Args:
        client (InfluxDBClient): The InfluxDB client.
        measurement (str): The measurement name.
        meas_time (datetime): The timestamp of the measurement.
        tags (dict): Tags associated with the measurement.
        fields (dict): Field values for the measurement.
    """
    json_body = [
        {
            "measurement": measurement,
            "time": meas_time,
            "tags": tags,
            "fields": fields
        }
    ]
    client.write_points(json_body)

def get_3em_data(port):
    """
    Retrieves data from Shelly 3EM for a specific port.

    Args:
        port (int): The Shelly 3EM port number.

    Returns:
        dict or None: A dictionary containing the retrieved data, or None if the request fails.
    """
    url = f"{SHELLY_3EM_IP}/emeter/{port}"  # Adjust the URL based on the device's API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve 3em data from port {port}. Status code: {response.status_code}")
        return None
    
def get_1pm_data():
    """
    Retrieves data from Shelly 1PM.

    Returns:
        dict or None: A dictionary containing the retrieved data, or None if the request fails.
    """
    response = requests.get(f"http://{SHELLY_1PM_IP}/rpc/Switch.GetStatus?id=0", timeout=5)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve balcony data. Status code: {response.status_code}")
        return None
    


def main():
    """
    Main function to collect and store data from Shelly devices.
    """
        
    # Connect to InfluxDB
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT,
                            database=INFLUXDB_DATABASE)
    
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

        # Check if the timeinterval has passed
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
