import threading
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
from server import data_queue
import pandas as pd
import datetime

# Initialize empty dataframe
df = pd.DataFrame(columns=['timestamp', 'sensor_id', 'value', 'type'])

# Data collector thread
def data_collector():
    global df
    while True:
        msg = data_queue.get()
        # Flatten the message for easier display
        for key, value in msg.items():
            if key not in ["sensor_id", "timestamp", "data_points"]:
                new_row = {
                    "timestamp": msg["timestamp"],
                    "sensor_id": msg["sensor_id"],
                    "value": value,
                    "type": key
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

threading.Thread(target=data_collector, daemon=True).start()

# Initialize Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Central Server Raw Data Display"),
    html.Pre(id="data-display", style={
        "overflow-y": "scroll",
        "height": "80vh",
        "border": "1px solid #ccc",
        "padding": "10px",
        "background-color": "#f4f4f4",
        "font-family": "monospace",
        "white-space": "pre-wrap"
    }),
    dcc.Interval(id="interval", interval=2000, n_intervals=0)
])

# Update the raw data display
@app.callback(
    Output("data-display", "children"),
    Input("interval", "n_intervals")
)
def update_data_display(_):
    if df.empty:
        return "No data received yet."
    
    # Create a nicely formatted text output
    rows = []
    for _, row in df.iterrows():
        rows.append(f"[{row['timestamp']}] {row['sensor_id']} - {row['type'].capitalize()}: {row['value']}")
    
    # Join the rows with line breaks
    return "\n".join(rows)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
