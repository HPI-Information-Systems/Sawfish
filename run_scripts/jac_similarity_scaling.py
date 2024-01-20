import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/token_similarity"
result_file = pathlib.Path(script_path / "../results/combined_stats/results_jac.csv").resolve()
experiment_id = 851
num_experiments = 1547

datasets = ["TPCH"]
algorithm = "de.metanome.algorithms.sawfish.SawfishInterface"
classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/sawfish-1.1-SNAPSHOT.jar"'

for ds in datasets:
    for similarity in range(1, 10):
        for i in range(0, 3):
            config = f"tokenMode:true,maxMemoryUsagePercentage:70,similarityThreshold:0.{similarity}"
            
            output_file = f'"{result_dir_path}/result_{ds}_0{similarity}_{i}"'
            input_file = f'"{data_path}/{ds}.csv"'

            command = (
                f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                f'-o file:{output_file} '
                f'--algorithm {algorithm} '
                f'--files {input_file} '
                f'--input-key INPUT_FILES '
                f'--header '
                f'--separator ";" '
                f'--escape \\\ '
                f'--algorithm-config {config} '
                f'| tail -n 2'
            )

            print(f"Experiment {experiment_id} / {num_experiments}")
            experiment_id += 1

            print(f"{ds} - SIM 0.{similarity} - run {i}")

            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
            print(output.stdout)
            
            if "Error" not in output.stdout:
                with open(result_file, 'a') as f:
                    dataset = "TPCH"
                    simplified_algo_name="SAWFISH"
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)
                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)
                        f.write("%s,%s,%s,0.%s,100,100,sim,%s,%s\n" % (i, simplified_algo_name, dataset, similarity, runtime, results_count))
            else:
                print("Error detected in the output. Program stopped.")
                exit(1)