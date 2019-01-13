import rrdtool
import sys

airport          = sys.argv[1]
airport_lo       = airport.lower()

# # where to store data. relative to current directory, MUST EXIST
store_path       = "/var/airpuff/rrd-data/"

# interval for feeding new data to rrd
step             = 300

### 1 DAY
# 1*300s         = 5 min (avg)
# 5min*288       = 1 day (duration)
dayavg           = 1
daysteps         = 288

### 7 DAYS (1 week)
# 3*300s         = 15 min (avg)
# 15min*672      = 7 days (duration)
weekavg          = 3
weeksteps        = 672

### 30 DAYS (~1 month)
# 6*300s         = 30 min (avg)
# 30min*1440     = 30 days (duration)
monavg           = 6
monsteps         = 1488

### 365 DAYS (~1 years)
# 12*300s        = 60 min (avg)
# 60min*86400    = 365 days (duration)
yearavg          = 12
yearsteps        = 8760

### 3650 DAYS (~10 years)
# 288*300s       = 1440 min  (avg)
# 1440min*86400  = 3650 days (duration)
tenyearavg       = 10
tenyearsteps     = 105120

temperature_filename = store_path + airport_lo + "-temp.rrd"
altimeter_filename   = store_path + airport_lo + "-altimeter.rrd"
wind_filename        = store_path + airport_lo + "-wind.rrd"
visibility_filename  = store_path + airport_lo + "-visibility.rrd"
ceiling_filename     = store_path + airport_lo + "-ceiling.rrd"
category_filename    = store_path + airport_lo + "-category.rrd"

rrdtool.create(
    temperature_filename,
    '--step', step,
    '--no-overwrite',
    'RRA:AVERAGE:0.5:%d:%d' % (dayavg, daysteps),
    'RRA:AVERAGE:0.5:%d:%d' % (weekavg, weeksteps),
    'RRA:AVERAGE:0.5:%d:%d' % (monavg, monsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (yearavg, yearsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (tenyearavg, tenyearsteps),
    'DS:temp_c:GAUGE:400:-64:64',
    'DS:temp_f:GAUGE:400:-64:150',
    'DS:dew_pt_c:GAUGE:400:-64:64',
    'DS:dew_pt_f:GAUGE:400:-64:150',
    'DS:t_dp_spread_c:GAUGE:400:-4:60',
    'DS:t_dp_spread_f:GAUGE:400:-4:130')

rrdtool.create(
    altimeter_filename,
    '--start', 'now',
    '--step', step,
    '--no-overwrite',
    'RRA:AVERAGE:0.5:%d:%d' % (dayavg, daysteps),
    'RRA:AVERAGE:0.5:%d:%d' % (weekavg, weeksteps),
    'RRA:AVERAGE:0.5:%d:%d' % (monavg, monsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (yearavg, yearsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (tenyearavg, tenyearsteps),
    'DS:altimeter:GAUGE:600:26:35')

rrdtool.create(
    wind_filename,
    '--start', 'now',
    '--step', step,
    '--no-overwrite',
    'RRA:AVERAGE:0.5:%d:%d' % (dayavg, daysteps),
    'RRA:AVERAGE:0.5:%d:%d' % (weekavg, weeksteps),
    'RRA:AVERAGE:0.5:%d:%d' % (monavg, monsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (yearavg, yearsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (tenyearavg, tenyearsteps),
    'DS:wind_dir:GAUGE:600:0:360',
    'DS:wind_speed:GAUGE:600:0:100')

rrdtool.create(
    visibility_filename,
    '--start', 'now',
    '--step', step,
    '--no-overwrite',
    'RRA:AVERAGE:0.5:%d:%d' % (dayavg, daysteps),
    'RRA:AVERAGE:0.5:%d:%d' % (weekavg, weeksteps),
    'RRA:AVERAGE:0.5:%d:%d' % (monavg, monsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (yearavg, yearsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (tenyearavg, tenyearsteps),
    'DS:visibility:GAUGE:600:0:100')

rrdtool.create(
    ceiling_filename,
    '--start', 'now',
    '--step', step,
    '--no-overwrite',
    'RRA:AVERAGE:0.5:%d:%d' % (dayavg, daysteps),
    'RRA:AVERAGE:0.5:%d:%d' % (weekavg, weeksteps),
    'RRA:AVERAGE:0.5:%d:%d' % (monavg, monsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (yearavg, yearsteps),
    'RRA:AVERAGE:0.5:%d:%d' % (tenyearavg, tenyearsteps),
    'DS:ceiling:GAUGE:600:0:20000')

# feed updates to the database
#rrdtool.update("test.rrd", "N:325")
