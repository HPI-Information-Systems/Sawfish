#!/bin/bash

scripts=(
  "column_plot_ed.py"
  "column_plot_jac.py"
  "competitors_plot_ed.py"
  "competitors_plot_jac.py"
  "ed_explanation_plot.py"
  "ed_scaling_plot.py"
  "row_plot.py"
  "jac_scaling_plot.py"
  "valid_sIND_impact_plot.py"
)

# Run the general scripts without arguments
for script in "${scripts[@]}"; do
    echo Running $script.py
  python3 -u $script
done
