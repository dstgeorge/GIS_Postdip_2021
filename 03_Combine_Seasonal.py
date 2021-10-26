# --------------------------------------------
# Name: David St. George
# Date: 2021-06-08
# File Name: 03_Combine_Seasonal
# --------------------------------------------

'''
Using:
- CSV file with daily means of observations
- Seasonal mean netCDF files for both reanalysis datasets
created in 01_ECMWF_netCDF and 01_NARR_netCDF
Create:
A CSV file with all seasonal means for all AVAILABLE dates included
'''

import pandas as pd
import numpy as np
import xarray as xr
import pyproj

def create_ecmwf_df(lat, lon, loc):
    # Create dataframe from seasonal mean files
    ecmwf_ds = xr.open_mfdataset("../../ECMWF_DATA/SEASONAL/wnd_spd.10m.*.nc")
    print("Imported ECMWF Dataset Files Completed.")

    ecmwf_df = pd.DataFrame([])
    for i, j, l in zip(lat, lon, loc):
        loc_ds = ecmwf_ds.sel(latitude=i, longitude=j, method='nearest')
        temp_df = loc_ds.to_dataframe()
        temp_df['location'] = l
        ecmwf_df = ecmwf_df.append(temp_df, sort=True)
    ecmwf_df.rename(columns={'wnd_spd_mag': 'ECMWF_mean'}, inplace=True)
    return (ecmwf_df)

# Function creates dataframe of seasonal mean values with lat, lon, location
# from NARR reanalysis dataset
def create_narr_df(lat, lon, loc):
    # Create merged dataset from annual daily mean files
    narr_ds = xr.open_mfdataset("../../NARR_DATA/SEASONAL/wnd_spd.10m.*.nc")
    print("Imported NARR Dataset Files Completed.")

    # Define Projection Coordinate System for NARR Data
    Proj_narr = pyproj.Proj(
        "+proj=lcc +lon_0=-107 +lat_0=50 +lat_1=50 +lat_2=50 +x_0=5632642.22547 +y_0=4612545.65137 +units=m +ellps=WGS84")

    narr_df = pd.DataFrame([])
    for i, j, l in zip(lat, lon, loc):
        x_loc, y_loc = Proj_narr(j, i)
        loc_ds = narr_ds.sel(x=x_loc, y=y_loc, method='nearest')
        temp_df = loc_ds.to_dataframe()
        temp_df['location'] = l
        narr_df = narr_df.append(temp_df, sort=True)
    narr_df.rename(columns={'wnd_spd_mag': 'NARR_mean'}, inplace=True)

    return (narr_df)

def main():

    # Convert Observed Daily Means to Seasonal Means, Create Observation CSV
    obsv = pd.read_csv("../Tabular/daily_obsv_means.csv", index_col=0)
    obsv['DATE'] = pd.to_datetime(obsv['DATE'], format='%m/%d/%Y')
    obsv.rename(columns={'DATE': 'time'}, inplace=True)
    obsv_ssn_mean = obsv.groupby(['location']).resample('QS', label='left',
                                                        closed='left',
                                                        on='time').mean()
    obsv_ssn_mean = obsv_ssn_mean.dropna(subset=["wind_spd"])
    obsv_gby = obsv.groupby(['location']).mean()[['lat', 'lon']]
    for i,j in obsv_gby.iterrows():
        obsv_ssn_mean.at[i,'lat'] = j.lat
        obsv_ssn_mean.at[i,'lon'] = j.lon

    obsv_ssn_mean.to_csv("../Tabular/seasonal_obsv_means.csv")

    # Create ECMWF Seasonal Mean CSV
    # (Using Seasonal NetCDF Datafiles created earlier)
    ecmwf_df = create_ecmwf_df(obsv_gby.lat.values, obsv_gby.lon.values,
                               obsv_gby.index.values)

    narr_df = create_narr_df(obsv_gby.lat.values, obsv_gby.lon.values,
                             obsv_gby.index.values)

    merged = pd.merge(obsv_ssn_mean, narr_df, on=['time', 'location'])
    merged.rename(columns={'lat_x': 'lat', 'lon_x': 'lon'}, inplace=True)
    merged.drop(columns=['x', 'y', 'lat_y', 'lon_y'], inplace=True)

    merged = pd.merge(merged, ecmwf_df, on=['time', 'location'])
    merged.drop(columns=['year', 'month', 'day', 'latitude',
                         'longitude'],
                inplace=True)

    merged.to_csv("../Tabular/seasonal_mean_merged.csv")

    merged['season'] = np.where(
        pd.DatetimeIndex(merged.index).month == 1, 'Winter',
        np.where(pd.DatetimeIndex(merged.index).month == 4, 'Spring',
                 np.where(pd.DatetimeIndex(merged.index).month == 7,
                          'Summer',
                          np.where(pd.DatetimeIndex(merged.index).month
                                   == 10, 'Fall',
                                                               ""))))
    merged.to_csv("../Tabular/seasonal_mean_merged_anova.csv")

main()

