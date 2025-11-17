import pandas as pd
import numpy as np
import sqlite3
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

##### FORECASTED DATA TRANSFORMATION #####

def preprocess_forecasted_data(forecasted_data):

    if 'Product Id' not in forecasted_data.columns:
        
        print(f"{nowtime()} 'Product Id' column not found in the dataset. Transforming Product Columns...")

        # Extract columns that start with 'Product_'
        product_columns = [col for col in forecasted_data.columns if col.startswith('Product_')]

        # Use idxmax to find the column with True/1 for each row
        forecasted_data['Product Id'] = forecasted_data[product_columns].idxmax(axis=1)

        # Remove the 'Product_' prefix to get only the product ID
        forecasted_data['Product Id'] = forecasted_data['Product Id'].str.replace('Product_', '').astype(int)

        # Drop the one-hot encoded columns as they are no longer needed
        forecasted_data = forecasted_data[['Order Month', 'Product Id', 'Predicted Quantity']]

    # Sum the predicted quantities for each product
    forecasted_data = forecasted_data.groupby('Product Id')['Predicted Quantity'].sum().reset_index()

    print(f"{nowtime()} Forecasted data preprocessed.")

    return forecasted_data

def calculate_EOQ_ROP(forecasted_data, product_info):
    """
    Calculate the Economic Order Quantity (EOQ) and Reorder Point (ROP) for each product based on forecasted demand and product information.
    """

    # Merge forecasted data with product information
    forecasted_data = forecasted_data.merge(product_info, how='left', on='Product Id')
    
    # Calculate EOQ and ROP
    forecasted_data['Economic Order Quantity'] = round(np.sqrt((2 * forecasted_data['Predicted Quantity'] * forecasted_data['Manufacturing Cost'] / (forecasted_data['Daily Storage Cost'] * 365))), 0)
    forecasted_data['Forecasted Avg Weekly Demand'] = round(forecasted_data['Predicted Quantity'] / 52, 0)
    forecasted_data['Reorder Point'] = round(forecasted_data['Forecasted Avg Weekly Demand'] * forecasted_data['Manufacturing Time'], 0)
    
    print(f"{nowtime()} EOQ and ROP calculated.")

    return forecasted_data

##### STOCK DATA TRANSFORMATION #####

def process_stock(stock_data, product_info):

    # Filter stock data to only include products in the product info data
    stock_data = stock_data[stock_data['Product Name'].isin(product_info['Product Name'])]

    # Convert 'Date' column to datetime
    stock_data["Date"] = pd.to_datetime(stock_data["Date"])

    # Drop columns
    stock_data = stock_data.drop(['Total Sold', 'Date'], axis=1)

    print(f"{nowtime()} Stock data processed.")

    return stock_data

def get_starting_stock(input_year, conn, product_info):
    """
    Get the starting stock for each product at the beginning of the year.
    """

    starting_date = f'{input_year}-01-01'
    
    stock_query = f'''SELECT * FROM stock_data WHERE "Date" = "{starting_date}"'''

    # Query the stock data
    stock_data = query_data(conn, stock_query)

    stock_data = process_stock(stock_data, product_info)

    return stock_data

def identify_understocked_products(stock_data, forecasted_data):

    # Merge stock data and forecasted data
    inventory_data = forecasted_data.merge(stock_data, how='left', on='Product Name')

    # Fill NaN values with 0
    inventory_data = inventory_data.fillna(0)

    # Identify understocked products
    inventory_data['Understocked'] = np.where(inventory_data['Current Stock'] < inventory_data['Reorder Point'], 1, 0)

    print(f"{nowtime()} Understocked products identified.")

    # Get understocked products
    understocked_products = inventory_data[inventory_data['Understocked'] == 1]

    # Select columns for output
    understocked_products = understocked_products[['Product Name', 'Product Id', 'Warehouse Id', 'Forecasted Avg Weekly Demand','Economic Order Quantity', 'Reorder Point', 'Current Stock']]

    return inventory_data, understocked_products

@click.command()
@click.argument('output_dir', type=click.Path())
@click.argument('database_path', type=click.Path())
@click.argument('product_info_query', type=str)
@click.argument('input_year', type=int)

def main(output_dir, database_path, product_info_query, input_year):

    # Connect to the database
    conn = open_connection(database_path)

    # Query the product info data
    product_info = query_data(conn, product_info_query)

    # Load the forecasted data
    forecasted_data = pd.read_csv(os.path.join(output_dir, "demand_forecast.csv"))

    # Preprocess the forecasted data
    forecasted_data = preprocess_forecasted_data(forecasted_data)

    # Calculate EOQ and ROP
    forecasted_data = calculate_EOQ_ROP(forecasted_data, product_info)

    # Get the starting stock for the input year
    stock_data = get_starting_stock(input_year, conn, product_info)

    # Identify understocked products
    inventory_data, understocked_products = identify_understocked_products(stock_data, forecasted_data)

    # Close the connection
    close_connection(conn)

    # Save output to CSV
    inventory_data.to_csv(os.path.join(output_dir, 'product_EOQ_ROP.csv'), index=False)

    understocked_products.to_csv(os.path.join(output_dir, 'products_for_immediate_restocking.csv'), index=False)

    return inventory_data, understocked_products

if __name__ == '__main__':
    main()
