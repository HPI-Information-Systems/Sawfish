import pandas
import sys
import os
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import random
import pathlib
import re
import statistics
import numpy as np

# competitors data
# separate plot for 4 DS:
#	5 competitors
#		3 runs each -> average

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
competitors = ["SAWFISH", "BASELINE", "BINDER"]
data_points = 10
script_path = pathlib.Path(__file__).parent.resolve()
matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "11"
matplotlib.rcParams["figure.figsize"] = (4, 2.7)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"
colors = [YELLOW, BLUE, GREEN]
similarities = [1.0, 0.4]

all_data_path = pathlib.Path(script_path / "all_results_token.csv").resolve()
# run_id,algorithm,dataset,similarity,mem_limit,row_share,column_share,experiment,runtime,results

data = pandas.read_csv(all_data_path)
data = data[(data["dataset"].isin(datasets)) & (data["mem_limit"] == "unlimited") & (data["column_share"] == 100) & (
        data["row_share"] == 100) & (data["experiment"] == "competitors")]
binder_data = pandas.read_csv(pathlib.Path(script_path / "all_results.csv").resolve())
binder_data = binder_data[(binder_data["dataset"].isin(datasets)) & (binder_data["mem_limit"] == "unlimited") & (binder_data["column_share"] == 100) & (
        binder_data["row_share"] == 100) & (binder_data["algorithm"] == "BINDER")]

fig, axis = plt.subplots(1, 2, figsize=(10, 3))

for sim_idx in range(2):
    sim = similarities[sim_idx]
    x = np.arange(len(datasets))  # the label locations
    width = 0.2  # the width of the bars

    ax = axis[sim_idx]
    tax = ax.twiny()

    binder_frame = binder_data.loc[:, ("dataset", "algorithm", "edit_distance", "runtime", "results")]
    binder_frame.rename(columns={"edit_distance": "similarity"}, inplace=True)

    sawfish_frame = data.loc[:, ("dataset", "algorithm", "similarity", "runtime", "results")]
    plot_data = pandas.concat([sawfish_frame, binder_frame])
    plot_data = plot_data[["dataset", "algorithm", "similarity", "runtime"]].groupby(
        ["dataset", "algorithm", "similarity"], as_index=False).agg({"runtime": "mean"})
    bar_plot_data = {}
    for c in competitors:
        competitor_data = []
        for dataset in datasets:
            similarity = sim if c != "BINDER" else 0
            series = list(
                plot_data[(plot_data["dataset"] == dataset) & (plot_data["algorithm"] == c) & (
                        plot_data["similarity"] == similarity)]["runtime"] / 1000)
            if len(series) == 1:
                competitor_data.append(series[0])
            else:
                competitor_data.append(0)
            bar_plot_data[c] = competitor_data

    percentage_data = {}
    for c in competitors:
        percentage_data[c] = []

    maximums = []
    for i, ds in enumerate(datasets):
        # find max for dataset
        maxi = 0
        for c in competitors:
            if bar_plot_data[c][i] > maxi:
                maxi = bar_plot_data[c][i]
        maximums.append(round(maxi, 2))
        for c in competitors:
            percentage_data[c].append(bar_plot_data[c][i] / maxi * 100)

    for i, c in enumerate(competitors):
        offset = (i - 1) * width
        # label = c + "(\u03B4 = 1)" if c == "BINDER" and sim == 0.4 else c
        label = c + "(\delta = 1)" if c == "BINDER" and sim == 0.4 else c
        for j, t in enumerate(percentage_data[c]):
            if t == 0:
                if c == "SAWFISH":
                    text = " time limit exceeded"
                else:
                    text = " memory limit exceeded"

                plt.text(j * 4 * width + offset + j * width, 0, text, ha='center', va='bottom', rotation=90)

        a = ax.bar(x + offset, percentage_data[c], width, label=label, color=colors[i])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    #ax.set_ylabel('Runtime (Percentage of Longest Run)')
    ax.set_ylim([0, 100])
    ax.set_xticks(x, [ds if ds != "TPCH" else "TPC-H" for ds in datasets])
    tax.tick_params(axis='x', pad=-4)
    tax.set_xlim(ax.get_xlim())
    tax.set_xticks(x, maximums)
    #tax.set_xlabel("Longest Runtime (Seconds)")
    ax.xaxis.set_ticks_position('none')
    tax.xaxis.set_ticks_position('none')
    # ax.set_title("\u03B4 = " + str(sim), y=-0.21, fontweight="bold")
    ax.set_title(r'$\delta = ' + str(sim) + '$', y=-0.21, fontweight="bold")

handles, labels = axis[0].get_legend_handles_labels()
lgd = fig.legend(handles, labels, ncol=3, loc='lower center', bbox_to_anchor=(0.5, -0.06))
t1 = fig.text(0.00, 0.5, 'Runtime (\% of Longest Run)', va='center', rotation='vertical')
t2 = fig.text(0.52, 0.965, 'Longest Runtime (s)', ha='center')
fig.tight_layout()
#plt.savefig("competitor_bars_" + str(sim) + "_token.pdf", dpi=300)
plt.savefig("competitor_bars_token.pdf", bbox_extra_artists=(lgd, t1, t2), dpi=300, bbox_inches='tight')
#plt.savefig("competitor_bars_token.png", bbox_extra_artists=(lgd, t1, t2), dpi=300, bbox_inches='tight')
#plt.show()
