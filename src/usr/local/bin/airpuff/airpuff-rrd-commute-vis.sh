#!/bin/bash

AIRPUFF_TM="AirPuff® 2023 ~ `date '+%a %d %b %y - %H:%M'`"

/bin/rrdtool graph \
        /var/www/vhosts/airpuff/gencon/airpuff-v1/html/images/rrd/commute-visi-day.png \
	-s -24h -e now --step 500 \
	-t "Commute Visibility" \
	-w 500 -h 309 \
	--lower-limit "0.0" --upper-limit "11.0" -r \
	--color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC \
	-Y -a PNG \
        -W "${AIRPUFF_TM}" \
	DEF:kdwa-visi=/var/airpuff/rrd-data/kdwa-visibility.rrd:visibility:AVERAGE \
	LINE2:kdwa-visi#FF0000:"KDWA" \
	GPRINT:kdwa-visi:LAST:" cur\:%3.1lf\n" \
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
	-s -24h -e now --step 500 \
	-t "Commute Ceiling" \
	-w 500 -h 309 \
	--lower-limit "0" --upper-limit "20000" -r \
	--color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC \
	-Y -a PNG \
        -W "${AIRPUFF_TM}" \
	DEF:kdwa-ceil=/var/airpuff/rrd-data/kdwa-ceiling.rrd:ceiling:AVERAGE \
	LINE2:kdwa-ceil#FF0000:"KDWA" \
	GPRINT:kdwa-ceil:LAST:" cur\:%3.1lf\n" \
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
