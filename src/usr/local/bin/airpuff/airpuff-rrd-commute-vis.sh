#!/bin/sh

/bin/rrdtool graph \
	/var/www/html/htdocs/airpuff/html/images/rrd/commute-visi-day.png \
	-s -24h -e now --step 500 \
	-t "Commute Visibility" \
	-w 500 -h 309 \
	--lower-limit "0.0" --upper-limit "11.0" -r \
	--color CANVAS#111111 --color BACK#333333 --color FONT#CCCCCC \
	-Y -a PNG -W "AirPuff® 2017" \
	DEF:kedu-visi=/var/airpuff/rrd-data/kedu-visibility.rrd:visibility:AVERAGE \
	LINE2:kedu-visi#FF0000:"KEDU" \
	GPRINT:kedu-visi:LAST:" cur\:%3.1lf\n" \
	DEF:kccr-visi=/var/airpuff/rrd-data/kccr-visibility.rrd:visibility:AVERAGE \
	LINE2:kccr-visi#00FF00:"KCCR" \
	GPRINT:kccr-visi:LAST:" cur\:%3.1lf\n" \
	DEF:klvk-visi=/var/airpuff/rrd-data/klvk-visibility.rrd:visibility:AVERAGE \
	LINE2:klvk-visi#0000FF:"KLVK" \
	GPRINT:klvk-visi:LAST:" cur\:%3.1lf\n" \
	DEF:knuq-visi=/var/airpuff/rrd-data/knuq-visibility.rrd:visibility:AVERAGE \
	LINE2:knuq-visi#FFFF00:"KNUQ" \
	GPRINT:knuq-visi:LAST:" cur\:%3.1lf\n" \
	DEF:kpao-visi=/var/airpuff/rrd-data/kpao-visibility.rrd:visibility:AVERAGE \
	LINE2:kpao-visi#00FFFF:"KPAO" \
	GPRINT:kpao-visi:LAST:" cur\:%3.1lf\n"
