#!/usr/bin/python

import sys
import requests
import json
import csv
import time
from datetime import date, timedelta
from ConfigParser import SafeConfigParser

"""
Python progam to create a csv file 'weather_data.csv' whose data is queried from DarkSky API.
Each data point is collected at 11:59pm. The timezone is based on the altitude and longitude.
Currently, only daily summary data is collected.
"""

def main():
    # argument format: 2017-02-10 2017-02-22
    dateStartArr = [int(numeric_string) for numeric_string in sys.argv[1].split("-")];
    dateEndArr = [int(numeric_string) for numeric_string in sys.argv[2].split("-")];

    dateStart = date(dateStartArr[0], dateStartArr[1], dateStartArr[2])
    dateEnd = date(dateEndArr[0], dateEndArr[1], dateEndArr[2])

    if (dateStart > dateEnd):
        raise ValueError("The end date should be greater or equal to the start date")

    config = get_config('config.ini')
    weather = get_weather_info(dateStart, dateEnd, config);
    fieldnames = get_all_fields(weather)

    with open('weather_data.csv', 'w') as csvfile:
        fieldnames = ["date"] + fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for key in weather:
            copied = weather[key].copy()
            copied["date"] = key
            writer.writerow(copied)

    print "File 'weather_data.csv' is successfully created."


def get_config(file_name):
    """
    Takes a configuration file name and returns the dictionary with parsed information including
    key, latitude, and longitude.
    """
    parser = SafeConfigParser()
    parser.read(file_name)
    config = {
        'key': parser.get('DEFAULT', 'secret_key'),
        'latitude': parser.get('DEFAULT', 'latitude'),
        'longitude': parser.get('DEFAULT', 'longitude')
    }
    return config


def get_all_fields(nested_dict):
    """
    Takes a dictionary of dictionaries in the form:
        {
            parent_key1: {
                child_key1: value1,
                child_key2: value2,
                ...
            },
            parent_key2: {
                child_key1: value3,
                child_key4: value4,
                ...
            },
            ...
        }
    Returns a list of all the nested keys with no duplicate.
    """
    keys = set()
    for value in nested_dict.values():
        keys.update(value.keys())
    return list(keys)


def get_weather_info(start, end, config):
    """
    Returns a dictionary of date-weatherData pairs, which are received from DarkSky
    """
    oneDay = timedelta(days=1)
    current = start
    data = {}
    key = config['key']
    longitude = config['longitude']
    latitude = config['latitude']
    while (current != (oneDay + end)):
        # [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS][timezone]  -  [timezone] is optional
        response = requests.get("https://api.darksky.net/forecast/" + key + "/" + latitude + "," + longitude + "," + current.isoformat() + "T23:59:59")
        data[current.isoformat()] = response.json()["daily"]["data"][0]
        current = current + oneDay
    return data


if __name__ == "__main__":
    main()
