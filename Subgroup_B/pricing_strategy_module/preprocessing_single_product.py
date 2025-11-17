import pandas as pd
import numpy as np
import sqlite3
from sklearn.preprocessing import LabelEncoder
import sql_queries
import os
import click

def nowtime():

    time = pd.Timestamp('now').strftime('%Y-%m-%d %H:%M:%S')

    return f"[{time}]"

##### SQL FUNCTIONS #####

# Function to connect to a database
def open_connection(database_path):

    conn = sqlite3.connect(database_path)
    print(f"{nowtime()} Connected to database at {database_path}")

    return conn

# Function to query data from a database
def query_data(conn, query):

    df = pd.read_sql_query(query, conn)
    print(f"{nowtime()} Data extracted from database.")

    return df

# Function to close the sql connection
def close_connection(conn):
        
    conn.close()
    print(f"{nowtime()} Connection to database closed.")

    return

##### DATA PREPROCESSING #####

# Function to preprocess the DataCo data
def preprocess_single_product_dataco(all_data):
    # Ensure 'Order Date' is in datetime format
    all_data['Order Date'] = pd.to_datetime(all_data['Order Date'], errors='coerce')
    all_data['Product Category'] = all_data['Product Category'].str.strip() # remove space at the end
    all_data.rename(columns={'Product Category': 'Product_Category'}, inplace=True)
    all_data["Final Price"] = round(all_data["Order Item Total"] / all_data["Total Quantity Purchased"], 2)

    relevant_cols = ['Index','Order Date','Order Month', 'Product Id','Product Name', 'Product_Category', 'Order Item Discount', 
                    'Order Item Discount Rate', 'Total Quantity Purchased', 
                    'Sales', 'Order Item Total', 'Order Profit', 'Final Price']
    dataco = all_data[relevant_cols]

    dataco['Order Date'] = pd.to_datetime(dataco['Order Date'])
    dataco = dataco[(dataco['Order Date'].dt.year >= 2016) & 
                        (dataco['Order Date'].dt.year <= 2018)]

    dataco = dataco.rename(columns={'Sales': 'price_before_discount'})

    # preparing single product data
    # Filter the DataFrame based on the Product Name
    dataco_filtered = dataco[dataco['Product Name'] == "Perfect Fitness Perfect Rip Deck"]

    dataco_filtered['Order Item Discount'] = dataco_filtered['Order Item Discount']/dataco_filtered['Total Quantity Purchased']
    dataco_filtered['Order Item Discount Rate'] = dataco_filtered['Order Item Discount Rate']/dataco_filtered['Total Quantity Purchased']
    dataco_filtered['price_before_discount'] = dataco_filtered['price_before_discount']/dataco_filtered['Total Quantity Purchased']
    dataco_filtered['Order Item Total'] = dataco_filtered['Order Item Total']/dataco_filtered['Total Quantity Purchased']

    dataco_filtered_agg = dataco_filtered.groupby(['Order Month']).agg({
        'Order Item Discount': 'mean',
        'Order Item Discount Rate': 'mean',
        'Total Quantity Purchased': 'sum', # to represent product demand
        'price_before_discount': 'mean', 
        'Final Price' : 'mean'
    }).reset_index()

    dataco_filtered_agg.rename(columns={'Order Item Discount': 'dataco_avg_item_discount', 'Order Item Discount Rate': 'dataco_avg_item_discount_rate', 'Total Quantity Purchased': 'dataco_demand', 'price_before_discount': 'dataco_price_before'}, inplace=True)

    # for each category, get PED based on prev mounth
    # Define a mapping for months to ensure correct sorting
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Apply this mapping to a new column for sorting
    dataco_filtered_agg['month_number'] = dataco_filtered_agg['Order Month'].map(month_order)

    # Sort by Product Category and Order Month (numerically)
    dataco_filtered_agg = dataco_filtered_agg.sort_values(by=['month_number'])

    # Calculate the percentage change in 'avg_order_item_discount' and 'total_quantity_purchased' for each Product Category
    dataco_filtered_agg['discount_change'] = dataco_filtered_agg['dataco_avg_item_discount'].pct_change().fillna(0)
    dataco_filtered_agg['quantity_change'] = dataco_filtered_agg['dataco_demand'].pct_change().fillna(0)

    # Calculate the price elasticity of demand (PED) as: % change in quantity / % change in discount
    dataco_filtered_agg['price_elasticity_of_demand'] = dataco_filtered_agg['quantity_change'] / dataco_filtered_agg['discount_change']

    dataco_filtered_agg.replace([float('inf'), -float('inf')], np.nan, inplace=True)
    dataco_filtered_agg.fillna(0, inplace=True)

    # Drop the 'month_number' column used for sorting
    dataco_filtered_agg = dataco_filtered_agg.drop(columns=['month_number'])

    print(f"{nowtime()} DataCo data preprocessed.")

    return dataco_filtered_agg

# Function to preprocess the Olist data
def preprocess_single_product_olist(olist):
    olist['order_purchase_timestamp'] = pd.to_datetime(olist['order_purchase_timestamp'])
    olist = olist[(olist['order_purchase_timestamp'].dt.year >= 2016) & 
                        (olist['order_purchase_timestamp'].dt.year <= 2018)]

    olist.drop(columns=['index_x', 'order_status','order_approved_at',
        'order_delivered_carrier_date', 'order_delivered_customer_date',
        'order_estimated_delivery_date', 'index_y', 'seller_id', 
        'shipping_limit_date', 'freight_value','index', 'product_category_name',
        'product_name_lenght', 'product_description_lenght',
        'product_photos_qty', 'product_weight_g', 'product_length_cm',
        'product_height_cm', 'product_width_cm', 'customer_id'], inplace=True)

    olist['order_purchase_timestamp'] = pd.to_datetime(olist['order_purchase_timestamp'])
    olist['order_purchase_timestamp'] = olist['order_purchase_timestamp'].dt.strftime('%m-%Y')

    mapping = {
        'cool_stuff': 'As Seen on  TV!', 'pet_shop': 'Pet Supplies', 'furniture_decor': 'Garden', 'perfumery': 'Health and Beauty',
        'garden_tools': 'Garden', 'housewares': 'Housewares', 'telephony': 'Consumer Electronics', 'health_beauty': 'Health and Beauty',
        'books_technical': 'Books', 'fashion_bags_accessories': "Women's Apparel", 'bed_bath_table': 'Health and Beauty',
        'sports_leisure': 'Sporting Goods', 'consoles_games': 'Video Games', 'office_furniture': 'Office Furniture',
        'luggage_accessories': 'Accessories', 'food': 'Food', 'agro_industry_and_commerce': 'Industry and Commerce',
        'electronics': 'Electronics', 'computers_accessories': 'Computers', 'construction_tools_construction': 'Construction Tools',
        'audio': 'Consumer Electronics', 'baby': 'Baby', 'construction_tools_lights': 'Construction Tools', 'toys': 'Toys',
        'stationery': 'Office Supplies', 'industry_commerce_and_business': 'Industry and Commerce', 'watches_gifts': 'Accessories',
        'auto': 'Automotive', 'home_appliances': 'Home Appliances', 'kitchen_dining_laundry_garden_furniture': 'Housewares',
        'air_conditioning': 'Home Appliances', 'home_confort': 'Housewares', 'fixed_telephony': 'Consumer Electronics',
        'small_appliances_home_oven_and_coffee': 'Small Appliances', 'diapers_and_hygiene': 'Baby', 'signaling_and_security': 'Electronics',
        'musical_instruments': 'Music', 'small_appliances': 'Small Appliances', 'costruction_tools_garden': 'Garden', 'art': 'Crafts',
        'home_construction': 'Crafts', 'books_general_interest': 'Books', 'party_supplies': 'Party Supplies', 'construction_tools_safety': 'Construction Tools',
        'cine_photo': 'Cameras', 'fashion_underwear_beach': "Women's Apparel", 'fashion_male_clothing': "Men's Clothing", 'food_drink': 'Food',
        'drinks': 'Beverages', 'furniture_living_room': 'Furniture', 'market_place': 'Market Place', 'music': 'Music', 'fashion_shoes': "Women's Apparel",
        'flowers': 'Garden', 'home_appliances_2': 'Home Appliances', 'fashio_female_clothing': "Women's Clothing", 'computers': 'Computers',
        'books_imported': 'Books', 'christmas_supplies': 'Seasonal Items', 'furniture_bedroom': 'Furniture', 'home_comfort_2': 'Housewares',
        'dvds_blu_ray': 'DVDs', 'cds_dvds_musicals': 'CDs', 'arts_and_craftmanship': 'Crafts', 'furniture_mattress_and_upholstery': 'Furniture',
        'tablets_printing_image': 'Tablets & Accessories', 'costruction_tools_tools': 'Construction Tools', 'fashion_sport': 'Sporting Goods',
        'la_cuisine': 'Kitchen', 'security_and_services': 'Electronics', 'fashion_childrens_clothes': "Children's Clothing"
    }

    olist['Product_Category'] = olist['product_category_name_english'].map(mapping)
    olist = olist.drop(columns=['product_category_name_english'])

    # filter to get as close products to dataco as possible
    olist_filtered = olist[(olist['price_before_discount'] >= 30) & (olist['price_before_discount'] <= 90) & (olist['Product_Category']=="Sporting Goods")]
    olist_filtered['order_purchase_timestamp'] = pd.to_datetime(olist_filtered['order_purchase_timestamp'], format='%m-%Y')
    olist_filtered['Order Month'] = olist_filtered['order_purchase_timestamp'].dt.strftime('%B')

    olist_filtered_agg = olist_filtered.groupby(['Order Month']).agg(
        product_demand=('order_item_id', 'sum'),                     # Sum of 'order_item_id' as 'product_demand'
        avg_price_before_discount=('price_before_discount', 'mean'), # Average of 'price_before_discount'
        avg_discount_rate=('discount_rate', 'mean'),                 # Average of 'discount_rate'
        avg_price_after_discount=('price_after_discount', 'mean')    # Average of 'price_after_discount'
    ).reset_index()

    olist_filtered_agg = olist_filtered_agg.rename(columns={'product_demand':'olist_product_demand', 'avg_price_before_discount':'olist_price_before_discount', 'avg_discount_rate':'olist_avg_discount_rate', 'avg_price_after_discount':'olist_avg_price_after_discount'})

    print(f"{nowtime()} Olist data preprocessed.")

    return olist_filtered_agg

# Function to classify the seasonality of a month
def classify_seasonality(month_name):
    if month_name == 'December':  # Christmas period
        return 'Holiday - Christmas'
    elif month_name == 'November':  # Black Friday / Cyber Monday period
        return 'Holiday - Cyber Monday'
    elif month_name == 'August':  # Back to School season
        return 'Seasonal - Back to School'
    elif month_name in ['May', 'June']:  # Summer Sales
        return 'Seasonal - Summer Sales'
    else:
        return 'Regular'
    
# Function to merge two DataFrames
def merge_olist_df(df1, df2, column, method):
    merged = df1.merge(df2, on=column, how=method)
    return merged
    
# Function to preprocess the DataCo data
def process_supply_chain_data(supply_chain_database_path, reference_dir):

    # Connect to the database
    supply_chain_conn = open_connection(supply_chain_database_path)

    # Extract data from the database
    all_data = query_data(supply_chain_conn, sql_queries.supply_chain_query())

    # Preprocess the DataCo data
    dataco_filtered_agg = preprocess_single_product_dataco(all_data)

    # Apply 
    single_product_df_prep = dataco_filtered_agg.copy()
    single_product_df_prep['Seasonality'] = single_product_df_prep['Order Month'].apply(classify_seasonality)

    le = LabelEncoder()
    single_product_df_prep['Seasonality_Encoded'] = le.fit_transform(single_product_df_prep['Seasonality'])
    single_product_df_prep = single_product_df_prep.drop(columns=['Order Month', 'dataco_price_before', 'discount_change', 'quantity_change', 'Seasonality'])

    single_product_df_prep.to_csv(os.path.join(reference_dir, 'dataco_single_product.csv'), index=False)

    print(f"{nowtime()} DataCo data processed and saved to CSV.")

    close_connection(supply_chain_conn)

    return dataco_filtered_agg

# Function to preprocess the Olist data
def process_olist_data(brazil_database_path, reference_dir, dataco_filtered_agg):

    olist_conn = open_connection(brazil_database_path)

    olist_items = query_data(olist_conn, sql_queries.olist_query1())
    olist_products = query_data(olist_conn, sql_queries.olist_query2())
    olist_translate = query_data(olist_conn, sql_queries.olist_query3())
    olist_orders = query_data(olist_conn, sql_queries.olist_query4())

    olist_translated = merge_olist_df(olist_products, olist_translate, 'product_category_name', 'inner')
    olist_translated = olist_translated[['product_id', 'product_category_name_english']]

    olist = merge_olist_df(olist_orders, olist_items, 'order_id', 'inner')
    olist = merge_olist_df(olist, olist_products, 'product_id', 'inner')
    olist = merge_olist_df(olist, olist_translated, 'product_id', 'inner')

    olist_filtered_agg = preprocess_single_product_olist(olist)

    merged_df = pd.merge(dataco_filtered_agg, olist_filtered_agg, on=['Order Month'], how='left')
    merged_df = merged_df.fillna(0)
    merged_df['Seasonality'] = merged_df['Order Month'].apply(classify_seasonality)

    le = LabelEncoder()
    merged_df['Seasonality_Encoded'] = le.fit_transform(merged_df['Seasonality'])
    merged_prep = merged_df.drop(columns=['Order Month', 'dataco_price_before', 'discount_change', 'quantity_change', 'olist_price_before_discount', 'olist_avg_price_after_discount', 'Seasonality'])

    merged_prep.to_csv(os.path.join(reference_dir, 'dataco_olist_single_product.csv'), index=False)

    print(f"{nowtime()} Olist data processed and saved to CSV.")

    close_connection(olist_conn)

    return

@click.command()
@click.argument('supply_chain_database_path', type=click.Path(exists=True))
@click.argument('brazil_database_path', type=click.Path(exists=True))
@click.argument('reference_dir', type=click.Path(exists=True))

def main(supply_chain_database_path, brazil_database_path, reference_dir):

    dataco_filtered_agg = process_supply_chain_data(supply_chain_database_path, reference_dir)

    process_olist_data(brazil_database_path, reference_dir, dataco_filtered_agg)

    return

if __name__ == '__main__':
    main()

