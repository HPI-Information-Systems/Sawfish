import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
config_path = pathlib.Path(script_path / "selected_columns_CENSUS.txt").resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
sample_path = pathlib.Path(data_path / "current_samples.csv").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/column_scaling/"
result_file = pathlib.Path(script_path / "../results/combined_states/all_results.csv")


datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]
column_sizes = {datasets[0]: [2, 6, 10, 14, 18, 22, 26, 30, 34, 38], datasets[1]: [2, 3, 4, 5, 6, 7, 8, 9, 10], datasets[2]: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]}
column_count = {datasets[0]: 42, datasets[1]: 11, datasets[2]: 55}
number_of_samples = 30
column_combinations = {datasets[0]: [], datasets[1]: [], datasets[2]: []}

for ds in datasets:
    for column_size in column_sizes[ds]:
        print(column_size)
        current_combinations_set = set()
        while len(current_combinations_set) != number_of_samples:
            if ds == datasets[0] and column_size == 10 and len(current_combinations_set) > 10:
                break
            current_combination = set()
            # TODO: At ds == datasets[1] and column_size 10,
            # It repeats forever (the len of current_combination goes up to 9, and then resets to an empty one)
            if ds == datasets[1] and column_size == 10:
                print(len(current_combinations_set))
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
            classpath = f'"{metanome_path / "metanome-cli-1.1.1.jar"}":"{metanome_path / "similarity_ind-1.1-SNAPSHOT.jar"}"'
            output_file_path = f'"{result_dir_path}/result_{ds}_{len(current_combination)}_{idx}"'
            samples_file_path = f'"{data_path / "current_samples.csv"}"'

            command = (
                f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                f'-o file:{output_file_path} '
                f'--algorithm de.metanome.algorithms.similarity_ind.AlgorithmInterface '
                f'--files {samples_file_path} '
                f'--input-key INPUT_FILES '
                f'--separator ";" '
                f'--escape \\\\ '
                f'--header '
                f'--algorithm-config editDistanceThreshold:1,maxMemoryUsagePercentage:70 '
                f'| tail -n 2'       
            )
            output_string = "DS %s - LEN %s - run %s" % (ds, len(current_combination), idx)
            print(output_string)
            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            print(output.stdout)

            moveCommand = "mv target/timingStats.csv ../results/column_scaling/target/timingStats_%s_%s_%s.csv" % (ds, len(current_combination), idx)
            subprocess.run(moveCommand, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

            if "Error" not in output.stdout.lower():
                with open(result_file, 'a') as f:
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)
                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)

                        # TODO: Calculate column share
                        f.write("%s,SAWFISH,%s,1,unlimited,100,%s,False,column,%s,%s\n" % (idx, ds,"TODO: FILL", runtime, results_count))