#!/bin/bash
echo --- Creating necessary folders ---

mkdir -p /app/results/column_scaling
mkdir -p /app/results/column_scaling_token
mkdir -p /app/results/combined_stats
mkdir -p /app/results/edit_distance
mkdir -p /app/results/grow_row_scaling
mkdir -p /app/results/grow_row_scaling_token
mkdir -p /app/results/related_work
mkdir -p /app/results/row_scaling
mkdir -p /app/results/timingStats
mkdir -p /app/results/token_similarity
mkdir -p /app/results/timingStats/edit_distance
mkdir -p /app/results/timingStats/row_scaling

touch /app/results/combined_stats/all_results.csv
touch /app/results/combined_stats/all_results_token.csv

echo "run_id,algorithm,dataset,edit_distance,mem_limit,row_share,column_share,ignore_short,experiment,runtime,results" > /app/results/combined_stats/all_results.csv
echo "run_id,algorithm,dataset,similarity,mem_limit,row_share,column_share,sample_base,experiment,runtime,results" > /app/results/combined_stats/all_results_token.csv

echo --- Starting execution of run_scripts ---

python3 -u /app/run_scripts/column_scaling_ed.py
python3 -u /app/run_scripts/column_scaling_jac.py
python3 -u /app/run_scripts/competitors_token.py
python3 -u /app/run_scripts/competitors.py
python3 -u /app/run_scripts/edit_distance_scaling.py
python3 -u /app/run_scripts/token_similarity_scaling.py
python3 -u /app/run_scripts/IMDB_competitors.py
python3 -u /app/run_scripts/grow_row_scaling_ed.py
python3 -u /app/run_scripts/grow_row_scaling_jac.py
