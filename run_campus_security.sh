#!/bin/bash

# Check for required environment variables

##### Run Subgroup A Modules #####
echo "Starting Subgroup A Modules..."

# Run data prepration module
echo "Running Data Preparation Module..."
docker-compose run data_preparation_subgroup_a
echo "Data Preparation Module Completed."

# Run customer behaviour analysis module
echo "Running Customer Behaviour Analysis Module..."
docker-compose run customer_behaviour_analysis_module
echo "Customer Behaviour Analysis Module Completed."

# Run customer churn analysis module
echo "Running Customer Churn Analysis Module..."
docker-compose run customer_churn_analysis_module
echo "Customer Churn Analysis Module Completed."

# Run customer segmentation module
echo "Running Marketing Analysis Module..."
docker-compose run marketing_analysis_module
echo "Marketing Analysis Module Completed."

# Run Customer Reviesw Sentiment Analysis Module
echo "Running Customer Reviews Sentiment Analysis Module..."
docker-compose run customer_reviews_sentiment_analysis_module
echo "Customer Reviews Sentiment Analysis Module Completed."

##### Run Subgroup B Modules #####
echo "Starting Subgroup B Modules..."

# Run data preparation module
echo "Running Data Preparation Module..."
docker-compose run data_preparation_subgroup_b
echo "Data Preparation Module Completed."

# Run pricing strategy module
echo "Running Pricing Strategy Module..."
docker-compose run pricing_strategy_module
echo "Pricing Strategy Module Completed."

# Run inventory management module
echo "Running Inventory Management Module..."
docker-compose run inventory_management_module
echo "Inventory Management Module Completed."

# Run Order Fulfillment module
echo "Running Order Fulfillment Module..."
docker-compose run order_fulfillment_process_module
echo "Order Fulfillment Module Completed."

##### Run Dashboarding Module #####
echo "Running Dashboarding Module..."
docker-compose run dashboarding_module
echo "Dashboarding Module Completed."
