#!/usr/bin/env python3
__author__ = "Maxwell Goldbas"

import logging
import os
import xlsxwriter
from openpyxl import load_workbook
import pandas as pd


CONFIG_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
FINAL_OUTPUT = CONFIG_DIRECTORY + os.sep + 'SevenParkChallenge.xlsx'

# Setup logging system
LOGGING_FORMAT = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
LOGGING_HANDLERS = [
        logging.FileHandler("{0}.log".format(CONFIG_DIRECTORY + os.sep + "SevenPark")),
        logging.StreamHandler()
    ]

#        IMPORTANT         !!!
# Switch this to true or false based on whether or not you want detailed logs
debugging = True

if debugging:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.basicConfig(
    level=log_level,
    format=LOGGING_FORMAT,
    handlers=LOGGING_HANDLERS)


class Challenge(object):
    logger = logging.getLogger()

    def initialize_workbook(self, filename):
        self.logger.debug('Initializing notebook')
        excel = pd.ExcelWriter(filename, engine='openpyxl')
        if os.path.exists(filename):
            self.logger.info('Loading notebook from {}'.format(filename))
            book = load_workbook(filename)
            excel.book = book
        else:
            self.logger.debug('Did not load from {}'.format(filename))
        return excel