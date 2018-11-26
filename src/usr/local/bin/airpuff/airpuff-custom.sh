#!/bin/sh

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

##### CUSTOMIZE HERE #####
REGION="$1"
AIRPORTS="$2"
##### END CUSTOMIZATION SECTION #####

REGION_LOWER=$(echo -e "${REGION}" | tr '[:upper:]' '[:lower:]')
REGION_LOWER_NOSPACE=$(echo -e "${REGION_LOWER}" | tr -d '[:space:]')
FILEPATH="/var/www/html/htdocs/airpuff.info/html"
PRODFILE="${FILEPATH}/${REGION_LOWER_NOSPACE}.html"
TEMPFILE="${PRODFILE}.temp"
W_COAST_TIME=`TZ='America/Los_Angeles' date +'%a %F %T %Z'`
E_COAST_TIME=`TZ='America/New_York' date +'%T %Z'`
ZULU_TIMEZONE=`date -u +'%a %F %T %Z/Zulu/Z'`
VFR_MIN=3000
MVFR_MIN=1000
MVFR_MAX=3000
IFR_MIN=500
IFR_MAX=1000
LIFR_MAX=500

cat /dev/null > ${TEMPFILE}
echo "<html>" > ${TEMPFILE}
echo "<head>" >> ${TEMPFILE}
echo '<meta http-equiv="refresh" content="300">' >> ${TEMPFILE}
echo "<title>${REGION} AirPuff Airport WX Info</title>" >> ${TEMPFILE}
echo "</head>" >> ${TEMPFILE}
echo '<body bgcolor="#333333">' >> ${TEMPFILE}
echo '<font color="white" face="Tahoma" size=5>' >> ${TEMPFILE}
echo "${REGION} AirPuff current run:" >> ${TEMPFILE}
echo '<font face="Courier" size=3>' >> ${TEMPFILE}
echo "<br><font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${TEMPFILE}
echo "<br><font color="lightgreen">${W_COAST_TIME} / ${E_COAST_TIME}" >> ${TEMPFILE}
echo "<br>" >> ${TEMPFILE}
echo "<br>" >> ${TEMPFILE}
echo '<font color="white" face="Courier" size=3>' >> ${TEMPFILE}
echo '<table style="color: #FFFFFF; border: 1; border-spacing: 3px; bordercolor: black ; text-align: left; ">' >> ${TEMPFILE}
echo '<tr style="color:yellow; border=1; text-align:center">' >> ${TEMPFILE}
echo "<th>ARPT</th><th>TIME</th><th>TYPE</th><th>CAT</th><th>TEMP</th><th>DEW PT</th><th>T-DP</th><th>WIND</th><th>VIS</th><th>ALT</th><th>SKY COVER</th><th>ELEV</th>" >> ${TEMPFILE}
echo '</tr>' >> ${TEMPFILE}
echo '<tr>' >> ${TEMPFILE}

for AIRPORT in ${AIRPORTS} ; do
    OBS_TIME=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep observation_time | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | awk -FT '{ print $2 }'` ;
    if [ -z ${OBS_TIME} ]; then
       echo "<td style=\"color:#999999; \">${AIRPORT}</td></tr>"  >> ${TEMPFILE} ;
       continue
    fi
    FLIGHT_CATEGORY=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep flight_category | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    #RAW_TEXT=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep raw_text | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | sed -e 's/AUTO//' -e 's/RMK.*//'` ;
    TEMP_C=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep temp_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    TEMP_C_FORMATTED=`printf "%000.1fF" "${TEMP_C}"` ;
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep dewpoint_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    DP_C_FORMATTED=`printf "%.1fF" "${DP_C}" ` ;
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD_C=`echo "${TEMP_C} - ${DP_C}" | bc -l` ;
    T_DP_SPREAD_C_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_C}" ` ;
    T_DP_SPREAD_F=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_F_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_F}" ` ;
    WIND_DIR=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_dir_degrees | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    WIND_DIR_FORMATTED=`printf "%003d" "${WIND_DIR}"` ;
    WIND_SPEED=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_speed_kt | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    VIS=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep visibility_statute_mi | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep altim_in_hg | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    METAR_TYPE=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep metar_type | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    SKY_COVERAGE=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    ELEVATION_M=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep elevation_m | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ELEVATION_FT=`echo "${ELEVATION_M} * 100 / 2.54 / 12" | bc -l` ;
    ELEVATION_FORMATTED=`printf "%0004.0f" "${ELEVATION_FT}" ` ;

    case "${FLIGHT_CATEGORY}" in
        VFR)
            WX_COLOR="#00FF00"
            ;;
        MVFR)
            WX_COLOR="#3333FF"
            ;;
        IFR)
            WX_COLOR="#FF0000"
            ;;
        LIFR)
            WX_COLOR="#FF00FF"
            ;;
        *)
            WX_COLOR="#AAAA00"
    esac

    # Convert VIS to integer
    VIS_INTEGER=${VIS/.*}

    if [ ${VIS_INTEGER} -ge 1 ] && [ "${VIS_INTEGER}" -lt 3 ]; then
            VIS_COLOR="#FF0000"
    elif [ ${VIS_INTEGER} -lt 1 ]; then
            VIS_COLOR="#FF00FF"
    elif [ ${VIS_INTEGER} -ge 3 ] && [ "${VIS_INTEGER}" -lt 5 ]; then
            VIS_COLOR="#3333FF"
    elif [ ${VIS_INTEGER} -ge 5 ]; then
            VIS_COLOR="#00FF00"
    else
            VIS_COLOR="333333"
    fi

    SKY_COVER=`curl -s "https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    SKY_COVER_ARRAY=(${SKY_COVER// / })
    SKY_COVER_ARRAY_LEN=${#SKY_COVER_ARRAY[@]}
    # VFR
    if [ ${SKY_COVER_ARRAY_LEN} -eq 1 ] && ([ ${SKY_COVER_ARRAY[0]} == "SKC" ] || [ ${SKY_COVER_ARRAY[0]} == "CLR" ]); then
        SKY_COVER_COLOR="#00FF00"
    # MVFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[1]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[3]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[5]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[5]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[7]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[7]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    # IFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[1]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[3]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[5]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[5]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[7]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[7]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    # LIFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[1]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[3]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[5]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[7]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    # Remaining VFR conditions
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && [ ${SKY_COVER_ARRAY[1]} -gt ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && [ ${SKY_COVER_ARRAY[3]} -gt ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && [ ${SKY_COVER_ARRAY[5]} -gt ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && [ ${SKY_COVER_ARRAY[7]} -gt ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    else
        SKY_COVER_COLOR="#999999"
    fi 

    echo "<td>${AIRPORT}</td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td style=\"color:${WX_COLOR}; \">${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_F_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}</td><td style=\"color:${VIS_COLOR}; \">${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td style=\"color:${SKY_COVER_COLOR}; \">${SKY_COVERAGE}</td><td>${ELEVATION_FORMATTED}</td>"  >> ${TEMPFILE} ;
    echo "</tr>" >> ${TEMPFILE} ;
    echo >> ${TEMPFILE} ;
done
echo "<td colspan=12><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
echo "</table>" >> ${TEMPFILE}
echo "</body>" >> ${TEMPFILE}
echo "</html>" >> ${TEMPFILE}
mv ${TEMPFILE} ${PRODFILE}

