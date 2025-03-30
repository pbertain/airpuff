#!/bin/bash

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Created: Wed 29 Feb 2012
# Modified: Fri 05 Feb 2021
# Modified: Fri 25 Aug 2023
# Modified: Sat 11 Nov 2023 <-- Copied over to fli-rite-custom.sh 
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

##### CUSTOMIZE HERE #####
REGION="$1"
AIRPORTS="$2"
##### END CUSTOMIZATION SECTION #####

REGION_LOWER=$(echo -e "${REGION}" | tr '[:upper:]' '[:lower:]')
REGION_LOWER_NOSPACE=$(echo -e "${REGION_LOWER}" | tr -d '[:space:]')
FILEPATH="/var/www/vhosts/airpuff/html"
PRODFILE="${FILEPATH}/${REGION_LOWER_NOSPACE}.html"
TEMPFILE="${PRODFILE}.temp"
W_COAST_TIME=`TZ="America/Los_Angeles" date +"%a %b %e %H:%M %Z"`
E_COAST_TIME=`TZ="America/New_York" date +"%a %b %e %H:%M %Z"`
ZULU_TIMEZONE=`date -u +"%a %b %e %H:%M %Z"`
VFR_MIN=3000
MVFR_MIN=1000
MVFR_MAX=3000
IFR_MIN=500
IFR_MAX=1000
LIFR_MAX=500
GET_SITE_NAME="/usr/local/bin/airpuff/get-icao-site-name.py"
PYTHON3="/usr/bin/python3"

/bin/logger "AirPuff run starting at `date` for ${REGION}."

cat /dev/null > ${TEMPFILE}
echo "<html>" > ${TEMPFILE}
echo "<head>" >> ${TEMPFILE}
echo '    <meta http-equiv="refresh" content="300">' >> ${TEMPFILE}
echo '    <link rel="stylesheet" type="text/css" href="/web/css/airpuff.css">' >> ${TEMPFILE}
echo "    <title>${REGION} AirPuff Airport WX Info</title>" >> ${TEMPFILE}
echo "</head>" >> ${TEMPFILE}
echo '<body bgcolor="#333333" link="#FFA500" alink="#FFA500" vlink="#FFA500">' >> ${TEMPFILE}
echo '<font color="white" face="Tahoma" size=5>' >> ${TEMPFILE}
echo '<table class="table">' >> ${TEMPFILE}
echo '<tr>' >> ${TEMPFILE}
echo '    <td class="td_titles" rowspan="3" colspan="4" vertical-align="center"><a href="https://www.airpuff.info/"><img width="100"  height="81" src="/web/icons/airpuff-logo.png"></a></td>' >> ${TEMPFILE}
echo "    <td class=\"td_titles\" colspan=\"9\" vertical-align=\"center\"><font size=+3 color="white">${REGION} <font size=+2 color=\"#ff0\">AirPuff current run:</td>" >> ${TEMPFILE}
echo '</tr>' >> ${TEMPFILE}
echo '<tr>' >> ${TEMPFILE}
echo "    <td class=\"td_cfb\" colspan=\"9\" vertical-align=\"center\">" >> ${TEMPFILE}
echo "        <font face="Courier" size=3>" >> ${TEMPFILE}
echo "        <font color="cornflowerblue">${ZULU_TIMEZONE}" >> ${TEMPFILE}
echo "        <font color="lightgreen">${W_COAST_TIME}" >> ${TEMPFILE}
echo "        <font color="pink">${E_COAST_TIME}" >> ${TEMPFILE}
echo '    </td>' >> ${TEMPFILE}
echo '</tr>' >> ${TEMPFILE}
echo '</table>' >> ${TEMPFILE}

echo '<font color="white" face="Courier" size=3>' >> ${TEMPFILE}
echo '<table style="color: #FFFFFF; border: 1; border-spacing: 3px; bordercolor: black ; text-align: left; ">' >> ${TEMPFILE}
echo '<tr style="color:yellow; border=1; text-align:center">' >> ${TEMPFILE}
echo "<th>ARPT</th><th>TIME</th><th>TYPE</th><th>CAT</th><th>TEMP</th><th>DEW PT</th><th>T-DP</th><th>WIND</th><th>VIS</th><th>ALT</th><th>SKY COVER</th><th>ELEV</th><th>SITE NAME</th>" >> ${TEMPFILE}
echo '</tr>' >> ${TEMPFILE}
echo '<tr>' >> ${TEMPFILE}

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr '[:upper:]' '[:lower:]')
    SITE_NAME=`${PYTHON3} ${GET_SITE_NAME} ${AIRPORT_LOWER}`
    ELEVATION_M=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $44 }'`
    ELEVATION_FT=`echo "${ELEVATION_M} * 100 / 2.54 / 12" | bc -l` ;
    ELEVATION_FORMATTED=`printf "%0004.0f" "${ELEVATION_FT}" ` ;
    OBS_TIME=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $3 }' | awk -FT '{ print $2 }' | awk -F: '{ print $1":"$2 }'`
    if [ -z ${OBS_TIME} ]; then
       echo "<td style=\"color:#999999; \">${AIRPORT}</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>${ELEVATION_FORMATTED}</td><td>${SITE_NAME}</td><tr>"  >> ${TEMPFILE} ;
       continue
    fi
    FLIGHT_CATEGORY=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $31 }'`
    #RAW_TEXT=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $1 }'`
    TEMP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $6 }'`
    TEMP_C_FORMATTED=`printf "%000.1fF" "${TEMP_C}"` ;
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $7 }'`
    DP_C_FORMATTED=`printf "%.1fF" "${DP_C}" ` ;
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD_C=`echo "${TEMP_C} - ${DP_C}" | bc -l` ;
    T_DP_SPREAD_C_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_C}" ` ;
    T_DP_SPREAD_F=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_F_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_F}" ` ;
    WIND_DIR=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $8 }'`
    WIND_DIR_FORMATTED=`printf "%003s" "${WIND_DIR}"` ;
    WIND_SPEED=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $9 }'`
    WIND_GUST=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $10 }'`
    VIS=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $11 }' | sed -e 's/+//g'`
    ALTIMETER=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $12 }'`
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    METAR_TYPE=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $43 }'`
    SKY_COVERAGE=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $23,$24,$25,$26,$27,$28,$29,$30 }'`

    case "${FLIGHT_CATEGORY}" in
        VFR)
            WX_COLOR="#00FF00"
            ;;
        MVFR)
            WX_COLOR="#5555FF"
            ;;
        IFR)
            WX_COLOR="#FF5555"
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
            VIS_COLOR="#FF5555"
    elif [ ${VIS_INTEGER} -lt 1 ]; then
            VIS_COLOR="#FF00FF"
    elif [ ${VIS_INTEGER} -ge 3 ] && [ "${VIS_INTEGER}" -le 5 ]; then
            VIS_COLOR="#5555FF"
    elif [ ${VIS_INTEGER} -gt 5 ]; then
            VIS_COLOR="#00FF00"
    else
            VIS_COLOR="333333"
    fi

    SKY_COVERAGE=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $23,$24,$25,$26,$27,$28,$29,$30 }'`
    SKY_COVER_ARRAY=(${SKY_COVER// / })
    SKY_COVER_ARRAY_LEN=${#SKY_COVER_ARRAY[@]}
    # VFR
    if [ ${SKY_COVER_ARRAY_LEN} -eq 1 ] && ([ ${SKY_COVER_ARRAY[0]} == "SKC" ] || [ ${SKY_COVER_ARRAY[0]} == "CLR" ]); then
        SKY_COVER_COLOR="#00FF00"
    # MVFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[7]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[7]} -lt ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#5555FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[5]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[5]} -lt ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#5555FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[3]} -lt ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#5555FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${MVFR_MIN} ] && [ ${SKY_COVER_ARRAY[1]} -lt ${MVFR_MAX} ]); then
        SKY_COVER_COLOR="#5555FF"
    # IFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[7]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[7]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF5555"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[5]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[5]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF5555"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[3]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[3]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF5555"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && ([ ${SKY_COVER_ARRAY[1]} -ge ${IFR_MIN} ] && [ ${SKY_COVER_ARRAY[1]} -lt ${IFR_MAX} ]); then
        SKY_COVER_COLOR="#FF5555"
    # LIFR
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && ([ ${SKY_COVER_ARRAY[6]} == "BKN" ] || [ ${SKY_COVER_ARRAY[6]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[7]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && ([ ${SKY_COVER_ARRAY[4]} == "BKN" ] || [ ${SKY_COVER_ARRAY[4]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[5]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && ([ ${SKY_COVER_ARRAY[2]} == "BKN" ] || [ ${SKY_COVER_ARRAY[2]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[3]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && ([ ${SKY_COVER_ARRAY[0]} == "BKN" ] || [ ${SKY_COVER_ARRAY[0]} == "OVC" ]) && [ ${SKY_COVER_ARRAY[1]} -lt ${LIFR_MAX} ]; then
        SKY_COVER_COLOR="#FF00FF"
    # Remaining VFR conditions
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 8 ] && [ ${SKY_COVER_ARRAY[7]} -ge ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 6 ] && [ ${SKY_COVER_ARRAY[5]} -ge ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 4 ] && [ ${SKY_COVER_ARRAY[3]} -ge ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    elif [ ${SKY_COVER_ARRAY_LEN} -eq 2 ] && [ ${SKY_COVER_ARRAY[1]} -ge ${VFR_MIN} ]; then
        SKY_COVER_COLOR="#00FF00"
    else
        SKY_COVER_COLOR="#999999"
    fi

    echo "<tr>" >> ${TEMPFILE} ;
    # Check if WIND_GUST is not empty and greater than 0
    if [[ ! -z "$WIND_GUST" ]] && (( $WIND_GUST > 0 )); then
        echo "<td><a href=\"https://www.airpuff.info/rrdweb/${AIRPORT_LOWER}-rrd.html\">${AIRPORT}</a></td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td style=\"color:${WX_COLOR}; \">${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_F_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}G${WIND_GUST}</td><td style=\"color:${VIS_COLOR}; \">${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td style=\"color:${SKY_COVER_COLOR}; \">${SKY_COVERAGE}</td><td>${ELEVATION_FORMATTED}</td><td>${SITE_NAME}</td>"  >> ${TEMPFILE} ;
    else
	echo "<td><a href=\"https://www.airpuff.info/rrdweb/${AIRPORT_LOWER}-rrd.html\">${AIRPORT}</a></td><td>${OBS_TIME}</td><td>${METAR_TYPE}</td><td style=\"color:${WX_COLOR}; \">${FLIGHT_CATEGORY}</td><td>${TEMP_F_FORMATTED}</td><td>${DP_F_FORMATTED}</td><td>${T_DP_SPREAD_F_FORMATTED}</td><td>${WIND_DIR_FORMATTED}@${WIND_SPEED}</td><td style=\"color:${VIS_COLOR}; \">${VIS}</td><td>${ALTIMETER_FORMATTED}</td><td style=\"color:${SKY_COVER_COLOR}; \">${SKY_COVERAGE}</td><td>${ELEVATION_FORMATTED}</td><td>${SITE_NAME}</td>"  >> ${TEMPFILE} ;
    fi
    echo "</tr>" >> ${TEMPFILE} ;
    echo >> ${TEMPFILE} ;
done
echo "<td colspan=12><font color=\"#444444\"><center>${HOSTNAME}</center></font>" >> ${TEMPFILE}
echo "</table>" >> ${TEMPFILE}
echo "</body>" >> ${TEMPFILE}
echo "</html>" >> ${TEMPFILE}
mv ${TEMPFILE} ${PRODFILE}

/bin/logger "AirPuff run complete at `date` for ${REGION}."

