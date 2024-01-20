import pathlib

import matplotlib
import matplotlib.pyplot as plt
import pandas
from matplotlib.ticker import MaxNLocator

# edit distance data
# separate plot for 2 DS:
#	7 ed
#		3 runs each -> average

datasets = ["CENSUS", "WIKIPEDIA"]
data_points = 7
script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "edit_distance.txt").resolve()
matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "11"
matplotlib.rcParams["figure.figsize"] = (4, 2.6)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"

script_path = pathlib.Path(__file__).parent.resolve()
combined_stats_path = pathlib.Path(script_path.parent / "results" / "combined_stats").resolve()
write_path = pathlib.Path(script_path.parent / "paper_generation" / "figures").resolve()

all_data_path = pathlib.Path(combined_stats_path / "results_ed.csv").resolve()

combined_stats_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)
# run_id,algorithm,dataset,edit_distance,row_share,column_share,ignore_short,experiment,runtime,results

data = pandas.read_csv(all_data_path)
data = data[(data["dataset"].isin(datasets)) & (data["algorithm"] == "SAWFISH") & (data["row_share"] == 100) &
            (data["column_share"] == 100) & (data["ignore_short"] == False)]

fig, axis = plt.subplots(1, 2, figsize=(6, 2))

for i,ds in enumerate(datasets):

    lax=axis[i]

    plot_data_view = data[(data["dataset"] == ds)]
    plot_data = plot_data_view.loc[:, ("edit_distance", "runtime", "results")]
    plot_data = plot_data[["edit_distance", "runtime", "results"]].groupby(["edit_distance"], as_index=False).agg({"runtime": "mean", "results": "min"})

    rax = lax.twinx()
    if i == 1:
        lax.set_yscale("log")
        rax.set_yscale("log")
    l1 = lax.plot(plot_data["edit_distance"], plot_data["runtime"] / 1000, color=YELLOW, label="runtime")
    l2 = rax.plot(plot_data["edit_distance"], plot_data["results"], color="black", label="\#sIND", linestyle="dashed")
    if ds != datasets[1]:
        rax.set_ylim([0, None])
        lax.set_ylim([0, None])
        lax.yaxis.set_major_locator(MaxNLocator(integer=True))
    lns = l1 + l2
    lax.set_title(ds if i == 0 else ds + " (log scale)")
t1 = fig.text(0.5, 0.01, 'Edit Distance Threshold', ha='center')
t2 = fig.text(0.00, 0.5, 'Runtime (s)', va='center', rotation='vertical')
t3 = fig.text(0.98, 0.5, "Number of sINDs", va='center', rotation='vertical')
labs = [l.get_label() for l in lns]
lgd = fig.legend(lns, labs, loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.2))
fig.set_tight_layout(True)
plt.savefig(pathlib.Path(write_path /"ed_scaling.pdf"), dpi=300,bbox_extra_artists=(lgd, t1, t2, t3), bbox_inches='tight')
#plt.show()
