#!/bin/bash

AIRPUFF_TM="AirPuff® 2023 ~ `date '+%a %d %b %y - %H:%M'`"

/bin/rrdtool graph \
        /var/www/vhosts/airpuff/gencon/airpuff-v1/html/images/rrd/commute-visi-day.png \
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
        --upper-limit "11.0" \
        --vertical-label 'Visibility' \
        --x-grid MINUTE:30:HOUR:1:HOUR:2:0:%R \
        --y-grid 0.5:2 \
        --color CANVAS#111111 \
        --color BACK#333333 \
        --color FONT#CCCCCC \
	DEF:klhm-visi=/var/airpuff/rrd-data/klhm-visibility.rrd:visibility:AVERAGE \
	LINE2:klhm-visi#FF0000:"KLHM" \
	GPRINT:klhm-visi:LAST:" cur\:%3.1lf\n" \
	DEF:kedu-visi=/var/airpuff/rrd-data/kedu-visibility.rrd:visibility:AVERAGE \
	LINE2:kedu-visi#9933FF:"KEDU" \
	GPRINT:kedu-visi:LAST:" cur\:%3.1lf\n" \
	DEF:kccr-visi=/var/airpuff/rrd-data/kccr-visibility.rrd:visibility:AVERAGE \
	LINE2:kccr-visi#00FF00:"KCCR" \
	GPRINT:kccr-visi:LAST:" cur\:%3.1lf\n" \
	DEF:klvk-visi=/var/airpuff/rrd-data/klvk-visibility.rrd:visibility:AVERAGE \
	LINE2:klvk-visi#0000FF:"KLVK" \
	GPRINT:klvk-visi:LAST:" cur\:%3.1lf\n" \
	DEF:khwd-visi=/var/airpuff/rrd-data/khwd-visibility.rrd:visibility:AVERAGE \
	LINE2:khwd-visi#FFFF00:"KHWD" \
	GPRINT:khwd-visi:LAST:" cur\:%3.1lf\n" \
	DEF:kpao-visi=/var/airpuff/rrd-data/kpao-visibility.rrd:visibility:AVERAGE \
	LINE2:kpao-visi#00FFFF:"KPAO" \
	GPRINT:kpao-visi:LAST:" cur\:%3.1lf\n"

/bin/rrdtool graph \
        /var/www/vhosts/airpuff/gencon/airpuff-v1/html/images/rrd/commute-ceil-day.png \
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
	DEF:klhm-ceil=/var/airpuff/rrd-data/klhm-ceiling.rrd:ceiling:AVERAGE \
	LINE2:klhm-ceil#FF0000:"KLHM" \
	GPRINT:klhm-ceil:LAST:" cur\:%3.1lf\n" \
	DEF:kedu-ceil=/var/airpuff/rrd-data/kedu-ceiling.rrd:ceiling:AVERAGE \
	LINE2:kedu-ceil#9933FF:"KEDU" \
	GPRINT:kedu-ceil:LAST:" cur\:%3.1lf\n" \
	DEF:kccr-ceil=/var/airpuff/rrd-data/kccr-ceiling.rrd:ceiling:AVERAGE \
	LINE2:kccr-ceil#00FF00:"KCCR" \
	GPRINT:kccr-ceil:LAST:" cur\:%3.1lf\n" \
	DEF:klvk-ceil=/var/airpuff/rrd-data/klvk-ceiling.rrd:ceiling:AVERAGE \
	LINE2:klvk-ceil#0000FF:"KLVK" \
	GPRINT:klvk-ceil:LAST:" cur\:%3.1lf\n" \
	DEF:khwd-ceil=/var/airpuff/rrd-data/khwd-ceiling.rrd:ceiling:AVERAGE \
	LINE2:khwd-ceil#FFFF00:"KHWD" \
	GPRINT:khwd-ceil:LAST:" cur\:%3.1lf\n" \
	DEF:kpao-ceil=/var/airpuff/rrd-data/kpao-ceiling.rrd:ceiling:AVERAGE \
	LINE2:kpao-ceil#00FFFF:"KPAO" \
	GPRINT:kpao-ceil:LAST:" cur\:%3.1lf\n"
