#!/bin/python

import cgitb
cgitb.enable(display=0, logdir="/var/log")

import urllib2
from xml.dom import minidom
import xml.etree.ElementTree as ET

import cgi
#form = cgi.FieldStorage()
#user = form.getfirst("user", "").upper()    # This way it's safe.
#for item in form.getlist("item"):
#    print item

AIRPORTS = ['kedu', 'kvcb', 'ksuu', 'kccr', 'klvk', 'khwd', 'koak', 'krhv', 'ksjc', 'ksql', 'knuq', 'kpao']
METARTAGS = ['metar_type', 'flight_category', 'station_id', 'observation_time', 'temp_c', 'dewpoint_c', 'wind_dir_degrees', 'wind_speed_kt', 'visibility_statute_mi', 'altim_in_hg']
HEADINGS = ['METAR', 'CAT', 'ICAO', 'Time', 'Temp C', 'Dew Pt C', 'Wind Dir', 'Wind Speed', 'Vis', 'Alt']

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers
print "<html>\n<title>AirPuff ATIS Reports</title>"
print "<body bgcolor=black>"
print "<font face='Georgia' color='yellow'>"
print "<h1>ATIS Reports from KEDU to KPAO</h1>"
print "<h2>This is AirPuff</h3>"
print "<table border=1>"
print "<tr>"
for HD in HEADINGS:
    print "<td><font face='Georgia' color='yellow'>%s</font></td>" % HD
print "</tr><br>"
for AP in AIRPORTS:
    metar = urllib2.urlopen("http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=%s" % AP)
    xmldoc = minidom.parse(metar)
    #for element in xmldoc.getElementsByTagName('flight_category','station_id','observation_time','temp_c',dewpoint_c','wind_dir','wind_speed_kt','visibility_statute_mi','altim_in_hg'):
    print '<tr>'
    for MT in METARTAGS:
        for element in xmldoc.getElementsByTagName("%s" % MT):
            print "<td><font face='Georgia' color='yellow'>" + element.firstChild.nodeValue + '</font></td>'
    print '</tr>'
print "</table></face></body>\n</html>"


