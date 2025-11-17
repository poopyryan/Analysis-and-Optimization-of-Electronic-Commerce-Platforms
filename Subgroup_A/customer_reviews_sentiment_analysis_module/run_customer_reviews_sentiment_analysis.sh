#!/bin/bash

# Check for required environment variables
: "${INPUT_DIR:?Environment variable INPUT_DIR not set}"
: "${OUTPUT_DIR:?Environment variable OUTPUT_DIR not set}"
: "${RUN_NOTEBOOKS:?Environment variable RUN_NOTEBOOKS not set}"

# Directories --------------------------------------------------
module_dir="/app/customer_reviews_sentiment_analysis_module"
export report_dir="/app/output/reports"

[ ! -d "$report_dir" ] && mkdir -p "$report_dir"

# File Paths --------------------------------------------------
export brazil_database_path="/app/input/brazil_dataset.db"
export reviews_stemmer_path="/app/input/reviews_stemmer.json"

# Scripts --------------------------------------------------
export customer_review_EDA_script="${module_dir}/customer_review_EDA.ipynb"
export sentiment_analysis_model_script="${module_dir}/sentiment_analysis_model.ipynb"

# Customer Customer Analysis EDA --------------------------------------------------
echo "Generating Customer Analysis Exploratory Data Analysis Report..."

# If RUN_NOTEBOOKS is set to True, run the notebook and save the output as an HTML file. Otherwise, save the notebook as an HTML file without running it.
if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${customer_review_EDA_script}" "${customer_review_EDA_script}"
fi

jupyter nbconvert --to html --output "${report_dir}/customer_review_exploratory_data_analysis_report.html" "${module_dir}/customer_review_EDA.ipynb"

echo "Customer Customer Analysis Report generated successfully!"

# Sentiment Analysis Model --------------------------------------------------
echo "Generating Sentiment Analysis Model Report..."

# If RUN_NOTEBOOKS is set to True, run the notebook and save the output as an HTML file. Otherwise, save the notebook as an HTML file without running it.
if [ "$RUN_NOTEBOOKS" = "True" ]; then
    jupyter nbconvert --to notebook --execute --output "${sentiment_analysis_model_script}" "${sentiment_analysis_model_script}"
fi

jupyter nbconvert --to html --output "${report_dir}/sentiment_analysis_model_report.html" "${sentiment_analysis_model_script}"

echo "Sentiment Analysis Model Report generated successfully!"
