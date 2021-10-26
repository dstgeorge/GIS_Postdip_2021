# --------------------------------------------
# Name: David St. George
# Date: 2021-05-23
# File Name: 03c_Create_Statistical_Plots_Seasonal
# --------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
'''
Using both seasonal analysis (no loc) CSV created
previously, this script creates bar # graphs representing
the various statistics enclosed
'''

def seasonal_analysis():
    '''
    Seasonal Analysis
    '''

    ssn_data = pd.read_csv(
        "../Tabular/STATS_RESULTS/Seasonal_Analysis_Statistics.csv",
        index_col=0, header=[0, 1],
        skipinitialspace=True)

    # MEAN, MEDIAN, RANGE, MEAN ABSOLUTE DEVIATION LOOP
    for stat in ssn_data.columns.get_level_values(0).unique()[1:5]:
        width = 0.05
    fig, ax = plt.subplots(1, 5, figsize=(30, 6))
    plt.subplots_adjust(wspace=0.25)
    for num, ssn in enumerate(ssn_data.index.values):
        means_df = ssn_data.loc[[ssn]].xs(f'{stat}', axis=1)
        means_df = means_df.T
        ind = np.arange(len(means_df.index)) / 6
        rect = ax[num].barh(ind, means_df[ssn], width,
                            color=['#00429d', '#93003a', 'darkgoldenrod'],
                            edgecolor='black')

        ax[num].bar_label(rect, fmt='%.2f')
        ax[num].set_yticks(ind)
        ax[num].set_yticklabels(means_df.index)
        ax[num].set_xlabel('Wind Speed (km/hr)')
        ax[0].set_ylabel('Dataset')

        ax[num].set_title(f'Seasonal {stat} Wind Speed (for {ssn})')

    plt.savefig(f'../Plots/SEASON_WHOLE/{stat}.png', facecolor='white')
    #plt.show()

    # MEAN ABSOLUTE ERROR, MEAN SQUARE ERROR, ROOT MEAN SQUARE ERROR LOOP
    for stat in ssn_data.columns.get_level_values(0).unique()[6:9]:
        for ssn in ssn_data.index.values:
            means_df = ssn_data.loc[[ssn]].xs(f'{stat}', axis=1)
            means_df = means_df.T
            width = 0.05
            fig, ax = plt.subplots(figsize=(9, 4))
            plt.grid(alpha=0.3)
            ind = np.arange(len(means_df.index)) / 6

            rect = ax.barh(ind, means_df[ssn], width, color=['#00429d',
                                                             '#93003a'],
                           edgecolor='black')

            ax.bar_label(rect, fmt='%.2f')
            ax.set_title(f'{stat} Seasonal Mean ({ssn})')
            ax.set_yticks(ind)
            ax.set_yticklabels(means_df.index)
            # plt.show()
            plt.savefig(f'../Plots/SEASON_WHOLE/{stat}_{ssn}.png',
                        facecolor='white')

    # CORRELATION
    for stat in ssn_data.columns.get_level_values(0).unique()[9:10]:
        for ssn in ssn_data.index.values:
            means_df = ssn_data.loc[[ssn]].xs(f'{stat}', axis=1)
            means_df = means_df.T
            means_df.drop(['ECMWF_OBSV_P', 'NARR_OBSV_P', 'ECMWF_NARR_P'],
                          inplace=True)
            width = 0.05
            fig, ax = plt.subplots(figsize=(9, 4))
            plt.grid(alpha=0.3)
            ind = np.arange(len(means_df.index)) / 6

            rect = ax.barh(ind, means_df[ssn], width,
                           color=['#00429d', 'darkgoldenrod', '#93003a'],
                           edgecolor='black')

            ax.bar_label(rect, fmt='%.2f')

            ax.set_title(f'{stat} Seasonal ({ssn})')
            ax.set_yticks(ind)
            ax.set_yticklabels(means_df.index)
            # plt.show()
            plt.savefig(f'../Plots/SEASON_WHOLE/{stat}_{ssn}.png',
                        facecolor='white')


def main():
    seasonal_analysis()


main()
