import datetime
import json
import platform
import pytz
import sys
import textwrap
import urllib.request

#from datetime import datetime
from decimal import Decimal
from numbers import Number
from fractions import Fraction

user_agent        = 'AirPuff/2.0; Python/3.6.5_or_later'

region            = sys.argv[1]
ap_csv            = sys.argv[2]
ap_csv_lo         = ap_csv.lower()
ap_csv_up         = ap_csv.upper()
ap_list           = ap_csv.split(",")
fqdn              = platform.node()

pac               = pytz.timezone('US/Pacific')
eas               = pytz.timezone('US/Eastern')
utc               = pytz.timezone("UTC")

full_fmt          = '%a %Y-%m-%d %H:%M %Z'
time_fmt          = '%H:%M %Z'

pac_cur_time      = datetime.datetime.now(pac).strftime(full_fmt)
eas_cur_time      = datetime.datetime.now(eas).strftime(time_fmt)
utc_cur_time      = datetime.datetime.now(utc).strftime(full_fmt)

#print("Work Commute AirPuff current run:\n%s / Zulu / Z\n%s / %s\n" % (utc_cur_time, pac_cur_time, eas_cur_time))
#print("ARPT	TIME	CAT  TEMP    DEW PT  T-DP    WIND    VIS ALT SKY COVER")

met_url           = 'https://api.checkwx.com/metar/' + ap_csv_lo + '/decoded?pretty=1'
met_hdrs          = {'X-API-Key'  : 'c5d65ffd02f05ddc608d5f0850',
                     'User-Agent' : user_agent }
met_req           = urllib.request.Request(met_url, headers=met_hdrs)
met_res           = urllib.request.urlopen(met_req)
met_data          = met_res.read()
#met_dump          = json.dumps(met_data)
met_json          = json.loads(met_data)
met_json_results  = met_json['results']

time_fmt       = '%H:%M %Z'

print(textwrap.dedent("""\
    <html>
    <head>
    <meta http-equiv="refresh" content="300">
    <link rel="stylesheet" type="text/css" href="/airpuff.css">
    <title>%s AirPuff Airport WX Info</title>
    </head>
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
    <th>ARPT</th><th>TIME</th><th>CAT</th><th>TEMP</th><th>DEW PT</th><th>T-DP</th><th>WIND</th><th>VIS</th><th>ALT</th><th>SKY COVER</th>
    </tr>
    """) % (region, region, utc_cur_time, pac_cur_time, eas_cur_time))

for count in range(0, met_json_results):
    met_icao          = met_json['data'][count]['icao']
    cardinal          = count + 1

    icao              = met_json['data'][count]['icao']
    icao_lo           = icao.lower()
    name              = met_json['data'][count]['name']
    obs_time          = met_json['data'][count]['observed']
    obs_time_obj      = datetime.datetime.strptime(obs_time, '%d-%m-%Y @ %H:%MZ')
    obs_time_conv     = obs_time_obj.strftime(time_fmt)
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
    if ceil_ft > 3000:
        ceil_class = "vfr_std"
    elif 1000 < ceil_ft <= 3000:
        ceil_class = "mvfr_std"
    elif 500 < ceil_ft <= 1000:
        ceil_class = "ifr_std"
    elif ceil_ft <= 500:
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
    flt_cat_lo        = flt_cat.lower()
    flt_cat_class     = flt_cat_lo + "_std"
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
        full_vis_mi, part_vis_mi = vis_mi.split(' ', 1)
    except:
        full_vis_mi        = vis_mi
        part_vis_mi        = '0.0'
    try:
        vis_mi_frac    = Fraction(part_vis_mi)
    except:
        vis_mi_frac    = '0.0'
    vis_mi_tot     = Fraction(vis_mi_frac) + int(full_vis_mi)
    if vis_mi_tot > 5:
        visi_class = "vfr"
    elif 3 < vis_mi_tot <= 5:
        visi_class = "mvfr"
    elif 1 < vis_mi_tot <= 3:
        visi_class = "ifr"
    elif vis_mi_tot <= 1:
        visi_class = "lifr"
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

#    print ("%-6s Temp: %-2d Dew Pt: %-2d T-DP Spread: %-2d - Ceil: %-s / %-d" % (icao, temp_f, dewpt_f, t_dp_spread_f, ceil_code, ceil_ft))
#123456781234567812345678123412345678123456781234567812345678123412341234567890121234
#ARPT	TIME	CAT	TEMP	DEW PT	T-DP	WIND	VIS	ALT	SKY COVER	ELEV
#    print("<tr><td>%-8s</td><td>%-8s</td><td>%-5s</td><td>%-8d</td><td>%-8d</td><td>%-8d</td><td>%3d@%-4d</td><td>%-4d</td><td>%-4d</td><td>%-4s</td><td>%-8s</td></tr>" % (icao, obs_time_conv, flt_cat, temp_f, dewpt_f, t_dp_spread_f, win_deg, win_spd_kts, vis_mi_tot, bar_hg, ceil_code, ceil_ft))
    print("<tr class=\"td\">\
<td><a class=\"%s\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>\
<td>%-s</td>\
<td class=\"%s\">%-s</td>\
<td><a href=\"https://www.airpuff.info/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>\
<td><a href=\"https://www.airpuff.info/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>\
<td><a href=\"https://www.airpuff.info/rrdweb/img-link/%s-temp-day-rrd.html\">%-d</a></td>\
<td><a href=\"https://www.airpuff.info/rrdweb/img-link/%s-wind-day-rrd.html\">%03d</a>@<a href=\"https://www.airpuff.info/rrdweb/img-link/%s-wind-day-rrd.html\">%02d</a></td>\
<td><a class=\"%s\" href=\"https://www.airpuff.info/rrdweb/img-link/%s-visi-day-rrd.html\">%0.2f</a></td>\
<td><a href=\"https://www.airpuff.info/rrdweb/img-link/%s-alti-day-rrd.html\">%0.2f</a></td>\
<td class=\"%s\">%-s %-d</td>\
</tr>\n" % \
    (flt_cat_class, icao_lo, icao, obs_time_conv, flt_cat_class, flt_cat, icao_lo, temp_f, icao_lo, dewpt_f, icao_lo, t_dp_spread_f, icao_lo, win_deg, icao_lo, win_spd_kts, visi_class, icao_lo, vis_mi_tot, icao_lo, bar_hg, ceil_class, ceil_code, ceil_ft))

print(textwrap.dedent("""\
    <td colspan=12><font color="#444444"><center>%s</center></font>
    </table>
    </body>
    </html>
    """) % (fqdn))

#https://www.airpuff.info/rrdweb/img-link/kedu-alti-day-rrd.html

#    print("icao:  %-8s" % (icao))
#    print("time:  %-8s" % (obs_time))
#    print("cat:   %-4s" % (flt_cat))
#    print("temp:  %-8d" % (temp_f))
#    print("dp:    %-8d" % (dewpt_f))
#    print("t-dp:  %-8d" % (t_dp_spread_f))
#    print("wind:  %-3d" % (win_deg))
#    print("spd:   %-4d" % (win_spd_kts))
#    print("vis:   %-4d" % (vis_mi))
#    print("alt:   %-4d" % (bar_hg))
#    print("cld:   %-12s" % (cld_len))
