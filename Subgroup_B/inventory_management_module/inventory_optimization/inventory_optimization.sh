#!/bin/bash

# Purpose: This script is used to optimize inventory for a set year

product_info_query='
    SELECT * FROM product_info;
'

# Set up --------------------------------------------------
inventory_optimization_log="${log_dir}/inventory_optimization.log"

## Begin Log
echo "----- Start Run -----" | tee "$inventory_optimization_log"

# Extract the country mappings
python "$inventory_optimization_script" \
    "$year_of_interest_dir" \
    "$database_path" \
    "$product_info_query" \
    "$input_year" | tee -a "$inventory_optimization_log"

# End Log
echo "----- End Run -----" | tee -a "$inventory_optimization_log"