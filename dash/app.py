import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import datetime
import pytz

# Create a Dash app
app = Dash(__name__)

# Data processing
server = "database-1.czm6aegec3xq.us-east-2.rds.amazonaws.com"
database = "pogoh"
username = "master"
password = "egahIeae$aevnef#4"
driver = "{ODBC Driver 17 for SQL Server}"
params = urllib.parse.quote_plus(
    'Driver=%s;Server=tcp:%s,1433;Database=%s;Uid=%s;Pwd={%s};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=90;pool_pre_ping=true' % (driver, server, database, username, password))

conn_str = 'mssql+pyodbc:///?odbc_connect=' + params
engine = sa.create_engine(conn_str)

def update_data():
    try:
        with engine.connect() as conn:
            stock = pd.read_sql('select s.station_id, num_bikes_available, num_docks_available, last_reported, global_update_time, name, lat, lon from dbo.fact_stock fs left join dbo.stations s on fs.station_id = s.station_id;', conn)
        return stock
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

def update_map():
    stock = update_data()

    fig = px.scatter_mapbox(stock, lat='lat', lon='lon', hover_name='name', size='num_bikes_available', color_continuous_scale = 'oxy', color='num_bikes_available', mapbox_style='carto-positron', size_max=7, range_color=(0, 15), animation_frame='global_update_time',
                            hover_data={'num_bikes_available': True, 'num_docks_available': True, 'last_reported': True, 'lat': False, 'lon': False, 'global_update_time': False})

    fig.update_layout(mapbox=dict(center={'lat': 40.4406, 'lon': -79.98}, zoom=11.75), margin={"r": 0, "t": 0, "l": 0, "b": 0}, autosize=True, height=750)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),  # Set margin to zero
        coloraxis_showscale=True,  # Hide the color legend
    )
    fig["layout"].pop("updatemenus")

    # Set the initial value of the animation frame slider to its maximum value
    fig.update_layout(
        sliders=[{
            "active": len(fig.frames) - 1,  # Set the active frame to the last frame
            "steps": [{"args": [[frame.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", }, ], "label": str(frame.name), "method": "animate", } for frame in fig.frames]
        }],
    )

    # Update the trace objects with the data from the last frame and customize hovertemplate
    last_frame_data = fig.frames[-1]["data"]
    for i, trace in enumerate(fig.data):
        trace.update(last_frame_data[i])
        trace.hovertemplate = 'Bikes available: %{customdata[0]}<br>' + \
                              'Docks available: %{customdata[1]}<br>' + \
                              'Last reported: %{customdata[2]}<br>'

    return fig


# Define the layout of the Dash app with a black background
def layout():
    return html.Div(
        children=[
            dcc.Graph(id='map-graph'),
            dcc.Interval(
                id='interval-component',
                interval=30 * 60 * 1000,  # in milliseconds
                n_intervals=0
            )
        ]
    )

app.layout = layout()

# Callback to update the map figure
@app.callback(
    Output('map-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map_figure(n):
    return update_map()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=9000)
