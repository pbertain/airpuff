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
metar_fmt         = '%d-%m-%Y @ %H:%MZ'
pattern           = '%d-%m-%Y @ %H:%MZ'

date_time1        = datetime.datetime.now(utc).strftime(pattern)
pac_cur_time      = datetime.datetime.now(pac).strftime(full_fmt)
eas_cur_time      = datetime.datetime.now(eas).strftime(time_fmt)
utc_cur_time      = datetime.datetime.now(utc).strftime(full_fmt)
utc_cur_comp_time = datetime.datetime.now(utc).strftime(short_fmt)
epoch_now         = calendar.timegm(time.strptime(date_time1, metar_fmt))

met_url           = 'http://online.saiawos.com/DWA/ios/webgetjson.php'
met_hdrs          = {'User-Agent' : user_agent }
met_req           = urllib.request.Request(met_url, headers=met_hdrs)
met_res           = urllib.request.urlopen(met_req)
met_data          = met_res.read().decode('utf-8')
met_json          = json.loads(met_data)
#met_json_results  = met_json['results']

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
            <td class="td_titles" rowspan="3" colspan="4" vertical-align="center"><img width="100"  height="81" src="/web/icons/airpuff-logo.png"></td>
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
            <th>SKY COVER</th>
        </tr>
    """) % (region, region, utc_cur_time, pac_cur_time, eas_cur_time))

temp_f            = int(met_json["temp"].split('(', 1)[0])
dewpt_f           = int(met_json["dwpt"].split('(', 1)[0])
t_dp_spread_f     = int(temp_f - dewpt_f)
win_spd_kts       = int(met_json["wndSpd"])
win_spd_mph       = float(win_spd_kts / 0.8689762)
win_deg           = int(met_json["wndDir"])
vis_mi_tot        = int(met_json["visib"].replace("+", ""))
bar_hg            = float(met_json["alt"])
ceil_full         = met_json["ceiling"]
ceil_list         = ceil_full.split()
ceil_len          = len(ceil_list)
ceil_cap          = ceil_len - 1
ceil_limit        = '12000'

for count in range(0, ceil_len):
    try:
        ceil_code             = ceil_list[count][:3]
        ceil_ht               = ceil_list[count][4:6]
        ceil_ht               = int(ceil_ht)
        if ceil_code == ("BKN" or "OVC" or "OVX"):
            ceil_ft           = int(ceil_ht * 100)
            if ceil_ft < ceil_limit:
                ceil_limit        = ceil_ft
        elif ceil_ht is None:
            ceil_ft           = '12000'
            ceil_limit        = ceil_ft
        else:
            ceil_ft           = int(ceil_ht * 100)
            ceil_limit        = ceil_ft
    except:
        ceil_code         = ceil_list[count][:3]
        if ceil_code == "CLR":
            ceil_ft           = int('12000')
            ceil_limit        = ceil_ft
        else:
            ceil_code         = "UNK"
            ceil_ft           = '-'
            ceil_limit        = ceil_ft

ceil_limit        = int(ceil_limit)

if ceil_ft > 3000:
    ceil_class = "vfr_std"
elif 1000 <= ceil_ft <= 3000:
    ceil_class = "mvfr_std"
elif 500 <= ceil_ft < 1000:
    ceil_class = "ifr_std"
elif ceil_ft < 500:
    ceil_class = "lifr_std"

pattern           = '%d-%m-%Y @ %H:%MZ'

# "utc":"23:02"
# "date":"05 FEB 19"
utc_time          = met_json["utc"].split(':')
utc_date          = met_json["date"].split()
utc_hour          = utc_time[0]
utc_mins          = utc_time[1]
utc_day           = utc_date[0]
utc_mon           = utc_date[1].title()
utc_year          = "20" + utc_date[2]
utc_combined      = utc_day + " " + utc_mon + " " + utc_year + " " + utc_hour + ":" + utc_mins

report_time       = datetime.datetime.strptime(utc_combined, '%d %b %Y %H:%M')
obs_time          = report_time.strftime(pattern)

#timediff          = int(date_time_short) - int(metar_time)

icao              = met_json['metar'].split(' ')[1]
icao_lo           = icao.lower()

epoch_report      = calendar.timegm(time.strptime(obs_time, metar_fmt))
epoch_secs        = epoch_report - epoch_now # It seems that KDWA AWOS is 2 mins ahead
epoch_hrs         = epoch_secs / 3600
hours             = epoch_hrs // 1
minutes           = str(round((epoch_hrs % 1) * 60))
mins              = minutes.zfill(2)

try:
    c.execute("SELECT wx_phone FROM airports WHERE airport=?", (icao_lo,))
    atis_phone        = "tel://+1-" + c.fetchone()[0]
except:
    atis_phone        = "https://www.airpuff.info/web/airpuff-airror.html"

if (temp_f <= 50 and win_spd_mph > 3):
    wind_chill           = 35.74 + (0.6215 * temp_f) - (35.75 * (int(win_spd_mph) ** 0.16)) + (0.4275 * temp_f * (win_spd_mph ** 0.16))
    wind_chill_fmt       = '{:.0f}'.format(wind_chill)
else:
    wind_chill           = "-"
    wind_chill_fmt       = "-"

wind_chill_act        = met_json["windChill"].split(' ')[0]

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

if vis_mi_tot > 5:
    if ceil_ft > 3000:
        flt_cat           = "VFR"
    elif 1000 <= ceil_ft <= 3000:
        flt_cat           = "MVFR"
    elif 500 <= ceil_ft < 1000:
        flt_cat           = "IFR"
    elif ceil_ft < 500:
        flt_cat           = "LIFR"
elif 3 <= vis_mi_tot <= 5
    if ceil_ft > 3000:
        flt_cat           = "MVFR"
    elif 1000 <= ceil_ft <= 3000:
        flt_cat           = "MVFR"
    elif 500 <= ceil_ft < 1000:
        flt_cat           = "IFR"
    elif ceil_ft < 500:
        flt_cat           = "LIFR"
elif 1 <= vis_mi_tot < 3
    if ceil_ft > 3000:
        flt_cat           = "IFR"
    elif 1000 <= ceil_ft <= 3000:
        flt_cat           = "IFR"
    elif 500 <= ceil_ft < 1000:
        flt_cat           = "IFR"
    elif ceil_ft < 500:
        flt_cat           = "LIFR"
0 <= vis_mi_tot < 1
    if ceil_ft > 3000:
        flt_cat           = "LIFR"
    elif 1000 <= ceil_ft <= 3000:
        flt_cat           = "LIFR"
    elif 500 <= ceil_ft < 1000:
        flt_cat           = "LIFR"
    elif ceil_ft < 500:
        flt_cat           = "LIFR"

flt_cat_link      = flt_cat.lower()
flt_cat_text      = flt_cat_link + "_std"

icon_name         = "/web/icons/" + ceil_code.lower() + "-" + flt_cat_link + "-icon.png"

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
            <td><a class=\"missing_std\" href=\"https://www.airpuff.info/rrdweb/%s-rrd.html\">%-s</a></td>
            <td class="td_list_lg" colspan=9>Stale Data (More than 3 hrs old)</td>
        </tr>
        """) % (atis_phone, icon_name, icao_lo, icao))

else:
    print(textwrap.dedent("""\
    <tr class="td">
        <td><a href=\"%s\"><img width=40 height=20 src=\"/web/icons/telephone-wide-icon.png\"︎></a></td>
        <td><img width=20 height=20 src=\"%s\"></td>
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
        <td class="%s">%-s %-d</td>
    </tr>
""") % (atis_phone, icon_name, flt_cat_link, icao_lo, icao, hours, mins, flt_cat_text, flt_cat, icao_lo, temp_f, icao_lo, dewpt_f, icao_lo, t_dp_spread_f, wind_chill_fmt, icao_lo, win_deg, icao_lo, win_spd_kts, visi_class, icao_lo, vis_mi_tot, icao_lo, bar_hg, ceil_class, ceil_code, ceil_limit))

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
