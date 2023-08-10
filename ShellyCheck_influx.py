from datetime import datetime
from influxdb import InfluxDBClient
import requests
import time

# InfluxDB configuration
INFLUXDB_HOST = 'localhost'  # Replace with your InfluxDB host IP/hostname
INFLUXDB_PORT = 8086
INFLUXDB_DATABASE = 'shelly1'  # Replace with the desired database name
INFLUXDB_USERNAME = 'admin'  # Replace with your InfluxDB username (if applicable)
INFLUXDB_PASSWORD = 'j1e1a1n1'  # Replace with your InfluxDB password (if applicable)

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"
SHELLY_1PM_IP = "192.168.0.12"

def write_to_influxdb(client, measurement, tags, fields):
    json_body = [
        {
            "measurement": measurement,
            "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
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
                            database=INFLUXDB_DATABASE,
                            username=INFLUXDB_USERNAME,
                            password=INFLUXDB_PASSWORD)
    
    last_3em_power = [0] * 3
    last_1pm_power = 0
    powertrigger = 1 # DeltaP to trigger the data writing in the DB

    while True:
        # Read and write data from Shelly 3EM ports
        for port in range(3):
            shelly_3em_data = get_3em_data(port=port)
            if shelly_3em_data:
                measurement = "shelly_3em"
                tags = {
                    "port": port
                }
                fields = {
                    "power": shelly_3em_data["power"],
                    "voltage": shelly_3em_data["voltage"],
                    "current": shelly_3em_data["current"],
                    "pf": shelly_3em_data["pf"]
                }
                
                if abs(fields["power"] - last_3em_power[port]) > powertrigger:
                    write_to_influxdb(client, measurement, tags, fields)
                    last_3em_power[port] = fields["power"]
                    print(f"Shelly 3EM data from port {port} written to InfluxDB.")
                    print(fields)
        
        # Read data from Shelly Plus 1PM
        shelly_1pm_data = get_balcon_data()
        if shelly_1pm_data:
            measurement = "shelly_1pm"
            tags = {
                "tag": "NA"
            }
            fields = {
                "power": shelly_1pm_data["apower"],
                "voltage": shelly_1pm_data["voltage"],
                "current": shelly_1pm_data["current"]
            }
            if abs(fields["power"] - last_1pm_power) > powertrigger:
                write_to_influxdb(client, measurement, tags, fields)
                last_1pm_power = fields["power"]
                print(f"Shelly Plus 1PM data written to InfluxDB.")
                print(fields)
        
        time.sleep(1)  # Adjust the time interval based on your requirements

if __name__ == "__main__":
    main()
