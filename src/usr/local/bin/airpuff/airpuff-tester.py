import calendar
import datetime
import json
import platform
import pytz
import sqlite3
import sys
import textwrap
import time
import urllib.request

from decimal import Decimal
from numbers import Number
from fractions import Fraction

user_agent        = 'AirPuff/2.0; Python/3.6.5'
region            = sys.argv[1]
ap_csv            = sys.argv[2]
ap_csv_lo         = ap_csv.lower()
ap_csv_up         = ap_csv.upper()
ap_list           = ap_csv.split(",")
fqdn              = platform.node()
shortname         = fqdn.split('.', 1)[0]

db_name            = '/var/airpuff/data/airport_info.db'

pac               = pytz.timezone('US/Pacific')
eas               = pytz.timezone('US/Eastern')
utc               = pytz.timezone("UTC")

full_fmt          = '%a %Y-%m-%d %H:%M %Z'
time_fmt          = '%H:%M %Z'
short_fmt         = '%H:%M'
metar_fmt         = '%Y-%m-%dT%H:%M:%S.%fZ'
# delete this if the time formatting on the previous line works:  d-%m-%Y @ %H:%MZ'
pattern           = '%d-%m-%Y @ %H:%MZ'

date_time1        = datetime.datetime.now(utc).strftime(metar_fmt)
pac_cur_time      = datetime.datetime.now(pac).strftime(full_fmt)
eas_cur_time      = datetime.datetime.now(eas).strftime(time_fmt)
utc_cur_time      = datetime.datetime.now(utc).strftime(full_fmt)
utc_cur_comp_time = datetime.datetime.now(utc).strftime(short_fmt)
epoch_now         = calendar.timegm(time.strptime(date_time1, metar_fmt))

met_url           = 'https://api.checkwx.com/metar/' + ap_csv_lo + '/decoded?pretty=1'
met_hdrs          = {'X-API-Key'  : 'c5d65ffd02f05ddc608d5f0850',
                     'User-Agent' : user_agent }
met_req           = urllib.request.Request(met_url, headers=met_hdrs)
met_res           = urllib.request.urlopen(met_req)
met_data          = met_res.read().decode('utf-8')
#met_dump          = json.dumps(met_data)
met_json          = json.loads(met_data)
met_json_results  = met_json['results']

conn              = sqlite3.connect(db_name)
c                 = conn.cursor()

print(textwrap.dedent("""\
    <html>
    <head>
        <meta http-equiv="refresh" content="300">
        <link rel="stylesheet" type="text/css" href="/web/css/airpuff.css">
    </head>

    <title>%s AirPuff Airport WX Info</title>

    <body bgcolor="#333333" link="#FFA500" alink="#FFA500" vlink="#FFA500">
    <table class="table">
        <tr>
            <td class="td_titles" rowspan="3" colspan="4" vertical-align="center"><a href="https://www.airpuff.info/"><img width="100"  height="81" src="/web/icons/airpuff-logo.png"></a></td>
            <td class="td_titles" colspan="9" vertical-align="center">%s AirPuff current run:</td>
        </tr>
        <tr>
            <td class="td_cfb" colspan="9" vertical-align="center">%s / Zulu / Z</td>
        </tr>
        <tr>
            <td class="td_lg" colspan="9" vertical-align="center">%s / %s</td>
        <tr>

        <tr class="th">
            <th></th>
            <th></th>
            <th>RAW</th>
            <th>ARPT</th>
            <th>AGE</th>
            <th>CAT</th>
            <th>TEMP</th>
            <th>DP</th>
            <th>T-DP</th>
            <th>WC</th>
            <th>WIND</th>
            <th>VIS</th>
            <th>ALT</th>
            <th>LAYERS</th>
        </tr>
    """) % (region, region, utc_cur_time, pac_cur_time, eas_cur_time))
#            <th>SKY COVER</th>

for count in range(0, met_json_results):
    if "Currently Unavailable" in (met_json['data'][count]):
        icon_name      = "/web/icons/unknown-icon.png"
        record_data    = met_json['data'][count]
        icao_guess     = record_data.split(" ", 1)[0]
        icao_guess_lo  = icao_guess.lower()
        try:
            c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_guess_lo,))
            atis_phone        = "tel://+1-" + c.fetchone()[0]
        except:
            atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"
        print(textwrap.dedent("""\
        <tr class="td">
            <td><a href=\"%s\"><img width=40 height=20 src=\"/web/icons/telephone-wide-icon.png\"︎></a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
            <td></td>
            <td><a class="missing_std" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td class="td_list_lg" colspan=9>Data Unavailable</td>
        </tr>
        """) % (atis_phone, icon_name, icao_guess_lo, icao_guess))
        continue
    icao              = met_json['data'][count]['icao']
    icao_lo           = icao.lower()
    try:
        c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_lo,))
        atis_phone        = "tel://+1-" + c.fetchone()[0]
    except:
        atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"
    name              = met_json['data'][count]['station']['name']
    obs_time_bkn      = met_json['data'][count]['observed']
    obs_time_str      = str(obs_time_bkn)
    obs_time          = obs_time_str.replace(' <span class="tx-light tx-12">@</span>', ' @')
    obs_time_obj      = datetime.datetime.strptime(obs_time, metar_fmt)
    obs_time_comp     = obs_time_obj.strftime(short_fmt)
    date_time2        = obs_time_obj.strftime(metar_fmt)
    utc_conv          = datetime.datetime.strptime(str(utc_cur_comp_time), short_fmt)
    obs_time_conv     = datetime.datetime.strptime(str(obs_time_comp), short_fmt)
    obs_time_age      = utc_conv - obs_time_conv
    epoch1            = int(time.mktime(time.strptime(date_time1, metar_fmt)))
    epoch2            = int(time.mktime(time.strptime(date_time2, metar_fmt)))
    timediff          = epoch2 - epoch1
    td_min            = timediff / 60
    td_hr             = timediff / 3600
    diff              = '{:2f}:{:2f}'.format(*divmod(td_min, 60))
    epoch_report      = calendar.timegm(time.strptime(obs_time, metar_fmt))
    epoch_secs        = epoch_now - epoch_report
    epoch_hrs         = epoch_secs / 3600
    hours             = epoch_hrs // 1
    minutes           = str(round((epoch_hrs % 1) * 60))
    mins              = minutes.zfill(2)


    raw               = met_json['data'][count]['raw_text']
    metar_ref         = icao_lo + "RawMetar"
    try:
        bar_hg            = met_json['data'][count]['barometer']['hg']
        bar_kpa           = met_json['data'][count]['barometer']['kpa']
        bar_mb            = met_json['data'][count]['barometer']['mb']
    except:
        bar_hg            = '29.92'
        bar_kpa           = '101.32075'
        bar_mb            = '1013.2075'
    try:
        ceil_code         = met_json['data'][count]['ceiling']['code']
    except:
        ceil_code         = 'CLR'
    try:
        ceil_ft           = met_json['data'][count]['ceiling']['feet_agl']
    except:
        ceil_ft           = 12000
    try:
        ceil_m            = met_json['data'][count]['ceiling']['meters_agl']
    except:
        ceil_m            = 3,657.6
    if ceil_ft > 3000:
        ceil_class = "vfr_std"
    elif 1000 <= ceil_ft <= 3000:
        ceil_class = "mvfr_std"
    elif 500 <= ceil_ft < 1000:
        ceil_class = "ifr_std"
    elif ceil_ft < 500:
        ceil_class = "lifr_std"
# START: Cloud layer
    clouds            = met_json['data'][count]['clouds']
    cld_len           = len(met_json['data'][count]['clouds'])
    cloud_layer       = ""
    for layer in clouds:
        code = str(layer['code'])
        if code == ('BKN' or 'OVC'):
            layer_class = "vfr_std"
        try:
            layer_ft = layer['base_feet_agl']
        except:
            layer_ft = 12001
#        print(code, " ", layer_ft, "\n")
        if layer_ft > 3000:
            layer_class = "vfr_std"
        elif 1000 <= layer_ft <= 3000:
            if code == 'FEW':
                layer_class = "vfr_std"
            elif code == 'SCT':
                layer_class = "vfr_std"
            elif code == 'BKN':
                layer_class = "mvfr_std"
            elif code == 'OVC':
                layer_class = "mvfr_std"
            else:
                layer_class = "mvfr_std"
        elif 500 <= layer_ft < 1000:
            if code == 'FEW':
                layer_class = "vfr_std"
            elif code == 'SCT':
                layer_class = "vfr_std"
            elif code == 'BKN':
                layer_class = "ifr_std"
            elif code == 'OVC':
                layer_class = "ifr_std"
            else:
                layer_class = "ifr_std"
        elif layer_ft < 500:
            if code == 'FEW':
                layer_class = "vfr_std"
            elif code == 'SCT':
                layer_class = "vfr_std"
            elif code == 'BKN':
                layer_class = "lifr_std"
            elif code == 'OVC':
                layer_class = "lifr_std"
            else:
                layer_class = "lifr_std"
        if str(code) == 'CLR':
            cloud_layer = cloud_layer + "<td class=\"" + str(layer_class) + "\">" + str(code) + "</td>"
        elif str(code) == 'SKC':
            cloud_layer = cloud_layer + "<td class=\"" + str(layer_class) + "\">" + str(code) + "</td>"
        else:
            cloud_layer = cloud_layer + "<td class=\"" + str(layer_class) + "\">" + str(code) + str(" ") + str(layer_ft) + "</td>"

# END: Cloud layer

    try:
        dewpt_c           = met_json['data'][count]['dewpoint']['celsius']
        dewpt_f           = met_json['data'][count]['dewpoint']['fahrenheit']
    except KeyError:
        dewpt_c           = 0
        dewpt_f           = 0
    except TypeError:
        dewpt_c           = 0
        dewpt_f           = 0
    elev_ft           = met_json['data'][count]['elevation']['feet']
    elev_m            = met_json['data'][count]['elevation']['meters']
    flt_cat           = met_json['data'][count]['flight_category']
    flt_cat_link      = flt_cat.lower()
    flt_cat_text      = flt_cat_link + "_std"
    if flt_cat == 'UNK':
        icon_name         = "/web/icons/unknown-icon.png"
    else:
        icon_name         = "/web/icons/" + ceil_code.lower() + "-" + flt_cat_link + "-icon.png"
    try:
        hum_pct           = met_json['data'][count]['humidity']['percent']
    except KeyError:
        hum_pct           = 0
    else:
        hum_pct           = 0
    try:
        temp_c            = met_json['data'][count]['temperature']['celsius']
        temp_f            = met_json['data'][count]['temperature']['fahrenheit']
    except KeyError:
        temp_c            = 0
        temp_f            = 0
    except TypeError:
        temp_c            = 0
        temp_f            = 0
    try:
        t_dp_spread_f     = temp_f - dewpt_f
    except:
        t_dp_spread_f     = 0
    try:
        vis_mi         = met_json['data'][count]['visibility']['miles']
        vis_m          = met_json['data'][count]['visibility']['meters']
    except:
    	vis_mi         = -1
    	vis_m          = -1
    try:
        vis_mi_tot_float  = met_json['data'][count]['visibility']['miles_float']
    except:
        vis_mi_tot_error  = true
    try:
        full_vis_mi, part_vis_mi = vis_mi.split(' ', 1)
    except:
        full_vis_mi        = vis_mi
        part_vis_mi        = '0.0'
    try:
        vis_mi_frac    = Fraction(part_vis_mi)
    except:
        vis_mi_frac    = '0.0'
    try:
        vis_mi_tot     = vis_mi_tot_float
    except TypeError:
        vis_mi_tot     = -1
    except:
        vis_mi_tot     = Fraction(vis_mi_frac) + int(full_vis_mi)
    if vis_mi_tot > 5:
        visi_class = "vfr"
    elif 3 <= vis_mi_tot <= 5:
        visi_class = "mvfr"
    elif 1 <= vis_mi_tot < 3:
        visi_class = "ifr"
    elif 0 <= vis_mi_tot < 1:
        visi_class = "lifr"
    elif vis_mi_tot < 0:
        visi_class = "missing_std"
    try:
        win_deg          = met_json['data'][count]["wind"]['degrees']
    except:
        win_deg          = 0
    if isinstance(win_deg, Number):
        empty_var         = "good"
    else:
        win_deg           = 0
    try:
        win_spd_kts      = met_json['data'][count]["wind"]['speed_kts']
    except:
        win_spd_kts      = 0
    if isinstance(win_spd_kts, Number):
        empty_var         = "good"
    else:
        win_spd_kts           = 0
    try:
        win_spd_mph      = met_json['data'][count]["wind"]['speed_mph']
    except:
        win_spd_mph      = 0
    try:
        win_spd_mps      = met_json['data'][count]["wind"]['speed_mps']
    except:
        win_spd_mps      = 0

    if (temp_f <= 50 and win_spd_mph > 3):
        wind_chill           = 35.74 + (0.6215 * temp_f) - (35.75 * (int(win_spd_mph) ** 0.16)) + (0.4275 * temp_f * (win_spd_mph ** 0.16))
        wind_chill_fmt       = '{:.0f}'.format(wind_chill)
    else:
        wind_chill           = "-"
        wind_chill_fmt       = "-"

    if vis_mi_tot < 0:
        icon_name      = "/web/icons/unknown-icon.png"
        try:
            c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_guess_lo,))
            atis_phone        = "tel://+1-" + c.fetchone()[0]
        except:
            atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"
        print(textwrap.dedent("""\
        <tr class="td">
            <td><a href=\"%s\"><img width=40 height=20 src=\"/web/icons/telephone-wide-icon.png\"︎></a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
            <td></td>
            <td><a class=\"missing_std\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td class="td_list_lg" colspan=9>Missing Data</td>
        </tr>
        """) % (atis_phone, icon_name, icao_lo, icao))
    elif epoch_hrs >= 3:
        icon_name      = "/web/icons/unknown-icon.png"
        try:
            c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_lo,))
            atis_phone        = "tel://+1-" + c.fetchone()[0]
        except:
            atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"
        print(textwrap.dedent("""\
        <tr class="td">
            <td><a href=\"%s\"><img width=40 height=20 src=\"/web/icons/telephone-wide-icon.png\"︎></a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
            <td></td>
            <td><a class=\"missing_std\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td class="td_list_lg" colspan=9>Stale Data (More than 3 hrs old)</td>
        </tr>
        """) % (atis_phone, icon_name, icao_lo, icao))
    else:
        print(textwrap.dedent("""\
        <tr class="td">
            <td><a href=\"%s\"><img width=40 height=20 src=\"/web/icons/telephone-wide-icon.png\"︎></a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
            <td>
                <a href="#%s"><img width=20 height=20 src="/web/icons/airpuff-raw-metar-icon.png"></a>
                <div id="%s" class="metarDialog">
                    <div>
                        <a href="#close" title="%s Raw METAR Data" class="close">X</a>
                        <h3 class="header_yel">%s Raw METAR Data</h3>
                        <p class="paragraph_metar">%s</p> 
                    </div>
                </div>
            </td>
            <td><a class="%s" href=\"/rrdweb/%s-rrd.html\">%-s</td>
            <td>%d:%s</td>
            <td class="%s">%-s</td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td>%-s</td>
            <td><a href=\"/rrdweb/img-link/%s-wind-day-rrd.html\">%03d</a>@<a href=\"/rrdweb/img-link/%s-wind-day-rrd.html\">%02d</a></td>
            <td><a class="%s" href=\"/rrdweb/img-link/%s-visi-day-rrd.html\">%0.2f</a></td>
            <td><a href=\"/rrdweb/img-link/%s-alti-day-rrd.html\">%0.2f</a></td>
            %s
        """) % (atis_phone, icon_name, metar_ref, metar_ref, icao, icao, raw, flt_cat_link, icao_lo, icao, hours, mins, flt_cat_text, flt_cat, icao_lo, temp_f, icao_lo, dewpt_f, icao_lo, t_dp_spread_f, wind_chill_fmt, icao_lo, win_deg, icao_lo, win_spd_kts, visi_class, icao_lo, vis_mi_tot, icao_lo, bar_hg, cloud_layer))
        print('</tr>')
#        """) % (atis_phone, icon_name, metar_ref, metar_ref, icao, icao, raw, flt_cat_link, icao_lo, icao, hours, mins, flt_cat_text, flt_cat, icao_lo, temp_f, icao_lo, dewpt_f, icao_lo, t_dp_spread_f, wind_chill_fmt, icao_lo, win_deg, icao_lo, win_spd_kts, visi_class, icao_lo, vis_mi_tot, icao_lo, bar_hg, ceil_class, ceil_code, ceil_ft))
#            <td class="%s">%-s %-d</td>

print(textwrap.dedent("""\
        <tr>
            <td class="footer" colspan=12><a href="https://www.checkwx.com/"><img width=134.7 height=50 src="/web/icons/check-wx-icon.png"></a></td>
        </tr>
        <tr>
            <td class="footer" colspan=12>%s</td>
        </tr>
    </table>
    </body>
    </html>
    """) % (shortname))

conn.commit()
conn.close()
