# --------------------------------------------
# Name: David St. George
# Date: 2021-05-19
# File Name: 05_extremes_analysis
# --------------------------------------------
'''
Creates csv file comparing OBSERVED, NARR, and ECMWF datasets for
sum/mean/median/max # of days per month that a DAILY mean wind speed is above a
'threshold value' (39km/hr - 'strong breeze', 50 - 'near gale', and 62 -
'gale') as classified in the Beaufort Wind Scale Table outlined by
Environment Canada.
As observations were not available at all stations for all 10958 days (365d x
30yrs + 8 leap yrs) in dataset, SUM values should be taken with caution.
'''

import pandas as pd
import numpy as np
import xarray as xr
import pyproj


# Function Creates empty df with MultiIndex of rows and columns

def create_extremes_df(base_df):
    months = list(range(1, 13))
    threshold_vals = [39, 50, 62]
    metrics = ['SUM', 'MEAN', 'MEDIAN', 'MAX']
    vals = ['OBSERVED', 'ECMWF', 'NARR']

    # Create Extremes MultiIndex

    multi_row_idx = pd.MultiIndex.from_arrays(
        [base_df.index.values.repeat(np.array(months).size),
         base_df.lat.values.repeat(np.array(months).size),
         base_df.lon.values.repeat(np.array(months).size),
         np.tile(np.array(months), base_df.index.values.size)],
        names=['LOCATION', 'LAT', 'LON', 'MONTH'])

    multi_col_idx = pd.MultiIndex.from_product(
        [threshold_vals, metrics, vals],
        names=['THRESHOLD VALUE', 'METRIC', 'SOURCE'])

    df = pd.DataFrame([], multi_row_idx, columns=multi_col_idx)

    return (df)


# Takes pandas series of counts (360 months for each row and sum of times
# threshold has been eclipsed) and computes SUM, MEAN, MAX, and MEDIAN across
# 30-year period for each calendar month

def threshold_stats(thres_count, data, source, thres_val, loc):
    idx = pd.IndexSlice
    thres_sum = thres_count.groupby(thres_count.index.month).sum()
    for i, val in enumerate(thres_sum):
        data.at[idx[loc, :, :, i + 1], idx[thres_val, 'SUM',
                                           source]] = val

    # Group by calendar month (Jan, Feb, Mar, etc.) MEAN number of days
    # above threshold
    thres_mean = thres_count.groupby(thres_count.index.month).mean()
    for i, val in enumerate(thres_mean):
        data.at[idx[loc, :, :, i + 1], idx[
            thres_val, 'MEAN', source]] = val

    # Group by calendar month (Jan, Feb, Mar, etc.) MEDIAN number of
    # days above threshold
    thres_median = thres_count.groupby(
        thres_count.index.month).median()
    for i, val in enumerate(thres_median):
        data.at[idx[loc, :, :, i + 1], idx[
            thres_val, 'MEDIAN', f'{source}']] = val

    # Group by calendar month (Jan, Feb, Mar, etc.) MAX number of days above
    # threshold in a year
    thres_max = thres_count.groupby(
            thres_count.index.month).max()
    for i, val in enumerate(thres_max):
        data.at[idx[loc, :, :, i + 1], idx[
            thres_val, 'MAX', f'{source}']] = val

    return(data)


def main():
    # Create obsv dataframe with station locations and data

    obsv = pd.read_csv("../Tabular/daily_obsv_means.csv",
                       index_col=0)

    obsv['DATE'] = pd.to_datetime(obsv['DATE'], format='%m/%d/%Y')

    # base dataframe that stats will be made up of location, lat, lon
    base_df = obsv.groupby(['location']).mean()[["lat", "lon"]]

    # Enter to function to create proper multi-indexed df
    data = create_extremes_df(base_df)

    # Analyze Observed Daily Means for Extremes

    idx = pd.IndexSlice

    thres_list = [39, 50, 62]
    for thres_val in thres_list:
        for loc in obsv.index.unique():

            obsv_loc = obsv.filter(like=loc, axis=0).copy()
            obsv_loc.set_index('DATE', inplace=True)

            # Create bool mask
            obsv_loc['wnd_spd_thres_bool'] = obsv_loc['wind_spd'] >= thres_val
            obsv_loc['wnd_spd_thres_bool'] = obsv_loc[
                'wnd_spd_thres_bool'].astype(int)

            # Create count of number of days greater than threshold value for
            # each month of 30 year cycle (360 months)
            thres_count = obsv_loc.groupby([pd.Grouper(freq='MS',
                                                       label='left')])[
                'wnd_spd_thres_bool'].sum()

            data = threshold_stats(thres_count, data, 'OBSERVED', thres_val,
                                   loc)


    # Analyze ECMWF Daily Means for Extremes

    # Extracts all annual netCDF4 data files into single ecmwf_ds file
    # Note: these files are not the raw data available direct from ECMWF,
    # but modified to calculate wind speed magnitude (combination of
    # u and v vectors) and resampled for daily mean

    ecmwf_ds = xr.open_mfdataset("../../ECMWF_DATA/wnd_spd.10m.*.nc")

    # Cycle through all locations
    for i, j in base_df.iterrows():
        loc_ds = ecmwf_ds.sel(latitude=j.lat, longitude=j.lon,
                              method='nearest')
        loc_df = loc_ds.to_dataframe()

        for thres_val in thres_list:

            # Resample - count number of days per month above threshold
            # Create bool mask
            loc_df['wnd_spd_thres_bool'] = loc_df['wnd_spd_mag'] >= thres_val
            loc_df['wnd_spd_thres_bool'] = loc_df[
                'wnd_spd_thres_bool'].astype(int)

            # Create count of number of days greater than threshold value for
            # each month of 30 year cycle (360 months)
            thres_count = loc_df.groupby([pd.Grouper(freq='MS',
                                                       label='left')])[
                'wnd_spd_thres_bool'].sum()

            data = threshold_stats(thres_count, data, 'ECMWF', thres_val, i)


    # Analyze NARR Daily Means for Extremes

    # Extracts all annual netCDF4 data files into single ecmwf_ds file
    # Note: these files are not the raw data available direct from NOAA,
    # but modified to calculate wind speed magnitude (combination of
    # u and v vectors) and resampled for daily mean

    narr_ds = xr.open_mfdataset("../../NARR_DATA/wnd_spd.10m.*.nc")

    # Introduce Projection for NARR Dataset (supplied in North American Lambert
    # Conformal Conic - non-standard EPSG)

    proj_narr = pyproj.Proj("+proj=lcc  +lon_0=-107 +lat_0=50 +lat_1=50 "
                            "+lat_2=50 "
                            "+x_0=5632642.22547 +y_0=4612542.65137 +units=m "
                            "+ellps=WGS84")

    # Cycle through all locations
    for i, j in base_df.iterrows():
        x_loc, y_loc = proj_narr(j.lon, j.lat)

        loc_ds = narr_ds.sel(x=x_loc, y=y_loc, method="nearest")

        loc_df = loc_ds.to_dataframe()

        for thres_val in thres_list:
            # Resample - count number of days per month above threshold
            # Create bool mask
            loc_df['wnd_spd_thres_bool'] = loc_df['wnd_spd_mag'] >= thres_val
            loc_df['wnd_spd_thres_bool'] = loc_df[
                'wnd_spd_thres_bool'].astype(int)

            # Create count of number of days greater than threshold value for
            # each month of 30 year cycle (360 months)
            thres_count = loc_df.groupby([pd.Grouper(freq='MS',
                                                     label='left')])[
                'wnd_spd_thres_bool'].sum()

            data = threshold_stats(thres_count, data, 'NARR', thres_val, i)

    print("Data exported to CSV")
    data.to_csv("../Tabular/extremes_analysis.csv")


main()
