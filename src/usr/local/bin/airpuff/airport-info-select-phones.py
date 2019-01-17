import sys
import sqlite3

db_name            = '/var/airpuff/data/airport_info.db'
icao               = sys.argv[1]

conn               = sqlite3.connect(db_name)
c                  = conn.cursor()
c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao,))
atis_phone         = c.fetchone()
print("%s" % atis_phone)

conn.commit()
conn.close()

