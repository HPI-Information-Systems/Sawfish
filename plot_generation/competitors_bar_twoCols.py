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

script_path = pathlib.Path(__file__).parent.resolve()
all_results_path = pathlib.Path(script_path.parent / "results").resolve()
combined_stats_path = pathlib.Path(all_results_path / "combined_stats").resolve()
all_results_csv = pathlib.Path(combined_stats_path / "all_results.csv").resolve()
write_path = pathlib.Path(script_path.parent / "paper_generation" / "figures").resolve()

all_results_path.mkdir(parents=True, exist_ok=True)
combined_stats_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)
# run_id,algorithm,dataset,edit_distance,mem_limit,row_share,column_share,ignore_short,experiment,runtime,results

data = pandas.read_csv(all_results_csv)
data = data[(data["dataset"].isin(datasets)) & (data["mem_limit"] == "unlimited") & (data["column_share"] == 100) & (
        data["row_share"] == 100) & (data["ignore_short"] == True)]

fig, axis = plt.subplots(1, 2, figsize=(10, 3))

for edit_distance in range(2):
    x = np.arange(len(datasets))  # the label locations
    width = 0.2  # the width of the bars

    ax = axis[edit_distance]
    tax = ax.twiny()

    plot_data = data.loc[:, ("dataset", "algorithm", "edit_distance", "runtime", "results")]
    plot_data = plot_data[["dataset", "algorithm", "edit_distance", "runtime"]].groupby(
        ["dataset", "algorithm", "edit_distance"], as_index=False).agg({"runtime": "mean"})
    bar_plot_data = {}
    for c in competitors:
        competitor_data = []
        for dataset in datasets:
            ed = edit_distance if c != "BINDER" else 0
            series = list(
                plot_data[(plot_data["dataset"] == dataset) & (plot_data["algorithm"] == c) & (
                        plot_data["edit_distance"] == ed)]["runtime"] / 1000)
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
        #label = c + "(\u03C4 = 0)" if c == "BINDER" and edit_distance == 1 else c
        label = c + "(\tau = 0)" if c == "BINDER" and edit_distance == 1 else c
        for j, t in enumerate(percentage_data[c]):
            if t == 0:
                text = " time limit exceeded"
                
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
    #ax.set_title("\u03C4 = " + str(edit_distance), y=-0.21, fontweight="bold")
    ax.set_title(r'$\tau = ' + str(edit_distance) + '$', y=-0.21, fontweight="bold")
handles, labels = axis[0].get_legend_handles_labels()
#lgd = fig.legend(handles, labels, ncol=3, loc='lower center', bbox_to_anchor=(0.5, -0.06))
t1 = fig.text(0.00, 0.5, 'Runtime (\% of Longest Run)', va='center', rotation='vertical')
t2 = fig.text(0.52, 0.965, 'Longest Runtime (s)', ha='center')

fig.tight_layout()

plt.savefig(pathlib.Path(write_path / "competitor_bars.pdf"), bbox_extra_artists=(t1, t2), dpi=300, bbox_inches='tight')
#plt.savefig("competitor_bars.png", bbox_extra_artists=(t1, t2, lgd), dpi=300, bbox_inches='tight')
#plt.show()
