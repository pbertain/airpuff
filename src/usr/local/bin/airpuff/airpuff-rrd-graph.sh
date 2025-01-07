#!/bin/bash

# airpuff.sh
# Looks up wx for airports on the commute and presents it as a webpage
# Paul Bertain paul@bertain.net
# Tue 31 Oct 2018

##### CUSTOMIZE HERE #####
AIRPORTS="$1"
##### END CUSTOMIZATION SECTION #####

##### GLOBAL VARS #####
AIRPUFF_TM="AirPuff® `date '+%Y'` ~ `date '+%a %d %b %y - %H:%M'`"
RRDBINPATH="/usr/bin/"
RRDIMGPATH="/var/www/vhosts/airpuff/html/images/rrd/"
RRDPATH="/var/airpuff/rrd-data"
##### GLOBAL VARS #####

for AIRPORT in ${AIRPORTS} ; do
    GET_SITE_NAME="/usr/local/bin/airpuff/get-icao-site-name.py"
    PYTHON3="/usr/bin/python3"
    AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr "[:upper:]" "[:lower:]")
    AIRPORT_LOWER_NOSPACE=$(echo -e "${AIRPORT_LOWER}" | tr -d "[:space:]")
    SITE_NAME=`${PYTHON3} ${GET_SITE_NAME} ${AIRPORT_LOWER}`

    # Altimeter
    ## Day
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-day.png \
        -r \
        -s -24h -e now --step 500 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Altimeter" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --upper-limit 31.00 -l 28.90 \
        --vertical-label Altimeter \
        --left-axis-format %2.2lf \
        --right-axis-label Altimeter \
        --right-axis 1:0 \
        --right-axis-format %2.2lf \
        --x-grid MINUTE:30:HOUR:1:MINUTE:120:0:%R \
        --y-grid 0.05:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:alti_avg=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
        DEF:alti_min=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MIN \
        DEF:alti_max=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MAX \
        LINE3:alti_avg#00FF00:"Altimeter [avg]" \
        GPRINT:alti_avg:LAST:"Avg \:%8.2lf %s\n" \
        LINE1:alti_min#0000FF:"          [min]" \
        GPRINT:alti_min:MIN:"Min \:%8.2lf %s\n" \
        LINE1:alti_max#FF0000:"          [max]" \
        GPRINT:alti_max:MAX:"Max \:%8.2lf %s\n";

    ## Week
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-week.png \
        -r \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Altimeter" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --upper-limit 31.00 -l 28.90 \
        --vertical-label Altimeter \
        --left-axis-format %2.2lf \
        --right-axis-label Altimeter \
        --right-axis 1:0 \
        --right-axis-format %2.2lf \
        --x-grid HOUR:12:DAY:1:DAY:1:0:"%a %m/%d" \
        --y-grid 0.05:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:alti_avg=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
        DEF:alti_min=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MIN \
        DEF:alti_max=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MAX \
        LINE3:alti_avg#00FF00:"Altimeter [avg]" \
        GPRINT:alti_avg:LAST:"Avg \:%8.2lf %s\n" \
        LINE1:alti_min#0000FF:"          [min]" \
        GPRINT:alti_min:MIN:"Min \:%8.2lf %s\n" \
        LINE1:alti_max#FF0000:"          [max]" \
        GPRINT:alti_max:MAX:"Max \:%8.2lf %s\n";

    ## Month
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-month.png \
        -r \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Altimeter" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --upper-limit 31.00 -l 28.90 \
        --vertical-label Altimeter \
        --left-axis-format %2.2lf \
        --right-axis-label Altimeter \
        --right-axis 1:0 \
        --right-axis-format %2.2lf \
        --x-grid DAY:1:DAY:7:DAY:7:0:"Week %U" \
        --y-grid 0.05:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:alti_avg=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
        DEF:alti_min=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MIN \
        DEF:alti_max=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MAX \
        LINE3:alti_avg#00FF00:"Altimeter [avg]" \
        GPRINT:alti_avg:LAST:"Avg \:%8.2lf %s\n" \
        LINE1:alti_min#0000FF:"          [min]" \
        GPRINT:alti_min:MIN:"Min \:%8.2lf %s\n" \
        LINE1:alti_max#FF0000:"          [max]" \
        GPRINT:alti_max:MAX:"Max \:%8.2lf %s\n";

    ## Year
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-year.png \
        -r \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Altimeter" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --upper-limit 31.00 -l 28.90 \
        --vertical-label Altimeter \
        --left-axis-format %2.2lf \
        --right-axis-label Altimeter \
        --right-axis 1:0 \
        --right-axis-format %2.2lf \
        --x-grid WEEK:1:MONTH:1:MONTH:2:0:"%b %Y" \
        --y-grid 0.05:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:alti_avg=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
        DEF:alti_min=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MIN \
        DEF:alti_max=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:MAX \
        LINE3:alti_avg#00FF00:"Altimeter [avg]" \
        GPRINT:alti_avg:LAST:"Avg \:%8.2lf %s\n" \
        LINE1:alti_min#0000FF:"          [min]" \
        GPRINT:alti_min:MIN:"Min \:%8.2lf %s\n" \
        LINE1:alti_max#FF0000:"          [max]" \
        GPRINT:alti_max:MAX:"Max \:%8.2lf %s\n";

  # Wind Speed and Direction
   ## Days
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-day.png \
        -r \
        -s -24h -e now --step 500 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Wind" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.0lf" \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        --upper-limit "360" -l 0 -r \
        --vertical-label 'Wind Dir' \
        --x-grid MINUTE:30:HOUR:1:HOUR:2:0:%R \
        --y-grid 10:3 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
	DEF:windspd_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:windgust_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_gust:AVERAGE \
        DEF:winddir_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd_avg=windspd_avg,10,* \
        CDEF:scaled_windgust_avg=windgust_avg,10,* \
        LINE5:winddir_avg#0000FF:"Wind Dir   [avg]" \
        GPRINT:winddir_avg:LAST:"Current\:%6.0lf\n" \
        LINE3:scaled_windspd_avg#00FF00:"Wind Speed [avg]" \
        GPRINT:windspd_avg:LAST:"Current\:%8.1lf\n" \
        LINE1:scaled_windgust_avg#FF0000:"Wind Gust  [avg]" \
        GPRINT:windgust_avg:LAST:"Current\:%8.1lf\n" ;

   ## Weeks
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-week.png \
        -r \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Wind" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.0lf" \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        --upper-limit "360" -l 0 -r \
        --vertical-label 'Wind Dir' \
        --x-grid HOUR:12:DAY:1:DAY:1:0:"%a %m/%d" \
        --y-grid 10:3 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:windspd_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:windgust_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_gust:AVERAGE \
        DEF:winddir_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd_avg=windspd_avg,10,* \
        CDEF:scaled_windgust_avg=windgust_avg,10,* \
        LINE5:winddir_avg#0000FF:"Wind Dir   [avg]" \
        GPRINT:winddir_avg:LAST:"Current\:%6.0lf\n" \
        LINE3:scaled_windspd_avg#00FF00:"Wind Speed [avg]" \
        GPRINT:windspd_avg:LAST:"Current\:%8.1lf\n" \
        LINE1:scaled_windgust_avg#FF0000:"Wind Gust  [avg]" \
        GPRINT:windgust_avg:LAST:"Current\:%8.1lf\n" ;
	
   ## Months
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-month.png \
        -r \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Wind" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.0lf" \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        --upper-limit "360" -l 0 -r \
        --vertical-label 'Wind Dir' \
        --x-grid DAY:1:DAY:7:DAY:7:0:"Week %U" \
        --y-grid 10:3 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:windspd_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:windgust_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_gust:AVERAGE \
        DEF:winddir_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd_avg=windspd_avg,10,* \
        CDEF:scaled_windgust_avg=windgust_avg,10,* \
        LINE5:winddir_avg#0000FF:"Wind Dir   [avg]" \
        GPRINT:winddir_avg:LAST:"Current\:%6.0lf\n" \
        LINE3:scaled_windspd_avg#00FF00:"Wind Speed [avg]" \
        GPRINT:windspd_avg:LAST:"Current\:%8.1lf\n" \
        LINE1:scaled_windgust_avg#FF0000:"Wind Gust  [avg]" \
        GPRINT:windgust_avg:LAST:"Current\:%8.1lf\n" ;
	
   ## Years
    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-year.png \
        -r \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Wind" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.0lf" \
        --right-axis-label 'Wind Speed' \
        --right-axis 0.1:0 \
        --right-axis-format %1.1lf \
        --upper-limit "360" -l 0 -r \
        --vertical-label 'Wind Dir' \
        --x-grid WEEK:1:MONTH:1:MONTH:2:0:"%b %Y" \
        --y-grid 10:3 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:windspd_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        DEF:windgust_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_gust:AVERAGE \
        DEF:winddir_avg=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
        CDEF:scaled_windspd_avg=windspd_avg,10,* \
        CDEF:scaled_windgust_avg=windgust_avg,10,* \
        LINE5:winddir_avg#0000FF:"Wind Dir   [avg]" \
        GPRINT:winddir_avg:LAST:"Current\:%6.0lf\n" \
        LINE3:scaled_windspd_avg#00FF00:"Wind Speed [avg]" \
        GPRINT:windspd_avg:LAST:"Current\:%8.1lf\n" \
        LINE1:scaled_windgust_avg#FF0000:"Wind Gust  [avg]" \
        GPRINT:windgust_avg:LAST:"Current\:%8.1lf\n" ;
	
  # Visibility
   ## Day
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-day.png \
        -r \
        -s -24h -e now --step 500 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Visibility" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0.0" \
        --right-axis-label 'Visibility' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "20.0" \
        --vertical-label 'Visibility' \
        --x-grid MINUTE:30:HOUR:1:HOUR:2:0:%R \
        --y-grid 0.5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE \
        LINE5:visibility#00FF00:"Visibility [avg]" \
        GPRINT:visibility:LAST:"Current\:%8.1lf\n" ;
  
   ## Week
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-week.png \
        -r \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Visibility" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0.0" \
        --right-axis-label 'Visibility' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "20.0" \
        --vertical-label 'Visibility' \
        --x-grid HOUR:12:DAY:1:DAY:1:0:"%a %m/%d" \
        --y-grid 0.5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE \
        LINE5:visibility#00FF00:"Visibility [avg]" \
        GPRINT:visibility:LAST:"Current\:%8.1lf\n" ;
      
   ## Month
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-month.png \
        -r \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Visibility" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0.0" \
        --right-axis-label 'Visibility' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "20.0" \
        --vertical-label 'Visibility' \
        --x-grid DAY:1:DAY:7:DAY:7:0:"Week %U" \
        --y-grid 0.5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE \
        LINE5:visibility#00FF00:"Visibility [avg]" \
        GPRINT:visibility:LAST:"Current\:%8.1lf\n" ;
          
   ## Year
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-year.png \
        -r \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Visibility" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0.0" \
        --right-axis-label 'Visibility' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "20.0" \
        --vertical-label 'Visibility' \
        --x-grid WEEK:1:MONTH:1:MONTH:2:0:"%b %Y" \
        --y-grid 0.5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE \
        LINE5:visibility#00FF00:"Visibility [avg]" \
        GPRINT:visibility:LAST:"Current\:%8.1lf\n" ;

  # Ceiling
   ## Day
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-day.png \
        -r \
        -s -24h -e now --step 500 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Ceiling" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%6.0lf000" \
        --lower-limit "0.0" \
        --right-axis-label 'Ceiling' \
        --right-axis 1:0 \
        --right-axis-format "%0.0lf" \
        --upper-limit "20000.0" \
        --vertical-label 'Ceiling' \
        --x-grid MINUTE:30:HOUR:1:HOUR:2:0:%R \
        --y-grid 500:4 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE \
        LINE5:ceiling#00FF00:"Ceiling [avg]" \
        GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
  
   ## Week
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-week.png \
        -r \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Ceiling" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%6.0lf000" \
        --lower-limit "0.0" \
        --right-axis-label 'Ceiling' \
        --right-axis 1:0 \
        --right-axis-format "%0.0lf" \
        --upper-limit "20000.0" \
        --vertical-label 'Ceiling' \
        --x-grid HOUR:12:DAY:1:DAY:1:0:"%a %m/%d" \
        --y-grid 500:4 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE \
        LINE5:ceiling#00FF00:"Ceiling [avg]" \
        GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
      
   ## Month
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-month.png \
        -r \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Ceiling" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%6.0lf000" \
        --lower-limit "0.0" \
        --right-axis-label 'Ceiling' \
        --right-axis 1:0 \
        --right-axis-format "%0.0lf" \
        --upper-limit "20000.0" \
        --vertical-label 'Ceiling' \
        --x-grid DAY:1:DAY:7:DAY:7:0:"Week %U" \
        --y-grid 500:4 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE \
        LINE5:ceiling#00FF00:"Ceiling [avg]" \
        GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
          
   ## Year
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-year.png \
        -r \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Ceiling" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%6.0lf000" \
        --lower-limit "0.0" \
        --right-axis-label 'Ceiling' \
        --right-axis 1:0 \
        --right-axis-format "%0.0lf" \
        --upper-limit "20000.0" \
        --vertical-label 'Ceiling' \
        --x-grid WEEK:1:MONTH:1:MONTH:2:0:"%b %Y" \
        --y-grid 500:4 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE \
        LINE5:ceiling#00FF00:"Ceiling [avg]" \
        GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;
        
  # Temperature
   ## Days
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-day.png \
        -r \
        -s -24h -e now --step 500 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Temperature" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0" \
        --right-axis-label 'Temperature / Dew Pt / Temp Spread' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "120" \
        --vertical-label 'Temperature / Dew Pt / Temp Spread' \
        --x-grid MINUTE:30:HOUR:1:HOUR:2:0:%R \
        --y-grid 5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F [avg]" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F [avg]" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread [avg]" \
        GPRINT:t_dp_spread_f:LAST:"%5.1lf\n" ;

   ## Weeks
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-week.png \
        -r \
        -s -7d -e now --step 3600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Temperature" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0" \
        --right-axis-label 'Temperature / Dew Pt / Temp Spread' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "120" \
        --vertical-label 'Temperature / Dew Pt / Temp Spread' \
        --x-grid HOUR:12:DAY:1:DAY:1:0:"%a %m/%d" \
        --y-grid 5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F [avg]" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F [avg]" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread [avg]" \
        GPRINT:t_dp_spread_f:LAST:"%5.1lf\n" ;

   ## Months
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-month.png \
        -r \
        -s -30d -e now --step 10800 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Temperature" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0" \
        --right-axis-label 'Temperature / Dew Pt / Temp Spread' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "120" \
        --vertical-label 'Temperature / Dew Pt / Temp Spread' \
        --x-grid DAY:1:DAY:7:DAY:7:0:"Week %U" \
        --y-grid 5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F [avg]" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F [avg]" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread [avg]" \
        GPRINT:t_dp_spread_f:LAST:"%5.1lf\n" ;

   ## Years
    ${RRDBINPATH}/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-temp-year.png \
        -r \
        -s -365d -e now --step 21600 --slope-mode \
        -t "${SITE_NAME} [${AIRPORT}] Temperature" \
        -w 500 -h 309 \
        -W "${AIRPUFF_TM}" \
        -Y -a PNG \
        --left-axis-format "%3.1lf" \
        --lower-limit "0" \
        --right-axis-label 'Temperature / Dew Pt / Temp Spread' \
        --right-axis 1:0 \
        --right-axis-format "%3.1lf" \
        --upper-limit "120" \
        --vertical-label 'Temperature / Dew Pt / Temp Spread' \
        --x-grid WEEK:1:MONTH:1:MONTH:2:0:"%b %Y" \
        --y-grid 5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:temp_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:temp_f:AVERAGE \
        DEF:dew_pt_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:dew_pt_f:AVERAGE \
        DEF:t_dp_spread_f=${RRDPATH}/${AIRPORT_LOWER}-temp.rrd:t_dp_spread_f:AVERAGE \
        LINE5:temp_f#00FF00:"Temp °F [avg]" \
        GPRINT:temp_f:LAST:"%16.1lf\n" \
        LINE5:dew_pt_f#0000FF:"Dew Pt °F [avg]" \
        GPRINT:dew_pt_f:LAST:"%14.1lf\n" \
        LINE3:t_dp_spread_f#FF0000:"Temp-Dew Pt Spread [avg]" \
        GPRINT:t_dp_spread_f:LAST:"%5.1lf\n" ;

done

