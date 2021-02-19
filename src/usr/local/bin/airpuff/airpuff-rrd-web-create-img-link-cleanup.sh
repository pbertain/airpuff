#!/bin/sh

cd /var/www/vhosts/airpuff/html/rrdweb/img-link
for FILE in `ls -1 | grep .temp$` ; do
    NAME=`echo ${FILE} | sed -e 's/.temp$//'` ;
    mv -f ${FILE} ${NAME}
done
