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

# edit distance data
# separate plot for 2 DS:
#	7 ed
#		3 runs each -> average

datasets = ["TPCH"]
script_path = pathlib.Path(__file__).parent.resolve()
runtime_regex = re.compile('(\d+) ms')
number_regex = re.compile('Number of results: (\d+)')
matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "10"
matplotlib.rcParams["figure.figsize"] = (3.5, 2)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"

script_path = pathlib.Path(__file__).parent.resolve()
combined_stats_path = pathlib.Path(script_path.parent / "results" / "combined_stats").resolve()
write_path = pathlib.Path(script_path.parent / "paper" / "plots").resolve()

all_data_path = pathlib.Path(combined_stats_path / "all_results_token.csv").resolve()

combined_stats_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)
# run_id,algorithm,dataset,similarity,mem_limit,row_share,column_share,experiment,runtime,results

data = pandas.read_csv(all_data_path)
data = data[(data["dataset"].isin(datasets)) & (data["algorithm"] == "SAWFISH") & (data["mem_limit"] == "unlimited") & (
            data["row_share"] == 100) & (data["column_share"] == 100)]

for ds in datasets:
    plot_data_view = data[(data["dataset"] == ds)]
    plot_data = plot_data_view.loc[:, ("similarity", "runtime", "results")]
    plot_data = plot_data[["similarity", "runtime", "results"]].groupby(["similarity"], as_index=False).agg({"runtime": "mean", "results": "min"})

    fig, lax = plt.subplots()
    rax = lax.twinx()
    l1 = lax.plot(plot_data["similarity"], plot_data["runtime"] / 1000, color=YELLOW, label="runtime")
    l2 = rax.plot(plot_data["similarity"], plot_data["results"], color="black", label="\#sIND", linestyle="dashed")
    # l3 = rax.plot(x_axis, simple_sinds[ds], color="red")
    lax.set_xlabel("Jaccard Similarity Threshold")
    lax.set_ylabel("Runtime (Seconds)")
    rax.set_ylabel("Number of sINDs\n")
    lax.set_title('TPC-H')
    lax.set_ylim([0, None])
    rax.set_ylim([0, None])
    lax.yaxis.set_major_locator(MaxNLocator(integer=True))
    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    lgd = fig.legend(lns, labs, loc='lower center', ncol=2, bbox_to_anchor=(0.49, -0.1))
    fig.set_tight_layout(True)
    plt.savefig(pathlib.Path(write_path / ("sim_scaling_" + ds + "_token.pdf")), bbox_extra_artists=(lgd, ), dpi=300, bbox_inches='tight')
    # plt.savefig("sim_scaling_" + ds + "_token.png", bbox_extra_artists=(lgd, ), dpi=300, bbox_inches='tight', transparent=True)
    #plt.show()
