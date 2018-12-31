#!/bin/sh

# Which airport is this data for?
AIRPORT=$1
AIRPORT_LOWER=$(echo -e "${AIRPORT}" | tr '[:upper:]' '[:lower:]')

# where to store data. relative to current directory, MUST EXIST
STOREPATH="/var/airpuff/rrd-data"

# at which interval do we feed new data to rrd
STEP="300"

### 1 DAY
# 1*300s = 5 min (avg)
# 5min*288 = 1 day (duration)
DAYAVG="1"
DAYSTEPS="288"

### 7 DAYS (1 week)
# 3*300s = 15 min (avg)
# 15min*672 = 7 days (duration)
WEEKAVG="3"
WEEKSTEPS="672"

### 30 DAYS (~1 month)
# 6*300s = 30 min (avg)
# 30min*1440 = 30 days (duration)
MONAVG="6"
MONSTEPS="1440"

### 3650 DAYS (~10 years)
# 12*300s = 60 min (avg)
# 60min*87600 = 3650 days (duration)
YEARAVG="12"
YEARSTEPS="87600"

rrdcreate $STOREPATH/${AIRPORT_LOWER}-temp.rrd \
  --no-overwrite --start now --step $STEP \
  DS:temp_c:GAUGE:400:-64:64 \
  DS:temp_f:GAUGE:400:-64:150 \
  DS:dew_pt_c:GAUGE:400:-64:64 \
  DS:dew_pt_f:GAUGE:400:-64:150 \
  DS:t_dp_spread_c:GAUGE:400:-4:60 \
  DS:t_dp_spread_f:GAUGE:400:-4:130 \
  RRA:AVERAGE:0.5:$DAYAVG:$DAYSTEPS \
  RRA:AVERAGE:0.5:$WEEKAVG:$WEEKSTEPS \
  RRA:AVERAGE:0.5:$MONAVG:$MONSTEPS \
  RRA:AVERAGE:0.5:$YEARAVG:$YEARSTEPS

rrdcreate $STOREPATH/${AIRPORT_LOWER}-altimeter.rrd \
  --no-overwrite --start now --step $STEP \
  DS:altimeter:GAUGE:600:26:35 \
  RRA:AVERAGE:0.5:$DAYAVG:$DAYSTEPS \
  RRA:AVERAGE:0.5:$WEEKAVG:$WEEKSTEPS \
  RRA:AVERAGE:0.5:$MONAVG:$MONSTEPS \
  RRA:AVERAGE:0.5:$YEARAVG:$YEARSTEPS

rrdcreate $STOREPATH/${AIRPORT_LOWER}-wind.rrd \
  --no-overwrite --start now --step $STEP \
  DS:wind_dir:GAUGE:600:0:360 \
  DS:wind_speed:GAUGE:600:0:100 \
  RRA:AVERAGE:0.5:$DAYAVG:$DAYSTEPS \
  RRA:AVERAGE:0.5:$WEEKAVG:$WEEKSTEPS \
  RRA:AVERAGE:0.5:$MONAVG:$MONSTEPS \
  RRA:AVERAGE:0.5:$YEARAVG:$YEARSTEPS

rrdcreate $STOREPATH/${AIRPORT_LOWER}-visibility.rrd \
  --no-overwrite --start now --step $STEP \
  DS:visibility:GAUGE:600:0:360 \
  RRA:AVERAGE:0.5:$DAYAVG:$DAYSTEPS \
  RRA:AVERAGE:0.5:$WEEKAVG:$WEEKSTEPS \
  RRA:AVERAGE:0.5:$MONAVG:$MONSTEPS \
  RRA:AVERAGE:0.5:$YEARAVG:$YEARSTEPS

rrdcreate $STOREPATH/${AIRPORT_LOWER}-ceiling.rrd \
  --no-overwrite --start now --step $STEP \
  DS:ceiling:GAUGE:600:0:20000 \
  RRA:AVERAGE:0.5:$DAYAVG:$DAYSTEPS \
  RRA:AVERAGE:0.5:$WEEKAVG:$WEEKSTEPS \
  RRA:AVERAGE:0.5:$MONAVG:$MONSTEPS \
  RRA:AVERAGE:0.5:$YEARAVG:$YEARSTEPS

