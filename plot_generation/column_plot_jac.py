import pathlib

import matplotlib
import matplotlib.pyplot as plt
import pandas

# column_scaling data
# separate plot for 2 DS:
#	10 data points
#		30 runs each -> box_plot

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
column_count = {datasets[0]: 42, datasets[1]: 11, datasets[2]: 55, datasets[3]: 94}
script_path = pathlib.Path(__file__).parent.resolve()
matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "11"
matplotlib.rcParams["figure.figsize"] = (4, 2.5)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"
LIGHT_BLUE = "#696f9b"
LIGHT_GREEN = "#92ab8e"
script_path = pathlib.Path(__file__).parent.resolve()
all_results_path = pathlib.Path(script_path.parent / "results" / "combined_stats").resolve()
all_results_csv = pathlib.Path(all_results_path / "results_jac.csv").resolve()
write_path = pathlib.Path(script_path.parent / "paper_generation" / "figures").resolve()

all_results_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)

# run_id,algorithm,dataset,similarity,row_share,column_share,experiment,runtime,results

data = pandas.read_csv(all_results_csv)
data = data[(data["dataset"].isin(datasets)) & (data["similarity"] == 0.4) & (data["algorithm"] == "SAWFISH") & (data["row_share"] == 100)]

fig, axis = plt.subplots(4, 1, figsize=(3.5, 9.4))

for i,ds in enumerate(datasets):

    ax=axis[i]

    plot_data_view = data[(data["dataset"] == ds)]
    plot_data = plot_data_view.loc[:, ("column_share", "runtime", "results")]
    plot_data["runtime"] = plot_data["runtime"].apply(lambda x: x / 1000)
    plot_data.loc[(plot_data["column_share"] == 100), 'column_share'] = column_count[ds]
    line_data = plot_data[["column_share", "runtime"]].groupby(["column_share"], as_index=False).agg(
        {"runtime": "mean"})
    box_plot_data = plot_data[["column_share", "runtime", "results"]].groupby(["column_share"], as_index=False)

    for name, group in box_plot_data:
        width = 0.5 if ds == datasets[1] else 2 if ds == datasets[0] else 3
        box = ax.boxplot(group["runtime"], positions=[name[0]], showmeans=True, meanline=True, patch_artist=True,
                          widths=width, boxprops=dict(facecolor="none"),
                          meanprops=dict(color=YELLOW), medianprops=dict(color=GREEN))
    ax.plot(line_data["column_share"], line_data["runtime"], color=YELLOW, zorder=5, linestyle="dashed")
    ax.set_ylim([0, None])
    if ds in ['TPCH']:
        ax.set_title("TPC-H")
    else:
        ax.set_title(ds)

t1 = fig.text(0.53, 0.001, 'Number of columns', ha='center')
t2 = fig.text(0.00, 0.5, 'Runtime (s)', va='center', rotation='vertical')

lgd = axis[0].legend([box['means'][0], box['medians'][0]], ['mean', 'median'] , loc='lower right')

plt.tight_layout()
plt.savefig(pathlib.Path(write_path / "column_scaling_jac.pdf"), dpi=300)
#plt.show()
