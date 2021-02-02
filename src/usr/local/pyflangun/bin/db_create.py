"""This script helps create the AirPuff™ databases"""
import sqlite3
from sqlite3 import Error
"""Set the global variables"""
dbdir = "/usr/local/pyflangun/var/db/"
def create_connection(db_file):
    """This module makes the connection to the DB"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn
def create_table(conn, create_table_sql):
    """This module creates the tables"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
def main():
    """This is the main module"""
    database = dbdir + "pyflangun.db"
    sql_create_airports_table = """CREATE TABLE IF NOT EXISTS airports (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    icao text
                                );"""
    sql_create_weather_table = """CREATE TABLE IF NOT EXISTS weather (
                                    id integer PRIMARY KEY,
                                    icao text NOT NULL,
                                    temp_f integer NOT NULL,
                                    dew_pt_f integer NOT NULL,
                                    status integer NOT NULL,
                                    FOREIGN KEY (icao) REFERENCES airports (icao)
                                );"""
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        create_table(conn, sql_create_airports_table)
        create_table(conn, sql_create_weather_table)
    else:
        print("Error! cannot create the database connection.")
if __name__ == '__main__':
    main()
