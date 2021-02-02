    # Altimeter
    /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-alti-day.png \
    --start -24h --end now --step 500 --title "${AIRPORT} Altimeter" --width 500 --height 309 \
    --color CANVAS#111111 \
    --color BACK#333333 \
    --color FONT#CCCCCC \
    --imgformat PNG --watermark "AirPuff® 2017" \
    --lower-limit "28.00" --upper-limit "31.00" --rigid \
    DEF:alti=${RRDPATH}/${AIRPORT_LOWER}-altimeter.rrd:altimeter:AVERAGE \
    LINE5:alti#00FF00:"Altimeter" \
    GPRINT:alti:LAST:" Current\:%3.2lf\n" ;

    # Wind Speed and Direction
    /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-wind-day.png \
    --start -24h --end now --step 500 --title "${AIRPORT} Wind" --width 500 --height 309 \
    --color CANVAS#111111 \
    --color BACK#333333 \
    --color FONT#CCCCCC \
    --imgformat PNG --watermark "AirPuff® 2017" \
    --left-axis-format %2.1lf \
    --right-axis-format %3.0lf --right-axis-label 'Wind Dir' --right-axis-upper-limit "370" \
    DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
    DEF:winddir=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_dir:AVERAGE \
    CDEF:scaled_windspd=windspd,100,* \
    LINE5:scaled_windspd#00FF00:"Wind Speed" \
    LINE2:winddir#0000FF:"Wind Dir" \
    GPRINT:winddir:LAST:" Direction:%3.0lf\n" \
    GPRINT:scaled_windspd:LAST:" Wind Speed:%3.1lf" ;

    # Visibility
    /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-visi-day.png \
    --start -24h --end now --step 500 --title "${AIRPORT} Visibility" --width 500 --height 309 \
    --color CANVAS#111111 \
    --color BACK#333333 \
    --color FONT#CCCCCC \
    --imgformat PNG --watermark "AirPuff® 2017" \
    --lower-limit "0.0" --upper-limit "11.0" --rigid \
    DEF:visibility=${RRDPATH}/${AIRPORT_LOWER}-visibility.rrd:visibility:AVERAGE \
    LINE5:visibility#00FF00:"Visibility" \
    GPRINT:visibility:LAST:" Current\:%3.1lf\n" ;

    # Ceiling
    /bin/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-ceil-day.png \
    --start  -24h --end now --step 500 --title "${AIRPORT} Ceiling" --width 500 --height 309 \
    --lower-limit "0" --upper-limit "15000" --rigid \
    --color CANVAS#111111 \
    --color BACK#333333 \
    --color FONT#CCCCCC \
    --imgformat PNG --watermark "AirPuff® 2017" \
    DEF:ceiling=${RRDPATH}/${AIRPORT_LOWER}-ceiling.rrd:ceiling:AVERAGE \
    LINE5:ceiling#00FF00:"Ceiling" \
    GPRINT:ceiling:LAST:" Current\:%5.0lf\n" ;


