#!/usr/bin/env bash
set -euo pipefail

datasets=("CENSUS" "WIKIPEDIA" "TPCH")
algorithms=("de.metanome.algorithms.similarity_ind.AlgorithmInterface" "de.metanome.algorithms.sindbaseline.SINDBaseline" "de.metanome.algorithms.binder.BinderFileAlgorithm")

for dataS in ${datasets[@]}; do
	for algo in ${algorithms[@]}; do
		for (( i = 0; i < 3; i++ )); do
				echo "DS $dataS - ALG $algo - ED 0 - run $i"
				config=""
				if [[ $algo == "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
					config="MAX_MEMORY_USAGE_PERCENTAGE:70"
				elif [[ $algo = "de.metanome.algorithms.sindbaseline.SINDBaseline" ]]; then
					config="editDistanceThreshold:0"
				else
					config="editDistanceThreshold:0,maxMemoryUsagePercentage:70"
				fi
				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_0_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --escape "\\" --algorithm-config "$config" | tail -n 2
		done
	done
done

for dataS in ${datasets[@]}; do
	for algo in ${algorithms[@]}; do
		if [[ $algo != "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
			for (( i = 0; i < 3; i++ )); do
				echo "DS $dataS - ALG $algo - ED 1 - run $i"
				config="editDistanceThreshold:1"
				if [[ $algo != "de.metanome.algorithms.sindbaseline.SINDBaseline" ]]; then
					config+=",maxMemoryUsagePercentage:70"
				fi
				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_1_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --escape \\ --algorithm-config "$config" | tail -n 2
			done
		fi
	done
done
