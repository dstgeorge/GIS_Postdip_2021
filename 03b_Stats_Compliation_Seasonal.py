# --------------------------------------------
# Name: David St. George
# Date: 2021-05-13
# File Name: 03b_Stats_Compliation_Seasonal
# --------------------------------------------

'''
Complete statistical analysis on seasonal means independant of location
'''

import pandas as pd
import numpy as np
import sklearn
from scipy.stats import f_oneway
from scipy.stats import iqr
from scipy.stats import pearsonr
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
        ('CORR', 'ECMWF_OBSV_R'), ('CORR', 'ECMWF_NARR_R'),
        ('CORR', 'NARR_OBSV_R'), ('CORR', 'NARR_OBSV_P'),
        ('CORR', 'ECMWF_OBSV_P'), ('CORR', 'ECMWF_NARR_P'),
        ('ANOVA', 'ECMWF_OBSV_F'), ('ANOVA', 'ECMWF_OBSV_P'),
        ('ANOVA', 'ECMWF_NARR_F'), ('ANOVA', 'ECMWF_NARR_P'),
        ('ANOVA', 'NARR_OBSV_F'), ('ANOVA', 'NARR_OBSV_P')],
        names=['STAT', 'SRC'])


    stats = pd.DataFrame([], seasons.values(), columns=multi_index_col)

    # For Indexing Later
    idx = pd.IndexSlice

    # Cycle Through All Seasons
    for ssn in seasons.keys():

        # Filter for Overall
        if ssn != 13:
            ssn_means = comb_df[comb_df.index.month == ssn].copy()
        else:
            ssn_means = comb_df.copy()

        # Calculate number of data points (# of years with seasonal data)
        stats.at[seasons[ssn],  idx['n', 'n']] = \
            len(ssn_means.wind_spd)

        # Calculate Mean
        stats.at[seasons[ssn],  idx['MEAN', 'OBSV']] = \
            np.mean(ssn_means['wind_spd'])
        stats.at[seasons[ssn],  idx['MEAN', 'ECMWF']] = \
            np.mean(ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['MEAN', 'NARR']] = \
            np.mean(ssn_means['NARR_mean'])

        # Calculate Median
        stats.at[seasons[ssn],  idx['MEDIAN', 'OBSV']] \
            = np.median(ssn_means['wind_spd'])
        stats.at[seasons[ssn],  idx['MEDIAN', 'ECMWF']] = \
            np.median(ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['MEDIAN', 'NARR']] = \
            np.median(ssn_means['NARR_mean'])

        # Calculate Range
        stats.at[seasons[ssn],  idx['RANGE', 'OBSV']] = \
            np.ptp(ssn_means['wind_spd'])
        stats.at[seasons[ssn],  idx['RANGE', 'ECMWF']] = \
            np.ptp(ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['RANGE', 'NARR']] = \
            np.ptp(ssn_means['NARR_mean'])

        # Calculate # Outliers Using IQR Rule
        stats.at[seasons[ssn],  idx['# OUTLIERS', 'OBSV']]\
            = outlier_qty(ssn_means['wind_spd'])
        stats.at[seasons[ssn],  idx['# OUTLIERS', 'ECMWF']] \
            = outlier_qty(ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['# OUTLIERS', 'NARR']] \
            = outlier_qty(ssn_means['NARR_mean'])

        # Calculate MAD (Mean Absolute Deviation)
        stats.at[seasons[ssn],  idx['MAD', 'OBSV']] = \
            ssn_means['wind_spd'].mad()
        stats.at[seasons[ssn],  idx['MAD', 'ECMWF']] = \
            ssn_means['ECMWF_mean'].mad()
        stats.at[seasons[ssn],  idx['MAD', 'NARR']] = \
            ssn_means['NARR_mean'].mad()

        # Calculate MAE (Mean Absolute Error)
        mae = sklearn.metrics.mean_absolute_error(ssn_means['wind_spd'],
                                                  ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['MAE', 'ECMWF_OBSV']] \
            = mae

        mae = sklearn.metrics.mean_absolute_error(ssn_means['wind_spd'],
                                                  ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['MAE', 'NARR_OBSV']] \
            = mae

        # Calculate MSE (Mean Square Error) / RMSE (Root Mean Square Error)
        mse = sklearn.metrics.mean_squared_error(ssn_means['wind_spd'],
                                                 ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['RMSE', 'ECMWF_OBSV']]\
            = math.sqrt(mse)
        stats.at[seasons[ssn],  idx['MSE', 'ECMWF_OBSV']] = mse

        mse = sklearn.metrics.mean_squared_error(ssn_means['wind_spd'],
                                                 ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['RMSE', 'NARR_OBSV']] = \
            math.sqrt(mse)
        stats.at[seasons[ssn],  idx['MSE', 'NARR_OBSV']] = mse

        # Calculate Correlation
        corr = pearsonr(ssn_means['wind_spd'], ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['CORR', 'ECMWF_OBSV_R']] = corr[0]
        stats.at[seasons[ssn],  idx['CORR', 'ECMWF_OBSV_P']] = corr[1]

        corr = pearsonr(ssn_means['wind_spd'], ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['CORR', 'NARR_OBSV_R']] = corr[0]
        stats.at[seasons[ssn],  idx['CORR', 'NARR_OBSV_P']] = corr[1]

        corr = pearsonr(ssn_means['ECMWF_mean'], ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['CORR', 'ECMWF_NARR_R']] = corr[0]
        stats.at[seasons[ssn],  idx['CORR', 'ECMWF_NARR_P']] = corr[1]

        # Calculate ANOVA
        F, p = f_oneway(ssn_means['wind_spd'], ssn_means['ECMWF_mean'])
        stats.at[seasons[ssn],  idx['ANOVA', 'ECMWF_OBSV_F']] = F
        stats.at[seasons[ssn],  idx['ANOVA', 'ECMWF_OBSV_P']] = p

        F, p = f_oneway(ssn_means['wind_spd'], ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['ANOVA', 'NARR_OBSV_F']] = F
        stats.at[seasons[ssn],  idx['ANOVA', 'NARR_OBSV_P']] = p

        F, p = f_oneway(ssn_means['ECMWF_mean'], ssn_means['NARR_mean'])
        stats.at[seasons[ssn],  idx['ANOVA', 'ECMWF_NARR_F']] = F
        stats.at[seasons[ssn],  idx['ANOVA', 'ECMWF_NARR_P']] = p

    stats.to_csv("../Tabular/STATS_RESULTS/Seasonal_Analysis_Statistics"
                 ".csv")
    print('Seasonal Statistics Export Complete')

main()
