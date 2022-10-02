import os
from dotenv import load_dotenv
import psycopg2
import sys

load_dotenv(".env")

db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
db_password = os.environ["DB_PASSWORD"]
db_port = os.environ["DB_PORT"]
db_user = os.environ["DB_USER"]




def create_connection():
    "Create Database Connection"

    host = db_host
    dbname = db_name
    user = db_user
    password = db_password
    sslmode = "require"

    # Constructing connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
        host, user, dbname, password, sslmode
    )

    try:
        connection = psycopg2.connect(conn_string)
        print("Connection established")

    except psycopg2.Error as e:
        print(f"Error connecting to Postgres DB : {e}")
        sys.exit(1)

    curr = connection.cursor()
    return connection, curr