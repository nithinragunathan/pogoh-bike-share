import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlalchemy as sa
import urllib
import plotly.graph_objects as go

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

def update_map(data_type):
    stock = update_data()
    stock = stock.rename(columns={
    'num_bikes_available': 'Number of Bikes',
    'num_docks_available': 'Open Docks',
    'last_reported': 'Last Reported',
    'global_update_time': 'Global Update Time'})

    # Convert time columns to datetime objects
    stock['Last Reported'] = pd.to_datetime(stock['Last Reported'], format='%m-%d-%Y %I:%M %p')
    stock['Global Update Time'] = pd.to_datetime(stock['Global Update Time'], format='%m-%d-%Y %I:%M %p')

    # Sort DataFrame by Global Update Time
    stock = stock.sort_values(by='Global Update Time')

    if data_type == 'bikes':
        size_column = 'Number of Bikes'
        color_column = 'Number of Bikes'
    elif data_type == 'docks':
        size_column = 'Open Docks'
        color_column = 'Open Docks'

    # Formatting the datetime objects for hover labels and slider
    stock['Last Reported'] = stock['Last Reported'].dt.strftime('%m-%d-%Y %I:%M %p')
    stock['Global Update Time'] = stock['Global Update Time'].dt.strftime('%m-%d-%Y %I:%M %p')

    fig = px.scatter_mapbox(stock, lat='lat', lon='lon', hover_name='name', size=size_column, color_continuous_scale='oxy', color=color_column, mapbox_style='carto-darkmatter', size_max=7, range_color=(0, 15), animation_frame='Global Update Time',
                             hover_data={'Number of Bikes': True, 'Open Docks': True, 'Last Reported': True, 'lat': False, 'lon': False, 'Global Update Time': False})
    fig.update_layout(mapbox=dict(center={'lat': 40.4406, 'lon': -79.98}, zoom=11.75), margin={"r": 0, "t": 0, "l": 0, "b": 0}, autosize=True, height=750)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),  # Set margin to zero
        coloraxis_showscale=True,  # Hide the color legend
        font=dict(family='Futura, sans-serif', color='white'),  # Set font to Futura and color to white
        plot_bgcolor='black',  # Set background color of the whitespace
        paper_bgcolor='black',  # Set background color of the paper
        hoverlabel=dict(font_color='black'),  # Set hover label font color to white
    )
    fig["layout"].pop("updatemenus")

    last_frame_num = len(fig.frames) - 1

    fig.layout['sliders'][0]['active'] = last_frame_num  # Set initial frame to the last frame
    fig = go.Figure(data=fig['frames'][-1]['data'], frames=fig['frames'], layout=fig.layout)

    return fig


def layout():
    return html.Div(
        style={'backgroundColor': 'black', 'padding': '20px', 'height': '90vh', 'width': '80vw', 'font-family': 'Futura, sans-serif', 'margin': '0'},
        children=[
            html.H1('POGOH Bikeshare Availability', style={'textAlign': 'center', 'color': '#FFC433', 'margin-bottom': '20px'}),

            html.Div([
                dcc.RadioItems(
                    id='toggle-data-type',
                    options=[
                        {'label': 'Bikes', 'value': 'bikes'},
                        {'label': 'Docks', 'value': 'docks'}
                    ],
                    value='bikes',  # Default value
                    labelStyle={'display': 'inline-block', 'margin-right': '10px', 'color': '#FFC433'}  # Change the font color to #FFC433
                )
            ], style={'textAlign': 'center', 'margin-bottom': '20px'}),
            dcc.Graph(id='map-graph', style={'margin': '0'}),
            dcc.Interval(
                id='interval-component',
                interval=30 * 60 * 1000,  # in milliseconds
                n_intervals=0
            )
        ],
        className='container'
    )

app.layout = layout()

# Callback to update the map figure based on the toggle selection
@app.callback(
    Output('map-graph', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('toggle-data-type', 'value')]
)
def update_map_figure(n, data_type):
    return update_map(data_type)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=9000)