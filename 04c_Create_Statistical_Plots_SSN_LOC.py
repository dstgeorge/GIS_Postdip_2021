# --------------------------------------------
# Name: David St. George
# Date: 2021-05-23
# File Name: 04c_Create_Statistical_Plots_SSN_LOC
# --------------------------------------------
'''
(For seasonal means by location)
Using both statistics CSVs (seasonal analysis and extremes analysis) created
previously, this script creates bar # graphs representing
the various statistics enclosed
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def seasonal_analysis():
    '''
    Seasonal Analysis
    '''

    ssn_data = pd.read_csv("../Tabular/Combined_Season_Analysis_Final.csv",
                           index_col=[0, 1, 2, 3], header=[0, 1],
                           skipinitialspace=True)


    # MEAN, MEDIAN, RANGE, MEAN ABSOLUTE DEVIATION LOOP
    for stat in ssn_data.columns.get_level_values(0).unique()[1:5]:
        for ssn in ssn_data.index.get_level_values(3).unique():
            means_df = ssn_data.xs(ssn, level=3).xs(f'{stat}', axis=1)
            means_df.index = means_df.index.get_level_values(0)
            width = 0.20
            fig, ax = plt.subplots(figsize=(40, 10))
            ind = np.arange(len(means_df.index))

            rect_obsv = ax.bar(ind - width, means_df.OBSV, width, label='OBSV')
            rect_narr = ax.bar(ind, means_df.NARR, width, label='NARR',
                               color='darksalmon')
            rect_ecmwf = ax.bar(ind + width, means_df.ECMWF, width,
                                label='ECMWF', color='brown')

            ax.bar_label(rect_obsv, fmt='%.2f')
            ax.bar_label(rect_narr, fmt='%.2f')
            ax.bar_label(rect_ecmwf, fmt='%.2f')

            ax.set_xticks(ind)
            ax.set_xticklabels(means_df.index)
            ax.legend(fontsize=20)

            ax.set_ylabel('Wind Speed (km/hr)')
            ax.set_xlabel('Location')
            ax.set_title(f'{stat} Daily Wind Speed (for {ssn})')

            ax.grid()
            plt.tight_layout()
            plt.savefig(f'../Plots/Season_Loc/PLOTS/{stat}_{ssn}.png',
                        facecolor='white')
            #plt.show()

    # MEAN ABSOLUTE ERROR, MEAN SQUARE ERROR, ROOT MEAN SQUARE ERROR LOOP
    for stat in ssn_data.columns.get_level_values(0).unique()[6:9]:
        for ssn in ssn_data.index.get_level_values(3).unique():
            means_df = ssn_data.xs(ssn, level=3).xs(f'{stat}', axis=1)
            means_df.index = means_df.index.get_level_values(0)
            width = 0.20
            fig, ax = plt.subplots(figsize=(40, 10))
            ind = np.arange(len(means_df.index))

            rect_narr = ax.bar(ind, means_df.NARR_OBSV, width,
                               label='NARR_OBSV', color='darksalmon')
            rect_ecmwf = ax.bar(ind + width, means_df.ECMWF_OBSV, width,
                                label='ECMWF_OBSV', color='brown')

            ax.bar_label(rect_narr, fmt='%.2f')
            ax.bar_label(rect_ecmwf, fmt='%.2f')

            ax.set_xticks(ind)
            ax.set_xticklabels(means_df.index)
            ax.legend(fontsize=20)

            ax.set_ylabel('Wind Speed (km/hr)')
            ax.set_xlabel('Location')
            ax.set_title(f'{stat} (for {ssn})')

            ax.grid()
            plt.tight_layout()
            plt.savefig(f'../Plots/SEASON_LOC/PLOTS/{stat}_{ssn}.png',
                        facecolor='white')
            #plt.show()

    # CORRELATION
    for stat in ssn_data.columns.get_level_values(0).unique()[9:10]:
        for ssn in ssn_data.index.get_level_values(3).unique():
            means_df = ssn_data.xs(ssn, level=3).xs(f'{stat}', axis=1)
            means_df.index = means_df.index.get_level_values(0)
            width = 0.20
            fig, ax = plt.subplots(figsize=(40, 10))
            ind = np.arange(len(means_df.index))

            rect_ecmwf_narr = ax.bar(ind - width, means_df.ECMWF_NARR_R, width,
                                     label='ECMWF_NARR',
                                     color='mediumslateblue')
            rect_narr_obsv = ax.bar(ind, means_df.NARR_OBSV_R, width,
                                    label='NARR_OBSV', color='lime')
            rect_ecmwf_obsv = ax.bar(ind + width, means_df.ECMWF_OBSV_R, width,
                                     label='ECMWF_OBSV', color='brown')

            ax.bar_label(rect_ecmwf_narr, fmt='%.2f')
            ax.bar_label(rect_narr_obsv, fmt='%.2f')
            ax.bar_label(rect_ecmwf_obsv, fmt='%.2f')

            ax.set_xticks(ind)
            ax.set_xticklabels(means_df.index)
            ax.legend(fontsize=20)

            ax.set_xlabel('Location')
            ax.set_title(f'{stat} (for {ssn})')

            ax.grid()
            plt.tight_layout()
            plt.savefig(f'../Plots/SEASON_LOC/PLOTS/{stat}_{ssn}.png',
                        facecolor='white')
            #plt.show()


# Takes extreme analysis.csv and creates a MEAN & MEDIAN plot based on each
# of the three threshold values by LOCATION

def extremes_analysis():
    '''
    Extremes Analysis
    '''

    extremes = pd.read_csv("../Tabular/extremes_analysis.csv",
                           index_col=[0, 1, 2, 3], header=[0, 1, 2],
                           skipinitialspace=True)

    # Analyze each location by month
    idx = pd.IndexSlice

    # Define colors based on threshold values
    thres_colors = {'39': ['palegoldenrod', 'goldenrod', 'darkgoldenrod'],
                    '50': ['moccasin', 'orange', 'darkorange'],
                    '62': ['lightsalmon', 'salmon', 'darksalmon']}

    # MEDIAN MEAN LOOP
    for stat in extremes.columns.get_level_values(1).unique()[1:3]:
        for loc in extremes.index.get_level_values(0).unique():
            loc_df = extremes.loc[idx[loc, :, :, :], idx[:, :, :]]
            # Remove lat, lon multiindexs
            loc_df.index = loc_df.index.get_level_values(3)
            for thres_val in loc_df.columns.get_level_values(0).unique():
                thres_df = loc_df.xs(thres_val, axis=1).xs(stat, axis=1)
                width = 0.20
                fig, ax = plt.subplots(figsize=(40, 10))
                ind = np.arange(len(thres_df.index))

                rect_obsv = ax.bar(ind - width, thres_df.OBSERVED, width,
                                   label='OBSERVED',
                                   color=thres_colors[thres_val][0])
                rect_narr = ax.bar(ind, thres_df.NARR, width, label='NARR',
                                   color=thres_colors[thres_val][1])
                rect_ecmwf = ax.bar(ind + width, thres_df.ECMWF, width,
                                    label='ECMWF',
                                    color=thres_colors[thres_val][2])

                ax.bar_label(rect_obsv, fmt='%.2f')
                ax.bar_label(rect_narr, fmt='%.2f')
                ax.bar_label(rect_ecmwf, fmt='%.2f')

                ax.set_xticks(ind)
                ax.set_xticklabels(thres_df.index)
                ax.legend(fontsize=20)

                ax.set_xlabel('Month')
                ax.set_title(
                    f'{stat} Number of Days Above {thres_val}km/hr '
                    f'for {loc} Between 1984-2013')

                ax.grid()
                plt.tight_layout()
                plt.savefig(f'../Plots/Extremes/{stat}_{loc}_{thres_val}.png',
                            facecolor='white')
                plt.show()

# # Differs from 'extremes_analysis' function only in that in combines all three
# # threshold values onto a single plot rather than three different plots

def extremes_analysis_combined_plots():
    extremes = pd.read_csv("../Tabular/extremes_analysis.csv",
                           index_col=[0, 1, 2, 3], header=[0, 1, 2],
                           skipinitialspace=True)

    # Analyze each location by month

    # Analyze each location by month
    idx = pd.IndexSlice

    # Define colors based on threshold values
    thres_colors = {'39': ['palegoldenrod', 'goldenrod', 'darkgoldenrod'],
                    '50': ['#93c4d2', '#5681b9', '#00429d'],
                    '62': ['#ffa59e', '#dd4c65', '#93003a']}

    for stat in extremes.columns.get_level_values(1).unique()[1:3]:
        for loc in extremes.index.get_level_values(0).unique():
            loc_df = extremes.loc[idx[loc, :, :, :], idx[:, :, :]]
            # Remove lat, lon multiindexs
            loc_df.index = loc_df.index.get_level_values(3)
            fig, ax = plt.subplots(figsize=(40, 10))
            for thres_val in loc_df.columns.get_level_values(0).unique():
                thres_df = loc_df.xs(thres_val, axis=1).xs(stat, axis=1)
                width = 0.20

                ind = np.arange(len(thres_df.index))

                rect_obsv = ax.bar(ind - width, thres_df.OBSERVED, width,
                                   label=f'OBSERVED > {thres_val}km/hr',
                                   color=thres_colors[thres_val][0])
                rect_narr = ax.bar(ind, thres_df.NARR, width,
                                   label=f'NARR > {thres_val}km/hr',
                                   color=thres_colors[thres_val][1])
                rect_ecmwf = ax.bar(ind + width, thres_df.ECMWF, width,
                                    label=f'ECMWF > {thres_val}km/hr',
                                    color=thres_colors[thres_val][2])

                ax.bar_label(rect_obsv, fmt='%.2f')
                ax.bar_label(rect_narr, fmt='%.2f')
                ax.bar_label(rect_ecmwf, fmt='%.2f')

                ax.set_xticks(ind)
                ax.set_xticklabels(thres_df.index)

            ax.set_ylabel('# of Days')
            ax.set_xlabel('Month')
            ax.set_title(
                f'{stat} Number of Days Above Threshold Values for {loc} Between 1984-2013')
            ax.legend(fontsize=18, loc=9)
            ax.grid()
            plt.tight_layout()
            plt.savefig(f'..Plots/Extremes/{stat}_{loc}_COMBINED.png',
                        facecolor='white')
            #plt.show()


def main():
    seasonal_analysis()
    extremes_analysis_combined_plots()


main()
