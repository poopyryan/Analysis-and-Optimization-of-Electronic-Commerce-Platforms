#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOK:?Environment variable RUN_NOTEBOOK not set}"

# Directories --------------------------------------------------
module_dir="/app/data_preparation_subgroup_b"

# File Paths --------------------------------------------------
export supply_chain_database_path="/app/input/supply_chain.db"

# Scripts --------------------------------------------------
export preprocessing_script="${module_dir}/preprocessing.ipynb"

# Perform Preprocessing --------------------------------------------------
echo "Preprocessing Supply Chain Data..."

if [ "$RUN_NOTEBOOK" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${preprocessing_script}" "${preprocessing_script}"
fi
