#!/bin/bash

# pypuff-kdwa-run.sh
# Invokes the Python version of AirPuff to generate a web page for KDWA in Woodland, CA
# Paul Bertain paul@bertain.net
# Tue 08 Jan 2019

##### CUSTOMIZE HERE #####
REGION="$1"
AIRPORTS="$2"
##### END CUSTOMIZATION SECTION #####

/bin/logger "PyPuff run starting at `date` for ${REGION}."

REGION_LOWER=$(echo -e "${REGION}" | tr '[:upper:]' '[:lower:]')
REGION_LOWER_NOSPACE=$(echo -e ${REGION_LOWER} | tr -d '[:space:]')

FILEPATH="/var/www/vhosts/airpuff/html/pypuff"
PRODFILE="${FILEPATH}/${REGION_LOWER_NOSPACE}.html"
PYPUFF="/usr/local/bin/airpuff/pypuff-kdwa.py"
PYTHON="/bin/python3"
TEMPFILE="${PRODFILE}.temp"

cat /dev/null > ${TEMPFILE}

${PYTHON} ${PYPUFF} "${REGION}" ${AIRPORTS} > ${TEMPFILE}

mv ${TEMPFILE} ${PRODFILE}

/bin/logger "PyPuff run complete at `date` for ${REGION}."

