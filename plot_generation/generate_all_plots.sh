#!/bin/bash

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

# Run the general scripts without arguments
for script in "${scripts[@]}"; do
    echo Running $script.py
  python3 -u $script
done