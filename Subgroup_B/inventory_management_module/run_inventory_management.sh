#!/bin/bash

# Check for required environment variables
: "${INPUT_YEAR:?Environment variable INPUT_YEAR not set}"
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Variable Set up --------------------------------------------------
export input_year="$INPUT_YEAR"

# Directories --------------------------------------------------
module_dir="/app/inventory_management_module"
export output_dir="/app/output/inventory_management_module"
export year_of_interest_dir="${output_dir}/${input_year}"
export log_dir="${year_of_interest_dir}/log"
export model_dir="${output_dir}/models"
export report_dir="${output_dir}/reports"

[ ! -d "$output_dir" ] && mkdir -p "$output_dir"
[ ! -d "$year_of_interest_dir" ] && mkdir -p "$year_of_interest_dir"
[ ! -d "$log_dir" ] && mkdir -p "$log_dir"
[ ! -d "$model_dir" ] && mkdir -p "$model_dir"
[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export database_path="/app/input/supply_chain.db"

# Scripts --------------------------------------------------
export demand_forecasting_script="${module_dir}/demand_forecasting/demand_forecasting_model.py"
export inventory_optimization_script="${module_dir}/inventory_optimization/inventory_optimization.py"

# Forecast Demand --------------------------------------------------
echo "Running Demand Forecasting Script..."
"$module_dir"/demand_forecasting/demand_forecasting_model.sh

# Generate Priority Score --------------------------------------------------
echo "Running Inventory Optimization Script..."
"$module_dir"/inventory_optimization/inventory_optimization.sh

# Execute Notebooks --------------------------------------------------
echo "Executing Notebooks..."

if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${module_dir}/demand_forecasting/demand_forecast_modelling.ipynb" "${module_dir}/demand_forecasting/demand_forecast_modelling.ipynb"
    jupyter nbconvert --to notebook --execute --output "${module_dir}/inventory_optimization/inventory_optimization.ipynb" "${module_dir}/inventory_optimization/inventory_optimization.ipynb"
fi

jupyter nbconvert --to html --output "${report_dir}/demand_forecasting_model_report.html" "/app/notebooks/demand_forecast_modelling.ipynb"
jupyter nbconvert --to html --output "${report_dir}/inventory_optimization_report.html" "/app/notebooks/inventory_optimization.ipynb"

echo "Notebooks executed successfully!"