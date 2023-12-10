#!/bin/bash

# Array of script names
scripts=(
  "alternative_row_plot.py"
  "column_plot_twoCols.py"
  "column_plot_twoCols_token.py"
  "competitors_bar_twoCols.py"
  "competitors_bar_token_twoCols.py"
  "ed_explanation_plot_twoCols.py"
  "ed_plot_twoCols.py"
  "sim_scaling_plot_token.py"
  "valid_sIND_impact_plot.py"
)

# Arguments for data_integration and data_integration_token scripts
data_integration_args=(
  "row"
  "sim"
  "ed"
  "competitors"
  "disk"
  "column"
  "competitors_imdb"
  "column_new"
  "column_CENSUS"
  "column_IMDB"
  "grow_row"
)

# Variables to keep count of successes and failures
success_count=0
failure_count=0
total_scripts=0

# Function to run a script with optional arguments
run_script() {
  local script=$1
  shift
  local args=("$@")
  local cmd=(python /app/scripts/"$script" "${args[@]}")
  "${cmd[@]}" 2>> /app/scripts/error_log.txt
  local exit_status=$?
  if [ $exit_status -eq 0 ]; then
    echo "Script $script ${args[*]} executed successfully."
    ((success_count++))
  else
    echo "Script $script ${args[*]} failed."
    ((failure_count++))
  fi
  ((total_scripts++))
}

# Run the general scripts without arguments
for script in "${scripts[@]}"; do
  run_script "$script"
done

# Run data_integration.py with each argument
for arg in "${data_integration_args[@]}"; do
  run_script "data_integration.py" "$arg"
done

# Run data_integration_token.py with each argument
for arg in "${data_integration_args[@]}"; do
  run_script "data_integration_token.py" "$arg"
done

# Print the final count
echo "$success_count/$total_scripts scripts executed successfully, $failure_count failed."
