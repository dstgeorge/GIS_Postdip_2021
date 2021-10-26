# --------------------------------------------
# Name: David St. George
# Date: 2021-05-15
# File Name: 02_Combine_Dailies
# --------------------------------------------

'''
Take daily means from each of the three datasets and create a CSV file
containing a date, location, lat, lon, and daily mean for each dataset.
ASSUMPTION: Reanalysis datasets have already been resampled for daily mean
and uwnd/vwnd combined for a magnitude vector (done in 01b_ECMWF_netCDF and
01b_NARR_netCDF scripts)
'''

import xarray as xr
import pandas as pd
import pyproj


# Function creates dataframe of daily mean values with lat, lon, location
# from ECMWF reanalysis dataset

def create_ecmwf_df(lat, lon, loc):
    # Create merged dataset from annual daily mean files
    ecmwf_ds = xr.open_mfdataset("../../ECMWF_DATA/wnd_spd.10m.*.nc")
    print("Imported ECMWF Dataset Files Completed.")

    ecmwf_df = pd.DataFrame([])
    for i, j, l in zip(lat, lon, loc):
        loc_ds = ecmwf_ds.sel(latitude=i, longitude=j, method='nearest')
        temp_df = loc_ds.to_dataframe()
        temp_df['location'] = l
        ecmwf_df = ecmwf_df.append(temp_df, sort=True)
    ecmwf_df.rename(columns={'wnd_spd_mag': 'ECMWF_mean'}, inplace=True)
    return (ecmwf_df)

# Function creates dataframe of daily mean values with lat, lon, location
# from NARR reanalysis dataset
def create_narr_df(lat, lon, loc):
    # Create merged dataset from annual daily mean files
    narr_ds = xr.open_mfdataset("../../NARR_DATA/wnd_spd.10m.*.nc")
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
    # Take daily mean observation data
    obsv = pd.read_csv("../Tabular/daily_obsv_means.csv", index_col=0)
    obsv['DATE'] = pd.to_datetime(obsv['DATE'], format='%m/%d/%Y')
    obsv.rename(columns={'DATE': 'time'}, inplace=True)
    obsv_gby = obsv.groupby(['location']).mean()
    obsv_gby = obsv_gby[['lat', 'lon', 'wind_spd']]

    ecmwf_df = create_ecmwf_df(obsv_gby.lat.values, obsv_gby.lon.values,
                               obsv_gby.index.values)

    narr_df = create_narr_df(obsv_gby.lat.values, obsv_gby.lon.values,
                             obsv_gby.index.values)

    # Merge observation values df and ECMWF dataframe.
    # Note: Through this method only dates where observations are made are kept
    # Add argument 'how: outer' if all records to be kept
    obsv_ecmwf_df = pd.merge(obsv, ecmwf_df, on=['time', 'location'])
    obsv_ecmwf_df.set_index('location', inplace=True)
    obsv_ecmwf_df.drop(columns=['year', 'month', 'day', 'latitude',
                                'longitude'],
                       inplace=True)

    # Merge NARR dataframe and ECMWF & Observation dataframe
    narr_obsv_ecmwf_df = pd.merge(obsv_ecmwf_df, narr_df, on=['time',
                                                              'location'])
    narr_obsv_ecmwf_df.rename(columns={'lat_x': 'lat', 'lon_x': 'lon'},
                              inplace=True)
    narr_obsv_ecmwf_df.set_index('location', inplace=True)
    narr_obsv_ecmwf_df.drop(columns=['x', 'y', 'lat_y', 'lon_y'], inplace=True)

    # Reorder Columns
    narr_obsv_ecmwf_df = narr_obsv_ecmwf_df[['time', 'lat', 'lon', 'wind_spd',
                                            'ECMWF_mean', 'NARR_mean']]
    narr_obsv_ecmwf_df.to_csv("../Tabular/daily_means_alldatasets.csv")
    print("CSV File Exported!")

main()
