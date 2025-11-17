#!/bin/bash

# Check for required environment variables
: "${ORDER_DATE_OF_INTEREST:?Environment variable ORDER_DATE_OF_INTEREST not set}"
: "${NUM_VEHICLES:?Environment variable NUM_VEHICLES not set}"
: "${VEHICLE_CAPACITY:?Environment variable VEHICLE_CAPACITY not set}"
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Variable Set up --------------------------------------------------
export order_date_of_interest="$ORDER_DATE_OF_INTEREST"
export num_vehicles="$NUM_VEHICLES"
export vehicle_capacity="$VEHICLE_CAPACITY"

# Directories --------------------------------------------------
module_dir="/app/order_fulfillment_process_module"
export output_dir="/app/output/order_fulfillment_process_module"
export delivery_plan_dir="${output_dir}/delivery_route/${order_date_of_interest}"
export log_dir="${output_dir}/log/${order_date_of_interest}"
export reference_dir="${output_dir}/references"
export report_dir="${output_dir}/reports"

[ ! -d "$output_dir" ] && mkdir -p "$output_dir"
[ ! -d "$delivery_plan_dir" ] && mkdir -p "$delivery_plan_dir"
[ ! -d "$log_dir" ] && mkdir -p "$log_dir"
[ ! -d "$reference_dir" ] && mkdir -p "$reference_dir"
[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export database_path="/app/input/supply_chain.db"
export city_data_path="/app/input/worldcities.csv"

# Scripts --------------------------------------------------
export country_mapping_script="${module_dir}/delivery_locations/get_country_mappings.py"
export route_optimization_script="${module_dir}/delivery_optimization/route_optimization/optimize_route.py"
export update_lat_long_script="${module_dir}/delivery_locations/update_lat_long.py"
export extract_priority_metrics_script="${module_dir}/delivery_optimization/priority_score/extract_priority_metrics.py"
export generate_priority_score_script="${module_dir}/delivery_optimization/priority_score/generate_priority_score.py"

# Weights for Priority Score --------------------------------------------------
export weights='{
    "late_delivery_probability": 0.5,
    "Days Till Scheduled Delivery": 0.4,
    "Avg Shipping Time": 0.3,
    "Order Profit": 0.1
}'

# Update Lat Long --------------------------------------------------
echo "Running Update Lat Long Script..."
"$module_dir"/delivery_locations/update_lat_long.sh

# Generate Priority Score --------------------------------------------------
echo "Running Generate Priority Score Script..."
"$module_dir"/delivery_optimization/priority_score/generate_priority_score.sh

# Route Optimization --------------------------------------------------
echo "Running Route Optimization Script..."
"$module_dir"/delivery_optimization/route_optimization//optimize_route.sh

# Execute Notebooks --------------------------------------------------
echo "Executing Notebooks..."

if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${module_dir}/delivery_optimization/delivery_optimization_concept.ipynb" "${module_dir}/delivery_optimization/delivery_optimization_concept.ipynb"
    jupyter nbconvert --to notebook --execute --output "${module_dir}/bottleneck_analysis/bottleneck_analysis_finalversion.ipynb" "${module_dir}/bottleneck_analysis/bottleneck_analysis_finalversion.ipynb"
fi

jupyter nbconvert --to html --output "${report_dir}/bottleneck_analysis_report.html" "/app/notebooks/bottleneck_analysis_finalversion.ipynb"
jupyter nbconvert --to html --output "${report_dir}/delivery_optimization_report.html" "/app/notebooks/delivery_optimization_concept.ipynb"

echo "Notebooks executed successfully!"
