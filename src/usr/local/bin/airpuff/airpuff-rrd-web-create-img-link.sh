#!/bin/bash

# airpuff-rrd-web-create.sh
# Paul Bertain paul@bertain.net
# Wed 04 Nov 2017

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORTS_LOWER_NOSPACE=$(echo -e "${AIRPORTS_LOWER}" | tr -d "[:space:]")
FILEPATH="/var/www/vhosts/airpuff/html/rrdweb/img-link"
W_COAST_TIME=`TZ="America/Los_Angeles" date +"%a %m/%d %T%Z"`
E_COAST_TIME=`TZ="America/New_York" date +"%a %m/%d %T%Z"`
ZULU_TIMEZONE=`date -u +"%a %m/%d %T%Z"`
GET_SITE_NAME="/usr/local/bin/airpuff/get-icao-site-name.py"
PYTHON3="/usr/bin/python3"
HTML_IMG_PATH="/rrdweb/img-link"

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr "[:upper:]" "[:lower:]")
    SITE_NAME=`${PYTHON3} ${GET_SITE_NAME} ${AIRPORT_LOWER}`
    for METRIC in alti ceil visi wind temp ; do 
        for TIMERANGE in day week month year ; do
            PRODFILE="${FILEPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}-rrd.html"
            DAYFILE="${HTML_IMG_PATH}/${AIRPORT_LOWER}-${METRIC}-day-rrd.html"
            WEEKFILE="${HTML_IMG_PATH}/${AIRPORT_LOWER}-${METRIC}-week-rrd.html"
            MONTHFILE="${HTML_IMG_PATH}/${AIRPORT_LOWER}-${METRIC}-month-rrd.html"
            YEARFILE="${HTML_IMG_PATH}/${AIRPORT_LOWER}-${METRIC}-year-rrd.html"
            TEMPFILE="${PRODFILE}.temp"

            cat /dev/null > ${TEMPFILE}

            echo "<html>" > ${TEMPFILE}
            echo "<head>" >> ${TEMPFILE}
            echo "<meta http-equiv="refresh" content="900">" >> ${TEMPFILE}
            echo "<title>AirPuff - ${AIRPORT} - ${METRIC^} - ${TIMERANGE^}</title>" >> ${TEMPFILE}
            echo "</head>" >> ${TEMPFILE}
            echo "<body bgcolor="#333333" link="#CCAAAA" alink="#CCAAAA" vlink="#CCAAAA">" >> ${TEMPFILE}
	    
	    echo '<table>' >> ${TEMPFILE}
            echo '<tr>' >> ${TEMPFILE}
            echo '    <td class="td_titles" rowspan="3" vertical-align="center"><a href="https://www.airpuff.info/"><img width="100"  height="81" src="/web/icons/airpuff-logo.png"></a></td>' >> ${TEMPFILE}
            echo "    <td><font color="yellow" face="Tahoma" size=2>" >> ${TEMPFILE}
            echo "<p><em><h2>${AIRPORT} Airport Historical Weather Data <font color="white">- <font color="#d16aff">${METRIC^} over the last ${TIMERANGE^}</h2></em></p>" >> ${TEMPFILE}
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
            echo "<tr>" >> ${TEMPFILE}
            echo "    <td><center><b><a href="/rrdweb/${AIRPORT_LOWER}-rrd.html">All metrics for ${AIRPORT}</a></b></center></td>" >> ${TEMPFILE}
            echo "</tr>" >> ${TEMPFILE}
            echo "<tr>" >> ${TEMPFILE}
            echo "  <td>" >> ${TEMPFILE}
            echo "  <center>" >> ${TEMPFILE}
            echo "  [ <a href="${DAYFILE}">day</a> ]" >> ${TEMPFILE}
            echo "  [ <a href="${WEEKFILE}">week</a> ]" >> ${TEMPFILE}
            echo "  [ <a href="${MONTHFILE}">month</a> ]" >> ${TEMPFILE}
            echo "  [ <a href="${YEARFILE}">year</a> ]" >> ${TEMPFILE}
            echo "  </center>" >> ${TEMPFILE}
            echo "  </td>" >> ${TEMPFILE}
            echo "</tr>" >> ${TEMPFILE}
            echo "<tr>" >> ${TEMPFILE}
            echo "  <td><center><b>${TIMERANGE^}</b></center></td>" >> ${TEMPFILE}
            echo "</tr>" >> ${TEMPFILE}
            echo "<tr>" >> ${TEMPFILE}
            echo "  <center>" >> ${TEMPFILE}
            echo "  <td><img src="/images/rrd/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png"></a></td>" >> ${TEMPFILE}
            echo "  </center>" >> ${TEMPFILE}
            echo "</tr>" >> ${TEMPFILE}
            echo >> ${TEMPFILE} ;
        done
        echo "<td colspan=1><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
        echo "</table>" >> ${TEMPFILE}
        echo "</body>" >> ${TEMPFILE}
        echo "</html>" >> ${TEMPFILE}
        mv -f ${TEMPFILE} ${PRODFILE}
    done
done

