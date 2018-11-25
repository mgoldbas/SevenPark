#!/usr/bin/env python3
__author__ = "Maxwell Goldbas"

from challenge_1.challenge_1 import ChallengeOne
from challenge_2.challenge_2 import ChallengeTwo
from utils import FINAL_OUTPUT
import os

"""
This is the submission by Maxwell Goldbas to the SevenPark data challenge

Change the debugging configuration in the utils script to enable 
DEBUG level logging

Logging will appear in "SevenPark.log" based on the debugging parameter

Final Results for all data will be sent to "SevenParkChallenge.xlsx" as an Excel workbook

Note: the 'use_cache' parameter can be used for testing to hold 
the API data locally as a csv file, and be reloaded as required
"""

def main():
    if os.path.exists(FINAL_OUTPUT):
        os.remove(FINAL_OUTPUT)
    ChallengeOne(FINAL_OUTPUT)
    ChallengeTwo(FINAL_OUTPUT)


if __name__ == "__main__":
    main()
