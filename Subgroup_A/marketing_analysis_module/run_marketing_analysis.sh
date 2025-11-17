#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Directories --------------------------------------------------
module_dir="/app/marketing_analysis_module"
export report_dir="/app/output/reports"

[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export brazil_database_path="/app/input/brazil_dataset.db"

# Scripts --------------------------------------------------
export marketing_analysis_script="${module_dir}/marketing_analysis.ipynb"

# Marketing Analysis --------------------------------------------------
echo "Generating Marketing Analysis Report..."

# If RUN_NOTEBOOKS is set to True, run the notebook and save the output as an HTML file. Otherwise, save the notebook as an HTML file without running it.
if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${marketing_analysis_script}" "${marketing_analysis_script}"
fi

jupyter nbconvert --to html --output "${report_dir}/marketing_analysis_report.html" "${marketing_analysis_script}"

echo "Marketing Analysis Report generated successfully!"
