#!/bin/sh

# airpuff-rrd-web-create.sh
# Paul Bertain paul@bertain.net
# Wed 02 Nov 2017

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORTS_LOWER_NOSPACE=$(echo -e "${AIRPORTS_LOWER}" | tr -d "[:space:]")
FILEPATH="/var/www/html/htdocs/airpuff/html/rrdweb"
W_COAST_TIME=`TZ="America/Los_Angeles" date +"%a %F %T %Z"`
E_COAST_TIME=`TZ="America/New_York" date +"%T %Z"`
ZULU_TIMEZONE=`date -u +"%a %F %T %Z/Zulu/Z"`


for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr "[:upper:]" "[:lower:]")
    PRODFILE="${FILEPATH}/${AIRPORT_LOWER}-rrd.html"
    TEMPFILE="${PRODFILE}.temp"

    cat /dev/null > ${TEMPFILE}

    echo "<html>" > ${TEMPFILE}
    echo "<head>" >> ${TEMPFILE}
    echo "<meta http-equiv="refresh" content="1800">" >> ${TEMPFILE}
    echo "<title>AirPuff - ${AIRPORT} Historical Data</title>" >> ${TEMPFILE}
    echo "</head>" >> ${TEMPFILE}
    echo "<body bgcolor="#333333" link="#CCAAAA" alink="#CCAAAA" vlink="#CCAAAA">" >> ${TEMPFILE}
    echo "<font color="yellow" face="Tahoma" size=2>" >> ${TEMPFILE}
    echo "<p><em><h2>${AIRPORT} Airport Historical Weather Data</h2></em></p>" >> ${TEMPFILE}
    echo "<font face="Courier" size=3>" >> ${TEMPFILE}
    echo "<br><font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${TEMPFILE}
    echo "<br><font color="lightgreen">${W_COAST_TIME} / ${E_COAST_TIME}" >> ${TEMPFILE}
    echo "<br>" >> ${TEMPFILE}
    echo "<br>" >> ${TEMPFILE}
    echo "<font color="white" face="Courier" size=3>" >> ${TEMPFILE}
    echo '<table style="color:#cccccc; font-family: Tahoma; font-size: 10px">' >> ${TEMPFILE}
    echo "<tr><th></th><th>Altimeter</th><th>Wind Speed & Dir</th><th>Visibility</th></tr>" >> ${TEMPFILE}
    echo "<tr>" >> ${TEMPFILE}
    echo "  <td>Day</td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-alti-day.png"><img src="/images/rrd/${AIRPORT_LOWER}-alti-day.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-wind-day.png"><img src="/images/rrd/${AIRPORT_LOWER}-wind-day.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-visi-day.png"><img src="/images/rrd/${AIRPORT_LOWER}-visi-day.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "</tr>" >> ${TEMPFILE}
    echo "<tr>" >> ${TEMPFILE}
    echo "  <td>Week</td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-alti-week.png"><img src="/images/rrd/${AIRPORT_LOWER}-alti-week.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-wind-week.png"><img src="/images/rrd/${AIRPORT_LOWER}-wind-week.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-visi-week.png"><img src="/images/rrd/${AIRPORT_LOWER}-visi-week.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "</tr>" >> ${TEMPFILE}
    echo "<tr>" >> ${TEMPFILE}
    echo "  <td>Month</td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-alti-month.png"><img src="/images/rrd/${AIRPORT_LOWER}-alti-month.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-wind-month.png"><img src="/images/rrd/${AIRPORT_LOWER}-wind-month.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-visi-month.png"><img src="/images/rrd/${AIRPORT_LOWER}-visi-month.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "</tr>" >> ${TEMPFILE}
    echo "<tr>" >> ${TEMPFILE}
    echo "  <td>Year</td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-alti-year.png"><img src="/images/rrd/${AIRPORT_LOWER}-alti-year.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-wind-year.png"><img src="/images/rrd/${AIRPORT_LOWER}-wind-year.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "  <td><a href="/images/rrd/${AIRPORT_LOWER}-visi-year.png"><img src="/images/rrd/${AIRPORT_LOWER}-visi-year.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
    echo "</tr>" >> ${TEMPFILE}
    echo >> ${TEMPFILE} ;
done
echo "<td colspan=4><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
echo "</table>" >> ${TEMPFILE}
echo "</body>" >> ${TEMPFILE}
echo "</html>" >> ${TEMPFILE}
mv -f ${TEMPFILE} ${PRODFILE}

