# File: icao_lookup.py

import json

def find_site_by_icaoId(data, icaoId):
    icaoId = icaoId.upper()  # Convert the provided ICAO ID to upper case
    for airport in data:  # Directly iterate over the data if it's a list
        if airport['icaoId'].upper() == icaoId:  # Convert each ICAO ID in the data to upper case
            return airport.get('site', 'Site not found')
    return 'ICAO ID not found'

def get_icao_site(icaoId):
    # Path to the JSON file
    json_file_path = '/var/fli-rite/data/stations_current.json'

    # Read the JSON data from the file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    return find_site_by_icaoId(data, icaoId)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Find airport site by ICAO ID.')
    parser.add_argument('icaoId', type=str, help='The ICAO ID of the airport')
    args = parser.parse_args()

    print(get_icao_site(args.icaoId))

