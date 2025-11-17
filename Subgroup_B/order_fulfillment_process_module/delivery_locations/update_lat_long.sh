#!/bin/bash

# Purpose: This script is used to update the latitude and longitude of the order data. The latitude and longitude are extracted from the city data.

# Query the database for the products
order_query='
    SELECT DISTINCT "Order Country" AS country, "Order City" AS city, "Order State" AS state
    FROM cleaned_order_data;
'

# Set up --------------------------------------------------
delivery_locations_log_file="${log_dir}/delivery_locations"

# mappings for countries
country_mappings='{
    "Republic of the Congo": "Congo (Brazzaville)",
    "Democratic Republic of the Congo": "Congo (Kinshasa)",
    "South Korea": "Korea, South",
    "Czech Republic": "Czechia",
    "Gambia": "Gambia, The",
    "Myanmar": "Burma",
    "Ivory Coast": "Côte d’Ivoire",
    "Western Sahara": "Morocco"
}'

# Directories --------------------------------------------------
[ ! -d "$delivery_locations_log_file" ] && mkdir -p "$delivery_locations_log_file"

log_file="${delivery_locations_log_file}/update_lat_long.log"

## Begin Log
echo "----- Start Run -----" | tee "${log_file}"

# Extract the country mappings
python "$update_lat_long_script" \
    "$city_data_path" \
    "$database_path" \
    "$order_query" \
    "$country_mappings" | tee -a "${log_file}"

# End Log
echo "----- End Run -----" | tee -a "${log_file}"