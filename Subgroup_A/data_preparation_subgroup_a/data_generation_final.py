# %%
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import random
from sql_queries import *
from data_preparation import write_data_using_sql_query
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import Metadata

synthetic_marketing_database_path = "/app/input/syntheticmarketingraw.csv"
supply_chain_database_path = "/app/input/supply_chain.db"
brazil_database_path = "/app/input/brazil_dataset_raw.db"

### Creating Synthetic Marketing Data
# %%
"""
## STEP 0: DROPPING IRRELEVANT COLUMNS
"""

# %%
df = pd.read_csv(synthetic_marketing_database_path)
df = df.drop(['leads', 'orders', 'c_date', 'campaign_name', 'campaign_id', 'id'], axis=1) 
df = df.sort_values(by=['revenue', 'clicks', 'impressions', 'mark_spent'], ascending= True)
df = df.reset_index(drop = True)
df
# sorting revenue by ascending order
# campaign distribution in terms of rows according to distribution of orders (60% -2017, 30% -2018, 10% -2016): 30 for 2016, 85 for 2018, 193 for 2017


# %%
"""
## STEP 1: ADDING CAMPAIGN START_ DATES
I first order the dataframe in descending order of revenue. The idea is to randomise the dates in sections of 2016, 2017 pt 1, 2017 pt2, and 2018. As the number of sales increase in 2017 and reaches its highest in the second half of 2017, I have decided to split that year into 2 parts, so when I stack the rows in this order to form a column,
1. 2017 pt 2
2. 2018
3. 2017 pt 1
4. 2016
and add this column to the dataframe, I get a reasonable distribution that aligns with the number of orders/ engagement in the brazilian dataset. 
"""

# %%
# RANDOMISING 2016 CAMPAIGN DATES
df2016 = pd.DataFrame({'id2016':range(1,31)})
start_date = '2016-09-13'
end_date = '2016-12-31'
def random_dates(start, end, n=10):
    # Convert string dates to datetime
    np.random.seed(11)
    start_u = pd.to_datetime(start).value // 10**9  # Convert to Unix timestamp
    end_u = pd.to_datetime(end).value // 10**9
    # Generate n random timestamps
    random_ts = np.random.randint(start_u, end_u, n)
    # Convert back to datetime
    return pd.to_datetime(random_ts, unit='s').date
df2016['date'] = random_dates(start_date, end_date, len(df2016))


# %%
# RANDOMISING 2017 CAMPAIGN DATES FOR FIRST HALF OF THE YEAR (sales had a gradual increase)
df2017pt1 = pd.DataFrame({'id2017':range(1,110)})
start_date1 = '2017-01-01'
end_date1 = '2017-07-31'
def random_dates(start, end, n=10):
    # Convert string dates to datetime
    np.random.seed(11)
    start_u = pd.to_datetime(start).value // 10**9  # Convert to Unix timestamp
    end_u = pd.to_datetime(end).value // 10**9
    # Generate n random timestamps
    random_ts = np.random.randint(start_u, end_u, n)
    # Convert back to datetime
    return pd.to_datetime(random_ts, unit='s').date
df2017pt1['date'] = random_dates(start_date1, end_date1, len(df2017pt1))

# %%
# RANDOMISING 2017 CAMPAIGN DATES FOR LATTER HALF OF THE YEAR (sale reaches its peak)
df2017pt2 = pd.DataFrame({'id2017':range(1,85)})
start_date1 = '2017-08-01'
end_date1 = '2017-12-31'
def random_dates(start, end, n=10):
    # Convert string dates to datetime
    np.random.seed(48)
    start_u = pd.to_datetime(start).value // 10**9  # Convert to Unix timestamp
    end_u = pd.to_datetime(end).value // 10**9
    # Generate n random timestamps
    random_ts = np.random.randint(start_u, end_u, n)
    # Convert back to datetime
    return pd.to_datetime(random_ts, unit='s').date
df2017pt2['date'] = random_dates(start_date1, end_date1, len(df2017pt2))

# %%
# RANDOMISING 2018 CAMPAIGN DATES (sale plateaus and drops after august)
df2018 = pd.DataFrame({'id2018':range(1,86)})
start_date = '2018-01-01'
end_date = '2018-08-31'
def random_dates(start, end, n=10):
    # Convert string dates to datetime
    np.random.seed(11)
    start_u = pd.to_datetime(start).value // 10**9  # Convert to Unix timestamp
    end_u = pd.to_datetime(end).value // 10**9
    # Generate n random timestamps
    random_ts = np.random.randint(start_u, end_u, n)
    # Convert back to datetime
    return pd.to_datetime(random_ts, unit='s').date
df2018['date'] = random_dates(start_date, end_date, len(df2018))

# %%
# CONCATENATING DATES TOGETHER
combined_df = pd.concat([df2016, df2017pt1, df2018, df2017pt2],  ignore_index =True)
combined_df = combined_df.drop(['id2016', 'id2017', 'id2018'], axis=1)
combined_df['date'] = pd.to_datetime(combined_df['date'])

# %%
# ADDING DATE COLUMN TO THE DF
df = df.sort_values(by = ['revenue', 'clicks', 'impressions', 'mark_spent'], ascending = True)
df['date'] = combined_df

# %%
"""
## STEP 2: RENAMING OF MARKETING CHANNELS
Renaming channels for better clarity of the 4 different types of marketing channels: 
- social = Social Media Marketing
- email = Email Marketing
- affiliate = Affiliate Marketing
- search = Search Engine Marketing
"""
# Renaming channels
df = df.sort_values(by= ['revenue', 'clicks', 'impressions', 'mark_spent'], ascending = False)
df['category'] = df['category'].replace({'influencer': 'affiliate', 'media': 'email'})

# %%
"""
## STEP 3: ADDING CAMPAIGN TYPES
After research on the different type of campaigns are used in e-commerce, the distribution and types are as follows: 
- Seasonal Sales: 30%
- Flash Sales: 25%
- Bundle(BOGO): 20%
- Loyalty: 15%
- Referral: 10% 
"""
# GENERATING CAMPAIGN_TYPE
df = df.rename(columns = {'revenue': 'campaign_revenue', 'mark_spent':'campaign_budget', 'category':'channel', 'date':'start_date'})
df['start_date'] = pd.to_datetime(df['start_date'])
# Distribution of campaign_types based on research is as shows
# Seasonal Sales: 30%, Flash Sales: 25%, Bundle(BOGO): 20%, Loyalty: 15%, Referral: 10% 
campaign_types = ['Seasonal Sales', 'Flash Sales', 'Bundle Offers (BOGO)', 
                  'Loyalty Promotions', 'Referral Programs']
counts = [92, 77, 62, 47, 30]
# Create a list to hold the expanded campaigns based on the defined counts
expanded_campaigns = []
for campaign, count in zip(campaign_types, counts):
    expanded_campaigns.extend([campaign] * count)

# Shuffle the expanded campaigns to randomize their order
np.random.seed(11)  # For reproducibility
np.random.shuffle(expanded_campaigns)

df['campaign_type'] = expanded_campaigns[:308]

# %%
"""
## STEP 4: ADDING CAMPAIGN END_DATES BASED ON INDUSTRY BENCHMARK DURATIONS
To add campaign durations and their end dates, I had researched on the duration of each campaign type and they are as follows:
"""
# GENERATING CAMPAIGN END DATES 

# taken from statistics of campaign_budget
print(df['campaign_budget'].describe())
low_budget_threshold = 634.168065
high_budget_threshold = 8667.940750

# Define a function to assign duration based on campaign type and budget
def assign_duration(campaign_type, budget):
    np.random.seed(11)
    if campaign_type == 'Flash Sales':
        if budget <= low_budget_threshold:
            return np.random.randint(1, 2)  # Short duration for low-budget flash sales
        elif budget <= high_budget_threshold:
            return np.random.randint(2, 3)  # Medium duration for mid-budget flash sales
        else:
            return 3  # Max duration for high-budget flash sales
    
    elif campaign_type == 'Seasonal Sales':
        if budget <= low_budget_threshold:
            return np.random.randint(15, 21)  # Shorter for low-budget seasonal
        elif budget <= high_budget_threshold:
            return np.random.randint(21, 26)  # Medium for mid-budget seasonal
        else:
            return np.random.randint(26, 31)  # Longer for high-budget seasonal
    
    elif campaign_type == 'Bundle Offers (BOGO)':
        if budget <= low_budget_threshold:
            return np.random.randint(7, 10)  # Shorter BOGO duration
        elif budget <= high_budget_threshold:
            return np.random.randint(10, 12)  # Medium BOGO duration
        else:
            return np.random.randint(12, 15)  # Longer BOGO duration
    
    elif campaign_type == 'Loyalty Promotions':
        if budget <= low_budget_threshold:
            return np.random.randint(20, 30)  # Shorter loyalty campaign
        elif budget <= high_budget_threshold:
            return np.random.randint(30, 45)  # Medium loyalty campaign
        else:
            return np.random.randint(45, 61)  # Longer loyalty campaign
    
    elif campaign_type == 'Referral Programs':
        if budget <= low_budget_threshold:
            return np.random.randint(30, 45)  # Shorter referral duration
        elif budget <= high_budget_threshold:
            return np.random.randint(45, 60)  # Medium referral duration
        else:
            return np.random.randint(60, 91)  # Longer referral duration

# Apply the function to assign duration to each campaign
df['duration'] = df.apply(lambda x: assign_duration(x['campaign_type'], x['campaign_budget']), axis=1)

# Create the End_Date column by adding the duration to the Start_Date
df['end_date'] = df['start_date'] + pd.to_timedelta(df['duration'], unit='D')
df['start_date'] = pd.to_datetime(df['start_date']).dt.date
df['end_date'] = pd.to_datetime(df['end_date']).dt.date
df = df.sort_values(by = ['start_date', 'end_date'])
df['id'] = range(1,309)
# %%
"""
## STEP 5: ADJUSTING CAMPAIGN REVENUE AND BUDGET VALUES
This artificial dataset was taken from Kaggle. To simulate the distribution of our orders in accordance with the campaign timeframes, I have calculated the campaign revenue via a weighted proportion formula. To create a believable campaign budget, we simulated the same estimated ratio of old campaign budget:old campaign revenue, and created a new campaign budget based on the new campaign revenue that was created from aggregating the orders. Based on research, a medium sized business would have around 50% ROI from marketing through different channels. (https://marketingsherpa.com/article/chart/ecommerce-chart-roi-spend#:~:text=Medium%2Dsized%20ecommerce%20companies%20reported,revenue%20spectrum%20reported%20lower%20ROIs.) I then adjusted it such that it followed realistic statistics. it to make it more logical. I also wanted to emulate a scenario where social media targetting is inefficient. Hence, I assigned revenue to where social media would have a low ROI
"""
##### ADJUSTING CAMPAIGN REVENUE #####
df['start_date'] = pd.to_datetime(df['start_date'])
df['end_date'] = pd.to_datetime(df['end_date'])
conn = sqlite3.connect(brazil_database_path)
query = """SELECT SUM(x.payment_value) AS purchase_value, strftime('%Y-%m-%d', y.order_purchase_timestamp) AS ymd
    FROM olist_order_payments_dataset AS x
    JOIN olist_orders_dataset AS y
    ON x.order_id = y.order_id
    GROUP BY ymd
    ORDER BY ymd;"""
dforders = pd.read_sql_query(query, conn)
dforders['ymd'] = pd.to_datetime(dforders['ymd'])

# Step 1: Sum purchase values within each campaign's date range
df['total_purchase_value'] = 0.0  # Initialize total purchase within each campaign's period
for idx, campaign in df.iterrows():
    start_date = campaign['start_date']
    end_date = campaign['end_date']
    # Filter dforders within the campaign's date range
    total_purchase_in_range = dforders[
        (dforders['ymd'] >= start_date) & (dforders['ymd'] <= end_date)
    ]['purchase_value'].sum()
    # Assign total purchase value for each campaign
    df.at[idx, 'total_purchase_value'] = total_purchase_in_range

# Step 2: Calculate a composite weight for each campaign based on initial revenue and total purchases
# This will balance df with high initial revenue and/or high total purchases
total_initial_revenue = df['campaign_revenue'].sum()
total_purchase_value = df['total_purchase_value'].sum()
# Calculate weighted contribution for each campaign
df['revenue_weight'] = ((df['campaign_revenue'] / total_initial_revenue))
# Step 3: Scale each campaign's purchase value by the weight to get adjusted revenue
# This ensures that df with higher initial revenue and/or higher purchase activity get proportionally higher adjusted revenue
df['new_campaign_revenue'] = df['revenue_weight'] * df['total_purchase_value']
# Step 4: Round adjusted revenue for readability
df['new_campaign_revenue'] = df['new_campaign_revenue'].round(2)

##### ADJUSTING CAMPAIGN BUDGET BASED ON CAMPAIGN REVENUE #####
df['budget_to_revenue_ratio'] = df['campaign_budget'] / df['campaign_revenue']
def estimated_budget(row): ## Assuming the average daily budget for a campaign is 20
    if row['campaign_revenue'] == 0.0 and row['new_campaign_revenue']==0.0:
        return row['duration'] * 20
    elif row['campaign_revenue'] == 0.0:
        return row['duration'] * 20
    elif row['new_campaign_revenue']==0.0:
        return row['duration'] * 20
    else:
        return row['new_campaign_revenue'] * row['budget_to_revenue_ratio']

df['new_campaign_budget'] = df.apply(estimated_budget, axis=1)
df['new_campaign_budget'] = df['new_campaign_budget'].round(2)

##### CAPPING ROI FOR TO SIMULATE REAL LIFE SCENARIOS #####
roi_caps = {
    ('affiliate', 'Flash Sales'): 100, 
    ('affiliate', 'Seasonal Sales'): 130,
    ('affiliate', 'Bundle Offers (BOGO)'): 40,
    ('affiliate', 'Referral Programs'): 30
}
df['current_roi'] = (df['new_campaign_revenue']-df['new_campaign_budget'])*100 / df['new_campaign_budget']

def adjust_budget(row):
    cap = roi_caps.get((row['channel'], row['campaign_type']), None)
    if cap is None:
        return row['new_campaign_budget']  # If no cap is defined, return current budget
    # If current ROI exceeds cap, adjust budget to match capped revenue
    if row['current_roi'] > cap and row['new_campaign_revenue'] != 0:
       adjusted_budget = row['new_campaign_revenue'] / (1 + cap/100)
       return adjusted_budget
    else: 
        return row['new_campaign_revenue']

df['adjusted_budget'] = df.apply(adjust_budget, axis=1)

df['campaign_budget'] = df['adjusted_budget']
df['campaign_revenue'] = df['new_campaign_revenue']
df['start_date'] = pd.to_datetime(df['start_date']).dt.date
df['end_date'] = pd.to_datetime(df['end_date']).dt.date
df = df.sort_values(by = ['start_date', 'end_date'])
df['id'] = range(1,309)
finaldf = df.reindex(columns = ['id', 'start_date', 'end_date', 'campaign_type', 'channel', 'campaign_budget', 'campaign_revenue', 'impressions', 'clicks'])

# %%
"""
## STEP 6: CREATING DATABASE
"""
# CREATING TABLE IN THE DATABASE
conn = sqlite3.connect(brazil_database_path)
finaldf.to_sql('olist_marketing_dataset', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

### Creating Synthetic Discount Rates
# Set a random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Load the supply chain dataset and metadata
connection = sqlite3.connect(supply_chain_database_path)
supply_chain_df = pd.read_sql_query("SELECT `Order Item Discount Rate` FROM raw_order_data", connection)
connection.close()

# Load metadata for the synthetic model
metadata_filename = "supply_chain_discount_rate_metadata.json"
if not os.path.isfile(metadata_filename):
    # Save metadata to JSON file only if it doesn't exist
    metadata = Metadata.detect_from_dataframe(supply_chain_df)
    metadata.save_to_json(metadata_filename)
else:
    metadata = Metadata.load_from_json(metadata_filename)

# Load the Brazil datasets
connection_brazil = sqlite3.connect(brazil_database_path)

# Read the order items and orders datasets
order_items_df = pd.read_sql_query("SELECT * FROM olist_order_items_dataset", connection_brazil)
orders_df = pd.read_sql_query("SELECT order_id, order_purchase_timestamp FROM olist_orders_dataset", connection_brazil)

# Merge order items with order timestamps
merged_df = pd.merge(order_items_df, orders_df, on='order_id')

# Generate synthetic discount data using GaussianCopula
model = GaussianCopulaSynthesizer(metadata, default_distribution='uniform')
model.fit(supply_chain_df)

# Set date with increased discount rate activity
target_date = '2017-11-24'

# Generate initial synthetic discount rates
num_rows = len(merged_df)
synthetic_discount_rates = model.sample(num_rows)['Order Item Discount Rate']

# Calculate the average discount rate from the real data
average_discount_rate = supply_chain_df['Order Item Discount Rate'].mean()

# Filter synthetic rates within valid ranges
num_bins = 80
counts, bin_edges = np.histogram(supply_chain_df['Order Item Discount Rate'], bins=num_bins)
valid_ranges = [(bin_edges[i], bin_edges[i + 1]) for i in range(len(counts)) if counts[i] > 0]

# Apply discount bias for the target date
discount_rates = []
for i, rate in enumerate(synthetic_discount_rates):
    if merged_df['order_purchase_timestamp'].iloc[i].startswith(target_date):
        # For Nov 24 (Black Friday), generate discounts more frequently in the upper half of the range
        biased_rate = np.random.uniform(low=average_discount_rate, high=max(bin_edges[-1], max(bin_edges[:num_bins//2]) + 0.1))
    else:
        # For other dates, keep standard rates within valid ranges
        biased_rate = rate
    # Ensure generated rates are within valid ranges
    for lower, upper in valid_ranges:
        if lower < biased_rate < upper:
            discount_rates.append(biased_rate)
            break

# Fill any remaining spots to match num_rows (if some rates were excluded by filtering)
while len(discount_rates) < num_rows:
    additional_rate = np.random.uniform(low=min(bin_edges[:-1]), high=max(bin_edges[1:]))
    for lower, upper in valid_ranges:
        if lower < additional_rate < upper:
            discount_rates.append(additional_rate)
            break

# Update the Brazil dataset with synthetic rates
merged_df['discount_rate'] = discount_rates[:num_rows]

# Remove the order_purchase_timestamp column
merged_df.drop(columns=['order_purchase_timestamp'], inplace=True)

# Save the updated DataFrame back to the olist_order_items_dataset table
merged_df.to_sql('olist_order_items_dataset', connection_brazil, if_exists='replace', index=False)

# Commit and close connection
connection_brazil.commit()
connection_brazil.close()

# Compare real and synthetic data distributions
plt.figure(figsize=(12, 6))
sns.histplot(supply_chain_df['Order Item Discount Rate'], color='blue', label='Real Data', kde=True, stat='density', bins=30)
sns.histplot(discount_rates, color='orange', label='Synthetic Data', kde=True, stat='density', bins=30)
plt.title('Comparison of Real and Synthetic Discount Rates')
plt.xlabel('Discount Rate')
plt.ylabel('Density')
plt.legend()
plt.show()

### Modify columns

# write_data_using_sql_query(brazil_database_path, add_churned_column_query())
# write_data_using_sql_query(brazil_database_path, update_churned_column_query())
# write_data_using_sql_query(brazil_database_path, change_column_names_and_add_price_after_discount_query())
# write_data_using_sql_query(brazil_database_path, drop_order_items_table_query())
# write_data_using_sql_query(brazil_database_path, rename_new_order_items_table_query())
# write_data_using_sql_query(brazil_database_path, add_price_before_discount_query())
# write_data_using_sql_query(brazil_database_path, round_discount_rate_query())
# write_data_using_sql_query(brazil_database_path, calculate_price_before_discount_query())
