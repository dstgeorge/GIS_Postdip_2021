# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 08:20:21 2021

@author: stg
"""

import wget

# Script to downloading direct from NARR website

def main():

    years = list(range(1984, 2014))
    variables = ["vwnd", "uwnd"]

    for year in years:
        for variable in variables:
            url = f"ftp://ftp.cdc.noaa.gov/Datasets/NARR/monolevel/{variable}.10m.{year}.nc"
            url = f"https://downloads.psl.noaa.gov/Datasets/NARR/Dailies/monolevel/{variable}.10m.{year}.nc"
            wget.download(url, "C:\Data\GS2310\CAPSTONE\GS3210_StGeorge\Arena\RAW_DATA\NARR")

main()