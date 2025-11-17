#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Directories --------------------------------------------------
module_dir="/app/customer_behaviour_analysis_module"
export report_dir="/app/output/reports"

[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export FILE_PATH="/app/input/brazil_dataset.db"
export TEST_SIZE=0.2
export RANDOM_STATE=42

# Scripts --------------------------------------------------
export customer_behaviour_analysis_script="${module_dir}/customer_behaviour_analysis.ipynb"

# Customer Churn Analysis --------------------------------------------------
echo "Generating Customer Behaviour Analysis Report..."

# If RUN_NOTEBOOKS is set to True, run the notebook and save the output as an HTML file. Otherwise, save the notebook as an HTML file without running it.
if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${customer_behaviour_analysis_script}" "${customer_behaviour_analysis_script}"
fi

jupyter nbconvert --to html --output "${report_dir}/customer_behaviour_analysis_report.html" "${customer_behaviour_analysis_script}"

echo "Customer Behaviour Analysis Report generated successfully!"