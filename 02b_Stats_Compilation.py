# --------------------------------------------
# Name: David St. George
# Date: 2021-05-13
# File Name: 02b_Stats_Compilation
# --------------------------------------------

'''
By taking daily means, compute various statistics
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

    comb_df = pd.read_csv("../Tabular/daily_means_alldatasets.csv", index_col=0)
    
    # Introduce Stats Database

    stats = pd.DataFrame([], ["OBSV", "ECMWF", "NARR",
                              "ECMWF_OBSV", "NARR_OBSV",
                              "ECMWF_NARR",
                              'ECMWF_OBSV_R', 'NARR_OBSV_R', 'ECMWF_NARR_R',
                              'ECMWF_OBSV_F', 'ECMWF_OBSV_P',
                              'NARR_OBSV_F', 'NARR_OBSV_P',
                              'ECMWF_NARR_F', 'ECMWF_NARR_P'],
                         columns=['n', 'MEAN', 'MEDIAN', 'RANGE', 'MAD',
                                  '# OUTLIERS', 'MAE', 'RMSE', 'MSE', 'CORR',
                                  'ANOVA'])

    # Calculate number of data points
    stats.at["OBSV", 'n'] = len(comb_df.wind_spd)
    stats.at["ECMWF", 'n'] = len(comb_df.ECMWF_mean)
    stats.at["NARR", 'n'] = len(comb_df.NARR_mean)

    # Calculate Mean
    stats.at["OBSV", 'MEAN'] = np.mean(comb_df['wind_spd'])
    stats.at["NARR", 'MEAN'] = np.mean(comb_df['ECMWF_mean'])
    stats.at["ECMWF", 'MEAN'] = np.mean(comb_df['NARR_mean'])

    # Calculate Median
    stats.at["OBSV", 'MEDIAN'] = np.median(comb_df['wind_spd'])
    stats.at["NARR", 'MEDIAN'] = np.median(comb_df['ECMWF_mean'])
    stats.at["ECMWF", 'MEDIAN'] = np.median(comb_df['NARR_mean'])

    # Calculate Range
    stats.at["OBSV", 'RANGE'] = np.ptp(comb_df['wind_spd'])
    stats.at["NARR", 'RANGE'] = np.ptp(comb_df['ECMWF_mean'])
    stats.at["ECMWF", 'RANGE'] = np.ptp(comb_df['NARR_mean'])

    # Calculate # Outliers Using IQR Rule
    stats.at["OBSV", '# OUTLIERS'] = outlier_qty(comb_df['wind_spd'])
    stats.at["NARR", '# OUTLIERS'] = outlier_qty(comb_df['ECMWF_mean'])
    stats.at["ECMWF", '# OUTLIERS'] = outlier_qty(comb_df['NARR_mean'])

    # Calculate MAD (Mean Absolute Deviation)
    stats.at["OBSV", 'MAD'] = comb_df['wind_spd'].mad()
    stats.at["NARR", 'MAD'] = comb_df['ECMWF_mean'].mad()
    stats.at["ECMWF", 'MAD'] = comb_df['NARR_mean'].mad()

    # Calculate MAE (Mean Absolute Error)
    mae = sklearn.metrics.mean_absolute_error(comb_df['wind_spd'],
                                              comb_df['ECMWF_mean'])
    stats.at["ECMWF_OBSV", 'MAE'] = mae

    mae = sklearn.metrics.mean_absolute_error(comb_df['wind_spd'],
                                              comb_df['NARR_mean'])
    stats.at['NARR_OBSV', 'MAE'] = mae

    # Calculate MSE (Mean Square Error) / RMSE (Root Mean Square Error)
    mse = sklearn.metrics.mean_squared_error(comb_df['wind_spd'],
                                             comb_df['ECMWF_mean'])
    stats.at['ECMWF_OBSV', 'RMSE'] = math.sqrt(mse)
    stats.at['ECMWF_OBSV', 'MSE'] = mse

    mse = sklearn.metrics.mean_squared_error(comb_df['wind_spd'],
                                             comb_df['NARR_mean'])
    stats.at['NARR_OBSV', 'RMSE'] = math.sqrt(mse)
    stats.at['NARR_OBSV', 'MSE'] = mse

    # Calculate Correlation
    # Compare ECMWF and OBSV
    corr = pearsonr(comb_df['wind_spd'], comb_df['ECMWF_mean'])

    stats.at['ECMWF_OBSV_R', 'CORR'] = corr[0]
    stats.at['ECMWF_OBSV_P', 'CORR'] = corr[1]

    # Compare NARR and OBSV
    corr = pearsonr(comb_df['wind_spd'], comb_df['NARR_mean'])

    stats.at['NARR_OBSV_R', 'CORR'] = corr[0]
    stats.at['NARR_OBSV_P', 'CORR'] = corr[1]

    # Compare ECMWF and NARR
    corr = pearsonr(comb_df['ECMWF_mean'], comb_df['NARR_mean'])

    stats.at['ECMWF_NARR_R', 'CORR'] = corr[0]
    stats.at['ECMWF_NARR_P', 'CORR'] = corr[1]

    # Calculate ANOVA
    F, p = f_oneway(comb_df['wind_spd'], comb_df['ECMWF_mean'])
    stats.at['ECMWF_OBSV_F', 'ANOVA'] = F
    stats.at['ECMWF_OBSV_P', 'ANOVA'] = p

    F, p = f_oneway(comb_df['wind_spd'], comb_df['NARR_mean'])
    stats.at['NARR_OBSV_F', 'ANOVA'] = F
    stats.at['NARR_OBSV_P', 'ANOVA'] = p

    F, p = f_oneway(comb_df['ECMWF_mean'], comb_df['NARR_mean'])
    stats.at['ECMWF_NARR_F', 'ANOVA'] = F
    stats.at['ECMWF_NARR_P', 'ANOVA'] = p

    print("Statistical Analysis Completed!")
    stats.to_csv("../Tabular/STATS_RESULTS/Daily_Analysis_Statistics.csv")

main()
