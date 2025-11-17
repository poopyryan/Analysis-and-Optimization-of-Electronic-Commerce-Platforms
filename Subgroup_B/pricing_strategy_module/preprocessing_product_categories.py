import pandas as pd
import numpy as np
import sqlite3
from sklearn.preprocessing import LabelEncoder
import os
import sql_queries
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

# Function to classify seasonality based on the date
def classify_seasonality(date):
    if date.month == 12 and (date.day >= 24 and date.day <= 31):  # Christmas period
        return 'Holiday - Christmas'
    elif date.month == 11 and date.day == 29:  # Black Friday
        return 'Holiday - Black Friday'
    elif date.month == 11 and date.day == 30:  # Cyber Monday
        return 'Holiday - Cyber Monday'
    elif date.month == 8:  # Back to School season
        return 'Seasonal - Back to School'
    elif date.month in [5, 6]:  # Summer Sales
        return 'Seasonal - Summer Sales'
    else:
        return 'Regular'
    
# Function to merge two dataframes on a specified column
def merge_olist_df(df1, df2, column, method):
    merged = df1.merge(df2, on=column, how=method)
    return merged

# Function to preprocess the data from the DataCo dataset
def preprocess_dataco(all_data, reference_dir):
    # Ensure 'Order Date' is in datetime format
    all_data['Order Date'] = pd.to_datetime(all_data['Order Date'], errors='coerce')
    all_data['Product Category'] = all_data['Product Category'].str.strip() # remove space at the end
    all_data.rename(columns={'Product Category': 'Product_Category'}, inplace=True)
    all_data["Final Price"] = round(all_data["Order Item Total"] / all_data["Total Quantity Purchased"], 2)

    relevant_cols = ['Order Date','Order Month', 'Product Id', 'Product_Category', 'Order Item Discount', 
                    'Order Item Discount Rate', 'Total Quantity Purchased', 
                    'Sales', 'Order Item Total', 'Order Profit', 'Final Price']
    dataco = all_data[relevant_cols]

    dataco['Order Date'] = pd.to_datetime(dataco['Order Date'])
    dataco = dataco[(dataco['Order Date'].dt.year >= 2016) & 
                        (dataco['Order Date'].dt.year <= 2018)]

    dataco = dataco.rename(columns={'Sales': 'price_before_discount'})
    # we decided to remove so that prices can be better binned into price ranges
    dataco = dataco[dataco['price_before_discount'] <= 800]

    # binning into 20 price ranges
    dataco['price_bins'] = dataco.groupby(['Product_Category'])['price_before_discount'].transform(
        lambda x: pd.cut(x, bins=20, labels=False)
    )

    dataco = dataco.groupby(['Order Date', 'Order Month', 'Product_Category', 'price_bins']).agg({
        'Order Item Discount': 'mean',
        'Order Item Discount Rate': 'mean',
        'Total Quantity Purchased': 'sum', # to represent product demand
        'price_before_discount': 'mean', 
        'Final Price' : 'mean'
    }).reset_index()

    test_dataco = dataco.copy()

    test_dataco.to_csv(os.path.join(reference_dir, 'dataco.csv'), index=False)

    dataco.rename(columns={'Order Item Discount': 'dataco_avg_item_discount', 'Order Item Discount Rate': 'dataco_avg_item_discount_rate', 'Total Quantity Purchased': 'dataco_demand', 'price_before_discount': 'dataco_price_before'}, inplace=True)

    # for each category, get PED based on prev mounth
    # Define a mapping for months to ensure correct sorting
    month_order = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Apply this mapping to a new column for sorting
    dataco['month_number'] = dataco['Order Month'].map(month_order)

    # Sort by Product Category and Order Month (numerically)
    dataco = dataco.sort_values(by=['Product_Category', 'month_number', 'price_bins'])

    # Calculate the percentage change in 'avg_order_item_discount' and 'total_quantity_purchased' for each Product Category
    dataco['discount_change'] = dataco.groupby(['Product_Category', 'price_bins'])['dataco_avg_item_discount'].pct_change().fillna(0)
    dataco['quantity_change'] = dataco.groupby(['Product_Category', 'price_bins'])['dataco_demand'].pct_change().fillna(0)

    # Calculate the price elasticity of demand (PED) as: % change in quantity / % change in discount
    dataco['price_elasticity_of_demand'] = dataco['quantity_change'] / dataco['discount_change']

    dataco.replace([float('inf'), -float('inf')], np.nan, inplace=True)
    dataco.fillna(0, inplace=True)

    # Drop the 'month_number' column used for sorting
    dataco = dataco.drop(columns=['month_number'])

    # allocating elastic/inelastic based on PED calculated
    dataco['price_elasticity'] = dataco['price_elasticity_of_demand'].apply(
        lambda x: 'Elastic' if abs(x) > 1 else ('Inelastic' if abs(x) < 1 else 'N/A')
    )

    # manual reassign, since anything with PED=0 was automatically considered Inelastic
    elasticity_mapping = {
        'Accessories': 'Inelastic', 'Baseball & Softball': 'Elastic', 'Boxing & MMA': 'Elastic',
        'Camping & Hiking': 'Elastic', 'Cardio Equipment': 'Elastic', 'Cleats': 'Elastic',
        'Electronics': 'Elastic', 'Fishing': 'Inelastic', 'Fitness Accessories': 'Inelastic',
        "Girls' Apparel": 'Elastic', 'Golf Apparel': 'Elastic', 'Golf Balls': 'Elastic',
        'Golf Gloves': 'Elastic', 'Golf Shoes': 'Elastic', 'Hockey': 'Elastic',
        'Hunting & Shooting': 'Inelastic', 'Indoor/Outdoor Games': 'Elastic', 'Lacrosse': 'Elastic',
        "Men's Footwear": 'Elastic', 'Shop By Sport': 'Elastic', 'Tennis & Racquet': 'Elastic',
        'Trade-In': 'Inelastic', 'Water Sports': 'Elastic', "Women's Apparel": 'Elastic',
        'As Seen on  TV!': 'Inelastic', 'Golf Bags & Carts': 'Elastic', "Kids' Golf Clubs": 'Elastic',
        "Men's Golf Clubs": 'Elastic', 'Soccer': 'Elastic', 'Strength Training': 'Elastic',
        "Women's Golf Clubs": 'Elastic', 'Basketball': 'Elastic', 'Baby': 'Inelastic', 'Books': 'Inelastic',
        'CDs': 'Inelastic', 'Cameras': 'Elastic', "Children's Clothing": 'Elastic', 'Computers': 'Elastic',
        'Consumer Electronics': 'Elastic', 'Crafts': 'Inelastic', 'DVDs': 'Inelastic', 'Garden': 'Inelastic',
        'Health and Beauty': 'Elastic', "Men's Clothing": 'Elastic', 'Music': 'Inelastic',
        'Pet Supplies': 'Elastic', 'Sporting Goods': 'Elastic', 'Toys': 'Elastic', 'Video Games': 'Elastic',
        "Women's Clothing": 'Inelastic', 'Golf Accessories':'Inelastic'
    }

    dataco.loc[dataco['price_elasticity_of_demand'] == 0, 'price_elasticity'] = dataco['Product_Category'].map(elasticity_mapping)
    dataco['price_elasticity'] = dataco.apply(
        lambda row: elasticity_mapping[row['Product_Category']] if row['price_elasticity'] == 'N/A' else row['price_elasticity'],
        axis=1
    )
    dataco = dataco.drop(columns=['Order Month', 'price_elasticity_of_demand'])

    dataco['Seasonality'] = dataco['Order Date'].apply(classify_seasonality)
    dataco['Order Date'] = pd.to_datetime(dataco['Order Date'])
    dataco['Order Date'] = dataco['Order Date'].dt.strftime('%m-%Y')

    return dataco

# Function to preprocess the data from the Olist dataset
def preprocess_olist(olist):
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

    olist = olist[olist['price_before_discount'] <= 800]
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

    olist['price_bins'] = olist.groupby('Product_Category')['price_before_discount'].transform(
        lambda x: pd.cut(x, bins=20, labels=False)
    )

    olist = olist.groupby(['order_purchase_timestamp', 'Product_Category', 'price_bins']).agg(
        product_demand=('order_item_id', 'sum'),                     # Sum of 'order_item_id' as 'product_demand'
        avg_price_before_discount=('price_before_discount', 'mean'), # Average of 'price_before_discount'
        avg_discount_rate=('discount_rate', 'mean'),                 # Average of 'discount_rate'
        avg_price_after_discount=('price_after_discount', 'mean')    # Average of 'price_after_discount'
    ).reset_index()

    olist = olist.rename(columns={'order_purchase_timestamp': 'Order Date', 'product_demand':'olist_product_demand', 'avg_price_before_discount':'olist_price_before_discount', })

    return olist

def process_supply_chain_data(supply_chain_database_path, reference_dir):

    supply_chain_conn = open_connection(supply_chain_database_path)

    all_data = query_data(supply_chain_conn, sql_queries.supply_chain_query())

    dataco = preprocess_dataco(all_data, reference_dir)

    close_connection(supply_chain_conn)

    df_prep = dataco.drop(columns=['Order Date', 'dataco_avg_item_discount', 'dataco_price_before', 'discount_change', 'quantity_change'])

    # Use one-hot encoding to create binary columns for each unique category in 'Seasonality' and 'elasticity'
    df_prep = pd.get_dummies(df_prep, columns=['Seasonality', 'price_elasticity'], drop_first=True)

    le = LabelEncoder()
    df_prep['Product_Category_Encoded'] = le.fit_transform(df_prep['Product_Category'])
    df_prep = df_prep.drop(columns=['Product_Category'])

    df_prep.to_csv(os.path.join(reference_dir, 'dataco_prepped.csv'), index=False)

    print(f"{nowtime()} DataCo data preprocessed.")

    return dataco, le 

def process_olist_data(olist_database_path):

    olist_conn = open_connection(olist_database_path)

    olist_items = query_data(olist_conn, sql_queries.olist_query1())
    olist_products = query_data(olist_conn, sql_queries.olist_query2())
    olist_translate = query_data(olist_conn, sql_queries.olist_query3())
    olist_orders = query_data(olist_conn, sql_queries.olist_query4())

    olist_translated = merge_olist_df(olist_products, olist_translate, 'product_category_name', 'inner')
    olist_translated = olist_translated[['product_id', 'product_category_name_english']]

    olist = merge_olist_df(olist_orders, olist_items, 'order_id', 'inner')
    olist = merge_olist_df(olist, olist_products, 'product_id', 'inner')
    olist = merge_olist_df(olist, olist_translated, 'product_id', 'inner')

    olist = preprocess_olist(olist)

    close_connection(olist_conn)

    print(f"{nowtime()} Olist data preprocessed.")

    return olist

def merge_dataco_olist(dataco, olist, le, reference_dir):

    merged_df = pd.merge(dataco, olist, on=['Product_Category', 'Order Date', 'price_bins'], how='left')
    merged_df = merged_df.fillna(0)

    merged_df['Product_Category_Encoded'] = le.fit_transform(merged_df['Product_Category'])
    merged_prep = merged_df.drop(columns=['Order Date', 'Product_Category', 'dataco_avg_item_discount', 'dataco_price_before', 'discount_change', 'quantity_change',
                                        'avg_price_after_discount'])

    merged_prep = pd.get_dummies(merged_prep, columns=['Seasonality', 'price_elasticity'], drop_first=True)
    merged_prep = merged_prep.rename(columns={'avg_discount_rate': 'olist_avg_discount_rate'})

    merged_prep.to_csv(os.path.join(reference_dir, 'dataco_olist_prepped.csv'), index=False)

    print(f"{nowtime()} DataCo and Olist data merged and preprocessed.")

    return

@click.command()
@click.argument('supply_chain_database_path', type=click.Path(exists=True))
@click.argument('olist_database_path', type=click.Path(exists=True))
@click.argument('reference_dir', type=click.Path(exists=True))

def main(supply_chain_database_path, olist_database_path, reference_dir):

    dataco, le = process_supply_chain_data(supply_chain_database_path, reference_dir)

    olist = process_olist_data(olist_database_path)

    merge_dataco_olist(dataco, olist, le, reference_dir)

    return

if __name__ == '__main__':
    main()
