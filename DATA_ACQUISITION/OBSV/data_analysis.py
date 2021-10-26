# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 21:18:52 2021

@author: stg

File intended to read data from all weather stations and manipulate 
"""

import pandas as pd
import numpy as np

# Remove Unnecessary Columns from Data, Add Column for Station Names Which May Have Changed Over Time
def observation_cleaning():
    
    all_stations = pd.read_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings.csv", index_col=0)
    
    all_stations['time'] = pd.to_datetime(all_stations['time'], 
                                          format='%Y-%m-%d %H:%M')
    
    remove_vars = ["weather",
                   "hmdx",
                   "hmdx_flag",
                   "precip_amt",
                   "precip_amt_flag",
                   "pressure",
                   "pressure_flag",
                   "rel_hum",
                   "rel_hum_flag",
                   "temp",
                   "temp_flag",
                   "temp_dew",
                   "temp_dew_flag",
                   "visib",
                   "visib_flag",
                   "wind_chill",
                   "wind_chill_flag"]
    
    all_stations.drop(columns = remove_vars, axis=1, inplace=True)
    
    all_stations.loc[(all_stations.station_name == "ST JOHN'S A"),
                     'station_name'] = "ST. JOHN'S A"
    
    all_stations.loc[(all_stations.station_name.isin(["BURGEO 2",
                                                      "BURGEO NL"])),
                     'station_name'] = "BURGEO"
    
    all_stations['location'] = all_stations['station_name'].str[:7]
    print(all_stations.station_name.unique())
    all_stations.to_csv('../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv')

#observation_cleaning()

# Function to remove weather station nulls which may exist on ends of dataset
def clean_tail_end_nulls():
    data = pd.read_csv('../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv', index_col=0)
    
    with open("../../../Arena/RAW_DATA/EC_DATA/station_start_end_dates.csv", "r") as in_file:
        counter = 0
        for line in in_file:
            line = line.rstrip('\n')
            lineList = line.split(',')
            if counter != 0:            
                print(lineList)
                if int(lineList[1]) > 1984:
                    data.drop(data[(data['station_id'] == int(lineList[0])) &
                                   (data.year.isin(range(1984,
                                                         int(lineList[1]))))].index,
                              inplace=True)       
                # If station data stops before 2013, remove all nulls after            
                if int(lineList[2]) < 2013:
                    data.drop(data[(data['station_id'] == int(lineList[0])) & 
                                   (data.year.isin(range(int(lineList[2])+1,
                                                         2014)))].index,
                                  inplace=True)
             
            counter += 1
    data.to_csv('../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv')                 
#clean_tail_end_nulls()

# Function to find % of nulls in dataset
def non_null_report():
    
    data = pd.read_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv", index_col = 0)
    #non_nulls = data.wind_spd.groupby([data['location'],
    #                                   data['year'],
    #                                   data['month'],
    #                                   data['station_id']]).agg('count').to_frame()
    #non_nulls.to_csv("non_null_hourly_summary.csv")

    # Dataframe of a table with non-null values summed by location    
    non_nulls_by_loc = data.wind_spd.groupby([data['location']]).agg('count').to_frame()
    non_nulls_by_loc.rename(columns={'wind_spd': 'non_null_cnt'},
                            inplace=True)  
    
    non_nulls_by_loc = non_nulls_by_loc.join(
        (data.wind_spd.isnull().groupby(data['location']).sum()))

    non_nulls_by_loc.rename(columns={'wind_spd': 'null_cnt'},
                            inplace=True)                 
    
    non_nulls_by_loc['%_non_null'] = (non_nulls_by_loc['non_null_cnt']
                                      /(non_nulls_by_loc['null_cnt']+
                                        non_nulls_by_loc['non_null_cnt']))*100
    
    non_nulls_by_loc = non_nulls_by_loc.round(2) 
    
    print(non_nulls_by_loc)
    
non_null_report()

def drop_duplicate_records():
    data = pd.read_csv('../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv', index_col=0)
    # sort values to get non-nulls on top
    data.sort_values(by=['time','location','wind_spd'], inplace=True)
    data.drop_duplicates(subset=['time','location'], inplace=True)
    data.sort_values(by=['location','time'], inplace=True)
    data.to_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv")

#drop_duplicate_records()


def location_holes_analysis():
    all_stations = pd.read_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv", index_col=0)
    print(np.sort(all_stations.station_id.unique()))
    print(len(np.sort(all_stations.station_id.unique())))
    print(all_stations.shape)
    print(all_stations.location.unique(), len(all_stations.location.unique()))
    
    # Do a count by year to analyze missed values:
    years = all_stations.year.unique()
    stations = all_stations.station_id.unique()
    with open("../../../Arena/RAW_DATA/EC_DATA/station_report.txt","w") as out_file:
        for station in stations:
            out_file.write("----"+"\n")
            out_file.write(f'{station} + "\n"')
            for year in years:
                temp = all_stations[(all_stations.station_id == station) &
                                    (all_stations.year == year)]
                out_file.write(str(year) + "," + str(temp.wind_spd.count())
                                + "," + str(round((temp.wind_spd.count()/(365*24))*100))
                              + "\n")
    
    print(all_stations.wind_spd.notnull().groupby(all_stations['location']).sum())
location_holes_analysis()

# Evaluate a location based on monthly or seasonal averages
def hourly_seasonal_averages():
    all_stations = pd.read_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv", index_col=0)
    
    all_stations_mean = all_stations.groupby(['location', 'month'],
                                             as_index=False)['wind_spd'].mean()
    print(all_stations_mean)
#hourly_seasonal_averages()

# Script to take daily mean of each location and input into ArcMap for Processing
def produce_daily_mean_csv():
    data = pd.read_csv("../../../Arena/RAW_DATA/EC_DATA/all_readings_cleaned.csv", 
                       index_col = 0, dtype={'climate_id': str, 'TC_id':str,
                                             'wind_dir_flag': str, 
                                             'wind_spd_flag': str})
    data['time'] = pd.to_datetime(data['time'], format='%Y-%m-%d %H:%M')
    data.set_index('time',inplace=True)
    data_grby_day = data.groupby([data.location, 
                                  data.index.year, 
                                  data.index.month, 
                                  data.index.day]).mean()
    data_grby_day = data_grby_day[['lat', 'lon', 'wind_spd']]
    data_grby_day.index.names = (['location','year','month','day'])
    data_grby_day.reset_index(inplace=True)
    data_grby_day['DATE'] = data_grby_day['month'].map(str).str.zfill(2) + '/' + data_grby_day['day'].map(str).str.zfill(2) + '/' + data_grby_day['year'].map(str)    
    data_grby_day.dropna(subset=['wind_spd'], inplace=True)
    data_grby_day.set_index("location", inplace=True)
    print(data_grby_day)
    data_grby_day.to_csv("../../../Tabular/daily_means.csv")
    
    
#produce_daily_mean_csv()