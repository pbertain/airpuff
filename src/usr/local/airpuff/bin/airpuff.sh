#!/bin/sh

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $Id: airpuff.sh 720 2012-09-23 16:42:44Z pbertain $
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

# Notes: This is the first pass as a shell script.  Next will be a perl script and then hopefully a python script.

DATAFILE="/var/www/html/airpuff/airpuff.html"
AIRPORTS="kedu kvcb ksuu kccr klvk khwd koak ksql krhv ksjc knuq kpao"
LOCALTIMEZONE=`TZ='America/Los_Angeles' date`
DATA=`/usr/local/bin/airpuff.py`

cat /dev/null > $DATAFILE
echo "<html>" > $DATAFILE
echo "<title>AirPuff Airport WX Info</title>" >> $DATAFILE
echo "<head>" >> $DATAFILE
echo '<meta http-equiv="refresh" content="1800">' >> $DATAFILE
echo "</head>" >> $DATAFILE
echo '<body bgcolor="black">' >> $DATAFILE
echo '<font color="white" face="Tahoma" size=5>' >> $DATAFILE
echo "AirPuff current run:" >> $DATAFILE
echo "<br>Zulu Time - `date -u`" >> $DATAFILE
echo "<br>Pacific Time - ${LOCALTIMEZONE}" >> $DATAFILE
echo "<br>" >> $DATAFILE
echo "<br>" >> $DATAFILE
echo '<font color="white" face="Courier" size=3>' >> $DATAFILE
for AIRPORT in $AIRPORTS ;
do echo "<tr>" >> $DATAFILE ;
curl -s http://weather.noaa.gov/mgetmetar.php?cccc=$AIRPORT | grep -A1 "^<hr>" | sed -e 's/<hr>//' | tr '\n' ' ' >> $DATAFILE ;
#cat ${DATA} >> $DATAFILE ;
echo "</tr>" >> $DATAFILE ;
echo >> $DATAFILE ;
echo "<br>" >> $DATAFILE ;
done
echo "</td>" >> $DATAFILE
echo "</body>" >> $DATAFILE
echo "</html>" >> $DATAFILE

