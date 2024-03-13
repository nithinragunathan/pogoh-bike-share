from dash import Dash, html, dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import timezone
from datetime import datetime
import pyodbc
import pytz

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

server = "database-1.czm6aegec3xq.us-east-2.rds.amazonaws.com"
database = "pogoh"
username = "master"
password = "egahIeae$aevnef#4"
driver = "{ODBC Driver 17 for SQL Server}"
connectionString = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes'

params = urllib.parse.quote_plus(
    'Driver=%s;' % driver +
    'Server=tcp:%s,1433;' % server +
    'Database=%s;' % database +
    'Uid=%s;' % username +
    'Pwd={%s};' % password +
    'Encrypt=yes;' +
    'TrustServerCertificate=yes;' +
    'Connection Timeout=90;')

conn_str = 'mssql+pyodbc:///?odbc_connect=' + params
engine = sa.create_engine(conn_str)

stock = pd.read_sql('select s.station_id, num_bikes_available, num_docks_available, last_reported, global_update_time, name, lat, lon from dbo.fact_stock fs left join dbo.stations s on fs.station_id = s.station_id;', engine)

utc_timezone = pytz.timezone('UTC')
eastern_timezone = pytz.timezone('US/Eastern')
stock['last_reported'] = stock['last_reported'].apply(lambda x : utc_timezone.localize(datetime.strptime(x[:-8], '%Y-%m-%d %H:%M:%S')).astimezone(eastern_timezone))
stock['last_reported'] = stock['last_reported'].apply(lambda x : x.astimezone(eastern_timezone))
stock['global_update_time'] = stock['global_update_time'].apply(lambda x : utc_timezone.localize(datetime.strptime(x[:-14], '%Y-%m-%d %H:%M:%S')).astimezone(eastern_timezone))
stock['global_update_time'] = stock['global_update_time'].apply(lambda x : x.astimezone(eastern_timezone))



stock

fig = px.scatter_mapbox(stock, lat='lat', lon='lon', hover_name='name', size='num_bikes_available', color='num_bikes_available', mapbox_style = 'carto-darkmatter', zoom = 11.5, animation_frame='global_update_time', size_max=6, range_color=(0, 25),
                        hover_data={'num_bikes_available': True, 'num_docks_available': True, 'last_reported': True, 'lat': False, 'lon': False, 'global_update_time': False})


fig.show()

'''
app = Dash(__name__)

app.layout = html.Div([
    #generate_table(stock),
    dcc.Graph(id='example-map',figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)
'''