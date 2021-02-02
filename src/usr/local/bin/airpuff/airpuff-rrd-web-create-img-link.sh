#!/bin/sh

# airpuff-rrd-web-create.sh
# Paul Bertain paul@bertain.net
# Wed 04 Nov 2017

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORTS_LOWER_NOSPACE=$(echo -e "${AIRPORTS_LOWER}" | tr -d "[:space:]")
FILEPATH="/var/www/html/htdocs/airpuff.info/html/rrdweb/img-link"
W_COAST_TIME=`TZ="America/Los_Angeles" date +"%a %F %T %Z"`
E_COAST_TIME=`TZ="America/New_York" date +"%T %Z"`
ZULU_TIMEZONE=`date -u +"%a %F %T %Z/Zulu/Z"`

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr "[:upper:]" "[:lower:]")
    for METRIC in alti ceil visi wind temp ; do 
        for TIMERANGE in day week month year ; do
            PRODFILE="${FILEPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}-rrd.html"
            TEMPFILE="${PRODFILE}.temp"

            cat /dev/null > ${TEMPFILE}

            echo "<html>" > ${TEMPFILE}
            echo "<head>" >> ${TEMPFILE}
            echo "<meta http-equiv="refresh" content="1800">" >> ${TEMPFILE}
            echo "<title>AirPuff - ${AIRPORT} - ${METRIC^} - ${TIMERANGE^}</title>" >> ${TEMPFILE}
            echo "</head>" >> ${TEMPFILE}
            echo "<body bgcolor="#333333" link="#CCAAAA" alink="#CCAAAA" vlink="#CCAAAA">" >> ${TEMPFILE}
            echo "<font color="yellow" face="Tahoma" size=2>" >> ${TEMPFILE}
            echo "<p><em><h2>${AIRPORT} Airport Historical Weather Data - ${METRIC^} over the last ${TIMERANGE^}</h2></em></p>" >> ${TEMPFILE}
            echo "<font face="Courier" size=3>" >> ${TEMPFILE}
            echo "<br><font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${TEMPFILE}
            echo "<br><font color="lightgreen">${W_COAST_TIME} / ${E_COAST_TIME}" >> ${TEMPFILE}
            echo "<br>" >> ${TEMPFILE}
            echo "<br>" >> ${TEMPFILE}
            echo "<font color="white" face="Courier" size=3>" >> ${TEMPFILE}
            echo '<table style="color:#cccccc; font-family: Tahoma; font-size: 10px">' >> ${TEMPFILE}
            echo "<tr>" >> ${TEMPFILE}
            echo "  <td><center><b>${TIMERANGE^}</b></center></td>" >> ${TEMPFILE}
            echo "</tr>" >> ${TEMPFILE}
            echo "<tr>" >> ${TEMPFILE}
            echo "  <td><img src="/images/rrd/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png"></a></td>" >> ${TEMPFILE}
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

