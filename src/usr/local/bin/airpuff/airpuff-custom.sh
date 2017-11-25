#!/bin/sh

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $Id: airpuff.sh 720 2012-09-23 16:42:44Z pbertain $
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

# Notes: This is the first pass as a shell script.  Next will be hopefully a python script.

##### CUSTOMIZE HERE #####
REGION="$1"
AIRPORTS="$2"
##### END CUSTOMIZATION SECTION #####

REGION_LOWER=$(echo -e "${REGION}" | tr '[:upper:]' '[:lower:]')
REGION_LOWER_NOSPACE=$(echo -e "${REGION_LOWER}" | tr -d '[:space:]')
FILEPATH="/var/www/html/htdocs/airpuff/html"
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
    OBS_TIME=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep observation_time | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | awk -FT '{ print $2 }'` ;
    if [ -z ${OBS_TIME} ]; then
       echo "<td style=\"color:#999999; \">${AIRPORT}</td></tr>"  >> ${TEMPFILE} ;
       continue
    fi
    FLIGHT_CATEGORY=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep flight_category | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    #RAW_TEXT=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep raw_text | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }' | sed -e 's/AUTO//' -e 's/RMK.*//'` ;
    TEMP_C=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep temp_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    TEMP_C_FORMATTED=`printf "%000.1fF" "${TEMP_C}"` ;
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep dewpoint_c | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    DP_C_FORMATTED=`printf "%.1fF" "${DP_C}" ` ;
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD_C=`echo "${TEMP_C} - ${DP_C}" | bc -l` ;
    T_DP_SPREAD_C_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_C}" ` ;
    T_DP_SPREAD_F=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_F_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_F}" ` ;
    WIND_DIR=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_dir_degrees | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    WIND_DIR_FORMATTED=`printf "%003d" "${WIND_DIR}"` ;
    WIND_SPEED=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep wind_speed_kt | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    VIS=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep visibility_statute_mi | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep altim_in_hg | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    METAR_TYPE=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep metar_type | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    SKY_COVERAGE=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    ELEVATION_M=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep elevation_m | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    ELEVATION_FT=`echo "${ELEVATION_M} * 100 / 2.54 / 12" | bc -l` ;
    ELEVATION_FORMATTED=`printf "%0004.0f" "${ELEVATION_FT}" ` ;

    #echo "Starting ${AIRPORT}: FC=${FLIGHT_CATEGORY}...";
    #if [ !-z ${FLIGHT_CATEGORY} ]; then
    #   continue
    #fi
    #if [ ${AIRPORT} == 'KSJC' ]; then
    #    echo "${RAW_TEXT}"
    #fi

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

    #VIS_INTEGER=`echo "${VIS}" | bc`
    #VIS_INTEGER=`echo "${VIS%%.*}"`
    VIS_INTEGER=${VIS/.*}
    # or maybe
    #VIS_INTEGER=${VIS/\.*}
    #echo "VIS = ${VIS} - VIS_INTEGER = ${VIS_INTEGER}"

#if [ -z "$MYSQL_ROOT_PASSWORD" -a -z "$MYSQL_ALLOW_EMPTY_PASSWORD" -a -z "$MYSQL_RANDOM_ROOT_PASSWORD" ]; then
    #...
#fi
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

    #sky_cover="BKN" cloud_base_ft_agl="600" />
    #SKY_COVER_ARRAY=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    #SKY_COVER_ARRAY_LEN=${#SKY_COVER_ARRAY[@]}
    #echo "## - ${SKY_COVER_ARRAY}"
    #echo ${SKY_COVER_ARRAY_LEN}
    #if [ ${SKY_COVER_ARRAY_LEN} -eq 1 ]; then
        #echo "${AIRPORT} - FONT = GREEN"
    #elif [ ${SKY_COVER_ARRAY_LEN} -gt 1 ]; then
        #if [[ "${SKY_COVER_ARRAY[0]}" == 'BKN' || "${SKY_COVER_ARRAY[0]}" == 'OVC' ]] && [[ "${SKY_COVER_ARRAY[1]}" < 3000 || "${SKY_COVER_ARRAY[1]}" -ge 1000 ]]; then
            #echo "${AIRPORT} - FONT = BLUE"
        #fi
    #else
        #echo "${AIRPORT} - FONT = RED / MAGENTA"
    #fi
    #for (( i=0; i<${SKY_COVER_ARRAY_LEN}; i++ ));
    #do
        #echo ${SKY_COVER_ARRAY[$i]}
    #done

    #echo "SKY COVER = ${SKY_COVERAGE} - SKY COVER ARRAY = ${SKY_COVER_ARRAY[0]} & ${SKY_COVER_ARRAY[1]}"
    #if [[ "${SKY_COVER_ARRAY[0]}" == 'BKN' || "${SKY_COVER_ARRAY[0]}" == 'OVC' ]] && [[ "${SKY_COVER_ARRAY[1]}" < 1000 || "${SKY_COVER_ARRAY[1]}" > 500 ]]; then
        #SKY_COVER_COLOR="#FF0000"
    #elif [[ "${SKY_COVER_ARRAY[0]}" == 'BKN' || "${SKY_COVER_ARRAY[0]}" == 'OVC' ]] && [[ "${SKY_COVER_ARRAY[1]}" -le 500 ]]; then
        #SKY_COVER_COLOR="#FF00FF"
    #elif [[ "${SKY_COVER_ARRAY[0]}" == 'BKN' || "${SKY_COVER_ARRAY[0]}" == 'OVC' ]] && [[ "${SKY_COVER_ARRAY[1]}" < 3000 || "${SKY_COVER_ARRAY[1]}" -ge 1000 ]]; then
        #SKY_COVER_COLOR="#3333FF"
    #else
        #SKY_COVER_COLOR="#00FF00"
    #fi
    #SKY_COVER_COLOR="#CCAACC"

    #my_error_flag=1
    #my_error_flag_o=1
    #if [ $my_error_flag -eq 1 ] ||  [ $my_error_flag_o -eq 2 ] || ([ $my_error_flag -eq 1 ] && [ $my_error_flag_o -eq 2 ]); then
      #echo "$my_error_flag"
    #else
        #echo "no flag"
    #fi
    #Although in your case you can discard the last two expressions and just stick with one or operation like this:
    #my_error_flag=1
    #my_error_flag_o=1
    #if [ $my_error_flag -eq 1 ] ||  [ $my_error_flag_o -eq 2 ]; then
        #echo "$my_error_flag"
    #else
        #echo "no flag"
    #fi

    SKY_COVER=`curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}" | grep sky_cover | awk -F\" '{ print $2,$4 }'` ;
    SKY_COVER_ARRAY=(${SKY_COVER// / })
    SKY_COVER_ARRAY_LEN=${#SKY_COVER_ARRAY[@]}
    # VFR
    if [ ${SKY_COVER_ARRAY_LEN} -eq 1 ]; then
        SKY_COVER_COLOR="#00FF00"
    # MVFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${MVFR_MIN} ] || [ ${SKY_COVER_ARRAY[1]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -gt 2 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${MVFR_MIN} ] || [ ${SKY_COVER_ARRAY[3]} -le ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#3333FF"
    # IFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${IFR_MIN} ] || [ ${SKY_COVER_ARRAY[1]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    elif [ ${SKY_COVER_ARRAY_LEN} -gt 2 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${IFR_MIN} ] || [ ${SKY_COVER_ARRAY[3]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF0000"
    # LIFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[1]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -gt 2 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[3]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    else
        SKY_COVER_COLOR="#999999"
    fi 
    #echo "## ${AIRPORT}"
    #echo "# Just print the array like a variable: ${SKY_COVER_ARRAY}"
    #echo "# Properly print the array: ${SKY_COVER_ARRAY[@]}"
    #echo "# Array length: ${SKY_COVER_ARRAY_LEN}"
    #echo "# Array [1]: ${SKY_COVER_ARRAY[1]}"

    echo "<td>${AIRPORT}</td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td style=\"color:${WX_COLOR}; \">${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_F_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}</td><td style=\"color:${VIS_COLOR}; \">${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td style=\"color:${SKY_COVER_COLOR}; \">${SKY_COVERAGE}</td><td>${ELEVATION_FORMATTED}</td>"  >> ${TEMPFILE} ;
    echo "</tr>" >> ${TEMPFILE} ;
    echo >> ${TEMPFILE} ;
done
echo "<td colspan=12><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
echo "</table>" >> ${TEMPFILE}
echo "</body>" >> ${TEMPFILE}
echo "</html>" >> ${TEMPFILE}
mv ${TEMPFILE} ${PRODFILE}

