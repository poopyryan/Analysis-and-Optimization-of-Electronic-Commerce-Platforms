#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${INPUT_YEAR:?Environment variable INPUT_YEAR not set}"

# Directories --------------------------------------------------
module_dir="/app/dashboarding_module"
export output_dir="/app/output/dashboard_data"
export input_year="${INPUT_YEAR}"
export input_dir="${INPUT_DIR}"
export inventory_management_dir="/app/output/inventory_management_module/"

forecasted_demand_file_path="${inventory_management_dir}/${input_year}/demand_forecast.csv"

echo "Waiting for forecast demand: $forecasted_demand_file_path"
while [ ! -f "$forecasted_demand_file_path" ]; do
    sleep 5
done

echo "Forecast demand generated: $forecasted_demand_file_path"
exec "$@"