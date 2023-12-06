#!/usr/bin/env bash
set -euo pipefail

datasets=("WIKIPEDIA")

for ds in $datasets; do
	for ((edit_distance = 2 ; edit_distance < 8 ; edit_distance++)); do
		for (( i = 0; i < 3; i++ )); do
			echo "$ds - ED $edit_distance - run $i"
			java -Xmx2g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:edit_distance/result_"$ds"_"$edit_distance"_"$i" --algorithm de.metanome.algorithms.similarity_ind.AlgorithmInterface --files ../data/"$ds"/*.csv --input-key INPUT_FILES --separator ";" --escape \\ --algorithm-config runBinderFirst:false ignoreShortStrings:false numericOptimizations:false errorDistance:"$edit_distance" measureTime:true maxMemoryUsagePercentage:70 | tail -n 2
			mv target/timingStats.csv target/timingStats_"$ds"_"$edit_distance"_"$i".csv
		done
	done
done
