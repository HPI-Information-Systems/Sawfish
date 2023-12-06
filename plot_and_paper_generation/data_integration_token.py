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
all_data_path = pathlib.Path(script_path / "all_results_token.csv").resolve()
# row schema: run_id,algorithm,dataset,similarity,mem_limit,row_share,column_share,sample_base,experiment,runtime,results
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
    data_path = pathlib.Path(script_path / "row_scaling_token.txt").resolve()
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
    similarity = "0.4"
    mem_limit = "unlimited"
    column_share = "100"
    experiment = "row"

    for ds in datasets:
        for dp in range(data_points):
            for idx, runtime in enumerate(data[RUNTIME][ds][dp]):
                row_share = (10 - dp) * 10
                result = data[RESULT][ds][dp][idx]
                row = [idx, algorithm, ds, similarity, mem_limit, row_share, column_share, experiment, runtime, result]
                writer.writerow(row)

elif sys.argv[1] == "sim":
    # similarity scaling data
    # separate plot for 2 DS:
    #	7 ed
    #		3 runs each -> average

    datasets = ["TPCH"]
    data_points = 9
    redundancy = 3
    data_path = pathlib.Path(script_path / "token_similarity_scaling.txt").resolve()
    id_regex = re.compile('([A-Z]+) - SIM (\d\.\d) - run (\d)')

    for t in types:
        top = {}
        for ds in datasets:
            middle = {}
            for i in range(data_points):
                middle[float("0." + str(i + 1))]=[]
            top[ds] = middle
        data[t] = top

    input = open(data_path, 'r')

    while True:
        line = input.readline()
        if not line:
            break
        regex_match = id_regex.search(line)
        ds = regex_match.group(1)
        sim = float(regex_match.group(2))
        rd = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        data[RUNTIME][ds][sim].append(runtime)
        data[RESULT][ds][sim].append(result)

    algorithm = "SAWFISH"
    mem_limit = "unlimited"
    column_share = "100"
    row_share = "100"
    experiment = "sim"

    for ds in datasets:
        for sim_idx in range(data_points):
            sim = float("0." + str(sim_idx + 1))
            for idx, runtime in enumerate(data[RUNTIME][ds][sim]):
                result = data[RESULT][ds][sim][idx]
                row = [idx, algorithm, ds, sim, mem_limit, row_share, column_share, experiment, runtime, result]
                writer.writerow(row)

elif sys.argv[1] == "competitors":
    # competitors data
    # separate plot for 3 DS:
    #	5 competitors
    #		3 runs each -> average

    datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
    competitor = ["BASELINE0.4", "BASELINE1.0", "SAWFISH0.4", "SAWFISH1.0"]
    raw_alg_names = {"de.metanome.algorithms.similarity_ind.AlgorithmInterface": "SAWFISH",
                     "de.metanome.algorithms.binder.BinderFileAlgorithm": "BINDER",
                     "de.metanome.algorithms.sindbaseline.SINDBaseline": "BASELINE",
                     "de.metanome.algorithms.tokenbaseline.TokenBaseline": "BASELINE"}
    data_path = pathlib.Path(script_path / "competitors_token.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - ALG (.+) - SIM (\d\.\d) - run (\d)')

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
        sim = regex_match.group(3)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        competitorName = raw_alg_names[alg]+sim

        data[RUNTIME][ds][competitorName].append(runtime)
        data[RESULT][ds][competitorName].append(result)

    mem_limit = "unlimited"
    column_share = "100"
    row_share = "100"
    experiment = "competitors"

    for ds in datasets:
        for c in competitor:
            for idx, runtime in enumerate(data[RUNTIME][ds][c]):
                result = data[RESULT][ds][c][idx]
                algorithm = c[:-3]
                sim = c[-3:]
                row = [idx, algorithm, ds, sim, mem_limit, row_share, column_share, experiment, runtime, result]
                writer.writerow(row)

elif sys.argv[1] == "column":
    # column_scaling data
    # separate plot for 2 DS:
    #	5 data points
    #		3 runs each -> average
    datasets = ["WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "column_scaling_token.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d+) - run (\d)')
    column_sizes = {datasets[0]: [2, 3, 4, 5, 6, 7, 8, 9, 10], datasets[1]: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]}

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
    similarity = "0.4"

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, similarity, mem_limit, row_share, size, experiment, runtime, result]
                writer.writerow(row)
elif sys.argv[1] == "grow_row":
    # row_scaling data
    # separate plot for 2 DS:
    #	10 data points
    #		3 runs each -> average
    datasets = ["WIKIPEDIA", "TPCH"]
    data_path = pathlib.Path(script_path / "new_grow_row_scaling_token_only.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d) - run (\d) - token ([A-Z][a-z]+)')
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
        token = regex_match.group(4)

        runtime_line = input.readline()
        runtime = int(runtime_regex.search(runtime_line).group(1))
        result_line = input.readline()
        result = int(number_regex.search(result_line).group(1))

        if token == "True":
            data[RUNTIME][ds][dp].append(runtime)
            data[RESULT][ds][dp].append(result)

    algorithm = "SAWFISH"
    similarity = "0.4"
    mem_limit = "unlimited"
    column_share = "100"
    experiment = "grow_row"
    sample_base = "TRUE"

    for ds in datasets:
        for dp in range(data_points):
            for idx, runtime in enumerate(data[RUNTIME][ds][dp]):
                row_share = (dp + 1) * 10
                result = data[RESULT][ds][dp][idx]
                row = [idx, algorithm, ds, similarity, mem_limit, row_share, column_share, sample_base, experiment, runtime, result]
                writer.writerow(row)
elif sys.argv[1] == "column_CENSUS":
    # column_scaling data
    # separate plot for 2 DS:
    #	5 data points
    #		3 runs each -> average
    datasets = ["CENSUS"]
    data_path = pathlib.Path(script_path / "column_scaling_token_CENSUS.txt").resolve()
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
    experiment = "column"
    algorithm = "SAWFISH"
    similarity = "0.4"
    sample_base = "TRUE"

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, similarity, mem_limit, row_share, size, sample_base, experiment, runtime, result]
                writer.writerow(row)
elif sys.argv[1] == "column_IMDB":
    # column_scaling data
    # separate plot for 2 DS:
    #	5 data points
    #		3 runs each -> average
    datasets = ["IMDB"]
    data_path = pathlib.Path(script_path / "column_scaling_token_IMDB.txt").resolve()
    id_regex = re.compile('DS ([A-Z]+) - LEN (\d+) - run (\d)')
    column_sizes = {datasets[0]: [4, 13, 22, 31, 40, 49, 58, 67, 76, 85]}

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
    similarity = "0.4"
    sample_base = "TRUE"

    for ds in datasets:
        for size in column_sizes[ds]:
            for idx, runtime in enumerate(data[RUNTIME][ds][size]):
                result = data[RESULT][ds][size][idx]
                row = [idx, algorithm, ds, similarity, mem_limit, row_share, size, sample_base, experiment, runtime, result]
                writer.writerow(row)
else:
    print("unknown option")
    exit(1)
