import csv
import random
import pathlib
import subprocess

script_path = pathlib.Path(__file__).parent.resolve()
data_path = pathlib.Path(script_path / "../data/").resolve()
sample_path = pathlib.Path(data_path / "current_row_samples.csv").resolve()
result_path = pathlib.Path(script_path / "grow_row_scaling_IMDB.txt").resolve()

datasets = ["IMDB"] #["CENSUS"] #["WIKIPEDIA", "TPCH"]
tokenMode = [True] #[True, False]
number_of_datapoints = 10
number_of_samples = 10

for ds in datasets:
    with open(pathlib.Path(data_path / (ds + ".csv")).resolve(), newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=';', quotechar='"', escapechar='\\'))

    num_lines = len(data)
    header = data[0]
    
    for tok in tokenMode:
        for sample_idx in range(number_of_samples):
            selected_rows = set()
            for data_point in range(number_of_datapoints):
                unselected_rows = []
                for i in range(1, num_lines):
                    if i not in selected_rows:
                        unselected_rows.append(i)
                newly_selected = random.sample(unselected_rows, int((num_lines - 1) / 10))
                selected_rows.update(newly_selected)
                print(len(selected_rows))
                with open(sample_path, 'w', newline='') as writefile:
                    writer = csv.writer(writefile, delimiter=';', quotechar='"', escapechar='\\')
                    writer.writerow(header)
                    for row_id in selected_rows:
                        writer.writerow(data[row_id])
                if tok:
                    options = "tokenMode:true,similarityThreshold:0.4"
                else:
                    options = "editDistanceThreshold:1"
                command = ("java -Xmx50g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:grow_row_scaling_token/result_%s_%s_%s_%s --algorithm de.metanome.algorithms.similarity_ind.AlgorithmInterface --files ../data/current_row_samples.csv --input-key INPUT_FILES --separator ';' --escape \\\\ --header --algorithm-config maxMemoryUsagePercentage:70 " + options + " | tail -n 2") % (ds, data_point, sample_idx, str(tok))
                #print(command)
                output_string = "DS %s - LEN %s - run %s - token %s" % (ds, data_point, sample_idx, str(tok))
                print(output_string)
                output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
                print(output.stdout)
                with open(result_path, 'a') as f:
                    f.write("%s\n" % output_string)
                    f.write(output.stdout)
