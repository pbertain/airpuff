#!/usr/bin/env python

import urllib2
from xml.dom import minidom

AIRPORTS = ['kedu', 'kvcb', 'ksuu', 'kccr', 'klvk', 'khwd', 'koak', 'krhv', 'ksjc', 'ksql', 'knuq', 'kpao']

for AP in AIRPORTS:
    metar = urllib2.urlopen("http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=%s" % AP)
    xmldoc = minidom.parse(metar)
    for element in xmldoc.getElementsByTagName('raw_text'):
        print element.firstChild.nodeValue

