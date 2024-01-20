import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/edit_distance"
results_dir = pathlib.Path(script_path / "../results")
result_file = pathlib.Path(results_dir / "combined_stats/results_ed.csv").resolve()
timing_stats_dir = pathlib.Path(results_dir / "timingStats").resolve()

datasets = ["WIKIPEDIA", "CENSUS"]

classpath = classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/sawfish-1.1-SNAPSHOT.jar"'
simplified_algo_name = "SAWFISH"
algorithm = 'de.metanome.algorithms.sawfish.SawfishInterface'

for ds in datasets:
    for edit_distance in range(2, 7):
        for i in range(3):
            print(f"{ds} - ED {edit_distance} - run {i}")

            output_file = f'"{result_dir_path}/result_{ds}_{edit_distance}_{i}"'
            input_file = f'"{data_path}/{ds}.csv"'

            config = f'editDistanceThreshold:{edit_distance},measureTime:true,maxMemoryUsagePercentage:70'

            command = (
                f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                f'-o file:{output_file} '
                f'--algorithm {algorithm} '
                f'--files {input_file} '
                f'--header '
                f'--input-key INPUT_FILES '
                f'--separator ";" '
                f'--escape \\\ '
                f'--algorithm-config {config} '
                f'| tail -n 2'
            )

            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
            print(output.stdout)
            moveCommand = "mv %s/timingStats.csv %s/timingStats_%s_%s_%s.csv" % (results_dir, timing_stats_dir, ds, str(edit_distance), i)
            subprocess.run(moveCommand, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

            if "Error" not in output.stdout:
                with open(result_file, 'a') as f:
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)

                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)
                        f.write("%s,%s,%s,%s,100,100,False,ed,%s,%s\n" % (i, simplified_algo_name, ds, edit_distance, runtime, results_count))

for ds in (datasets + ["TPCH"]):
    for edit_distance in range(2):
        for i in range(3):
            print(f"{ds} - ED {edit_distance} - run {i}")

            output_file = f'"{result_dir_path}/timingStats_{ds}_{edit_distance}_{i}"'
            input_file = f'"{data_path}/{ds}.csv"'

            config = f'editDistanceThreshold:{edit_distance},measureTime:true,maxMemoryUsagePercentage:70'

            command = (
                f'java -Xmx8g -cp {classpath} de.metanome.cli.App '
                f'-o file:{output_file} '
                f'--algorithm {algorithm} '
                f'--files {input_file} '
                f'--header '
                f'--input-key INPUT_FILES '
                f'--separator ";" '
                f'--escape \\\ '
                f'--algorithm-config {config} '
                f'| tail -n 2'
            )

            output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True, cwd=pathlib.Path(script_path / ".."))
            print(output.stdout)
            moveCommand = "mv %s/timingStats.csv %s/timingStats_%s_%s_%s.csv" % (results_dir, timing_stats_dir, ds, str(edit_distance), i)
            subprocess.run(moveCommand, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

            if "Error" not in output.stdout:
                with open(result_file, 'a') as f:
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)

                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)
                        f.write("%s,%s,%s,%s,100,100,False,ed,%s,%s\n" % (i, simplified_algo_name, ds, edit_distance, runtime, results_count))
