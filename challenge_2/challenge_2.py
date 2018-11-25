#!/usr/bin/env python3
__author__ = "Maxwell Goldbas"


import requests
import base64
import pandas as pd
import os
import logging
from .api import _get_countries, _get_data_on_country_and_date
from utils import Challenge, CONFIG_DIRECTORY
from openpyxl.formatting.rule import ColorScaleRule



"""
Maxwell Goldbas submission for SevenPark Data Challenge 2:

'Use 7Park Data's API to show what percent of Netflix's new 
subscriptions came from the USA vs. International countries 
from Sep 1, 2017 to Sep 30, 2017.'
"""


class ChallengeTwo(Challenge):
    """
    An object for creating a dashboard to visualize the Netflix data
    from Seven Park
    """
    _cache_folder = CONFIG_DIRECTORY + os.sep + 'challenge_2/data_cache' + os.sep
    _us_df_filename = _cache_folder + 'us_df.csv'
    _total_df_filename = _cache_folder + 'total_df.csv'


    def __init__(self, filename, date_from='2018-09-01', date_to='2018-09-30', use_cache=False):
        self.cache = use_cache
        self.date_from = date_from
        self.date_to = date_to
        self.us_df, self.total_df = self.get_all_data_by_date(self.date_from, self.date_to)
        self.create_excel(filename, self.us_df, self.total_df)


    def fill_from_cache(self, filename):
        """
        For development purposes only
        Get data from files in data_cache folder
        :return:
        """

        if os.path.exists(filename):
            return pd.read_csv(filename)

    def refill_cache(self, dataframe, filename):
        """
        Always refresh the cache when you can
        :param dataframe: pandas dataframe to be put into the cache
        :param filename: the filename of the csv in the cache
        :return:
        """
        if os.path.exists(filename):
            os.remove(filename)
        else:
            self.logger.info("The {} was not in the cache".format(filename))

        self.logger.debug('Filling {} into the cache'.format(filename))
        dataframe.to_csv(filename, index=False)



    def get_countries(self):
        self.logger.debug('Getting countries')
        countries = _get_countries()
        self.logger.debug('Got {} countries'.format(len(countries)))
        return countries

    def get_all_data_by_date(self, date_from, date_to):
        """
        :param date_from: beginning date of query
        :param date_to: end date of query
        :return: pandas dataframe of data
        """

        # Fill from the cache if required
        if self.cache:
            us_df = self.fill_from_cache(self._us_df_filename)
            total_df = self.fill_from_cache(self._total_df_filename)
            return us_df, total_df
        else:
            us_df = None
            total_df = pd.DataFrame()

        # Find all countries and initialize an empty dataframe
        countries = self.get_countries()

        # Loop through each country and add data to dataframe if data exists
        for country in countries:
            response = _get_data_on_country_and_date(country, date_from, date_to).json()

            # Some countries do not receive data, this output will only be logged in debug mode
            if not response['data']:
                self.logger.debug('Did not receive data for {}'.format(country))
                continue

            # US data will be held in a seperate dataframe for later analysis
            if country == "United States of America":
                self.logger.info('Filling out information for the USA')
                us_df = pd.DataFrame(response['data'])
            else:
                self.logger.info("Filling {} rows for {}".format(len(response['data']), country))
                country_df = pd.DataFrame(response['data'])
                total_df = pd.concat([total_df, country_df])

        #If data is not received for the USA due upstream error or logging difficult, report it
        if us_df is None:
            self.logger.warn("Not returning information for USA")

        #Refill the caches on every run
        else:
            self.refill_cache(us_df, self._us_df_filename)
        self.refill_cache(total_df, self._total_df_filename)
        return us_df, total_df


    def create_excel(self, filename, us_df, total_df):
        self.logger.info('Writing output from Challenge 2 to {}'.format(filename))
        excel = self.initialize_workbook(filename)


        comparision_worksheet_name = 'Challenge 2 - Final Comparision'
        comparision_df = self.format_and_join(us_df, total_df)

        comparision_df.to_excel(excel, comparision_worksheet_name)

        avg_login_worksheet = excel.book[comparision_worksheet_name]
        avg_login_worksheet.conditional_formatting.add('E2:E29',
                                      ColorScaleRule(start_type='min', start_color='AA0000',
                                                     end_type = 'max', end_color = '00AA00'))

        # USA dataframe may not always come thru depending on debugging
        if us_df is not None:
            self.logger.debug('Writing output of USA dataframe')
            us_df.to_excel(excel, sheet_name='Challenge 2 - Raw USA Data')

        self.logger.debug("Writing output of Total dataframe")
        total_df.to_excel(excel, sheet_name='Challenge 2 - Raw World Data')

        self.logger.debug('Saving excel document to {}'.format(filename))
        excel.save()

    def format_and_join(self, us_df, total_df):
        total_agg_df = total_df[['date', 'country_name', 'value']]
        total_agg_df = total_agg_df.groupby('date').mean()
        all_df = pd.merge(us_df, total_agg_df, left_on = 'date', right_index = True)
        final_df = all_df[['date', 'value_x', 'value_y']]
        final_df['Comparision'] = final_df['value_x'] - final_df['value_y']
        final_df = final_df.rename({'value_x':'US Value', 'value_y': 'All Other Value'})
        return final_df




if __name__ == "__main__":
    filename = CONFIG_DIRECTORY + os.sep + 'challenge_2.xlsx'
    ChallengeTwo(filename, '2018-09-01', '2018-09-30', cache=True)