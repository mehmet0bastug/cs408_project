import threading
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
from server import dataQueue

df = pd.DataFrame(columns=['timestamp', 'sensorId', 'value'])

def dataCollector():
    while True:
        msg = dataQueue.get()
        global df
        df = pd.concat([df, pd.DataFrame([msg])], ignore_index=True)

threading.Thread(target=dataCollector, daemon=True).start()

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Central Server Dashboard"),
    dcc.Graph(id='liveGraph'),
    dcc.Interval(id='interval', interval=2000)
])

@app.callback(Output('liveGraph', 'figure'), Input('interval', 'n_intervals'))
def updateGraph(_):
    if df.empty:
        return {}
    fig = px.line(df, x='timestamp', y='value', color='sensorId', title='Sensor Values Over Time')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
