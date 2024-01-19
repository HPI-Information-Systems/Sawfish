import csv
import json
import pathlib

import matplotlib
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas

matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "10"
matplotlib.rcParams["figure.figsize"] = (4, 2)
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['mathtext.fontset'] = 'cm'
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"

script_path = pathlib.Path(__file__).parent.resolve()
all_results_path = pathlib.Path(script_path.parent / "results").resolve()
result_path = pathlib.Path(all_results_path / "row_scaling").resolve()
combined_stats_path = pathlib.Path(all_results_path / "combined_stats").resolve()
target_path = pathlib.Path(all_results_path / "timingStats" / "row_scaling").resolve()
write_path = pathlib.Path(script_path.parent / "paper_generation" / "figures").resolve()

all_results_path.mkdir(parents=True, exist_ok=True)
result_path.mkdir(parents=True, exist_ok=True)
combined_stats_path.mkdir(parents=True, exist_ok=True)
target_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)

datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]

fig, ax = plt.subplots()
ax.set_yscale("log")
ax.set_xscale("log")

for d in datasets:
    valid_sinds = set()  # set of int tuples
    column_size = []  # list of ints
    timing_stats = []  # 2d array with timing stats per column combination
    column_dict = {}

    valid_time = []
    valid_count = []
    invalid_time = []
    invalid_count = []

    with open(pathlib.Path(combined_stats_path / (d + "_id_to_column.csv"))) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            column_dict[row[1]] = int(row[0])

    result_file = open(pathlib.Path(result_path / ("result_" + d + "_0_0_inds")))
    while True:
        line = result_file.readline()
        if not line:
            break

        data = json.loads(line)
        dependent_column = data["dependant"]["columnIdentifiers"][0]["columnIdentifier"]
        referenced_column = data["referenced"]["columnIdentifiers"][0]["columnIdentifier"]
        valid_sinds.add((column_dict[dependent_column], column_dict[referenced_column]))

    result_file.close()

    with open(pathlib.Path(combined_stats_path / (d + "_stats.csv"))) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            column_size.append(int(row[0]))

    with open(pathlib.Path(target_path / ("timingStats_" + d + "_0_0.csv"))) as csv_file:
        is_first = True
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if is_first:
                is_first = False
                continue
            elif len(row) < len(column_size):
                break
            times_of_row = []
            for i in range(len(column_size)):
                times_of_row.append(int(row[i + 1]))
            timing_stats.append(times_of_row)

    for i, row in enumerate(timing_stats):
        for j, time in enumerate(row):
            if time != 0:
                if (j, i) in valid_sinds:
                    valid_time.append(time / 1000000)
                    valid_count.append(column_size[j])
                else:
                    invalid_time.append(time / 1000000)
                    invalid_count.append(column_size[j])

    if d == datasets[1]:
        ax.plot(valid_count, valid_time, marker='o', fillstyle='none', linestyle='', label="Valid sINDs", color=YELLOW,
                ms=4)
        ax.plot(invalid_count, invalid_time, marker='o', fillstyle='none', linestyle='', label="Invalid sINDs",
                color=GREEN,
                ms=4)
    elif d == datasets[2]:
        ax.plot(valid_count, valid_time, marker='x', linestyle='', fillstyle='none', label="Valid sINDs", color=YELLOW,
                ms=4)
        ax.plot(invalid_count, invalid_time, marker='x', linestyle='', fillstyle='none', label="Invalid sINDs",
                color=GREEN,
                ms=4)
    else:
        ax.plot(valid_count, valid_time, marker='v', linestyle='', fillstyle='none', label="Valid sINDs", color=YELLOW,
                ms=4)
        ax.plot(invalid_count, invalid_time, marker='v', linestyle='', fillstyle='none', label="Invalid sINDs",
                color=GREEN,
                ms=4)

ax.set_xlabel("Number of Distinct Values in the Dependent Column")
ax.set_ylabel("Runtime (Milliseconds)")


valid_patch = mpatches.Patch(color=YELLOW, label='Valid sINDs')
invalid_patch = mpatches.Patch(color=GREEN, label='Invalid sINDs')
wiki_line = mlines.Line2D([], [], color='black', marker='o', linestyle='', fillstyle='none', ms=4, label='WIKIPEDIA')
tpch_line = mlines.Line2D([], [], color='black', marker='x', linestyle='', fillstyle='none', ms=4, label='TPCH-H')
census_line = mlines.Line2D([], [], color='black', marker='v', linestyle='', fillstyle='none', ms=4, label='CENSUS')

lgd = fig.legend(handles=[valid_patch, invalid_patch], loc='lower center', ncol=2, bbox_to_anchor=(0.55, -0.1))
ax.add_artist(lgd)
lgd2 = fig.legend(handles=[census_line, wiki_line, tpch_line], loc='lower center', ncol=3, bbox_to_anchor=(0.55, -0.24))
fig.set_tight_layout(True)
plt.savefig(pathlib.Path(write_path / "valid_sIND_impact.pdf"), bbox_extra_artists=(lgd, lgd2), dpi=300, bbox_inches='tight')
#plt.show()
