# POGOH Bikeshare Map

Link:
https://9jdgmtuxtq.us-east-2.awsapprunner.com/

This is a webapp that allows users to see historical bike availability for the POGOH Bikeshare service in Pittsburgh, Pennsylvania.

# Stack
Database: Amazon RDS Microsoft SQL Server

ETL: Dockerized Python on AWS Lambda

Front-End: Dockerized Plotly Dash App on AWS App Runner

The data refreshes every 30 minutes, at :20 and :50 of each hour.

![alt text](<Architecture Diagram.png>)