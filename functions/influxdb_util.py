from influxdb import InfluxDBClient

def create_influxdb_client():
    """
    Create and return an InfluxDB client instance.

    Returns:
        InfluxDBClient: An InfluxDB client instance.
    """
    return InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database=INFLUXDB_DATABASE)

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
