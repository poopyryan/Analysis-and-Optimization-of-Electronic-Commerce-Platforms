#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Directories --------------------------------------------------
module_dir="/app/customer_churn_analysis_module"
export report_dir="/app/output/reports"

[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export brazil_database_path="/app/input/brazil_dataset.db"

# Scripts --------------------------------------------------
export customer_churn_analysis_script="${module_dir}/customer_churn_analysis_report.ipynb"

# Customer Churn Analysis --------------------------------------------------
echo "Generating Customer Churn Analysis Report..."

# If RUN_NOTEBOOKS is set to True, run the notebook and save the output as an HTML file. Otherwise, save the notebook as an HTML file without running it.
if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${customer_churn_analysis_script}" "${customer_churn_analysis_script}"
fi

jupyter nbconvert --to html --output "${report_dir}/customer_churn_analysis_report.html" "${module_dir}/customer_churn_analysis_report.ipynb"

echo "Customer Churn Analysis Report generated successfully!"