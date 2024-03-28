import requests
import pandas as pd
import sqlalchemy as sa
import urllib
from datetime import datetime
import pyodbc
import pytz
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# Define the Eastern Time zone
eastern = pytz.timezone('America/New_York')

from config import DATABASE_CONFIG
db_config = DATABASE_CONFIG

params = urllib.parse.quote_plus(
    'Driver=%s;' % db_config['driver'] +
    'Server=tcp:%s,1433;' % db_config['server'] +
    'Database=%s;' % db_config['database'] +
    'Uid=%s;' % db_config['username'] +
    'Pwd={%s};' % db_config['password'] +
    'Encrypt=yes;' +
    'TrustServerCertificate=yes;' +
    'Connection Timeout=90;')



conn_str = 'mssql+pyodbc:///?odbc_connect=' + params

Base = declarative_base()

class FactStock(Base):
    __tablename__ = 'fact_stock'

    id = Column(Integer, primary_key=True)
    station_id = Column(String)
    num_bikes_available = Column(Integer)
    num_bikes_disabled = Column(Integer)
    num_docks_available = Column(Integer)
    num_docks_disabled = Column(Integer)
    last_reported = Column(String)
    is_charging_station = Column(String)
    status = Column(String)
    is_installed = Column(String)
    is_renting = Column(String)
    is_returning = Column(String)
    traffic = Column(String)
    global_update_time = Column(DateTime)


from datetime import timedelta

from sqlalchemy.orm import sessionmaker

def update_stock():
    engine = sa.create_engine(conn_str)

    try:
        r = requests.get('https://pittsburgh.publicbikesystem.net/customer/gbfs/v2/en/station_status')
        r.raise_for_status()

        j = r.json()
        stock = pd.DataFrame(j['data']['stations'])

        stock['last_reported'] = (pd.to_datetime(stock['last_reported'], unit='s', utc=True).dt.tz_convert('US/Eastern')).apply(lambda x: x.strftime('%m-%d-%Y %I:%M %p'))

        stock['global_update_time'] = datetime.now(tz=eastern)
        stock['id'] = stock['station_id'].astype(str) + '@' + stock['global_update_time'].astype(str)
        stock.set_index('id', inplace=True)

        cols = ['station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available',
                'num_docks_disabled', 'last_reported', 'is_charging_station', 'status', 'is_installed',
                'is_renting', 'is_returning', 'traffic', 'global_update_time']

        # Delete rows older than 7 days
        oldest_allowed_time = datetime.now(tz=eastern) - timedelta(days=7)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(FactStock).filter(FactStock.global_update_time < oldest_allowed_time).delete()
        session.commit()
        session.close()

        # Write new data to the database
        stock[cols].to_sql("fact_stock", engine, if_exists='append', index=True, chunksize=1000)

        return {"statusCode": 200, "body": {"message": 'Finished refreshing stock'}}
    except Exception as e:
        return {"statusCode": 500, "body": {"error": str(e)}}


def handler(event, context):
    print(event)
    return update_stock()

# Uncomment the line below to test the update_stock function locally
#print(handler('event', 'context'))