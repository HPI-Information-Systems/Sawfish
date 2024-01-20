#!/bin/bash
echo --- Creating necessary folders ---

mkdir -p /app/results/column_scaling_ed
mkdir -p /app/results/column_scaling_jac
mkdir -p /app/results/combined_stats
mkdir -p /app/results/edit_distance
mkdir -p /app/results/row_scaling_ed
mkdir -p /app/results/row_scaling_jac
mkdir -p /app/results/related_work
mkdir -p /app/results/timingStats
mkdir -p /app/results/token_similarity

touch /app/results/combined_stats/results_ed.csv
touch /app/results/combined_stats/results_jac.csv

echo "run_id,algorithm,dataset,edit_distance,row_share,column_share,ignore_short,experiment,runtime,results" > /app/results/combined_stats/results_ed.csv
echo "run_id,algorithm,dataset,similarity,row_share,column_share,experiment,runtime,results" > /app/results/combined_stats/results_jac.csv

echo --- Starting execution of run_scripts ---

python3 -u /app/run_scripts/column_scaling_ed.py
python3 -u /app/run_scripts/column_scaling_jac.py
python3 -u /app/run_scripts/competitors_ed.py
python3 -u /app/run_scripts/competitors_jac.py
python3 -u /app/run_scripts/edit_distance_scaling.py
python3 -u /app/run_scripts/jac_similarity_scaling.py
python3 -u /app/run_scripts/row_scaling_ed.py
python3 -u /app/run_scripts/row_scaling_jac.py
