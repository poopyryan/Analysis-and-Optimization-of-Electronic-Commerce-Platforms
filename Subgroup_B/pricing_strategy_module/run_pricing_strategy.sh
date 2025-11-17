#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Directories --------------------------------------------------
module_dir="/app/pricing_strategy_module"
export output_dir="/app/output/pricing_strategy_module"
export reference_dir="${output_dir}/references"
export report_dir="/app/output/reports"
export pricing_results_dir="${output_dir}/pricing_results" 

[ ! -d "$output_dir" ] && mkdir -p "$output_dir"
[ ! -d "$reference_dir" ] && mkdir -p "$reference_dir"
[ ! -d "$report_dir" ] && mkdir -p "$report_dir"
[ ! -d "$pricing_results_dir" ] && mkdir -p "$pricing_results_dir"

# File Paths --------------------------------------------------
export supply_chain_database_path="/app/input/supply_chain.db"
export brazil_database_path="/app/input/brazil_dataset.db"

# Scripts --------------------------------------------------
export PED_analysis_script="${module_dir}/PED_analysis.ipynb"
export preprocessing_product_categories_script="${module_dir}/preprocessing_product_categories.py"
export preprocessing_single_product_script="${module_dir}/preprocessing_single_product.py"
export pricing_for_product_categories_script="${module_dir}/pricing_for_product_categories.ipynb"
export pricing_for_single_product_script="${module_dir}/pricing_for_single_product.ipynb"

# PED Analysis --------------------------------------------------
echo "Saving PED Analysis Results..."

if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --inplace "${PED_analysis_script}"
fi

jupyter nbconvert --to html --output "${report_dir}"/PED_analysis_report.html "${PED_analysis_script}"

# Preprocessing for product categories --------------------------------------------------
echo "Running Preprocessing for product categories..."
python "$preprocessing_product_categories_script" "$supply_chain_database_path" "$brazil_database_path" "$reference_dir"

# Preprocessing for single product --------------------------------------------------
echo "Running Preprocessing for single product..."
python "$preprocessing_single_product_script" "$supply_chain_database_path" "$brazil_database_path" "$reference_dir"

# Pricing for Product Categories --------------------------------------------------
echo "Running Pricing for Product Categories Script..."

if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --inplace "${pricing_for_product_categories_script}"
fi

jupyter nbconvert --to html --output "${report_dir}"/pricing_for_product_categories_report.html "${pricing_for_product_categories_script}"

# Pricing for Single Product --------------------------------------------------
echo "Running Pricing for Single Product Script..."

if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --inplace "${pricing_for_single_product_script}"
fi

jupyter nbconvert --to html --output "${report_dir}"/pricing_for_single_product_report.html "${pricing_for_single_product_script}"

echo "Pricing strategy module completed successfully."