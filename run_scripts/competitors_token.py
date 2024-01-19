# --------- PROBABLY NOT USED IN ORIGINAL RESULTS -----------

import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/related_work"
result_file = pathlib.Path(script_path / "../results/combined_stats/all_results_token.csv").resolve()

datasets = ["CENSUS", "WIKIPEDIA", "TPCH"]
algorithms=("de.metanome.algorithms.similarity_ind.AlgorithmInterface" "de.metanome.algorithms.tokenbaseline.TokenBaseline")
simplified_algo_name = "BASELINE"

classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/similarity_ind-1.1-SNAPSHOT.jar"'

for ds in datasets:
    for algorithm in algorithms:
        for sim in [0.4, 1]:
            for i in range(0, 3):
                print(f"DS {ds} - ALG {algorithm} - SIM {sim} - run {i}")

                config=f"maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:{sim}"

                output_file = f'"{result_dir_path}/token_result_{ds}_{algorithm}_{0 if sim == 1 else 1}_{i}"'
                input_file = f'"{data_path}/{ds}.csv"'

                max_heap_size = "Xmx32g" if ds == "IMDB" else "Xmx4g"
                separator = "," if ds == "IMDB" else ";"

                command = (
                    f'java -{max_heap_size} -cp {classpath} de.metanome.cli.App '
                    f'-o file:{output_file} '
                    f'--algorithm {algorithm} '
                    f'--files {input_file} '
                    f'--input-key INPUT_FILES '
                    f'--separator "{separator}" '
                    f'--escape \\\ '
                    f'--algorithm-config {config} '
                    f'| tail -n 2'
                )

                output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
                print(output.stdout)

                if "Error" not in output.stdout:
                    with open(result_file, 'a') as f:
                        runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                        results_count = re.search(r"Number of results: (\d+)", output.stdout)
                        if runtime and results_count:
                            runtime = runtime.group(1)
                            results_count = results_count.group(1)

                            f.write("%s,%s,%s,%s,unlimited,100,100,FALSE,competitors,%s,%s\n" % (i, simplified_algo_name, ))
                            
                else:
                    print("Error detected in the output. Program stopped.")
                    exit(1)