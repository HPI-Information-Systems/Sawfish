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
import csv

# competitors data
# separate plot for 3 DS:
#	5 competitors
#		3 runs each -> average


script_path = pathlib.Path(__file__).parent.resolve()
combined_stats_path = pathlib.Path(script_path.parent / "results" / "combined_stats").resolve()
write_path = pathlib.Path(script_path.parent / "paper" / "plots").resolve()

all_data_path = pathlib.Path(combined_stats_path / "all_results.csv").resolve()
# row schema: run_id,algorithm,dataset,edit_distance,mem_limit,row_share,column_share,ignore_short,experiment,runtime,results
csvfile = open(all_data_path, 'a', newline='')
writer = csv.writer(csvfile, delimiter=',', quotechar='"')
data = {}
RUNTIME = "runtime"
RESULT = "RESULT"
types = [RUNTIME, RESULT]
runtime_regex = re.compile('(\d+) ms')
number_regex = re.compile('Number of results: (\d+)')

if len(sys.argv) < 2:
    print("arguments")
    exit(1)
elif sys.argv[1] == "row":
    # row_scaling data
    # separate plot for 2 DS:
    #	10 data points
    #		3 runs each -> average
    datasets = ["WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "row_scaling.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - DP (\d) - run (\d)')
    data_points = 10
    for t in types:
        top = {}
        for ds in datasets:
            curr_top = []
            for i in range(data_points):
                curr_top.append([])
            top[ds] = curr_top
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        dp = int(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds][dp].append(runtime)
        data[RESULT][ds][dp].append(result)

    algorithm = "SAWFISH"
    edit_distance = "1"
    mem_limit = "unlimited"
    column_share = "100"
    experiment = "row"
    ignore_short = False

    for ds in datasets:
        for dp in range(data_points):
            for idx, runtime in enumerate(data[RUNTIME][ds][dp]):
                row_share = (10 - dp) * 10
                result = data[RESULT][ds][dp][idx]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, column_share, ignore_short, experiment,
                       runtime,
                       result]
                writer.writerow(row)

elif sys.argv[1] == "ed":
    # edit distance data
    # separate plot for 2 DS:
    #	7 ed
    #		3 runs each -> average

    datasets = ["WIKIPEDIA", "CENSUS"]
    data_points = 7
    redundancy = 3
    data_path = pathlib.Path(script_path / "edit_distance.txt").resolve()
    id_regex = re.compile('([A-Z]+) - ED (\d) - run (\d)')

    for t in types:
        top = {}
        for ds in datasets:
            middle = []
            for i in range(data_points):
                middle.append([])
            top[ds] = middle
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        ed = int(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        if ed < 7:
            data[RUNTIME][ds][ed].append(runtime)
            data[RESULT][ds][ed].append(result)

    algorithm = "SAWFISH"
    mem_limit = "unlimited"
    column_share = "100"
    row_share = "100"
    experiment = "ed"
    ignore_short = False

    for ds in datasets:
        for edit_distance in range(data_points):
            for idx, runtime in enumerate(data[RUNTIME][ds][edit_distance]):
                result = data[RESULT][ds][edit_distance][idx]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, column_share, ignore_short, experiment,
                       runtime,
                       result]
                writer.writerow(row)

elif sys.argv[1] == "competitors":
    # competitors data
    # separate plot for 3 DS:
    #	5 competitors
    #		3 runs each -> average

    datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]
    competitor = ["SAWFISH0", "SAWFISH1", "BASELINE0", "BASELINE1", "BINDER"]
    raw_alg_names = {"de.metanome.algorithms.similarity_ind.AlgorithmInterface": "SAWFISH",
                     "de.metanome.algorithms.binder.BinderFileAlgorithm": "BINDER",
                     "de.metanome.algorithms.sindbaseline.SINDBaseline": "BASELINE"}
    data_path = pathlib.Path(script_path / "related_work.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - ALG (.+) - ED (\d) - run (\d)')

    for t in types:
        top = {}
        for ds in datasets:
            middle = {}
            for c in competitor:
                middle[c] = []
            top[ds] = middle
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        alg = regex_match.group(2)
        ed = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        competitorName = raw_alg_names[alg]
        if not competitorName == "BINDER":
            competitorName += ed

        data[RUNTIME][ds][competitorName].append(runtime)
        data[RESULT][ds][competitorName].append(result)

    mem_limit = "unlimited"
    column_share = "100"
    row_share = "100"
    experiment = "competitors"
    ignore_short = True

    for ds in datasets:
        for c in competitor:
            for idx, runtime in enumerate(data[RUNTIME][ds][c]):
                result = data[RESULT][ds][c][idx]
                algorithm = c if c == "BINDER" else c[:-1]
                edit_distance = "0" if c == "BINDER" else c[-1]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, column_share, ignore_short, experiment,
                       runtime,
                       result]
                writer.writerow(row)

elif sys.argv[1] == "disk":
    # disk data
    # separate plot for 3 DS:
    #		3 runs each -> average

    datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "disk_scaling.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - run (\d)')

    for t in types:
        top = {}
        for ds in datasets:
            top[ds] = []
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds].append(runtime)
        data[RESULT][ds].append(result)

    mem_limit = "limited"
    column_share = "100"
    row_share = "100"
    experiment = "disk"
    algorithm = "SAWFISH"
    edit_distance = "1"
    ignore_short = False

    for ds in datasets:
        for idx, runtime in enumerate(data[RUNTIME][ds]):
            result = data[RESULT][ds][idx]
            row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, column_share, ignore_short, experiment,
                   runtime,
                   result]
            writer.writerow(row)

elif sys.argv[1] == "column":
    # column_scaling data
    # separate plot for 2 DS:
    #	5 data points
    #		3 runs each -> average
    datasets = ["WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "column_scaling.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d+) - run (\d)')
    column_sizes = {datasets[0]: [2, 4, 6, 8, 10], datasets[1]: [10, 20, 30, 40, 50]}

    for t in types:
        top = {}
        for ds in datasets:
            curr_top = {}
            for size in column_sizes[ds]:
                curr_top[size] = []
            top[ds] = curr_top
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        size = int(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds][size].append(runtime)
        data[RESULT][ds][size].append(result)

    mem_limit = "unlimited"
    row_share = "100"
    experiment = "column"
    algorithm = "SAWFISH"
    edit_distance = "1"
    ignore_short = False

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, size, ignore_short, experiment, runtime,
                       result]
                writer.writerow(row)
elif sys.argv[1] == "competitors_imdb":
    # competitors data
    #	3 competitors
    #		3 runs each -> average

    dataset = "IMDB"
    competitor = ["SAWFISH", "BINDER"]
    raw_alg_names = {"de.metanome.algorithms.similarity_ind.AlgorithmInterface": "SAWFISH",
                     "de.metanome.algorithms.binder.BinderFileAlgorithm": "BINDER",
                     "de.metanome.algorithms.sindbaseline.SINDBaseline": "BASELINE"}
    data_path = pathlib.Path(script_path / "related_work_imdb.txt").resolve()
    id_regex = re.compile('ALG (.+) - run (\d)')

    for t in types:
        top = {}
        for c in competitor:
            top[c] = []
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        alg = regex_match.group(1)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        competitorName = raw_alg_names[alg]

        if competitorName in competitor:
            data[RUNTIME][competitorName].append(runtime)
            data[RESULT][competitorName].append(result)

    mem_limit = "unlimited"
    column_share = "100"
    row_share = "100"
    experiment = "competitors_imdb"
    ignore_short = True
    edit_distance = "0"

    for c in competitor:
        for idx, runtime in enumerate(data[RUNTIME][c]):
            result = data[RESULT][c][idx]
            row = [idx, c, dataset, edit_distance, mem_limit, row_share, column_share, ignore_short, experiment,
                   runtime,
                   result]
            writer.writerow(row)
elif sys.argv[1] == "column_new":
    # new column_scaling data
    # separate plot for 2 DS:
    #   5 data points
    #       3 runs each -> average
    datasets = ["WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "column_scaling_new.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d+) - run (\d)')
    column_sizes = {datasets[0]: [3, 5, 7, 9], datasets[1]: [5, 15, 25, 35, 45]}

    for t in types:
        top = {}
        for ds in datasets:
            curr_top = {}
            for size in column_sizes[ds]:
                curr_top[size] = []
            top[ds] = curr_top
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        size = int(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds][size].append(runtime)
        data[RESULT][ds][size].append(result)

    mem_limit = "unlimited"
    row_share = "100"
    experiment = "column_new"
    algorithm = "SAWFISH"
    edit_distance = "1"
    ignore_short = False

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, size, ignore_short, experiment, runtime,
                       result]
                writer.writerow(row)
elif sys.argv[1] == "column_CENSUS":
    # new column_scaling data
    # separate plot for 2 DS:
    #   5 data points
    #       3 runs each -> average
    datasets = ["CENSUS"]
    data_path = pathlib.Path(script_path /  "column_scaling_CENSUS.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d+) - run (\d)')
    column_sizes = {datasets[0]: [2, 6, 10, 14,18,22,26,30,34,38]}

    for t in types:
        top = {}
        for ds in datasets:
            curr_top = {}
            for size in column_sizes[ds]:
                curr_top[size] = []
            top[ds] = curr_top
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        size = int(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds][size].append(runtime)
        data[RESULT][ds][size].append(result)

    mem_limit = "unlimited"
    row_share = "100"
    experiment = "column_CENSUS"
    algorithm = "SAWFISH"
    edit_distance = "1"
    ignore_short = False

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, edit_distance, mem_limit, row_share, size, ignore_short, experiment, runtime,
                       result]
                writer.writerow(row)
else:
    print("unknown option")
    exit(1)
