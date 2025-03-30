import json
import argparse

def find_site_by_icaoId(data, icaoId):
    icaoId = icaoId.upper()  # Convert the provided ICAO ID to upper case
    for airport in data:  # Directly iterate over the data if it's a list
        if airport['icaoId'].upper() == icaoId:  # Convert each ICAO ID in the data to upper case
            return airport.get('site', 'Site not found')
    return 'ICAO ID not found'

def main(icaoId):
    # Path to the JSON file
    json_file_path = '/var/fli-rite/data/stations_current.json'

    # Read the JSON data from the file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    site = find_site_by_icaoId(data, icaoId)
    print(site)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find airport site by ICAO ID.')
    parser.add_argument('icaoId', type=str, help='The ICAO ID of the airport')
    args = parser.parse_args()

    main(args.icaoId)

