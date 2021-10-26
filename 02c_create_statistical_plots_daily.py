# --------------------------------------------
# Name: David St. George
# Date: 2021-05-26
# File Name: 02c_create_statistical_plots_daily
# --------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''
Using daily means statistics - create plots to compare accuracy of dataset 
metrics
'''

def main():

    daily_data = pd.read_csv(
        "../Tabular/STATS_RESULTS/Daily_Analysis_Statistics.csv",
        index_col=0)

    # Create three unique plots for MAE, RMSE, and MSE
    stats = ['MAE', 'RMSE', 'MSE']
    src = ['ECMWF_OBSV', 'NARR_OBSV']
    src_corr = ['ECMWF_OBSV', 'NARR_OBSV', 'ECMWF_NARR']
    daily_data2 = daily_data[stats].dropna()
    ind = np.arange(len(src)) / 6
    width = 0.05
    # Compare MAE, RMSE, MSE
    for stat in stats:
        fig, ax = plt.subplots(figsize=(9, 4))
        plt.grid(alpha=0.3)
        rect = ax.barh(ind, daily_data2[stat], width,
                       color=['#00429d', '#93003a'], edgecolor='black')
        ax.bar_label(rect, fmt='%.2f')
        ax.set_title(f'Daily Mean {stat} ')
        ax.set_yticks(ind)
        ax.set_yticklabels(src)
        plt.savefig(f'../Plots/DAILY_WHOLE/{stat}.png',
                    facecolor='white')
        #plt.show()

    # Compare Correlation
    fig, ax = plt.subplots(figsize=(9, 4))
    plt.grid(alpha=0.3)
    ind = np.arange(len(src_corr)) / 6
    daily_data2 = daily_data[['CORR']].dropna()
    daily_data2.drop(['ECMWF_OBSV_P', 'NARR_OBSV_P', 'ECMWF_NARR_P'],
                     inplace=True)
    daily_data2.rename(index={'ECMWF_OBSV_R':'ERA5', 'NARR_OBSV_R':'NARR',
                              'ECMWF_NARR_R':'ERA5-NARR'},
                       inplace=True)
    rect = ax.barh(ind, daily_data2['CORR'], width,
                   color=['#00429d', '#93003a', 'darkgoldenrod'],
                   edgecolor='black')
    ax.bar_label(rect, fmt='%.2f')
    ax.set_title('Daily Mean - CORRELATION')
    ax.set_yticks(ind)
    ax.set_yticklabels(src_corr)
    plt.savefig('../Plots/DAILY_WHOLE/correlation.png',
                facecolor='white')
    #plt.show()

main()