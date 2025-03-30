    $RRDBINPATH/rrdtool graph ${RRDIMGPATH}/${AIRPORT_LOWER}-winddir-day.png \
        -s -24h -e now --step 500 --slope-mode \
        -t "${AIRPORT} Wind Dir" \
        -w 500 -h 309 \
        -Y -a PNG \
        -W "${AIRPUFF_TM}" \
        --upper-limit "370" \
        -r \
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
        -W "${AIRPUFF_TM}" \
        --upper-limit "40" \
        -r \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
        DEF:windspd=${RRDPATH}/${AIRPORT_LOWER}-wind.rrd:wind_speed:AVERAGE \
        CDEF:scaled_windspd=windspd,10,* \
        LINE5:scaled_windspd#00FF00:"Wind Speed" \
        GPRINT:windspd:LAST:" Current\:%3.1lf\n" ;

