import requests

# Shelly device configuration
SHELLY_3EM_IP = "http://192.168.0.11"
SHELLY_1PM_IP = "192.168.0.12"

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
    
