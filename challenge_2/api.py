import requests
import base64
import pandas as pd
import logging


#TODO add logging

AUTH_HEADERS = {'Authorization': 'Token XXXXXXXX'}


def _seven_park_get(path='', params=None, json=None):
    """

    :param path: the required path of the URL endpoint
    :param params: any query strings for the request
    :param json: the json body passed to the request
    :return:
    """
    # must be done to avoid declaring object in the keyword arguments
    if not params:
        params = {}
    if not json:
        json = {}

    #build the request
    base_url = "https://avenue-api.7parkdata.com/v4/"

    base_url += path

    #return the pure request
    return requests.get(base_url, headers=AUTH_HEADERS, params=params, data=json)

def _get_countries():
    """
    :return: a list of the countries
    """
    querystring = {"entity_id": 46399, "respformat": "urlencode"}
    countries = _seven_park_get('dimensions/countries', params=querystring).json()['data']
    return [country['name'] for country in countries]

def _get_data_on_country_and_date(country, date_from, date_to):
    """
    :param country: country to find data on
    :param date_from: starting date of query
    :param date_to: ending date of query
    :return: total data on country
    """
    querystring = {"entity_id": "46399", "metric_id": "173", "metric_periodicity": "Daily",
                   "discovery_name": "netflix_subscriptions", "company_name": "Netflix%2C+Inc.",
                   "country_name": country, "metric_name": "CancellationIndex", "respformat": "flat",
                   "date_from":date_from, "date_to":date_to}
    return _seven_park_get('data', params=querystring)






if __name__ == "__main__":
    us_df, total_df = get_all_data_by_date('2017-09-01', "2017-09-10")