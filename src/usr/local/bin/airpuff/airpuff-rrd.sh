#!/bin/bash

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Wed 29 Feb 2012
# $Id: airpuff.sh 720 2012-09-23 16:42:44Z pbertain $
# $HeadURL: svn+ssh://pbertain@pan.lipadesogesk.name/opt/svn/pbertain/pacman/airpuff/bin/data/pacman/airpuff/bin/airpuff.sh $

# Notes: This is the first pass as a shell script.  Next will be a perl script and then hopefully a python script.

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

CURRDATE="/bin/date +%s"
RRDPATH="/var/airpuff/rrd-data"
AIRPORTS_LOWER=$(echo -e "${AIRPORTS}" | tr '[:upper:]' '[:lower:]')

for AIRPORT in ${AIRPORTS_LOWER} ; do
    TEMP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $6 }'`
    TEMP_F=`echo "9 * ${TEMP_C} / 5 + 32" | bc -l` ;
    TEMP_F_FORMATTED=`printf "%000.1fF" "${TEMP_F}"` ;
    DP_C=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $7 }'`
    DP_F=`echo "9 * ${DP_C} / 5 + 32" | bc -l` ;
    DP_C_FORMATTED=`printf "%.1fF" "${DP_C}" ` ;
    DP_F_FORMATTED=`printf "%.1fF" "${DP_F}" ` ;
    T_DP_SPREAD_C=`echo "${TEMP_C} - ${DP_C}" | bc -l` ;
    T_DP_SPREAD_F=`echo "${TEMP_F} - ${DP_F}" | bc -l` ;
    T_DP_SPREAD_C_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_C}" ` ;
    T_DP_SPREAD_F_FORMATTED=`printf "%02.0f" "${T_DP_SPREAD_F}" ` ;
    WIND_DIR=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $8 }'`
    WIND_DIR_FORMATTED=`printf "%003d" "${WIND_DIR}"` ;
    WIND_SPEED=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $9 }'`
    WIND_GUST=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $10 }'`
    VIS=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $11 }' | sed -e 's/+//g'`
    ALTIMETER=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $12 }'`
    ALTIMETER_FORMATTED=`printf "%.2f" "${ALTIMETER}" ` ;
    SKY_COVER=`grep -i ${AIRPORT} /var/fli-rite/data/metars_current.csv | awk -F, '{ print $23,$24,$25,$26,$27,$28,$29,$30 }'`
    SKY_COVER_ARRAY=(${SKY_COVER// / })
    SKY_COVER_ARRAY_LEN=${#SKY_COVER_ARRAY[@]}
    if [ ${SKY_COVER_ARRAY_LEN} -eq 1 ] ; then
        CEILING=12000
    else
        CEILING=${SKY_COVER_ARRAY[1]}
    fi

    rrdupdate ${RRDPATH}/${AIRPORT}-temp.rrd -t temp_c:temp_f:dew_pt_c:dew_pt_f:t_dp_spread_c:t_dp_spread_f N:${TEMP_C}:${TEMP_F}:${DP_C}:${DP_F}:${T_DP_SPREAD_C}:${T_DP_SPREAD_F}
    rrdupdate ${RRDPATH}/${AIRPORT}-altimeter.rrd -t altimeter N:${ALTIMETER_FORMATTED}
    # Check if WIND_GUST is not empty and greater than 0
    if [[ ! -z "$WIND_GUST" ]] && (( $WIND_GUST > 0 )); then
	#echo "WITH Gust: ${AIRPORT} -> ${WIND_SPEED} G ${WIND_GUST}"
        rrdupdate ${RRDPATH}/${AIRPORT}-wind.rrd -t wind_dir:wind_speed:wind_gust N:${WIND_DIR}:${WIND_SPEED}:${WIND_GUST}
    else
	#echo "WITHOUT Gust: ${AIRPORT} -> ${WIND_SPEED} G ${WIND_GUST}"
	WIND_GUST=${WIND_SPEED}
        rrdupdate ${RRDPATH}/${AIRPORT}-wind.rrd -t wind_dir:wind_speed:wind_gust N:${WIND_DIR}:${WIND_SPEED}:${WIND_GUST}
    fi
    rrdupdate ${RRDPATH}/${AIRPORT}-visibility.rrd -t visibility N:${VIS}
    rrdupdate ${RRDPATH}/${AIRPORT}-ceiling.rrd -t ceiling N:${CEILING}
done
