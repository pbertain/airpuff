#!/bin/sh

cd /var/www/html/htdocs/airpuff.info/html/rrdweb
for FILE in `ls -1 | grep temp` ; do
    NAME=`echo ${FILE} | sed -e 's/.temp//'` ;
    mv -f ${FILE} ${NAME}
done
