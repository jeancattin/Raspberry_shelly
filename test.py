#!/usr/bin/python3

from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import requests
import time
import sys

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"


def get_3em_data(port):
    """
    Retrieves data from Shelly 3EM for a specific port.

    Args:
        port (int): The Shelly 3EM port number.

    Returns:
        dict or None: A dictionary containing the retrieved data, or None if the request fails.
    """
    url = f"{SHELLY_3EM_IP}/emeter/{port}/em_data.cs"  # Adjust the URL based on the device's API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve 3em data from port {port}. Status code: {response.status_code}")
        return None
    
    
def main():
    """
    Main function to collect and store data from Shelly devices.
    """
    while True:
        shelly_3em_data = get_3em_data(port=1)
        print(shelly_3em_data)
        time.sleep(10)
    
if __name__ == "__main__":
    main()