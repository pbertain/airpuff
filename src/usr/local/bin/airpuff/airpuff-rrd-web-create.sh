#!/bin/sh

# airpuff-rrd-web-create.sh
# Paul Bertain paul@bertain.net
# Wed 02 Nov 2017

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORTS_LOWER_NOSPACE=$(echo -e "${AIRPORTS_LOWER}" | tr -d "[:space:]")
FILEPATH="/var/www/html/htdocs/airpuff.info/html/rrdweb"
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
    echo "<tr><th></th><th>Altimeter</th><th>Ceiling</th><th>Visibility</th><th>Wind Speed & Dir</th><th>Temp</th></tr>" >> ${TEMPFILE}
    echo "<tr>" >> ${TEMPFILE}
    for TIMERANGE in day week month year ; do
        echo "  <td>${TIMERANGE^}</td>" >> ${TEMPFILE}
        for METRIC in alti ceil visi wind temp ; do 
            echo "  <td><a href="/rrdweb/img-link/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}-rrd.html"><img src="/images/rrd/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png" width="150" height="75"></a></td>" >> ${TEMPFILE}
        done
        echo "</tr>" >> ${TEMPFILE}
    done
    echo >> ${TEMPFILE} ;
done
echo "<td colspan=4><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
echo "</table>" >> ${TEMPFILE}
echo "</body>" >> ${TEMPFILE}
echo "</html>" >> ${TEMPFILE}
mv -f ${TEMPFILE} ${PRODFILE}

