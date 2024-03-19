import requests
import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import datetime
import pyodbc
import pytz

# Define the Eastern Time zone
eastern = pytz.timezone('America/New_York')

server = "database-1.czm6aegec3xq.us-east-2.rds.amazonaws.com"
database = "pogoh"
username = "master"
password = "egahIeae$aevnef#4"
driver = "{ODBC Driver 18 for SQL Server}"
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

def update_stock():
    engine = sa.create_engine(conn_str)

    try:
        r = requests.get('https://pittsburgh.publicbikesystem.net/customer/gbfs/v2/en/station_status')
        r.raise_for_status()

        j = r.json()
        stock = pd.DataFrame(j['data']['stations'])

        stock['last_reported'] = pd.to_datetime(stock['last_reported'], unit='s')
        
        stock['global_update_time'] = datetime.now(tz=eastern)
        stock['id'] = stock['station_id'].astype(str) + '@' + stock['global_update_time'].astype(str)
        stock.set_index('id', inplace=True)

        cols = ['station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available',
                'num_docks_disabled', 'last_reported', 'is_charging_station', 'status', 'is_installed',
                'is_renting', 'is_returning', 'traffic', 'global_update_time']

        stock[cols].to_sql("fact_stock", engine, if_exists='append', index=True, chunksize=1000)

        return {"statusCode": 200, "body": {"message": 'Finished refreshing stock'}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}

def handler(event, context):
    print(event)
    return update_stock()

# Uncomment the line below to test the update_stock function locally
#print(handler('event', 'context'))
