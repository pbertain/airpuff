#!/bin/sh

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Tue 31 Oct 2018

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

AIRPORT_LOWER_NOSPACE=$(echo -e "${AIRPORT_LOWER}" | tr -d '[:space:]')
FILEPATH="/var/www/html/htdocs/airpuff.info/html"
PRODFILE="${FILEPATH}/${REGION_LOWER_NOSPACE}.html"
RRDPATH="/var/airpuff/rrd-data"
RRDBINPATH="/opt/rrdtool/bin/"
RRDIMGPATH="/var/www/html/htdocs/airpuff.info/html/images/rrd/"
TEMPFILE="${PRODFILE}.temp"

W_COAST_TIME=`TZ='America/Los_Angeles' date +'%a %F %T %Z'`
E_COAST_TIME=`TZ='America/New_York' date +'%T %Z'`
ZULU_TIMEZONE=`date -u +'%a %F %T %Z/Zulu/Z'`
AP_TIMESTAMP=`date '+%a %d %b %y - %H:%M'`

for AIRPORT in ${AIRPORTS} ; do
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr '[:upper:]' '[:lower:]')

  ## Days
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Altimeter" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018 ~ `date '+%a %d %b %y - %H:%M'`" \
        --upper-limit 31.00 -l 28.00 -r \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        --left-axis-format %2.2lf \
        --right-axis 1:0 \
        --right-axis-format %2.2lf \
        --x-grid MINUTE:30:HOUR:1:MINUTE:120:0:%R \
        DEF:alti_avg=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
        LINE5:alti_avg#00FF00:"Alti - Avg" \
        GPRINT:alti_avg:LAST:"Current\:%8.2lf %s\n";

    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Wind" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "360" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:"%8.1lf\n" \
        LINE5:winddir#0000FF:"Wind Dir" \
        GPRINT:winddir:LAST:"%10.1lf\n" ;

    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-winddir-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Wind Dir" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "370" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        LINE5:winddir#0000FF:"Wind Dir" \
        GPRINT:winddir:LAST:" Current\:%3.1lf\n" ;

    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-windspd-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Wind Speed" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "40" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:" Current\:%3.1lf\n" ;

    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-day.png -s -24h -e now --step 500 --slope-mode -t "${AIRPORT} Visibility" -w 500 -h 309 --lower-limit "0.0" --upper-limit "11.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE LINE5:visibility#00FF00:"Visibility" GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-day.png -s -24h -e now --step 500 --slope-mode -t "${AIRPORT} Ceiling" -w 500 -h 309 --lower-limit "0.0" --upper-limit "20000.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE LINE5:ceiling#00FF00:"Ceiling" GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Temp" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "120" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread" \
        GPRINT:t_dp_spread_f:LAST:"% 5.1lf\n" ;

  ## Weeks
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-week.png -s -7d -e now --step 3600 -t "${AIRPORT} Altimeter" -w 500 -h 309 --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -u 31.00 -l 28.00 -r -a PNG -W "AirPuff® 2018" DEF:alti=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE LINE5:alti#00FF00:"Altimeter" GPRINT:alti:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-week.png \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${AIRPORT} Wind" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "370" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:"%8.1lf\n" \
        LINE5:winddir#0000FF:"Wind Dir" \
        GPRINT:winddir:LAST:"%10.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-week.png -s -7d -e now --step 3600 -t "${AIRPORT} Visibility" -w 500 -h 309 --lower-limit "0.0" --upper-limit "11.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE LINE5:visibility#00FF00:"Visibility" GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-week.png -s -7d -e now --step 3600 -t "${AIRPORT} Ceiling" -w 500 -h 309 --lower-limit "0" --upper-limit "20000" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE LINE5:ceiling#00FF00:"Ceiling" GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-week.png \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${AIRPORT} Temp" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "120" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread" \
        GPRINT:t_dp_spread_f:LAST:"% 5.1lf\n" ;

    #Months
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-month.png -s -30d -e now --step 10800 -t "${AIRPORT} Altimeter" -w 500 -h 309 --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -u 31.00 -l 28.00 -r -a PNG -W "AirPuff® 2018" DEF:alti=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE LINE5:alti#00FF00:"Altimeter" GPRINT:alti:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-month.png \
        -s -30d -e now --step 10800 \
        -t "${AIRPORT} Wind" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "370" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:"%8.1lf\n" \
        LINE5:winddir#0000FF:"Wind Dir" \
        GPRINT:winddir:LAST:"%10.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-month.png -s -30d -e now --step 10800 -t "${AIRPORT} Visibility" -w 500 -h 309 --lower-limit "0.0" --upper-limit "11.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE LINE5:visibility#00FF00:"Visibility" GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-month.png -s -30d -e now --step 10800 -t "${AIRPORT} Ceiling" -w 500 -h 309 --lower-limit "0" --upper-limit "20000" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE LINE5:ceiling#00FF00:"Ceiling" GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-month.png \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${AIRPORT} Temp" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "120" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread" \
        GPRINT:t_dp_spread_f:LAST:"% 5.1lf\n" ;

    # Years
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-year.png -s -365d -e now --step 21600 -t "${AIRPORT} Altimeter" -w 500 -h 309 --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -u 31.00 -l 28.00 -r -a PNG -W "AirPuff® 2018" DEF:alti=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE LINE5:alti#00FF00:"Altimeter" GPRINT:alti:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-year.png \
        -s -365d -e now --step 21600 \
        -t "${AIRPORT} Wind" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "360" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:"%8.1lf\n" \
        LINE5:winddir#0000FF:"Wind Dir" \
        GPRINT:winddir:LAST:"%10.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-year.png -s -365d -e now --step 21600 -t "${AIRPORT} Visibility" -w 500 -h 309 --lower-limit "0.0" --upper-limit "11.0" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE LINE5:visibility#00FF00:"Visibility" GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-year.png -s -365d -e now --step 21600 -t "${AIRPORT} Ceiling" -w 500 -h 309 --lower-limit "0" --upper-limit "20000" -r --color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC -Y -a PNG -W "AirPuff® 2018" DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE LINE5:ceiling#00FF00:"Ceiling" GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-year.png \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${AIRPORT} Temp" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "AirPuff® 2018" \
        --upper-limit "120" \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread" \
        GPRINT:t_dp_spread_f:LAST:"% 5.1lf\n" ;

done
