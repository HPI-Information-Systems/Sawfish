from cmath import rect
import pandas
import sys
import os
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
import random
import pathlib
import re
import statistics
import json

# edit distance data
# separate plot for 2 DS:
#	7 ed
#		3 runs each -> average

datasets = ["CENSUS", "WIKIPEDIA"]
column_count = {datasets[1]: 14, datasets[0]: 42}
data_points = 7
script_path = pathlib.Path(__file__).parent.resolve()
matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "11"
matplotlib.rcParams["figure.figsize"] = (4, 2.5)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
column_reg = re.compile('column(\d+)')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"


script_path = pathlib.Path(__file__).parent.resolve()
all_results_path = pathlib.Path(script_path.parent / "results").resolve()
combined_stats_path = pathlib.Path(all_results_path / "combined_stats").resolve()
edit_distance_timing_stats_path = pathlib.Path(all_results_path / "timingStats" / "edit_distance").resolve()

write_path = pathlib.Path(script_path.parent / "paper" / "plots").resolve()

all_data_path = pathlib.Path(combined_stats_path / "all_results.csv").resolve()

combined_stats_path.mkdir(parents=True, exist_ok=True)
edit_distance_timing_stats_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)
# run_id,algorithm,dataset,edit_distance,mem_limit,row_share,column_share,ignore_short,experiment,runtime,results

data = pandas.read_csv(all_data_path)
data = data[(data["dataset"].isin(datasets)) & (data["algorithm"] == "SAWFISH") & (data["mem_limit"] == "unlimited") & (
            data["row_share"] == 100) & (data["column_share"] == 100) & (data["ignore_short"] == False)]

table_offset = {"IMAGE.csv": 0, "IMAGELINKS.csv": 12, "CENSUS.csv": 0}

fig, axis = plt.subplots(1, 2, figsize=(6, 2))


index_map = {}

for ds in datasets:
    value_columns = []
    index_columns = []
    value_counts = []
    index_counts = []
    for i in range(column_count[ds]):
        value_columns.append("valueCount_%s" % i)
        index_columns.append("indexMatches_%s" % i)

    for ed in range(data_points):
        time_path = pathlib.Path(edit_distance_timing_stats_path / ("timingStats_%s_%s_0.csv" % (ds, str(ed)))).resolve()
        timing = pandas.read_csv(time_path)
        value_sum = 0
        index_sum = 0
        for c in index_columns:
            index_sum += timing[c].sum()
        for c in value_columns:
            value_sum += timing[c].sum()
        value_counts.append(value_sum)
        index_counts.append(index_sum)
    index_map[ds] = index_counts


for i,ds in enumerate(datasets):
    lax=axis[i]

    plot_data_view = data[(data["dataset"] == ds)]
    plot_data = plot_data_view.loc[:, ("edit_distance", "runtime", "results")]
    plot_data = plot_data[["edit_distance", "runtime", "results"]].groupby(["edit_distance"], as_index=False).agg({"runtime": "mean", "results": "min"})

    rax = lax.twinx()
    l1 = lax.plot(plot_data["edit_distance"], plot_data["runtime"] / 1000, color=YELLOW, label="runtime")
    l2 = rax.plot(plot_data["edit_distance"], index_map[ds], color=GREEN, label="\#index matches", linestyle="dashed")
    #l3 = lax.plot(plot_data["edit_distance"], value_counts, color="black")
    #l3 = rax.plot(plot_data["edit_distance"], plot_data["results"])
    # l3 = rax.plot(x_axis, simple_sinds[ds], color="red")
    if ds != datasets[1]:
        lax.set_ylim([3, None])
        lax.yaxis.set_major_locator(MaxNLocator(integer=True))
    #lax.set_xlabel("Edit Distance")
    #lax.set_ylabel("Runtime (Seconds)")
    #rax.set_ylabel("Number of Index Matches\nuntil Similar String Found")
    lax.set_title(ds)

t1 = fig.text(0.51, 0.01, 'Edit Distance Threshold', ha='center')
t2 = fig.text(0.00, 0.5, 'Runtime (s)', va='center', rotation='vertical')
t3 = fig.text(0.965, 0.5, "Number of Index Matches\nuntil Similar String Found", va='center', rotation='vertical')
lns = l1 + l2
labs = [l.get_label() for l in lns]
lgd = fig.legend(lns, labs, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.2))
fig.tight_layout()
plt.savefig(pathlib.Path(write_path / "ed_scaling_explanation.pdf"), dpi=300, bbox_extra_artists=(lgd, t1, t2, t3), bbox_inches='tight')
#plt.show()
