#!/usr/bin/env bash
set -euo pipefail

datasets=("TPCH")

for ds in $datasets; do
	for ((similarity = 1 ; similarity < 10 ; similarity++)); do
		for (( i = 0; i < 3; i++ )); do
			echo "$ds - SIM 0.$similarity - run $i"
			java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:token_similarity/result_"$ds"_"$similarity"_"$i" --algorithm de.metanome.algorithms.similarity_ind.AlgorithmInterface --files ../data/"$ds"/*.csv --input-key INPUT_FILES --separator ";" --escape \\ --algorithm-config runBinderFirst:false ignoreShortStrings:false measureTime:false tokenMode:true maxMemoryUsagePercentage:70 similarityThreshold:0."$similarity" | tail -n 2
		done
	done
done
