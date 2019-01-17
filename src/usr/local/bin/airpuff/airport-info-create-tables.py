import sqlite3
import sys

db_name            = '/var/airpuff/data/airport_info.db'
table_name         = 'airports'
fields             = 'airport, wx_phone, tower_phone'

# Connect to the database (and create if necessary)
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Create table with 'table_name' and list of 'fields'
c.execute('''CREATE TABLE airports (airport, wx_phone, tower_phone)''')

conn.commit()
conn.close()

