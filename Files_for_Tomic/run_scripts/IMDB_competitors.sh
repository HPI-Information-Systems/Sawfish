#!/usr/bin/env bash
set -euo pipefail

algorithms=("de.metanome.algorithms.similarity_ind.AlgorithmInterface" "de.metanome.algorithms.sindbaseline.SINDBaseline" "de.metanome.algorithms.binder.BinderFileAlgorithm")
#algorithms=("de.metanome.algorithms.binder.BinderFileAlgorithm")

for algo in ${algorithms[@]}; do
	for (( i = 0; i < 3; i++ )); do
		echo "ALG $algo - run $i"
		config=""
		if [[ $algo == "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
			config="MAX_MEMORY_USAGE_PERCENTAGE:70"
		elif [[ $algo = "de.metanome.algorithms.sindbaseline.SINDBaseline" ]]; then
			config="editDistanceThreshold:0"
		else
			config="editDistanceThreshold:0,maxMemoryUsagePercentage:70"
		fi
		
		java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_IMDB_"$algo"_0_"$i" --algorithm "$algo" --files ../data/IMDB/*.csv --input-key INPUT_FILES --separator "," --escape "\\" --algorithm-config "$config" | tail -n 2
	done
done

