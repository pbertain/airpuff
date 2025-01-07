#!/bin/bash

# rdog-rrd-web-create.sh
# Paul Bertain paul@bertain.net
# From: Wed 02 Nov 2017
# Wed 03 Jan 2024

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORTS_LOWER_NOSPACE=$(echo -e "${AIRPORTS_LOWER}" | tr -d "[:space:]")
FILEPATH="/var/www/vhosts/airpuff/html/rrdweb"
W_COAST_TIME=`TZ="America/Los_Angeles" date +"%a %m/%d %T%Z"`
E_COAST_TIME=`TZ="America/New_York" date +"%a %m/%d %T%Z"`
ZULU_TIMEZONE=`date -u +"%a %m/%d %T%Z"`
GET_SITE_NAME="/usr/local/bin/airpuff/get-icao-site-name.py"
PYTHON3="/usr/bin/python3"

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr "[:upper:]" "[:lower:]")
    PRODFILE="${FILEPATH}/${AIRPORT_LOWER}-rrd.html"
    TEMPFILE="${PRODFILE}.temp"
    SITE_NAME=`${PYTHON3} ${GET_SITE_NAME} ${AIRPORT_LOWER}`

    cat /dev/null > ${TEMPFILE}

    echo "<html>" > ${TEMPFILE}
    echo "<head>" >> ${TEMPFILE}
    echo "<meta http-equiv="refresh" content="900">" >> ${TEMPFILE}
    echo "<title>AirPuff - ${AIRPORT} Historical Data</title>" >> ${TEMPFILE}
    echo "</head>" >> ${TEMPFILE}
    echo "<body bgcolor="#333333" link="#CCAAAA" alink="#CCAAAA" vlink="#CCAAAA">" >> ${TEMPFILE}

    echo "<font color="yellow" face="Tahoma" size=2>" >> ${TEMPFILE}

    echo '<table>' >> ${TEMPFILE}
    echo '<tr>' >> ${TEMPFILE}
    echo '    <td class="td_titles" rowspan="3" vertical-align="center"><a href="https://www.airpuff.info/"><img width="100"  height="81" src="/web/icons/airpuff-logo.png"></a></td>' >> ${TEMPFILE}
    echo "    <td><font color="yellow" face="Tahoma" size=2>" >> ${TEMPFILE}
    echo "<p><em><h><font face=+3>${AIRPORT} Airport Historical Weather Data</font></h2></em></p>" >> ${TEMPFILE}
    echo '    </td>' >> ${TEMPFILE}
    echo '</tr>' >> ${TEMPFILE}

    echo '<tr>' >> ${TEMPFILE}
    echo "    <td><p><em><h3><font color="orange" face="Tahoma" size=4>Site name: ${SITE_NAME}</h3></em></p></td>" >> ${TEMPFILE}
    echo '</tr>' >> ${TEMPFILE}

    echo '<tr>' >> ${TEMPFILE}
    echo '    <td>' >> ${TEMPFILE}
    echo "        <font face="Courier" size=3>" >> ${TEMPFILE}
    echo "        <font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${TEMPFILE}
    echo "        <font color="lightgreen">${W_COAST_TIME}" >> ${TEMPFILE}
    echo "        <font color="pink">${E_COAST_TIME}" >> ${TEMPFILE}
    echo '    </td>' >> ${TEMPFILE}
    echo '</tr>' >> ${TEMPFILE}
    echo '</table>' >> ${TEMPFILE}

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

