import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome").resolve()
result_dir_path = "/related_work"
result_file = pathlib.Path(script_path / "../results/combined_stats/results_ed.csv")

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
algorithms = ["de.metanome.algorithms.sawfish.SawfishInterface", "de.metanome.algorithms.sindbaseline.SINDBaseline", "de.metanome.algorithms.binder.BinderFileAlgorithm"]
classpath = classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/sawfish-1.1-SNAPSHOT.jar"'

for ds in datasets:
    for algo in algorithms:
            for i in range(0, 3):
                print(f"DS {ds} - ALG {algo} - ED 0 - run {i}")

                config=""
                simplified_algo_name=""

                if algo == "de.metanome.algorithms.binder.BinderFileAlgorithm":
                     config="MAX_MEMORY_USAGE_PERCENTAGE:70"
                     simplified_algo_name = "BINDER"
                elif algo == "de.metanome.algorithms.sindbaseline.SINDBaseline":
                     config="editDistanceThreshold:0"
                     simplified_algo_name = "BASELINE"
                else:
                     config="editDistanceThreshold:0,maxMemoryUsagePercentage:70"
                     simplified_algo_name = "SAWFISH"
                
                output_file = f'"{result_dir_path}/result_{ds}_{algo}_0_{i}"'
                input_file = f'"{data_path}/{ds}.csv"'

                max_heap_size = "Xmx32g" if ds == "IMDB" else "Xmx8g"

                command = (
                     f'java -{max_heap_size} -cp {classpath} de.metanome.cli.App '
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

                print(command)

                output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
                print(output.stdout)

                if "Error" not in output.stdout:
                     with open(result_file, 'a') as f:
                        runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                        results_count = re.search(r"Number of results: (\d+)", output.stdout)

                        if runtime and results_count:
                             runtime = runtime.group(1)
                             results_count = results_count.group(1)
                             f.write("%s,%s,%s,0,100,100,True,competitors,%s,%s\n" % (i, simplified_algo_name, ds, runtime, results_count))

for ds in datasets:
    if ds != "IMDB":
        for algo in algorithms:
                if algo != "de.metanome.algorithms.binder.BinderFileAlgorithm":
                    for i in range(0, 3):
                        print(f"DS {ds} - ALG {algo} - ED 1 - run {i}")

                        config="editDistanceThreshold:1"
                        simplified_algo_name=""

                        if algo != "de.metanome.algorithms.sindbaseline.SINDBaseline":
                            config= config +",maxMemoryUsagePercentage:70,ignoreShortStrings:true"
                            simplified_algo_name = "SAWFISH"
                        else:
                            simplified_algo_name = "BASELINE"
                        
                        output_file = f'"{result_dir_path}/result_{ds}_{algo}_1_{i}"'
                        input_file = f'"{data_path}/{ds}.csv"'

                        command = (
                            f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
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
                                runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                                results_count = re.search(r"Number of results: (\d+)", output.stdout)

                                if runtime and results_count:
                                    runtime = runtime.group(1)
                                    results_count = results_count.group(1)
                                    f.write("%s,%s,%s,1,100,100,True,competitors,%s,%s\n" % (i, simplified_algo_name, ds, runtime, results_count))
