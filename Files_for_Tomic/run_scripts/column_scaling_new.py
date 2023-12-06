import csv
import random
import pathlib
import subprocess

script_path = pathlib.Path(__file__).parent.resolve()
config_path = pathlib.Path(script_path / "selected_columns_CENSUS.txt").resolve()
data_path = pathlib.Path(script_path / "../data/").resolve()
sample_path = pathlib.Path(data_path / "current_samples.csv").resolve()
result_path = pathlib.Path(script_path / "column_scaling_CENSUS.txt").resolve()

datasets = ["CENSUS"] #["WIKIPEDIA", "TPCH"]
column_sizes = {datasets[0]: [2,6,10]} # [4,8,12,14,18,22,26,30,34,38]} {datasets[0]: [3, 5, 7, 9], datasets[1]: [5, 15, 25, 35, 45]}
column_count = {datasets[0]: 42} #{datasets[0]: 11, datasets[1]: 55}
number_of_samples = 30
column_combinations = {datasets[0]: []} #, datasets[1]: []}

for ds in datasets:
    for column_size in column_sizes[ds]:
        current_combinations_set = set()
        while len(current_combinations_set) != number_of_samples:
            if ds == datasets[0] and column_size == 10 and len(current_combinations_set) > 10:
                break
            current_combination = set()
            while len(current_combination) != column_size:
                current_combination.add(random.randrange(column_count[ds]))
            current_combinations_set.add(frozenset(current_combination))
        column_combinations[ds].append(current_combinations_set)

with open(config_path, 'w') as f:
    for ds in datasets:
        f.write(ds + "\n")
        for combinations_set in column_combinations[ds]:
            for combination in combinations_set:
                for item in combination:
                    f.write("%s, " % item)
                f.write("\n")

for ds in datasets:
    with open(pathlib.Path(data_path / (ds + ".csv")).resolve(), newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=';', quotechar='"', escapechar='\\'))

    for current_combinations_set in column_combinations[ds]:
        for idx, current_combination in enumerate(current_combinations_set):
            with open(sample_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                index = 0
                while True:
                    finished_columns = 0
                    row = []
                    for column in current_combination:
                        if index >= len(data):
                            finished_columns = len(current_combination)
                            break
                        if data[index][column] != "":
                            row.append(data[index][column])
                        else:
                            row.append("")
                            finished_columns += 1
                    if finished_columns == len(current_combination):
                        break
                    writer.writerow(row)
                    index += 1
            command = "java -Xmx2g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:column_scaling/result_%s_%s_%s --algorithm de.metanome.algorithms.similarity_ind.AlgorithmInterface --files ../data/current_samples.csv --input-key INPUT_FILES --separator ';' --escape \\\\ --header --algorithm-config editDistanceThreshold:1 maxMemoryUsagePercentage:70 | tail -n 2" % (ds, len(current_combination), idx)
            output_string = "DS %s - LEN %s - run %s" % (ds, len(current_combination), idx)
            print(output_string)
            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            print(output.stdout)
            with open(result_path, 'a') as f:
                f.write("%s\n" % output_string)
                f.write(output.stdout)
            # moveCommand = "mv target/timingStats.csv target/column_scaling/timingStats_%s_%s_%s.csv" % (ds, len(current_combination), idx)
            # subprocess.run(moveCommand, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
