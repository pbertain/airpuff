

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $Id: airpuff.sh 720 2012-09-23 16:42:44Z pbertain $
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

# Notes: This is the first pass as a shell script.  Next will be a perl script and then hopefully a python script.

DATAFILE="/var/www/vhosts/airpuff/html/airpuff.html.temp"
PRODFILE="/var/www/vhosts/airpuff/html/airpuff.html"
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
    FLIGHT_CATEGORY=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $31 }'`
    RAW_TEXT=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $1 }'`
    TEMP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $6 }'`
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $7 }'`
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD}" ` ;
    WIND_DIR=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $8 }'`
    WIND_DIR_FORMATTED=`printf "%003d" "${WIND_DIR}"` ;
    WIND_SPEED=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $9 }'`
    VIS=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $11 }' | sed -e 's/+//g'`
    ALTIMETER=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $12 }'`
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    METAR_TYPE=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $43 }'`
    SKY_COVER=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $23,$24,$25,$26,$27,$28,$29,$30 }'`k
    ELEVATION_M=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $44 }'`
    ELEVATION_FT=`echo "${ELEVATION_M} * 100 / 2.54 / 12" | bc -l` ;
    ELEVATION_FORMATTED=`printf "%0004.0f" "${ELEVATION_FT}" ` ;
    OBS_TIME=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $3 }' | awk -FT '{ print $2 }' | awk -F: '{ print $1":"$2 }'`


    echo "<tr>" >> ${DATAFILE} ;
    echo "<td>${AIRPORT}</td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td>${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}</td><td>${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td>${SKY_COVER}</td><td>${ELEVATION_FORMATTED}</td>"  >> ${DATAFILE} ;
    echo "</tr>" >> ${DATAFILE} ;
    echo >> ${DATAFILE} ;
done
echo "<td colspan=14><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${DATAFILE}
echo "</table>" >> ${DATAFILE}
echo "</body>" >> ${DATAFILE}
echo "</html>" >> ${DATAFILE}
mv ${DATAFILE} ${PRODFILE}
