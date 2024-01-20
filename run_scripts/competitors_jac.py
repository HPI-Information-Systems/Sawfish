import pathlib
import re
import subprocess

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/related_work"
result_file = pathlib.Path(script_path / "../results/combined_stats/results_jac.csv").resolve()
experiment_id = 755
num_experiments = 1547

datasets = ["CENSUS", "WIKIPEDIA", "TPCH", "IMDB"]
algorithms=["de.metanome.algorithms.sawfish.SawfishInterface", "de.metanome.algorithms.tokenbaseline.TokenBaseline"]

classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/sawfish-1.1-SNAPSHOT.jar"'

for ds in datasets:
    for algorithm in algorithms:
        for sim in [0.4, 1]:
            for i in range(0, 3):

                config=f"similarityThreshold:{sim}"
                simplified_algo_name = "BASELINE"
                if algorithm == "de.metanome.algorithms.sawfish.SawfishInterface":
                    config += ",tokenMode:true,maxMemoryUsagePercentage:70,"
                    simplified_algo_name = "SAWFISH"

                output_file = f'"{result_dir_path}/token_result_{ds}_{algorithm}_{0 if sim == 1 else 1}_{i}"'
                input_file = f'"{data_path}/{ds}.csv"'

                max_heap_size = "Xmx32g" if ds == "IMDB" else "Xmx8g"

                command = (
                    f'java -{max_heap_size} -cp {classpath} de.metanome.cli.App '
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

                print(f"DS {ds} - ALG {algorithm} - SIM {sim} - run {i}")

                output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
                print(output.stdout)

                if "Error" not in output.stdout:
                    with open(result_file, 'a') as f:
                        runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                        results_count = re.search(r"Number of results: (\d+)", output.stdout)
                        if runtime and results_count:
                            runtime = runtime.group(1)
                            results_count = results_count.group(1)
                            f.write("%s,%s,%s,%s,100,100,competitors,%s,%s\n" % (i, simplified_algo_name, ds, sim, runtime, results_count))
                            
                else:
                    print("Error detected in the output. Program stopped.")
                    exit(1)
