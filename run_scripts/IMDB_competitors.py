import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/related_work"
result_file = pathlib.Path(script_path / "../results/combined_stats/all_results.csv").resolve()


algorithms = ["de.metanome.algorithms.similarity_ind.AlgorithmInterface", "de.metanome.algorithms.sindbaseline.SINDBaseline", "de.metanome.algorithms.binder.BinderFileAlgorithm"]
classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/similarity_ind-1.1-SNAPSHOT.jar"'

with open(result_file, 'a') as f:
    f.write("\n")

for algo in algorithms:
    for i in range(0, 3):
        print(f"ALG {algo} - run {i}")

        config = ""
        simplified_algo_name=""
        if algo == "de.metanome.algorithms.binder.BinderFileAlgorithm":
            config = "MAX_MEMORY_USAGE_PERCENTAGE:70"
            simplified_algo_name = "BINDER"
        elif algo == "de.metanome.algorithms.sindbaseline.SINDBaseline":
            config = "editDistanceThreshold:0"
            simplified_algo_name = "BASELINE"
        else:
            config = "editDistanceThreshold:0,maxMemoryUsagePercentage:70"
            simplified_algo_name = "SAWFISH"
        
        output_file = f'"{result_dir_path}/result_IMDB_{algo}_0_{i}"'
        input_file = f'"{data_path}/IMDB.csv"'

        command = (
            f'java -Xmx32g -cp {classpath} de.metanome.cli.App '
            f'-o file:{output_file} '
            f'--algorithm {algo} '
            f'--files {input_file} '
            f'--input-key INPUT_FILES '
            f'--header '
            f'--separator ";" '
            f'--escape \\\ '
            f'--algorithm-config {config} '
            f'| tail -n 2'
        )

        output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
        print(output.stdout)
        if "Error" not in output.stdout:
            with open(result_file, 'a') as f:
                dataset = "IMDB"
                competitor = ["SAWFISH", "BINDER"]
                runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                results_count = re.search(r"Number of results: (\d+)", output.stdout)
                if runtime and results_count:
                    runtime = runtime.group(1)
                    results_count = results_count.group(1)
                    f.write("%s,%s,%s,0,unlimited,100,100,True,competitors_imdb,%s,%s\n" % (i, simplified_algo_name, dataset, runtime, results_count))
        else:
            print("Error detected in the output. Program stopped.")
            exit(1)