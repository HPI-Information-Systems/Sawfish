#!/usr/bin/env bash
set -euo pipefail

datasets=("CENSUS" "WIKIPEDIA" "TPCH")
algorithms=("de.metanome.algorithms.similarity_ind.AlgorithmInterface" "de.metanome.algorithms.binder.BinderFileAlgorithm")
tokenAlgorithms=("de.metanome.algorithms.similarity_ind.AlgorithmInterface" "de.metanome.algorithms.tokenbaseline.TokenBaseline")

# ED Mode
#for dataS in ${datasets[@]}; do
#	for algo in ${algorithms[@]}; do
#		for (( i = 0; i < 3; i++ )); do
#				echo "DS $dataS - ALG $algo - ED 0 - run $i"
#				config=""
#				if [[ $algo == "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
#					config="MAX_MEMORY_USAGE_PERCENTAGE:70"
#				elif [[ $algo = "de.metanome.algorithms.sindbaseline.SINDBaseline" ]]; then
#					config="editDistanceThreshold:0"
#				else
#					config="editDistanceThreshold:0,maxMemoryUsagePercentage:70"
#				fi
#				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_0_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape "\\" --algorithm-config "$config" | tail -n 2
#		done
#	done
#done

#for dataS in ${datasets[@]}; do
#	for algo in ${algorithms[@]}; do
#		if [[ $algo != "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
#			for (( i = 0; i < 3; i++ )); do
#				echo "DS $dataS - ALG $algo - ED 1 - run $i"
#				config="editDistanceThreshold:1"
#				if [[ $algo != "de.metanome.algorithms.sindbaseline.SINDBaseline" ]]; then
#					config+=",maxMemoryUsagePercentage:70"
#				fi
#				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_1_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape \\ --algorithm-config "$config" | tail -n 2
#			done
#		fi
#	done
#done
#
# tokenMode
#for dataS in ${datasets[@]}; do
#	for algo in ${tokenAlgorithms[@]}; do
#		for (( i = 0; i < 3; i++ )); do
#				echo "DS $dataS - ALG $algo - SIM 1.0 - run $i"
#				config=""
#				if [[ $algo == "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
#					config="MAX_MEMORY_USAGE_PERCENTAGE:70"
#				elif [[ $algo = "de.metanome.algorithms.tokenbaseline.TokenBaseline" ]]; then
#					config="similarityThreshold:1.0"
#				else
#					config="similarityThreshold:1.0,maxMemoryUsagePercentage:70,tokenMode:true"
#				fi
#				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_0_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape "\\" --algorithm-config "$config" | tail -n 2
#		done
#	done
#done
#
#for dataS in ${datasets[@]}; do
#	for algo in ${tokenAlgorithms[@]}; do
#		if [[ $algo != "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
#			for (( i = 0; i < 3; i++ )); do
#				echo "DS $dataS - ALG $algo - SIM 0.4 - run $i"
#				config="similarityThreshold:0.4"
#				if [[ $algo != "de.metanome.algorithms.tokenbaseline.TokenBaseline" ]]; then
#					config+=",maxMemoryUsagePercentage:70,tokenMode:true"
#				fi
#				java -Xmx4g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_1_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape \\ --algorithm-config "$config" | tail -n 2
#			done
#		fi
#	done
#done
#
#IMDB ED
dataS="IMDB"
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
			java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_0_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape "\\" --algorithm-config "$config" | tail -n 2
	done
done

# IMDB Token
for algo in ${tokenAlgorithms[@]}; do
	for (( i = 0; i < 3; i++ )); do
			echo "DS $dataS - ALG $algo - SIM 1.0 - run $i"
			config=""
			if [[ $algo == "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
				config="MAX_MEMORY_USAGE_PERCENTAGE:70"
			elif [[ $algo = "de.metanome.algorithms.tokenbaseline.TokenBaseline" ]]; then
				config="similarityThreshold:1.0"
			else
				config="similarityThreshold:1.0,maxMemoryUsagePercentage:70,tokenMode:true"
			fi
			java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_0_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape "\\" --algorithm-config "$config" | tail -n 2
	done
done

for algo in ${tokenAlgorithms[@]}; do
	if [[ $algo != "de.metanome.algorithms.binder.BinderFileAlgorithm" ]]; then
		for (( i = 0; i < 3; i++ )); do
			echo "DS $dataS - ALG $algo - SIM 0.4 - run $i"
			config="similarityThreshold:0.4"
			if [[ $algo != "de.metanome.algorithms.tokenbaseline.TokenBaseline" ]]; then
				config+=",maxMemoryUsagePercentage:70,tokenMode:true"
			fi
			java -Xmx32g -cp metanome-cli-1.1.1.jar:similarity_ind-1.1-SNAPSHOT.jar de.metanome.cli.App -o file:related_work/result_"$dataS"_"$algo"_1_"$i" --algorithm "$algo" --files ../data/samples/"$dataS".csv --input-key INPUT_FILES --separator ";" --header --escape \\ --algorithm-config "$config" | tail -n 2
		done
	fi
done
