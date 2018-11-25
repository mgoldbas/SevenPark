#!/usr/bin/env python3
__author__ = "Maxwell Goldbas"

import pandas as pd
import logging
import os
from utils import Challenge, CONFIG_DIRECTORY, FINAL_OUTPUT
from openpyxl.formatting.rule import ColorScaleRule

"""
Maxwell Goldbas submission for SevenPark Data Challenge 1:

'...calculate an average value of logins for every company per country.' 
"""


class ChallengeOne(Challenge):
    _countries = {1: 'USA', 2: 'Canada', 3: 'Mexico'}
    _data_filename = CONFIG_DIRECTORY + os.sep + 'challenge_1' + os.sep + 'challenge_1_data.tsv'

    def __init__(self, filename):
        self.data_lines = self.pull_data_set_from_file()
        self.dataframe = self.create_dataframe(self.data_lines)
        self.dataframe = self.format_dataframe(self.dataframe)
        self.find_average_logins(self.dataframe)
        self.format_excel(filename, self.dataframe)

    def pull_data_set_from_file(self):
        """
        Go to the tab seperated value and return the data as a list
        Data is not big enough to warrant a Spark solution
        Data would not read initially as a pandas dataframe
        :return: array of strings
        """
        self.logger.debug('Reading file')

        # Cound not get the pandas reader working properly
        # challenge_1_data = pd.read_csv('challenge_1_data.tsv', sep='\\t')
        with open(self._data_filename, 'r') as f:
            data_lines = f.read().split('\\n')
        self.logger.debug('Read file: {} rows'.format(len(data_lines)))
        return data_lines

    def create_dataframe(self, data_lines):
        """
        Turn array into dataframe
        :param data_lines: array of strings to be turned into dataframe
        :return: pandas dataframe
        """
        self.logger.debug('Formatting rows')
        initial_row_count = len(data_lines)
        data_rows = [line.split('\\t') for line in data_lines if len(line.split('\\t')) == 4]
        self.logger.debug(data_rows)
        dataframe = pd.DataFrame(data_rows, columns=['timestamp', 'app_name', 'number_of_logins', 'country_id'])
        final_row_count = len(dataframe.index)
        self.logger.debug('Printing Dataframe: {} rows'.format(final_row_count))
        self.logger.debug(dataframe.head())
        if final_row_count != initial_row_count:
            self.logger.error("Lost {} rows due to formatting".format(abs(final_row_count - initial_row_count)))
        return dataframe

    def format_dataframe(self, dataframe):
        """
        Leaving the formatting function seperate from the create dataframe function to increase modularity
        :param dataframe: dataframe to be formatted
        :return:
        """
        self.logger.debug('Formatting datatypes')
        self.logger.debug("Original datatypes:")
        self.logger.debug(dataframe.dtypes)
        dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'], unit='s')
        dataframe['number_of_logins'] = pd.to_numeric(dataframe['number_of_logins'], errors='coerce')
        self.logger.debug(dataframe.dtypes)
        dataframe['app_name'].replace({r'[^\x00-\x7F]+': ''}, regex=True, inplace=True)
        dataframe['app_name'].replace({'Facbook': 'Facebook', 'Fcebook': 'Facebook'}, inplace=True)
        look_up_country = lambda x: self._countries[int(x)]
        dataframe['country_name'] = dataframe['country_id'].apply(look_up_country)
        return dataframe

    def find_average_logins(self, dataframe):
        """
        find the average number of logins by app
        :param dataframe:
        :return: dataframe with a row per app
        """
        avg_dataframe = dataframe.groupby(['app_name', 'country_name'][::-1])
        avg_dataframe = avg_dataframe.agg({'number_of_logins': 'count'})
        return avg_dataframe

    def format_excel(self, filename, dataframe):
        avg_login_dataframe = self.find_average_logins(dataframe)
        excel = self.initialize_workbook(filename)

        avg_login_worksheet_name = 'Challenge 1 - Average Logins Report'
        avg_login_dataframe = avg_login_dataframe.rename(lambda x: x.replace('_', ' ').capitalize(), axis='columns')
        avg_login_dataframe.to_excel(excel, avg_login_worksheet_name)

        avg_login_worksheet = excel.book[avg_login_worksheet_name]
        avg_login_worksheet.conditional_formatting.add('C1:C10',
                                      ColorScaleRule(start_type='min', start_color='AA0000',
                                                     end_type = 'max', end_color = '00AA00'))

        # Remove excess columns
        del dataframe['country_id']
        raw_data_worksheet_name = 'Challenge 1 - Raw Data'
        dataframe = dataframe.rename(lambda x: x.replace('_', ' ').capitalize(), axis='columns')
        dataframe.to_excel(excel, raw_data_worksheet_name, index=False)
        raw_data_worksheet = excel.book[raw_data_worksheet_name]
        excel.save()


if __name__ == "__main__":
    filename = CONFIG_DIRECTORY + os.sep + 'challenge_1.xlsx'
    ChallengeOne(filename)
