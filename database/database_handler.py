import psycopg2
import json

def get_connection(credentials_file):
    with open(credentials_file, "r") as read_file:
        credentials = json.load(read_file)
    conn = psycopg2.connect(host = credentials['host'],
        port = "5432",
        user=credentials['user'],
        password=credentials['password'],
        database = credentials['database'],
        options=str("-c search_path="+credentials['schema'])
        )
    return conn