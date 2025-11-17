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

[ ! -d "$output_dir" ] && mkdir -p "$output_dir"

# File Paths --------------------------------------------------
export supply_chain_database_path="/app/input/supply_chain.db"
export inventory_management_dir="/app/output/inventory_management_module/"
export brazil_database_path="/app/input/brazil_dataset.db"

# Scripts --------------------------------------------------
export extract_supply_chain_dashboard_script="${module_dir}/extract_supply_chain_dashboard_data.py"
export extract_customer_data_script="${module_dir}/extract_customer_data_dashboard_data.py"

# Extracting supply chain data --------------------------------------------------
echo "Extracting supply chain data..."

python "$extract_supply_chain_dashboard_script" "$supply_chain_database_path" "$output_dir" "$inventory_management_dir" "$input_year"

echo "Completed extracting supply chain data."

