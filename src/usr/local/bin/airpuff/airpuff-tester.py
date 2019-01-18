import datetime
import json
import platform
import pytz
import sqlite3
import sys
import textwrap
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

db_name            = '/var/airpuff/data/airport_info.db'

pac               = pytz.timezone('US/Pacific')
eas               = pytz.timezone('US/Eastern')
utc               = pytz.timezone("UTC")

full_fmt          = '%a %Y-%m-%d %H:%M %Z'
time_fmt          = '%H:%M %Z'
short_fmt         = '%H:%M'
metar_fmt         = '%d-%m-%Y @ %H:%MZ'

pac_cur_time      = datetime.datetime.now(pac).strftime(full_fmt)
eas_cur_time      = datetime.datetime.now(eas).strftime(time_fmt)
utc_cur_time      = datetime.datetime.now(utc).strftime(full_fmt)
utc_cur_comp_time = datetime.datetime.now(utc).strftime(short_fmt)

met_url           = 'https://api.checkwx.com/metar/' + ap_csv_lo + '/decoded?pretty=1'
met_hdrs          = {'X-API-Key'  : 'c5d65ffd02f05ddc608d5f0850',
                     'User-Agent' : user_agent }
met_req           = urllib.request.Request(met_url, headers=met_hdrs)
met_res           = urllib.request.urlopen(met_req)
met_data          = met_res.read()
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
    <font color="white" face="Tahoma" size=5>
    %s AirPuff current run:
    <font face="Courier" size=3>
    <br><font color=cornflowerblue>%s / Zulu / Z
    <br><font color=lightgreen>%s / %s
    <br>
    <br>
    <font color="white" face="Courier" size=3>
    <table class="table">
        <tr class="th">
            <th></th>
            <th></th>
            <th>ARPT</th>
            <th>AGE</th>
            <th>CAT</th>
            <th>TEMP</th>
            <th>DEW PT</th>
            <th>T-DP</th>
            <th>WIND</th>
            <th>VIS</th>
            <th>ALT</th>
            <th>SKY COVER</th>
        </tr>
    """) % (region, region, utc_cur_time, pac_cur_time, eas_cur_time))

for count in range(0, met_json_results):
    if "Currently Unavailable" in (met_json['data'][count]):
        icon_name      = "/web/icons/unknown-icon.png"
        record_data    = met_json['data'][count]
        icao_guess     = record_data.split(" ", 1)[0]
        icao_guess_lo  = icao_guess.lower()
        print(textwrap.dedent("""\
        <tr class=\"td\">
            <td><a class=\"missing_std\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
        </tr>
        """) % (icao_guess_lo, icao_guess, icon_name))
        break
    icao              = met_json['data'][count]['icao']
    icao_lo           = icao.lower()
    try:
        c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_lo,))
        atis_phone        = "tel://+1-" + c.fetchone()[0]
    except:
        atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"
    name              = met_json['data'][count]['name']
    obs_time          = met_json['data'][count]['observed']
    obs_time_obj      = datetime.datetime.strptime(obs_time, metar_fmt)
    obs_time_comp     = obs_time_obj.strftime(short_fmt)
    utc_conv          = datetime.datetime.strptime(str(utc_cur_comp_time), short_fmt)
    obs_time_conv     = datetime.datetime.strptime(str(obs_time_comp), short_fmt)
    obs_time_age      = utc_conv - obs_time_conv

    raw               = met_json['data'][count]['raw_text']
    bar_hg            = met_json['data'][count]['barometer']['hg']
    bar_kpa           = met_json['data'][count]['barometer']['kpa']
    bar_mb            = met_json['data'][count]['barometer']['mb']
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
    if ceil_ft >= 3000:
        ceil_class = "vfr_std"
    elif 1000 <= ceil_ft < 3000:
        ceil_class = "mvfr_std"
    elif 500 <= ceil_ft < 1000:
        ceil_class = "ifr_std"
    elif ceil_ft < 500:
        ceil_class = "lifr_std"
    cld_len           = len(met_json['data'][count]['clouds'])
#   for cld_ct in range(0, cld_len):
#        cld_code          = met_json['data'][cld_ct]['clouds']['code']
#        cld_text          = met_json['data'][cld_ct]['clouds']['text']
#        cld_base_ft       = met_json['data'][cld_ct]['clouds']['base_feet_agl']
#        cld_base_m        = met_json['data'][cld_ct]['clouds']['base_meters_agl']
#        cld_levels.append  = [cld_code, cld_base_ft, cld_base_m]
    try:
        dewpt_c           = met_json['data'][count]['dewpoint']['celsius']
        dewpt_f           = met_json['data'][count]['dewpoint']['fahrenheit']
    except TypeError:
        dewpt_c           = 0
        dewpt_f           = 0
    if isinstance(dewpt_f, Number):
        empty_var         = "good"
    else:
        dewpt_f           = 0
    elev_ft           = met_json['data'][count]['elevation']['feet']
    elev_m            = met_json['data'][count]['elevation']['meters']
    flt_cat           = met_json['data'][count]['flight_category']
    flt_cat_link      = flt_cat.lower()
    flt_cat_text      = flt_cat_link + "_std"
    icon_name         = "/web/icons/" + ceil_code.lower() + "-" + flt_cat_link + "-icon.png"
    hum_pct           = met_json['data'][count]['humidity_percent']
    try:
        temp_c            = met_json['data'][count]['temperature']['celsius']
        temp_f            = met_json['data'][count]['temperature']['fahrenheit']
    except TypeError:
        temp_c            = 0
        temp_f            = 0
    try:
        t_dp_spread_f     = temp_f - dewpt_f
    except:
        t_dp_spread_f     = 0
    vis_mi         = met_json['data'][count]['visibility']['miles']
    vis_m          = met_json['data'][count]['visibility']['meters']
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

    if vis_mi_tot < 0:
        print(textwrap.dedent("""\
        <tr class=\"td\">
            <td><a class=\"missing_std\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
        </tr>
        """) % (icao_lo, icon_name))
    else:
        print(textwrap.dedent("""\
        <tr class=\"td\">
            <td><a href=\"%s\"><img width=20 height=20 src=\"/web/icons/telephone-icon.png\"︎></a></td>
            <td><img width=20 height=20 src=\"%s\"></td>
            <td><a class=\"%s\" href=\"/rrdweb/%s-rrd.html\">%-s</td>
            <td>%-s</td>
            <td class=\"%s\">%-s</td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td><a href=\"/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>
            <td><a href=\"/rrdweb/img-link/%s-wind-day-rrd.html\">%03d</a>@<a href=\"/rrdweb/img-link/%s-wind-day-rrd.html\">%02d</a></td>
            <td><a class=\"%s\" href=\"/rrdweb/img-link/%s-visi-day-rrd.html\">%0.2f</a></td>
            <td><a href=\"/rrdweb/img-link/%s-alti-day-rrd.html\">%0.2f</a></td>
            <td class=\"%s\">%-s %-d</td>
        </tr>
    """) % (atis_phone, icon_name, flt_cat_link, icao_lo, icao, obs_time_age, flt_cat_text, flt_cat, icao_lo, temp_f, icao_lo, dewpt_f, icao_lo, t_dp_spread_f, icao_lo, win_deg, icao_lo, win_spd_kts, visi_class, icao_lo, vis_mi_tot, icao_lo, bar_hg, ceil_class, ceil_code, ceil_ft))

print(textwrap.dedent("""\
        <tr>
            <td colspan=12><font color="#444444"><center>%s</center></font></td>
        </tr>
    </table>
    </body>
    </html>
    
    """) % (fqdn))
conn.commit()
conn.close()
