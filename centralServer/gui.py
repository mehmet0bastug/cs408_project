import dash
from dash import dcc, html
import threading
import time
import random
import json
from queue import Queue

# Create a global data queue and a persistent data storage
data_queue = Queue()
all_data = []

# Simulate data for testing (you can remove this if your server is running)
def simulate_data():
    while True:
        data = {
            "sensor_id": "test_sensor",
            "temperature": round(random.uniform(15, 30), 2),
            "humidity": round(random.uniform(30, 70), 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        data_queue.put(data)
        time.sleep(2)

# Start data simulation in a separate thread
threading.Thread(target=simulate_data, daemon=True).start()

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Central Server Raw Data Display"),
    html.Div(id="data-display"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0)
])

@app.callback(
    dash.dependencies.Output("data-display", "children"),
    [dash.dependencies.Input("interval-component", "n_intervals")]
)
def update_data(_):
    # Retrieve all current data in the queue
    while not data_queue.empty():
        all_data.append(data_queue.get())

    # Format all received data as HTML
    if all_data:
        formatted_data = "<br>".join([json.dumps(data) for data in all_data])
        return formatted_data
    else:
        return "No data received yet."

if __name__ == "__main__":
    app.run(debug=True, port=8050)
