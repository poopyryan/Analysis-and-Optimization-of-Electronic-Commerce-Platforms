#!/bin/bash

# Set up --------------------------------------------------
delivery_optimization_log_file="${log_dir}/delivery_optimization"

one_year_before_date=$(date -d "$order_date_of_interest -1 year" +"%Y-%m-%d")

order_data_metrics_query='
    SELECT *
    FROM cleaned_order_data
    WHERE "Order Date" BETWEEN "'${one_year_before_date}'" AND "'${order_date_of_interest}'"
    AND "Warehouse Name" = "Apparel";
'

start_date_of_interest=$(date -d "$order_date_of_interest -2 days" +"%Y-%m-%d")

# Query the database for orders of interest
delivery_orders_of_interest_query='
    SELECT *
    FROM cleaned_order_data
    WHERE "Order Date" BETWEEN "'${start_date_of_interest}'" AND "'${order_date_of_interest}'"
    AND "Warehouse Name" = "Apparel";
'

# Directories --------------------------------------------------
[ ! -d "$delivery_optimization_log_file" ] && mkdir -p "$delivery_optimization_log_file"

extraction_log_file="${delivery_optimization_log_file}/extract_priority_score.log"

## Begin Log to extract priority metrics
echo "----- Beggining Extraction of Priority Score Metrics -----" 
echo
echo "----- Start Run -----" | tee "${extraction_log_file}"

# Extract the country mappings
python "$extract_priority_metrics_script" \
    "$reference_dir" \
    "$database_path" \
    "$order_data_metrics_query" | tee -a "${extraction_log_file}"

# End Log
echo "----- End Run -----" | tee -a "${extraction_log_file}"
echo

generate_priority_score_log_file="${delivery_optimization_log_file}/generate_priority_score.log"

## Begin Log to generate priority score
echo "----- Beggining Generation of Priority Score -----"
echo
echo "----- Start Run -----" | tee "${generate_priority_score_log_file}"

# Generate the priority score
python "$generate_priority_score_script" \
    "$delivery_plan_dir" \
    "$reference_dir" \
    "$database_path" \
    "$order_date_of_interest" \
    "$delivery_orders_of_interest_query" \
    --weights "$weights" | tee -a "${generate_priority_score_log_file}"

# End Log
echo "----- End Run -----" | tee -a "${generate_priority_score_log_file}"