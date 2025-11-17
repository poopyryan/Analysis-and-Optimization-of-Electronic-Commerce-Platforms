#!/bin/bash

# Purpose: This script is used to optimize the delivery routes for the orders. The script uses the priority scores of the orders to optimize the routes.

# Set up --------------------------------------------------
delivery_optimization_log_file="${log_dir}/delivery_optimization"
orders_file_path="${delivery_plan_dir}/${order_date_of_interest}_priority_scores.csv"

# Directories --------------------------------------------------
[ ! -d "$delivery_optimization_log_file" ] && mkdir -p "$delivery_optimization_log_file"

route_optimization_log_file="${delivery_optimization_log_file}/optimize_route.log"

## Begin Log to optimize route
echo "----- Beggining Route Optimization -----" 
echo
echo "----- Start Run -----" | tee "${route_optimization_log_file}"

# Perform Route Optimization
python "$route_optimization_script" \
    "$orders_file_path" \
    "$num_vehicles" \
    "$vehicle_capacity" \
    "$database_path" \
    "$delivery_plan_dir" |  tee -a "${route_optimization_log_file}"

# End Log
echo "----- End Run -----" | tee -a "${route_optimization_log_file}"