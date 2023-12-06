#!/usr/bin/env bash
set -euo pipefail

datasets=("CENSUS" "WIKIPEDIA" "TPCH")
#algorithm="de.metanome.algorithms.similarity_ind.AlgorithmInterface"
algorithm="de.metanome.algorithms.tokenbaseline.TokenBaseline"

for dataS in ${datasets[@]}; do
	for (( i = 0; i < 3; i++ )); do
		echo "DS $dataS - ALG $algorithm - SIM 1 - run $i"
		#config="maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:1.0"
		config="similarityThreshold:1.0"
		java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/token_result_"$dataS"_"$algorithm"_0_"$i" --algorithm "$algorithm" --files ../data/"$dataS"/*.csv --input-key INPUT_FILES --separator ";" --escape "\\" --algorithm-config "$config" | tail -n 2
	done
done

for dataS in ${datasets[@]}; do
	for (( i = 0; i < 3; i++ )); do
		echo "DS $dataS - ALG $algorithm - SIM 0.4 - run $i"
		#config="maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:0.4"
		config="similarityThreshold:0.4"
		java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/token_result_"$dataS"_"$algorithm"_1_"$i" --algorithm "$algorithm" --files ../data/"$dataS"/*.csv --input-key INPUT_FILES --separator ";" --escape \\ --algorithm-config "$config" | tail -n 2
	done
done

dataset="IMDB"
for (( i = 0; i < 3; i++ )); do
	echo "DS $dataset - ALG $algorithm - SIM 1 - run $i"
	#config="maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:1.0"
	config="similarityThreshold:1.0"
	java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/token_result_"$dataset"_"$algorithm"_0_"$i" --algorithm "$algorithm" --files ../data/IMDB/*.csv --input-key INPUT_FILES --separator "," --escape "\\" --algorithm-config "$config" | tail -n 2
done

for (( i = 0; i < 3; i++ )); do
	echo "DS $dataset - ALG $algorithm - SIM 0.4 - run $i"
	#config="maxMemoryUsagePercentage:70,tokenMode:true,similarityThreshold:0.4"
	config="similarityThreshold:0.4"
	java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/token_result_"$dataset"_"$algorithm"_1_"$i" --algorithm "$algorithm" --files ../data/IMDB/*.csv --input-key INPUT_FILES --separator "," --escape "\\" --algorithm-config "$config" | tail -n 2
done
