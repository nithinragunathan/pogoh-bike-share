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
driver = "{ODBC Driver 18 for SQL Server}"
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

fig = go.Figure(data=go.Scattergeo(
    lon=stock['lon'],
    lat=stock['lat'],
    mode='markers',
    marker_color='black'
))

fig.update_geos(fitbounds="locations", visible=True, showland = True)


fig.update_layout(
    geo_scope='usa'
)






app = Dash(__name__)

app.layout = html.Div([
    #generate_table(stock),
    dcc.Graph(id='example-map',figure=fig)
])

if __name__ == '__main__':
    app.run(debug=True)