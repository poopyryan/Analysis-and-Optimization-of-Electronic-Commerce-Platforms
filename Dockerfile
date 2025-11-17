# Base Stage: Install shared dependencies
FROM python:3.10-slim AS base
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy common requirements and install shared dependencies, including Jupyter
COPY requirements/common_requirements.txt .
RUN pip install --no-cache-dir -r common_requirements.txt

################################### SUBGROUP A ###################################

##### DATA PREPARATION #####

FROM base AS data_preparation_subgroup_a
WORKDIR /app/data_preparation_subgroup_a

# Copy data_preparation_subgroup_a scripts and notebooks
COPY Subgroup_A/data_preparation_subgroup_a/* /app/data_preparation_subgroup_a/

# Set executable permissions for necessary scripts
RUN chmod +x /app/data_preparation_subgroup_a/data_generation_final.py \
             /app/data_preparation_subgroup_a/data_preparation.py \
             /app/data_preparation_subgroup_a/sql_queries.py

# Run the main scripts
CMD python /app/data_preparation_subgroup_a/data_generation_final.py

## CUSTOMER REVIEWS SENTIMENT ANALYSIS #####

FROM base AS customer_reviews_sentiment_analysis_module
WORKDIR /app/customer_reviews_sentiment_analysis_module

# Copy Customer_Reviews_Sentiment_Analysis scripts and notebooks
COPY Subgroup_A/customer_reviews_sentiment_analysis_module/ /app/customer_reviews_sentiment_analysis_module/

# download and cache nltk data
RUN python -m nltk.downloader stopwords rslp punkt

# Set executable permissions for necessary scripts
RUN chmod +x /app/customer_reviews_sentiment_analysis_module/customer_review_EDA.ipynb \
             /app/customer_reviews_sentiment_analysis_module/SentAn_machine_learning.py \
             /app/customer_reviews_sentiment_analysis_module/SentAn_cleaning_and_preprocessing.py \
             /app/customer_reviews_sentiment_analysis_module/SentAn_visualisations.py \
             /app/customer_reviews_sentiment_analysis_module/sentiment_analysis_model.ipynb

#             /app/customer_reviews_sentiment_analysis_module/run_customer_reviews_sentiment_analysis.sh

# Run the main scripts and notebook
CMD bash -c "./run_customer_reviews_sentiment_analysis.sh"

##### CUSTOMER BEHAVIOUR ANALYSIS #####
FROM base AS customer_behaviour_analysis_module
WORKDIR /app/customer_behaviour_analysis_module

# Copy specific requirements and install for customer_behaviour_analysis
COPY requirements/customer_behaviour_analysis_requirements.txt .
RUN pip install --no-cache-dir -r customer_behaviour_analysis_requirements.txt

# Copy customer_behaviour_analysis scripts and notebooks
COPY Subgroup_A/customer_behaviour_analysis_module/ /app/customer_behaviour_analysis_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/customer_behaviour_analysis_module/customer_behaviour_analysis.ipynb \
             /app/customer_behaviour_analysis_module/customer_lifetime_value_model.py \
             /app/customer_behaviour_analysis_module/customer_segmentation_model.py \
             /app/customer_behaviour_analysis_module/data_preprocessing.py \
             /app/customer_behaviour_analysis_module/main_pipeline.py \
             /app/customer_behaviour_analysis_module/queries.py \
             /app/customer_behaviour_analysis_module/run_customer_behaviour_analysis.sh \
             /app/customer_behaviour_analysis_module/segment_test.py

# Run the main scripts and notebook
CMD bash -c "./run_customer_behaviour_analysis.sh"

###### CUSTOMER CHURN ANALYSIS MODULE ##### 

# Define target stage for customer_churn_analysis_module
FROM base AS customer_churn_analysis_module
WORKDIR /app/customer_churn_analysis_module

# Copy Customer_Churn_Analysis scripts and notebooks
COPY Subgroup_A/customer_churn_analysis_module/* /app/customer_churn_analysis_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/customer_churn_analysis_module/data_preparation.py \
             /app/customer_churn_analysis_module/data_processing.py \
             /app/customer_churn_analysis_module/data_visualisation.py \
             /app/customer_churn_analysis_module/sql_queries.py \
             /app/customer_churn_analysis_module/customer_churn_analysis_report.ipynb \
             /app/customer_churn_analysis_module/run_customer_churn_analysis.sh

# Run the main scripts and notebook
CMD bash -c "./run_customer_churn_analysis.sh"

# ##### MARKETING ANALYSIS MODULE #####

# Define target stage for marketing_analysis_module
FROM base AS marketing_analysis_module
WORKDIR /app/marketing_analysis_module

# Copy Marketing_Analysis scripts and notebooks
COPY Subgroup_A/marketing_analysis_module/* /app/marketing_analysis_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/marketing_analysis_module/marketing_analysis.ipynb \
             /app/marketing_analysis_module/run_marketing_analysis.sh

# Run the main scripts
CMD bash -c "./run_marketing_analysis.sh"

################################### SUBGROUP B ###################################

#### DATA PREPARATION #####

FROM base AS data_preparation_subgroup_b
WORKDIR /app/data_preparation_subgroup_b

# Copy data_preparation_subgroup_a scripts and notebooks
COPY Subgroup_B/data_preparation_subgroup_b/* /app/data_preparation_subgroup_b/

# Set executable permissions for necessary scripts
RUN chmod +x /app/data_preparation_subgroup_b/preprocessing.ipynb \
             /app/data_preparation_subgroup_b/run_preprocessing.sh

# Run the main scripts
CMD bash -c "./run_preprocessing.sh"

#### PRICING STRATEGY MODULE #####

# Define target stage for pricing_strategy_module 
FROM base AS pricing_strategy_module
WORKDIR /app/pricing_strategy_module

# Copy pricing_strategy_module scripts and notebooks
COPY Subgroup_B/pricing_strategy_module/ /app/pricing_strategy_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/pricing_strategy_module/PED_Analysis.ipynb \
             /app/pricing_strategy_module/preprocessing_product_categories.py \
             /app/pricing_strategy_module/preprocessing_single_product.py \
             /app/pricing_strategy_module/sql_queries.py \
             /app/pricing_strategy_module/pricing_for_product_categories.ipynb \
             /app/pricing_strategy_module/pricing_for_single_product.ipynb \
             /app/pricing_strategy_module/run_pricing_strategy.sh

# Run the main scripts and notebook
CMD bash -c "./run_pricing_strategy.sh"

##### INVENTORY MANAGEMENT MODULE #####

# Define target stage for inventory_management_module
FROM base AS inventory_management_module
WORKDIR /app/inventory_management_module

# Copy inventory_management_module scripts and notebooks
COPY Subgroup_B/inventory_management_module/demand_forecasting /app/inventory_management_module/demand_forecasting/
COPY Subgroup_B/inventory_management_module/inventory_optimization /app/inventory_management_module/inventory_optimization/
COPY Subgroup_B/inventory_management_module/notebooks/ /app/notebooks/
COPY Subgroup_B/inventory_management_module/run_inventory_management.sh /app/inventory_management_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/inventory_management_module/demand_forecasting/demand_forecasting_model.sh \
             /app/inventory_management_module/inventory_optimization/inventory_optimization.sh \
             /app/inventory_management_module/run_inventory_management.sh \
             /app/notebooks/demand_forecast_modelling.ipynb \
             /app/notebooks/inventory_optimization.ipynb

# Run the main scripts and notebook
CMD bash -c "./run_inventory_management.sh"

##### ROUTE OPTIMIZATION MODULE #####

# Define target stage for order_fulfillment_process_module
FROM base AS order_fulfillment_process_module
WORKDIR /app/order_fulfillment_process_module

# Copy order_fulfillment_process_module scripts and notebooks
COPY Subgroup_B/order_fulfillment_process_module/delivery_locations/ /app/order_fulfillment_process_module/delivery_locations/
COPY Subgroup_B/order_fulfillment_process_module/delivery_optimization/priority_score /app/order_fulfillment_process_module/delivery_optimization/priority_score
COPY Subgroup_B/order_fulfillment_process_module/delivery_optimization/route_optimization /app/order_fulfillment_process_module/delivery_optimization/route_optimization
COPY Subgroup_B/order_fulfillment_process_module/notebooks/* /app/notebooks/
COPY Subgroup_B/order_fulfillment_process_module/run_delivery_plan.sh /app/order_fulfillment_process_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/order_fulfillment_process_module/delivery_locations/update_lat_long.sh \
             /app/order_fulfillment_process_module/delivery_optimization/priority_score/generate_priority_score.sh \
             /app/order_fulfillment_process_module/delivery_optimization/route_optimization/optimize_route.sh \
             /app/order_fulfillment_process_module/run_delivery_plan.sh \
             /app/notebooks/delivery_optimization_concept.ipynb \
             /app/notebooks/bottleneck_analysis_finalversion.ipynb

# Run the main scripts and notebook
CMD bash -c "./run_delivery_plan.sh &&"

################################# DASHBOARDING ###################################

# Define target stage for dashboarding_module
FROM base AS dashboarding_module
WORKDIR /app/dashboarding_module

# Copy dashboarding scripts and notebooks
COPY dashboarding_module/* /app/dashboarding_module/

# Set executable permissions for necessary scripts
RUN chmod +x /app/dashboarding_module/extract_supply_chain_dashboard_data.py \
             /app/dashboarding_module/run_extract_dashboard_data.sh \
             /app/dashboarding_module/sql_queries.py \ 
             /app/dashboarding_module/wait_for_forecasted_demand.sh

# Set the entrypoint script
ENTRYPOINT ["/app/dashboarding_module/wait_for_forecasted_demand.sh"]

# Run the main scripts
CMD bash -c "./run_extract_dashboard_data.sh"