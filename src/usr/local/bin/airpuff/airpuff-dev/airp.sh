#!/bin/sh

##### CUSTOMIZE HERE #####
REGION="$1"
AIRPORTS="$2"
##### END CUSTOMIZATION SECTION #####


for AIRPORT in ${AIRPORTS} ; do
    echo "### Reporting for ${AIRPORT}"
    AIRPUFF=$(curl -s "http://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=3&mostRecent=true&stationString=${AIRPORT}") ;
    #FLIGHT_CATEGORY=`cat $(AIRPUFF) | grep flight_category | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    FLIGHT_CATEGORY=`grep flight_category ${AIRPUFF} | awk -F\> '{ print $2 }' | awk -F\< '{ print $1 }'` ;
    echo "${AIRPORT} - ${FLIGHT_CATEGORY}"
done


