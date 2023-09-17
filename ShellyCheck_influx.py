#!/usr/bin/python3

from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import requests
import time
import sys
print(sys.version)


# InfluxDB configuration
INFLUXDB_HOST = 'localhost'  # Replace with your InfluxDB host IP/hostname
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'shelly1'  # Replace with the desired database name

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"
SHELLY_1PM_IP = "192.168.0.12"

# Constants for Time Intervals
DATA_INTERVAL = timedelta(seconds=10)
SLEEP_INTERVAL = 1  # Adjust the time interval based on your requirements


def write_to_influxdb(client, measurement, meas_time, tags, fields):
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
    url = f"{SHELLY_3EM_IP}/emeter/{port}"  # Adjust the URL based on the device's API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve 3em data from port {port}. Status code: {response.status_code}")
        return None
    
def get_1pm_data():
    response = requests.get(f"http://{SHELLY_1PM_IP}/rpc/Switch.GetStatus?id=0", timeout=5)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve balcony data. Status code: {response.status_code}")
        return None
    


def main():
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
