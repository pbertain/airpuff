import sys
import sqlite3

db_name            = '/var/airpuff/data/airport_info.db'
icao               = sys.argv[1]
wx_phone           = sys.argv[2]
tower_phone        = sys.argv[3]

#conn               = sqlite3.connect('%s' % (db_name))
conn               = sqlite3.connect(db_name)
c                  = conn.cursor()

params             = (icao, wx_phone, tower_phone)

c                  = conn.cursor()
c.execute("INSERT INTO airports VALUES (?, ?, ?)", params)

conn.commit()
conn.close()

