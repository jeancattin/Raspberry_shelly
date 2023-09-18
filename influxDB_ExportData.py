import pandas as pd
from influxdb import InfluxDBClient
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

# Function to execute when the "Export" button is clicked
def export_data():
    start_date = start_time_calendar.get_date()
    end_date = end_time_calendar.get_date()

    # Convert selected dates to datetime.date objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    # Adjust the end_date to the end of the day (23:59:59)
    end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    # Your InfluxDB connection settings
    host = 'localhost'
    port = 8086
    database = 'shelly1'

    # Define your query to extract data
    query = f'SELECT * FROM shelly_3em WHERE time >= \'{start_date}\' AND time <= \'{end_date}\''

    # Initialize InfluxDB client
    client = InfluxDBClient(host=host, port=port, database=database)

    # Execute the query
    result = client.query(query)

    # Convert the result to a DataFrame
    dataframe = pd.DataFrame(result.get_points())

    # Get the current date and time
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Create a file name with the current date and time
    file_name = f'data_{current_datetime}.csv'

    # Save the DataFrame to the CSV file
    dataframe.to_csv(file_name, index=False)

    output_label.config(text=f'Data saved to {file_name}')

# Create a Tkinter window
window = tk.Tk()
window.title("Data Export")

# Calendar widgets for start and end times
start_time_label = ttk.Label(window, text="Select Start Date:")
start_time_label.pack()
start_time_calendar = Calendar(window, date_pattern='yyyy-mm-dd')
start_time_calendar.pack()

end_time_label = ttk.Label(window, text="Select End Date:")
end_time_label.pack()
end_time_calendar = Calendar(window, date_pattern='yyyy-mm-dd')
end_time_calendar.pack()

# Export button
export_button = ttk.Button(window, text="Export Data", command=export_data)
export_button.pack()

# Output label
output_label = ttk.Label(window, text="")
output_label.pack()

# Start the GUI main loop
window.mainloop()
