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
import csv

matplotlib.rcParams['font.family'] = "serif"
matplotlib.rcParams['font.size'] = "10"
matplotlib.rcParams["figure.figsize"] = (4.2, 3)
plt.rc('text', usetex=True)
plt.rc('font', family='serif')

RUNTIME = "RUNTIME"
RESULT = "RESULT"
types = [RUNTIME, RESULT]
tokenMode = ["True", "False"]
runtime_regex = re.compile('(\d+) ms')
number_regex = re.compile('Number of results: (\d+)')
BLUE = "#4d4979"
YELLOW = "#e09b36"
GREEN = "#5b7159"
LIGHT_BLUE = "#696f9b"
LIGHT_GREEN = "#92ab8e"

script_path = pathlib.Path(__file__).parent.resolve()
datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
result_path = pathlib.Path(script_path.parent / "results").resolve()
grow_row_scaling_path = pathlib.Path(result_path / "grow_row_scaling").resolve()
data_path = pathlib.Path(grow_row_scaling_path / "grow_row_scaling_token.txt").resolve()
second_data_path = pathlib.Path(grow_row_scaling_path / "new_grow_row_scaling_token_only.txt").resolve()
third_data_path = pathlib.Path(grow_row_scaling_path / "grow_row_scaling_CENSUS.txt").resolve()
fourth_data_path = pathlib.Path(grow_row_scaling_path / "grow_row_scaling_IMDB.txt").resolve()
write_path = pathlib.Path(script_path.parent / "paper" / "plots").resolve()

result_path.mkdir(parents=True, exist_ok=True)
grow_row_scaling_path.mkdir(parents=True, exist_ok=True)
write_path.mkdir(parents=True, exist_ok=True)

print('EXECUTING alternative_row_plot.py')
print(write_path)


id_regex = re.compile('DS ([A-Z]+) - LEN (\d) - run (\d) - token ([A-Z][a-z]+)')
data_points = 10
sample_count = 10
data = {}

for t in types:
    top = {}
    for ds in datasets:
        mid = {}
        for tok in tokenMode:
            curr_top = []
            for i in range(sample_count):
                curr_top.append([0] * data_points)
            mid[tok] = curr_top
        top[ds] = mid
    data[t] = top

input = open(data_path, 'r')
while True:
    line = input.readline()
    if not line:
        break
    regex_match = id_regex.search(line)
    ds = regex_match.group(1)
    len = int(regex_match.group(2))
    sample_id = int(regex_match.group(3))
    tok = regex_match.group(4)

    runtime_line = input.readline()
    runtime = int(runtime_regex.search(runtime_line).group(1))
    result_line = input.readline()
    result = int(number_regex.search(result_line).group(1))

    if tok == "False":
        data[RUNTIME][ds][tok][sample_id][len] = runtime
        data[RESULT][ds][tok][sample_id][len] = result
input.close()

input = open(second_data_path, 'r')
while True:
    line = input.readline()
    if not line:
        break
    regex_match = id_regex.search(line)
    ds = regex_match.group(1)
    len = int(regex_match.group(2))
    sample_id = int(regex_match.group(3))
    tok = regex_match.group(4)

    runtime_line = input.readline()
    runtime = int(runtime_regex.search(runtime_line).group(1))
    result_line = input.readline()
    result = int(number_regex.search(result_line).group(1))

    data[RUNTIME][ds][tok][sample_id][len] = runtime
    data[RESULT][ds][tok][sample_id][len] = result
input.close()

input = open(third_data_path, 'r')
while True:
    line = input.readline()
    if not line:
        break
    regex_match = id_regex.search(line)
    ds = regex_match.group(1)
    len = int(regex_match.group(2))
    sample_id = int(regex_match.group(3))
    tok = regex_match.group(4)

    runtime_line = input.readline()
    runtime = int(runtime_regex.search(runtime_line).group(1))
    result_line = input.readline()
    result = int(number_regex.search(result_line).group(1))

    data[RUNTIME][ds][tok][sample_id][len] = runtime
    data[RESULT][ds][tok][sample_id][len] = result
input.close()
input = open(fourth_data_path, 'r')
while True:
    line = input.readline()
    if not line:
        break
    regex_match = id_regex.search(line)
    ds = regex_match.group(1)
    len = int(regex_match.group(2))
    sample_id = int(regex_match.group(3))
    tok = regex_match.group(4)

    runtime_line = input.readline()
    runtime = int(runtime_regex.search(runtime_line).group(1))
    result_line = input.readline()
    result = int(number_regex.search(result_line).group(1))

    data[RUNTIME][ds][tok][sample_id][len] = runtime
    data[RESULT][ds][tok][sample_id][len] = result
input.close()

fig, axis = plt.subplots(2, 2, figsize=(6, 4))

legend_lines = []
for i,ds in enumerate(datasets):
    lax=axis[i // 2][i % 2]
    rax = lax.twinx()
    x_axis = []
    for i in range(data_points):
        x_axis.append((i + 1) * 10)
    for tok in tokenMode:
        rt_means = []
        rt_stdev = []
        res_means = []
        res_stdev = []
        for i in range(data_points):
            runtimes = []
            results = []
            for j in range(sample_count):
                runtimes.append(data[RUNTIME][ds][tok][j][i] / 1000)
                results.append(data[RESULT][ds][tok][j][i])
            rt_means.append(statistics.mean(runtimes))
            rt_stdev.append(statistics.stdev(runtimes))
            res_means.append(statistics.mean(results))
            res_stdev.append(statistics.stdev(results))

        #linestyle = "solid" if tok == tokenMode[0] else "dashed"
        #linestyle_res = "dashdot" if tok == tokenMode[0] else "dotted"
        color = YELLOW if tok == tokenMode[0] else BLUE
        l1 = lax.errorbar(x_axis, rt_means, yerr=rt_stdev, linestyle="solid", color=color, label="runtime")
        l2 = rax.errorbar(x_axis, res_means, yerr=res_stdev, linestyle="dashed", color=color, label="#sIND")
        legend_lines.append(l1) 
        legend_lines.append(l2)
            #for i in range(sample_count):
            #    l1 = lax.plot(x_axis, [x/1000 for x in data[RUNTIME][ds][tok][i]], linestyle="solid", label="runtime"), #color=color, label="runtime")
            #    l2 = rax.plot(x_axis, data[RESULT][ds][tok][i], linestyle="dashed", color=color, label="#sIND")
            #    if i == 0:
            #        legend_lines += l1
            #        legend_lines += l2

    # l3 = rax.plot(x_axis, simple_sinds[ds], color="red")
    #lax.set_xlabel("Row Percentage")
    #lax.set_ylabel("Runtime (Seconds)")
    #rax.set_ylabel("Number of sINDs\n")
    lax.yaxis.set_major_locator(MaxNLocator(integer=True))
    rax.yaxis.set_major_locator(MaxNLocator(integer=True))
    lax.set_ylim([0, None])
    rax.set_ylim([0, None])
    lax.set_title("TPC-H" if ds == datasets[2] else ds)
    #lns = l1 + l2
    #labs = [l.get_label() for l in lns]
labs = ["runtime - JAC mode", "\#sIND - JAC mode", "runtime - ED mode", "\#sIND - ED mode"]
#print(len(legend_lines))
#print(len(labs))
#axis[0].legend(legend_lines, labs, loc='upper center', bbox_to_anchor=(0, 0), ncol=2)
t1 = fig.text(0.49, 0.01, 'Row Percentage', ha='center')
t2 = fig.text(-0.01, 0.5, 'Runtime (s)', va='center', rotation='vertical')
t3 = fig.text(0.99, 0.5, "Number of sINDs", va='center', rotation='vertical')
#lax.legend(loc=0)
lgd = fig.legend(legend_lines, labs, ncol=2, loc='lower center', bbox_to_anchor=(0.5, -0.15))
fig.set_tight_layout(True)
print(write_path)
try:
    plt.savefig(pathlib.Path(write_path / "row_scaling.pdf"), bbox_extra_artists=(lgd, t1, t2, t3), dpi=300, bbox_inches='tight')
except Exception as e:
    print(e)
    print("Could not save figure")
#plt.show()
