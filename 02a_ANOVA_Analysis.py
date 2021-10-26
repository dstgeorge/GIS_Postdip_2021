# --------------------------------------------
# Name: David St. George
# Date: 2021-05-23
# File Name: 02a_ANOVA_Analysis
# --------------------------------------------

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import seaborn as sns
import matplotlib.pyplot as plt
import dataframe_image as dfi
import pingouin as pg

'''
Function completes ANOVA analysis on a df-derived CSV file and produces 
violinplot, residual histo and qq plot, and post-hoc analysis
'''

def main():

    # Take daily means and complete ANOVA analysis between three datasets
    daily_data = pd.read_csv("../Tabular/daily_means_alldatasets.csv",
                             index_col=0)

    # Reform data into two columns; one with all readings, the other with dataset name

    # Create new dataframe with all data points as individual rows
    daily_data['OBSV'] = 'OBSV'
    daily_data['ECMWF'] = 'ERA5'
    daily_data['NARR'] = 'NARR'
    wnd_spd_data = daily_data['wind_spd'].append(daily_data['ECMWF_mean'],
                                                 ignore_index=True)
    wnd_spd_data = wnd_spd_data.append(daily_data['NARR_mean'],
                                       ignore_index=True)
    dataset_titles = daily_data['OBSV'].append(daily_data['ECMWF'],
                                               ignore_index=True)
    dataset_titles = dataset_titles.append(daily_data['NARR'],
                                           ignore_index=True)
    anva_data = pd.concat([wnd_spd_data, dataset_titles], axis=1)
    anva_data.columns = ['wnd_spd', 'dataset']

    # Create model
    model = smf.ols('wnd_spd ~ dataset', data=anva_data).fit()
    aov_table = anova_lm(model, typ=2)
    #aov_table.to_csv("../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/aov_table.csv")
    dfi.export(aov_table,
               f"../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/aov_table.png")

    # Violin Plot via Seaborn
    plt.figure(figsize=(10, 10))
    ax = sns.violinplot(x='dataset', y='wnd_spd', data=anva_data,
                        palette='deep')
    sns.stripplot(x='dataset', y='wnd_spd', data=anva_data, jitter=True, size=4,
                  edgecolor='grey', zorder=0, palette='deep')

    plt.ylabel('Wind Speed (km/hr)')
    plt.xlabel('Reanalysis Dataset')
    plt.title("Mean Daily Wind Speed, Weather Stations in Newfoundland")
    plt.grid()
    plt.savefig('../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/violinplot_means.png',
                facecolor='white')
    #plt.show()

    # Pairwise test
    pair_t = model.t_test_pairwise('dataset')
    pair_t.result_frame.to_csv("../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/pair_t_test"
                           ".csv")
    dfi.export(pair_t.result_frame,
               '../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/pair_t_result.png')

    # Method #2 - Pingouin
    aov = pg.anova(data=anva_data, dv='wnd_spd', between='dataset',
                   detailed=True)
    print(aov)
    pt = pg.pairwise_tukey(dv='wnd_spd', between='dataset', data=anva_data)
    print(pt)


    # Normality of Residuals - QQ Plot
    fig = sm.qqplot(model.resid, line='s')
    plt.title("Q-Q Plot")
    plt.savefig('../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/q-q_plot.png',
                facecolor='white')
    #plt.show()

    # Histogram of Residuals
    plt.clf()
    plt.hist(model.resid, edgecolor='black')
    plt.ylabel('Frequency')
    plt.xlabel('ANOVA Model Residuals')
    plt.title("Histogram of Residuals")
    plt.savefig('../Plots/DAILY_WHOLE/ANOVA_ANALYSIS/residual_histogram.png',
                facecolor='white')
    #plt.show()

    print('ANOVA analysis completed')
main()