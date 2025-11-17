#!/bin/bash

# Purpose: This script is used to extract the country mappings from the order data and the city data. The country mappings are used to standardize the country names in the order data.

# Query the database for the relevant order data 
order_query='
    SELECT DISTINCT "Order City" AS city, "Order State" AS state, "Order Country" AS country
    FROM cleaned_order_data;
'

# Set up --------------------------------------------------
country_mapping_log_dir="${log_dir}/country_mapping_log"

# Directories --------------------------------------------------
[ ! -d "$country_mapping_log_dir" ] && mkdir -p "$country_mapping_log_dir"

log_file="${country_mapping_log_dir}/${order_date_of_interest}_get_country_mapping.log"

## Begin Log
echo "----- Start Run -----" | tee "$log_file"

# Extract the country mappings
python "$country_mapping_script" \
    "$reference_dir" \
    "$city_data_path" \
    "$database_path" \
    "$order_query" | tee -a "$log_file"

# End Log
echo "----- End Run -----" | tee -a "$log_file"