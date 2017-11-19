

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $Id: airpuff.sh 720 2012-09-23 16:42:44Z pbertain $
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

# Notes: This is the first pass as a shell script.  Next will be a perl script and then hopefully a python script.

DATAFILE="/var/www/html/htdocs/airpuff/html/airpuff.html.temp"
PRODFILE="/var/www/html/htdocs/airpuff/html/airpuff.html"
AIRPORTS="KEDU KVCB KSUU KCCR KLVK KHWD KOAK KSQL KRHV KSJC KNUQ KPAO"
LOCALTIMEZONE=`TZ='America/Los_Angeles' date +'%a %F %T %Z'`
ZULU_TIMEZONE=`date -u +'%a %F %T %Z/Zulu/Z'`

cat /dev/null > ${DATAFILE}
echo "<html>" > ${DATAFILE}
echo "<head>" >> ${DATAFILE}
echo '<meta http-equiv="refresh" content="1800">' >> ${DATAFILE}
echo "<title>AirPuff Airport WX Info</title>" >> ${DATAFILE}
echo "</head>" >> ${DATAFILE}
echo '<body bgcolor="#333333">' >> ${DATAFILE}
echo '<font color="white" face="Tahoma" size=5>' >> ${DATAFILE}
echo "AirPuff current run:" >> ${DATAFILE}
echo '<font face="Courier" size=3>' >> ${DATAFILE}
echo "<br><font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${DATAFILE}
echo "<br><font color="lightgreen">${LOCALTIMEZONE}" >> ${DATAFILE}
echo "<br>" >> ${DATAFILE}
echo "<br>" >> ${DATAFILE}
echo '<font color="white" face="Courier" size=3>' >> ${DATAFILE}
echo '<table style="color: #FFFFFF; border: 1; border-spacing: 5px; bordercolor: black ; text-align: left; ">' >> ${DATAFILE}
echo '<tr style="color:yellow; border=1; text-align:center">' >> ${DATAFILE}
echo "<th>ARPT</th><th>TIME</th><th>TYPE</th><th>CAT</th><th>TEMP</th><th>DEW PT</th><th>T-DP</th><th>WIND</th><th>VIS</th><th>ALT</th><th>SKY COVER</th><th>ELEV</th>" >> ${DATAFILE}
echo '</tr>' >> ${DATAFILE}

for AIRPORT in $AIRPORTS ; do
    FLIGHT_CATEGORY=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep flight_category | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    #RAW_TEXT=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep raw_text | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | sed -e 's/AUTO//' -e 's/RMK.*//'` ;
    TEMP_C=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep temp_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep dewpoint_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD}" ` ;
    WIND_DIR=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_dir_degrees | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    WIND_DIR_FORMATTED=`printf "%003d" "${WIND_DIR}"` ;
    WIND_SPEED=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_speed_kt | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    VIS=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep visibility_statute_mi | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep altim_in_hg | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    METAR_TYPE=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep metar_type | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    SKY_COVER=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    ELEVATION_M=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep elevation_m | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ELEVATION_FT=`echo "${ELEVATION_M} * 100 / 2.54 / 12" | bc -l` ;
    ELEVATION_FORMATTED=`printf "%0004.0f" "${ELEVATION_FT}" ` ;
    OBS_TIME=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep observation_time | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | awk -FT '{ print $2 }'` ;

    echo "<tr>" >> ${DATAFILE} ;
    echo "<td>${AIRPORT}</td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td>${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}</td><td>${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td>${SKY_COVER}</td><td>${ELEVATION_FORMATTED}</td>"  >> ${DATAFILE} ;
    echo "</tr>" >> ${DATAFILE} ;
    echo >> ${DATAFILE} ;
done
echo "<td colspan=12><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${DATAFILE}
echo "</table>" >> ${DATAFILE}
echo "</body>" >> ${DATAFILE}
echo "</html>" >> ${DATAFILE}
mv ${DATAFILE} ${PRODFILE}
