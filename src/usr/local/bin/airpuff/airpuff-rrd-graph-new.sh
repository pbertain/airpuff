#!/bin/sh

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Tue 31 Oct 2017

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORT_LOWER_NOSPACE=$(echo -e "${AIRPORT_LOWER}" | tr -d '[:space:]')
RRDIMGPATH="/var/www/vhosts/airpuff/html/images/rrd/"
RRDPATH="/var/airpuff/rrd-data"
FILEPATH="/var/www/vhosts/airpuff/html"
PRODFILE="${FILEPATH}/${REGION_LOWER_NOSPACE}.html"
TEMPFILE="${PRODFILE}.temp"
W_COAST_TIME=`TZ='America/Los_Angeles' date +'%a %F %T %Z'`
E_COAST_TIME=`TZ='America/New_York' date +'%T %Z'`
ZULU_TIMEZONE=`date -u +'%a %F %T %Z/Zulu/Z'`

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr '[:upper:]' '[:lower:]')
    for METRIC in alti ceil visi wind ; do 
        for TIMERANGE in day week month year ; do
            /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png -s -24h -e now --step 500 -t "${AIRPORT} Altimeter" -w 500 -h 309 --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -u 31.00 -l 28.00 -r -a PNG -W "AirPuff® 2017" DEF:alti=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE LINE5:alti#00FF00:"Altimeter" GPRINT:alti:LAST:" Current\:%3.2lf\n" ;
            /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png -s -24h -e now --step 500 -t "${AIRPORT} Wind" -w 500 -h 309 --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC --right-axis-label 'Wind Dir' --right-axis 0.01:0 --right-axis-format %1.1lf --upper-limit "370" -Y -a PNG -W "AirPuff® 2017" DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE CDEF:scaled_windspd=windspd,100,* LINE5:scaled_windspd#00FF00:"Wind Speed" LINE5:winddir#0000FF:"Wind Dir" GPRINT:scaled_windspd:LAST:" Current\:%3.1lf\n" GPRINT:winddir:LAST:" Current\:%3.1lf\n" ;
            /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png -s -24h -e now --step 500 -t "${AIRPORT} Visibility" -w 500 -h 309 --lower-limit "0.0" --upper-limit "11.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2017" DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE LINE5:visibility#00FF00:"Visibility" GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;
            /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-${METRIC}-${TIMERANGE}.png -s -24h -e now --step 500 -t "${AIRPORT} Ceiling" -w 500 -h 309 --lower-limit "0" --upper-limit "20000" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2017" DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE LINE5:ceiling#00FF00:"Ceiling" GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
        done
    done
done

#GPRINT:scaled_windspd:LAST:" Current\:%3.1lf\\n" GPRINT:winddir:LAST:" Current\:%3.1lf\\n" ;


#GPRINT:Cost:AVERAGE:"$(printf \\" cost %11s\\" £%.2lf | sed 's/\£/\£ /g')\\n" \
#GPRINT:Cost:AVERAGE:"$(printf ' cost %11s' £%.2lf | sed 's/\£/\£ /g')\\n" \  # GOOD

