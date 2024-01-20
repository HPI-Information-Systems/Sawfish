import csv
import pathlib
import random
import re
import subprocess

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
sample_path = pathlib.Path(data_path / "current_row_samples.csv").resolve()
result_dir_path = "/row_scaling_ed"
experiment_id = 878
num_experiments = 1547

result_file = pathlib.Path(script_path / "../results/combined_stats/results_ed.csv")

datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]
number_of_datapoints = 10
number_of_samples = 10

for ds in datasets:
    with open(pathlib.Path(data_path / (ds + ".csv")).resolve(), newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=';', quotechar='"', escapechar='\\'))

    num_lines = len(data)
    header = data[0]
    
    for sample_idx in range(number_of_samples):
        selected_rows = set()
        for data_point in range(number_of_datapoints - 1):
            unselected_rows = []
            for i in range(1, num_lines):
                if i not in selected_rows:
                    unselected_rows.append(i)
            newly_selected = random.sample(unselected_rows, int((num_lines - 1) / number_of_datapoints))
            selected_rows.update(newly_selected)
            with open(sample_path, 'w', newline='') as writefile:
                writer = csv.writer(writefile, delimiter=';', quotechar='"', escapechar='\\')
                writer.writerow(header)
                for row_id in selected_rows:
                    writer.writerow(data[row_id])
                
                classpath = f'"{metanome_path / "metanome-cli-1.1.1.jar"}":"{metanome_path / "sawfish-1.1-SNAPSHOT.jar"}"'
                output_file_path = f'"{result_dir_path + f"/result_{ds}_{data_point}_{sample_idx}_False"}"'
                samples_file_path = f'"{data_path / "current_row_samples.csv"}"'

                command = (
                    f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                    f'-o file:{output_file_path} '
                    f'--algorithm de.metanome.algorithms.sawfish.SawfishInterface '
                    f'--files {samples_file_path} '
                    f'--input-key INPUT_FILES '
                    f'--separator ";" '
                    f'--escape \\\ '
                    f'--header '
                    f'--algorithm-config maxMemoryUsagePercentage:70,editDistanceThreshold:1 '
                    f'| tail -n 2'
                    )

                print(f"Experiment {experiment_id} / {num_experiments}")
                experiment_id += 1

                output_string = "DS %s - LEN %s - run %s - token False" % (ds, data_point, sample_idx)
                print(output_string)
                output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
                print(output.stdout)
                if "Error" not in output.stdout:
                    with open(result_file, 'a') as f:
                        runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                        results_count = re.search(r"Number of results: (\d+)", output.stdout)
                        if runtime and results_count:
                            runtime = runtime.group(1)
                            results_count = results_count.group(1)

                            f.write("%s,SAWFISH,%s,1,%s,100,False,row,%s,%s\n" % (sample_idx, ds, (data_point + 1) * 10, runtime, results_count))
