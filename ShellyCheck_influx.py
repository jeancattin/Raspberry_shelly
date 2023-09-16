from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import requests
import time

# InfluxDB configuration
INFLUXDB_HOST = 'localhost'  # Replace with your InfluxDB host IP/hostname
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'shelly1'  # Replace with the desired database name

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"
SHELLY_1PM_IP = "192.168.0.12"

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
    
def get_balcon_data():
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
    start_time = datetime.utcnow()
    power_accumulated_3em = [0] * 3
    power_accumulated_1pm = 0
    samples_count = 0

    while True:
        # Read data from Shelly 3EM ports and accumulate power
        for port in range(3):
            shelly_3em_data = get_3em_data(port=port)
            if shelly_3em_data:
                power_accumulated_3em[port] += shelly_3em_data["power"]
        
        # Read data from Shelly Plus 1PM and accumulate power
        shelly_1pm_data = get_balcon_data()
        if shelly_1pm_data:
            power_accumulated_1pm += shelly_1pm_data["apower"]
        
        samples_count += 1

        # Check if 10 seconds have passed
        current_time = datetime.utcnow()
        time_difference = current_time - start_time
        if time_difference >= timedelta(seconds=5):
            # Calculate mean power for each channel
            mean_power_3em = [power / samples_count for power in power_accumulated_3em]
            mean_power_1pm = power_accumulated_1pm / samples_count
            
            # Write mean power to InfluxDB
            for port in range(3):
                measurement = "shelly_3em"
                tags = {
                    "port": port
                }
                fields = {
                    "power": mean_power_3em[port]
                }
                write_to_influxdb(client, measurement, current_time, tags, fields)
            measurement = "shelly_1pm"
            tags = {
                "tag": "NA"
            }
            fields = {
                "power": mean_power_1pm
            }
            write_to_influxdb(client, measurement, current_time, tags, fields)
            
            # Reset variables for the next 10-second interval
            power_accumulated_3em = [0] * 3
            power_accumulated_1pm = 0
            samples_count = 0
            start_time = current_time

        time.sleep(1)  # Adjust the time interval based on your requirements

if __name__ == "__main__":
    main()
