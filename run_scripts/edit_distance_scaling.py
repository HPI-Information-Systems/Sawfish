import csv
import random
import pathlib
import subprocess
import re

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../datasets/").resolve()
metanome_path = pathlib.Path(script_path / "../metanome/").resolve()
result_dir_path = "/timingStats/edit_distance"
result_file = pathlib.Path(script_path / "../results/combined_stats/results_ed.csv").resolve()

datasets = ["WIKIPEDIA", "CENSUS"]

classpath = classpath = f'"{metanome_path}/metanome-cli-1.1.1.jar":"{metanome_path}/sawfish-1.1-SNAPSHOT.jar"'
simplified_algo_name = "SAWFISH"
algorithm = 'de.metanome.algorithms.sawfish.SawfishInterface'

for ds in datasets:
    for edit_distance in range(2, 8):
        for i in range(3):
            print(f"{ds} - ED {edit_distance} - run {i}")

            output_file = f'"{result_dir_path}/timingStats_{ds}_{edit_distance}_{i}"'
            input_file = f'"{data_path}/{ds}.csv"'


            config = f'runBinderFirst:false ignoreShortStrings:false editDistanceThreshold:{edit_distance} measureTime:true maxMemoryUsagePercentage:70'

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

            if "Error" not in output.stdout:
                with open(result_file, 'a') as f:
                    runtime = re.search(r"Elapsed time: [^)]*\((\d+) ms\)", output.stdout)
                    results_count = re.search(r"Number of results: (\d+)", output.stdout)

                    if runtime and results_count:
                        runtime = runtime.group(1)
                        results_count = results_count.group(1)
                        f.write("%s,%s,%s,%s,100,100,False,ed,%s,%s\n" % (i, simplified_algo_name, ds, edit_distance, runtime, results_count))

