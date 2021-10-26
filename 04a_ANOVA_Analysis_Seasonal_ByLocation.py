# --------------------------------------------
# Name: David St. George
# Date: 2021-05-23
# File Name: 04a_ANOVA_Analysis_Seasonal_ByLocation
# --------------------------------------------

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import seaborn as sns
import matplotlib.pyplot as plt
import dataframe_image as dfi
from scipy.stats import f_oneway

'''
Function completes ANOVA analysis on a df-derived CSV file and produces 
violinplot, residual histo and qq plot, and post-hoc analysis
'''

def main():
    # Take daily means and complete ANOVA analysis between three datasets
    ssn_data_all = pd.read_csv("../Tabular/seasonal_records_merged_anova.csv",
                               index_col=0)
    for loc in ssn_data_all.location.unique():
        print(loc)
        ssn_data_loc = ssn_data_all[ssn_data_all.location == loc].copy()
    # Reform data into two columns; one with all readings, the other with dataset name
        for ssn in ssn_data_loc.season.unique():
            ssn_data = ssn_data_loc[ssn_data_loc.season == ssn].copy()
            # Create new dataframe with all data points as individual rows
            ssn_data['OBSV'] = 'OBSV'
            ssn_data['ECMWF'] = 'ERA5'
            ssn_data['NARR'] = 'NARR'
            wnd_spd_data = ssn_data['wind_spd'].append(ssn_data['ECMWF_mean'],
                                                       ignore_index=True)
            wnd_spd_data = wnd_spd_data.append(ssn_data['NARR_mean'],
                                               ignore_index=True)
            dataset_titles = ssn_data['OBSV'].append(ssn_data['ECMWF'],
                                                     ignore_index=True)
            dataset_titles = dataset_titles.append(ssn_data['NARR'],
                                                   ignore_index=True)
            anva_data = pd.concat([wnd_spd_data, dataset_titles], axis=1)
            anva_data.columns = ['wnd_spd', 'dataset']

            # Create model

            model = smf.ols('wnd_spd ~ C(dataset)', data=anva_data).fit()
            aov_table = anova_lm(model, typ=2)
            dfi.export(aov_table,
                       f"../Plots/SEASON_LOC/ANOVA_ANALYSIS"
                       f"/{loc}_{ssn}_aov_table.png")

            # Violin Plot via Seaborn

            plt.figure(figsize=(10, 10))
            ax = sns.violinplot(x='dataset', y='wnd_spd', data=anva_data)
            sns.stripplot(x='dataset', y='wnd_spd', data=anva_data, jitter=True,
                          size=4,
                          edgecolor='grey', zorder=0)

            plt.ylabel('Wind Speed (km/hr)')
            plt.xlabel('Reanalysis Dataset')
            plt.title(f"Mean Seasonal Wind Speed ({ssn}, {loc})")
            plt.grid()
            plt.savefig(
                f"../Plots/SEASON_LOC/ANOVA_ANALYSIS"
                f"/{loc}_{ssn}_violinplot_means.png",
                facecolor='white')
            # plt.show()

            # Pairwise test
            pair_t = model.t_test_pairwise('C(dataset)')
            dfi.export(pair_t.result_frame,
                       f"../Plots/SEASON_LOC/ANOVA_ANALYSIS/{loc}_{ssn}_pair_t_test.png")


            # Normality of Residuals - QQ Plot
            fig = sm.qqplot(model.resid, line='s')
            plt.title(f"Q-Q Plot ({loc}, {ssn})")
            plt.savefig(f"../Plots/SEASON_LOC/ANOVA_ANALYSIS"
                        f"/{loc}_{ssn}_q-q_plot.png",
                        facecolor='white')
            # plt.show()

            # Histogram of Residuals
            plt.clf()
            plt.hist(model.resid, edgecolor='black')
            plt.ylabel('Frequency')
            plt.xlabel('ANOVA Model Residuals')
            plt.title(f"Histogram of Residuals ({loc}, {ssn})")
            plt.savefig(
                f"../Plots/SEASON_LOC/ANOVA_ANALYSIS/{loc}_"
                f"{ssn}_residual_histogram.png",
                facecolor='white')
            # plt.show()

    print('Anova analysis completed')
main()