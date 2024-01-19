import pandas
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pathlib
import numpy as np

matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "10"
matplotlib.rcParams["figure.figsize"] = (4.2, 3)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

RUNTIME = "RUNTIME"
RESULT = "RESULT"
types = [RUNTIME, RESULT]
tokenMode = ["True", "False"]
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"
LIGHT_BLUE = "#696f9b"
LIGHT_GREEN = "#92ab8e"
script_path = pathlib.Path(__file__).parent.resolve()
all_data_token_path = pathlib.Path(script_path / "results_jac.csv").resolve()
all_data_path = pathlib.Path(script_path / "results_ed.csv").resolve()

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]

data = pandas.read_csv(all_data_path)
data = data[(data["dataset"].isin(datasets)) & (data["edit_distance"] == 1) & (data["algorithm"] == "SAWFISH") &
             (data["column_share"] == 100) & (data["ignore_short"] == True)]
token_data = pandas.read_csv(all_data_token_path)
token_data = token_data[(token_data["dataset"].isin(datasets)) & (token_data["similarity"] == 0.4) & (token_data["algorithm"] == "SAWFISH") & 
                        (token_data["column_share"] == 100)]

data_points = 10
sample_count = 10

fig, axis = plt.subplots(2, 2, figsize=(6, 4))

legend_lines = []
for i,ds in enumerate(datasets):

    lax=axis[i // 2][i % 2]
    rax = lax.twinx()
    x_axis = []
    for i in range(data_points):
        x_axis.append((i + 1) * 10)
    for tok in tokenMode:
        if tok == tokenMode[0]:
            plot_data_view = data[(data["dataset"] == ds)]
        else:
            plot_data_view = token_data[(token_data["dataset"] == ds)]
        plot_data = plot_data_view.loc[:, ("row_share", "runtime", "results")]
        plot_data["runtime"] = plot_data["runtime"].apply(lambda x: x / 1000)
        means = plot_data[["row_share", "runtime", "results"]].groupby(["row_share"], as_index=False).agg(
            {"runtime": "mean","results": "mean"})
        stdevs = plot_data[["row_share", "runtime", "results"]].groupby(["row_share"], as_index=False).agg(
            {"runtime": np.std,"results": np.std})

        color = YELLOW if tok == tokenMode[1] else BLUE
        l1 = lax.errorbar(means["row_share"], means["runtime"], yerr=stdevs["runtime"], linestyle="solid", color=color, label="runtime")
        l2 = rax.errorbar(means["row_share"], means["results"], yerr=stdevs["results"], linestyle="dashed", color=color, label="#sIND")
        legend_lines.append(l1)
        legend_lines.append(l2)

    lax.yaxis.set_major_locator(MaxNLocator(integer=True))
    rax.yaxis.set_major_locator(MaxNLocator(integer=True))
    lax.set_ylim([0, None])
    rax.set_ylim([0, None])
    lax.set_title("TPC-H" if ds == datasets[2] else ds)
    
labs = ["runtime - JAC mode", "\#sIND - JAC mode", "runtime - ED mode", "\#sIND - ED mode"]
t1 = fig.text(0.49, 0.01, 'Row Percentage', ha='center')
t2 = fig.text(-0.01, 0.5, 'Runtime (s)', va='center', rotation='vertical')
t3 = fig.text(0.99, 0.5, "Number of sINDs", va='center', rotation='vertical')
lgd = fig.legend(legend_lines, labs, ncol=2, loc='lower center', bbox_to_anchor=(0.5, -0.15))
fig.set_tight_layout(True)

plt.savefig("row_scaling.pdf", bbox_extra_artists=(lgd, t1, t2, t3), dpi=300, bbox_inches='tight')
# plt.show()
