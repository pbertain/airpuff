#!/bin/sh

/bin/logger "Starting AirPuff run now."
/bin/python /usr/local/bin/airpuff.py | sed -e 's/AUTO//' -e 's/RMK.*//' | mail -s "Airpuff - `TZ='America/Los_Angeles' /bin/date '+%H:00 Hour - %a %d %b %y'`" paul@bertain.net
/bin/logger "AirPuff run complete."
