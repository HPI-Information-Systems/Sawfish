import csv
import random
import pathlib
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor

script_path = pathlib.Path(__file__).parent.resolve()
config_path = pathlib.Path(script_path / "selected_columns_token.txt").resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
sample_path = pathlib.Path(data_path / "current_samples.csv").resolve()
result_dir_path = "/column_scaling_jac/"
result_file = pathlib.Path(script_path / "../results/combined_stats/results_jac.csv")

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
column_sizes = {datasets[0]: [2, 6, 10, 14, 18, 22, 26, 30, 34, 38], datasets[1]: [2, 3, 4, 5, 6, 7, 8, 9, 10], datasets[2]: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50], datasets[3]: [4, 13, 22, 31, 40, 49, 58, 67, 76, 85]}
column_count = {datasets[0]: 42, datasets[1]: 11, datasets[2]: 55, datasets[3]: 94}
number_of_samples = 10
column_combinations = {datasets[0]: [], datasets[1]: [], datasets[2]: [], datasets[3]: []}
number_of_process = 8

def write_subparts(data, identifier, current_combination):
    with open(pathlib.Path(data_path / ("current_samples_%s.csv" % identifier)).resolve(), 'w', newline='') as csvfile:
        num_lines = int(len(data) / number_of_process)
        start_idx = num_lines * identifier
        end_idx = len(data) if identifier == number_of_process - 1 else start_idx + num_lines
        output_rows = []

        for idx in range(start_idx, end_idx):
            finished_columns = 0
            row = []
            for column in current_combination:
                if data[idx][column] != "":
                    row.append(data[idx][column])
                else:
                    row.append("")
                    finished_columns += 1
            if finished_columns == len(current_combination):
                    break
            output_rows.append('"' + '";"'.join(row) + '"\n')
        csvfile.writelines(output_rows)


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
        data = list(csv.reader(csvfile, delimiter=';', quotechar='"'))

    for current_combinations_set in column_combinations[ds]:
        for idx, current_combination in enumerate(current_combinations_set):
            with ThreadPoolExecutor(number_of_process) as exe:
                a = [exe.submit(write_subparts, data, i, current_combination) for i in range(number_of_process)]
                for x in a:
                    x.result()

            mv_command = "cat %s > " % ' '.join([f'"{str(pathlib.Path(data_path / ("current_samples_%s.csv" % i)).resolve())}"' for i in range(number_of_process)]) + f'"{str(sample_path)}"'
            subprocess.run(mv_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

            classpath = f'"{metanome_path / "metanome-cli-1.1.1.jar"}":"{metanome_path / "sawfish-1.1-SNAPSHOT.jar"}"'

            output_file_path = f'"{result_dir_path}/result_{ds}_{len(current_combination)}_{idx}"'
            samples_file_path = f'"{data_path / "current_samples.csv"}"'

            command = (
                f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                f'-o file:{output_file_path} '
                f'--algorithm de.metanome.algorithms.sawfish.SawfishInterface '
                f'--files {samples_file_path} '
                f'--input-key INPUT_FILES '
                f'--separator ";" '
                f'--escape \\\ '
                f'--header '
                f'--algorithm-config maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:0.4 '
                f'| tail -n 2'
            )
            output_string = "DS %s - LEN %s - run %s" % (ds, len(current_combination), idx)
            print(output_string)
            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
            print(output.stdout)
            if "Error" not in output.stdout.lower():
                with open(result_file, 'a') as f:
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)
                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)

                        f.write("%s,SAWFISH,%s,0.4,100,%s,column,%s,%s\n" % (idx, ds,len(current_combination), runtime, results_count))
