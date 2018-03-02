import json
import requests
import sys
from numbers import Number

AIRPORTS = ['kedu', 'kvcb', 'ksuu', 'kccr', 'klvk', 'koak', 'khwd', 'krhv', 'ksjc', 'ksql', 'knuq', 'kpao']

#print("{0:^5} {1:^10} {2:^5} {3:^6} {4:^7} {5:^5} {6:^7} {7:^5} {8:^5} {9:^20}".format("ARPT", "TIME", "CAT", "TEMP", "DEW PT", "T-DP", "WIND", "VIS", "ALT", "SKY COVER"))
print("{0:^5} {1:^10} {2:^5} {3:^6} {4:^7} {5:^6} {6:^5} {7:^5} {8:^20}".format("ARPT", "TIME", "CAT", "TEMP", "DEW PT", "WIND", "VIS", "ALT", "SKY COVER"))
for AIRPORT in AIRPORTS:
    #print("AIRPORT: ")
    url = "https://avwx.rest/api/metar/{0}".format(AIRPORT)
    req = requests.get(url)
    obj = json.loads(req.text)

    #TEMP = int(obj["Temperature"])
    #DP = int(obj["Dewpoint"])
    #T_DP_SPREAD = TEMP - DP
    #if obj["Temperature"].isdigit():
        #isinstance(value, Number)
        #TEMP = int(obj["Temperature"])
        #if obj["Dewpoint"].isdigit():
            #DP = int(obj["Dewpoint"])
            #T_DP_SPREAD = TEMP - DP
    #else:
        #TEMP = 100
        #DP = 200
        #T_DP_SPREAD = 300

    #TEMP = int(obj["Temperature"]) if obj["Temperature"].isdigit()
    #DP = int(obj["Dewpoint"]) if obj["Dewpoint"].isdigit()
    #TEMP_DP_STUFF = [TEMP, DP]
    #[int(td) for td in TEMP_DP_STUFF if td.isdigit()]
    #for td in [TEMP, DP]:
        
    #isinstance(n, Number)
    #TEMP = [int(ORIG_TEMP) if ORIG_TEMP.isdigit()]
    
    print("{0:^5} {1:^10} {2:^5} {3:^6} {4:^7} {5:>3}@{6:<2} {7:^6} {8:^4} {9:<20}".format(obj["Station"], obj["Time"], obj["Flight-Rules"], obj["Temperature"], obj["Dewpoint"], obj["Wind-Direction"], obj["Wind-Speed"], obj["Visibility"], obj["Altimeter"], obj["Cloud-List"]))
    #print("{0:^5} {1:^10} {2:^5} {3:^6} {4:^7} {5:^5} {6:>3}@{7:<2} {8:^5} {9:^5} {10:<20}".format(obj["Station"], obj["Time"], obj["Flight-Rules"], TEMP, DP, T_DP_SPREAD, obj["Wind-Direction"], obj["Wind-Speed"], obj["Visibility"], obj["Altimeter"], obj["Cloud-List"]))


#01 00 - ARPT		 5 - CTR
#02 01 - TIME		10 - CTR
#03 02 - CAT		 5 - CTR
#04 03 - TEMP		 6 - CTR
#05 04 - DEW PT		 7 - CTR
#06 05 - T-DP		 5 - CTR
#07 06 - WIND DIR	 3 - CTR
#08 07 - WIND SPD	 2 - CTR
#09 08 - VIS		 5 - LFT
#10 09 - ALT		 5 - CTR
#11 10 - SKY COVER	20 - LFT
