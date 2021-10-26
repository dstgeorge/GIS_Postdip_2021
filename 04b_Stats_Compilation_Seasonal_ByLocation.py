# --------------------------------------------
# Name: David St. George
# Date: 2021-05-13
# File Name: 04b_Stats_Compilation_Seasonal_ByLocation
# --------------------------------------------

'''
Generate statistics file on seasonal means by location
'''


import pandas as pd
import numpy as np
import sklearn
import scipy
from scipy.stats import f_oneway
from scipy.stats import iqr
from sklearn import metrics
import math



def outlier_qty(column):
    Q1, Q3 = np.percentile(column, [25, 75])
    IQR = iqr(column)
    lwr_bnd = Q1 - (1.5 * IQR)
    upr_bnd = Q3 + (1.5 * IQR)
    return len(column[(column < lwr_bnd) | (column > upr_bnd)])

def main():

    comb_df = pd.read_csv('../Tabular/seasonal_mean_merged.csv',
                           index_col=0)
    comb_df.index = pd.to_datetime(comb_df.index, format='%Y-%m-%d %H:%M')

    # Create dataframe with all performance metrics included
    seasons = {1: 'WINTER', 4: 'SPRING', 7: 'SUMMER', 10: 'FALL', 13: 'OVERALL'}

    # Introduce Stats Database
    gby = comb_df.groupby(['location']).mean()
    stats = gby[["lat", "lon"]]

    multi_idx = pd.MultiIndex.from_arrays(
        [stats.index.values.repeat(np.array(list(seasons.values())).size),
         stats.lat.values.repeat(np.array(list(seasons.values())).size),
         stats.lon.values.repeat(np.array(list(seasons.values())).size),
         np.tile(np.array(list(seasons.values())), stats.index.values.size)],
        names=['LOCATION', 'LAT', 'LON', 'SEASON'])

    multi_index_col = pd.MultiIndex.from_tuples([
        ('n', 'n'),
        ('MEAN', 'OBSV'), ('MEAN', 'ECMWF'), ('MEAN', 'NARR'),
        ('MEDIAN', 'OBSV'), ('MEDIAN', 'ECMWF'), ('MEDIAN', 'NARR'),
        ('RANGE', 'OBSV'), ('RANGE', 'ECMWF'), ('RANGE', 'NARR'),
        ('MAD', 'OBSV'), ('MAD', 'ECMWF'), ('MAD', 'NARR'),
        ('# OUTLIERS', 'OBSV'), ('# OUTLIERS', 'ECMWF'), ('# OUTLIERS', 'NARR'),
        ('MAE', 'ECMWF_OBSV'), ('MAE', 'NARR_OBSV'),
        ('RMSE', 'ECMWF_OBSV'), ('RMSE', 'NARR_OBSV'),
        ('MSE', 'ECMWF_OBSV'), ('MSE', 'NARR_OBSV'),
        ('CORR', 'ECMWF_OBSV_R'), ('CORR', 'ECMWF_OBSV_P'),
        ('CORR', 'ECMWF_NARR_R'), ('CORR', 'ECMWF_NARR_P'),
        ('CORR','NARR_OBSV_R'), ('CORR', 'NARR_OBSV_P'),
        ('ANOVA', 'ECMWF_OBSV_F'), ('ANOVA', 'ECMWF_OBSV_P'),
        ('ANOVA', 'ECMWF_NARR_F'), ('ANOVA', 'ECMWF_NARR_P'),
        ('ANOVA', 'NARR_OBSV_F'), ('ANOVA', 'NARR_OBSV_P')],
        names=['STAT', 'SRC'])


    stats = pd.DataFrame([], multi_idx, columns=multi_index_col)

    # For Indexing Later
    idx = pd.IndexSlice

    # Cycle Through All Seasons
    for ssn in seasons.keys():
        #print(seasons[ssn])
        # Filter for Overall
        if ssn != 13:
            ssn_means = comb_df[comb_df.index.month == ssn].copy()
        else:
            ssn_means = comb_df

        # Cycle Through All Locations
        for loc in comb_df.location.unique():
            #print(loc)
            loc_means = ssn_means[ssn_means.location == loc].copy()

            # Calculate number of data points (# of years with seasonal data)
            stats.at[idx[loc, :, :, seasons[ssn]], idx['n', 'n']] = \
                len(loc_means.wind_spd)

            # Calculate Mean
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEAN', 'OBSV']] = \
                np.mean(loc_means['wind_spd'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEAN', 'ECMWF']] = \
                np.mean(loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEAN', 'NARR']] = \
                np.mean(loc_means['NARR_mean'])

            # Calculate Median
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEDIAN', 'OBSV']] \
                = np.median(loc_means['wind_spd'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEDIAN', 'ECMWF']] = \
                np.median(loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MEDIAN', 'NARR']] = \
                np.median(loc_means['NARR_mean'])

            # Calculate Range
            stats.at[idx[loc, :, :, seasons[ssn]], idx['RANGE', 'OBSV']] = \
                np.ptp(loc_means['wind_spd'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['RANGE', 'ECMWF']] = \
                np.ptp(loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['RANGE', 'NARR']] = \
                np.ptp(loc_means['NARR_mean'])

            # Calculate # Outliers Using IQR Rule
            stats.at[idx[loc, :, :, seasons[ssn]], idx['# OUTLIERS', 'OBSV']]\
                = outlier_qty(loc_means['wind_spd'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['# OUTLIERS', 'ECMWF']] \
                = outlier_qty(loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['# OUTLIERS', 'NARR']] \
                = outlier_qty(loc_means['NARR_mean'])

            # Calculate MAD (Mean Absolute Deviation)
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MAD', 'OBSV']] = \
                loc_means['wind_spd'].mad()
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MAD', 'ECMWF']] = \
                loc_means['ECMWF_mean'].mad()
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MAD', 'NARR']] = \
                loc_means['NARR_mean'].mad()

            # Calculate MAE (Mean Absolute Error)
            mae = sklearn.metrics.mean_absolute_error(loc_means['wind_spd'],
                                                      loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MAE', 'ECMWF_OBSV']] \
                = mae

            mae = sklearn.metrics.mean_absolute_error(loc_means['wind_spd'],
                                                      loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MAE', 'NARR_OBSV']] \
                = mae

            # Calculate MSE (Mean Square Error) / RMSE (Root Mean Square Error)
            mse = sklearn.metrics.mean_squared_error(loc_means['wind_spd'],
                                                     loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['RMSE', 'ECMWF_OBSV']]\
                = math.sqrt(mse)
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MSE', 'ECMWF_OBSV']] = mse

            mse = sklearn.metrics.mean_squared_error(loc_means['wind_spd'],
                                                     loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['RMSE', 'NARR_OBSV']] = \
                math.sqrt(mse)
            stats.at[idx[loc, :, :, seasons[ssn]], idx['MSE', 'NARR_OBSV']] =\
                mse

            # Calculate Correlation
            corr = scipy.stats.pearsonr(loc_means['wind_spd'],
                                        loc_means['ECMWF_mean'])

            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR', 'ECMWF_OBSV_R']]\
                = corr[0]
            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR',
                                                       'ECMWF_OBSV_P']] \
                = corr[1]

            corr = scipy.stats.pearsonr(loc_means['wind_spd'],
                                        loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR', 'NARR_OBSV_R']]\
                = corr[0]
            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR', 'NARR_OBSV_P']] \
                = corr[1]

            corr = scipy.stats.pearsonr(loc_means['ECMWF_mean'],
                                        loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR', 'ECMWF_NARR_R']]\
                = corr[0]
            corr = scipy.stats.pearsonr(loc_means['ECMWF_mean'],
                                        loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['CORR',
                                                       'ECMWF_NARR_P']] \
                = corr[1]

            # Calculate ANOVA
            F, p = f_oneway(loc_means['wind_spd'], loc_means['ECMWF_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'ECMWF_OBSV_F']] = F
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'ECMWF_OBSV_P']] = p

            F, p = f_oneway(loc_means['wind_spd'], loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'NARR_OBSV_F']] = F
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'NARR_OBSV_P']] = p

            F, p = f_oneway(loc_means['ECMWF_mean'], loc_means['NARR_mean'])
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'ECMWF_NARR_F']] = F
            stats.at[idx[loc, :, :, seasons[ssn]], idx['ANOVA',
                                                       'ECMWF_NARR_P']] = p

    stats.to_csv("../Tabular/STATS_RESULTS/Seasonal_Analysis_Statistics_ByLoc"
                 ".csv")


main()
