import requests
import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import datetime
import pyodbc

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


def update_stock():
    engine = sa.create_engine(conn_str)

    r = requests.get('https://pittsburgh.publicbikesystem.net/customer/gbfs/v2/en/station_status')
    j = r.json()

    stock = pd.DataFrame(j['data']['stations'])
    stock['last_reported'] = pd.to_datetime(stock['last_reported'], unit = 's')
    stock['global_update_time'] = pd.to_datetime(datetime.utcnow())
    stock['id'] = stock['station_id'].apply(lambda x: str(x)) + '@' + stock['global_update_time'].apply(lambda x: str(x))
    stock.set_index(['id'])


    cols = ['station_id', 'num_bikes_available', 'num_bikes_disabled',
       'num_docks_available', 'num_docks_disabled', 'last_reported',
       'is_charging_station', 'status', 'is_installed', 'is_renting',
       'is_returning', 'traffic', 'global_update_time', 'id']

    stock[cols].to_sql("fact_stock", engine, index = False, if_exists = 'append', chunksize = 10)
    print('Finished refreshing stock @ ', datetime.utcnow())
    return {"statusCode": 200,
             "body": {"message": 'Finished refreshing stock'}}

if __name__ == '__main__':
    update_stock()
    