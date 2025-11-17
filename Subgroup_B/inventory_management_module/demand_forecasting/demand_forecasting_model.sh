#!/bin/bash

# Purpose: This script is used to forecast demand for a set year
# input_year=2017
# demand_forecasting_script="/Users/robbs/Documents/Campus-Security/Subgroup_B/inventory_management_module/demand_forecasting/demand_forecasting_model.py"
# output_dir="/Users/robbs/Documents/TEST_CAMPUS_SECURITY_OUTPUT/inventory_optimization_module/${input_year}"
# model_dir="/Users/robbs/Documents/TEST_CAMPUS_SECURITY_OUTPUT/inventory_optimization_module/models"
# database_path="/Users/robbs/Documents/Campus_Security_Data/Product_&_Inventory_Data/Supply_chain_datasets/supply_chain.db"
# log_dir="${output_dir}/log"

# Set up --------------------------------------------------
demand_forecasting_log="${log_dir}/demand_forecasting.log"

## Begin Log
echo "----- Start Run -----" | tee "$demand_forecasting_log"

# Extract the country mappings
python "$demand_forecasting_script" \
    "$year_of_interest_dir" \
    "$input_year" \
    "$model_dir" \
    "$database_path" | tee -a "$demand_forecasting_log"

# End Log
echo "----- End Run -----" | tee -a "$demand_forecasting_log"