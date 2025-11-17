# Import necessary packages
import pandas as pd
import sqlite3
import os 
import json
import click

def nowtime():

    time = pd.Timestamp('now').strftime('%Y-%m-%d %H:%M:%S')

    return f"[{time}]"

def get_today():

    today = pd.Timestamp('now').strftime('%Y-%m-%d')

    return today

# Function to retrieve weights
def retrieve_weights(weights_input):

    weights = json.loads(weights_input)

    print(f"{nowtime()} Weights loaded.")

    return weights

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

##### PRIORITY SCORE FUNCTIONS #####

def extract_days_till_scheduled_delivery(df, late_delivery_summary, avg_shipping_time, date_of_interest = None):

    # Merge the DataFrames
    df = df.merge(late_delivery_summary, on = ['Product Name', 'Shipping Mode'], how = 'left')
    df = df.merge(avg_shipping_time, on = ['Product Name', 'Shipping Mode'], how = 'left')

    # Fill NaN values in 'Avg Shipping Time' with values from 'Days for shipment (scheduled)'
    df['Avg Shipping Time'] = df['Avg Shipping Time'].fillna(df['Days for shipment (scheduled)'])

    # Calculate the scheduled delivery date
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Scheduled Delivery Date'] = df['Order Date'] + pd.to_timedelta(df['Days for shipment (scheduled)'], unit='D')

    # Create a new column for Days Till Scheduled Delivery Date
    if not date_of_interest:
        date_of_interest = get_today()

    df['Days Till Scheduled Delivery'] = (df['Scheduled Delivery Date'] - pd.to_datetime(date_of_interest)).dt.days

    print(f"{nowtime()} Days till scheduled delivery extracted.")

    return df

def calculate_priority_score(df, weights = None):
    """
    Calculate the priority score for each order based on late delivery probability, 
    days till scheduled delivery, and average shipping time, with custom weights.
    
    Parameters:
    - df: DataFrame containing the required columns: Order Id, Product Name, Order Region, 
           Avg Shipping Time, Order Profit, late_delivery_probability, Days Till Scheduled Delivery.
    - weights: Dictionary to customize weights for each metric. If None, default weights are used.
    
    Returns:
    - DataFrame with priority scores.
    """
    
    # Default weights
    default_weights = {
        'late_delivery_probability': 0.5,   # Higher weight for late delivery probability
        'Days Till Scheduled Delivery': 0.4, # Higher weight for days till scheduled delivery
        'Avg Shipping Time': 0.3,           # Moderate weight for average shipping time --> takes into consideration order region 
        'Order Profit': 0.1            # Lowest weight for Order Profit
    }
    
    # Use custom weights if provided
    if weights:
        for key in weights:
            if key in default_weights:
                default_weights[key] = weights[key]

    # Normalize Days Till Scheduled Delivery (lower values should result in higher priority, so use inverse normalization)
    days_till_min = df['Days Till Scheduled Delivery'].min()
    days_till_max = df['Days Till Scheduled Delivery'].max()
    df['Days Till Scheduled Delivery'] = (days_till_max - df['Days Till Scheduled Delivery']) / (days_till_max - days_till_min)

    # Normalize Avg Shipping Time (shorter shipping times should result in higher priority, so use inverse normalization)
    shipping_time_min = df['Avg Shipping Time'].min()
    shipping_time_max = df['Avg Shipping Time'].max()
    df['Avg Shipping Time'] = (shipping_time_max - df['Avg Shipping Time']) / (shipping_time_max - shipping_time_min)

    # Normalize Order Profit (direct normalization as higher Order Profit increases priority)
    benefit_min = df['Order Profit'].min()
    benefit_max = df['Order Profit'].max()
    df['Order Profit'] = (df['Order Profit'] - benefit_min) / (benefit_max - benefit_min)

    # Calculate the priority score using the updated formula
    df['priority_score'] = (
        df['late_delivery_probability'] * default_weights['late_delivery_probability'] +  # Higher probability, higher priority
        df['Days Till Scheduled Delivery'] * default_weights['Days Till Scheduled Delivery'] +  # Lower days till delivery, higher priority
        df['Avg Shipping Time'] * default_weights['Avg Shipping Time'] +  # Shorter shipping time, higher priority
        df['Order Profit'] * default_weights['Order Profit']  # Lower weight for Order Profit
    )

    # Order the df based on priority_score
    df = df.sort_values(by = 'priority_score', ascending = False)
    
    print(f"{nowtime()} Priority scores calculated.")

    return df

@click.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.argument('references_dir', type=click.Path(exists=True))
@click.argument('database_path', type=click.Path(exists=True))
@click.argument('date_of_interest', type=str)
@click.argument('query', type=str)
@click.option('--weights', type=str, default=None, help='Custom weights for priority score calculation.')

def main(output_dir, references_dir, database_path, date_of_interest, query, weights): 
    
    # Connect to the database
    conn = open_connection(database_path)

    # Extract data between specified timeframe
    print(f"{nowtime()} Extracting order data...")
    df = query_data(conn, query)

    # Extracting summaries
    print(f"{nowtime()} Extracting late delivery summaries...")
    late_delivery_summary = pd.read_csv(os.path.join(references_dir, 'late_delivery_summary.csv'))
    print(f"{nowtime()} Late average shipping time...")
    avg_shipping_time = pd.read_csv(os.path.join(references_dir, 'avg_shipping_time.csv'))

    # Extract days till scheduled delivery
    print(f"{nowtime()} Extracting days till scheduled delivery...")
    df = extract_days_till_scheduled_delivery(df, late_delivery_summary, avg_shipping_time, date_of_interest = date_of_interest)
    
    if weights is not None:
        weights = retrieve_weights(weights)

    # Calculate the priority score
    print(f"{nowtime()} Calculating priority scores...")
    df = calculate_priority_score(df, weights = weights)

    # Save the priority scores to a CSV file
    df.to_csv(os.path.join(output_dir, f'{date_of_interest}_priority_scores.csv'), index=False)

    print(f"{nowtime()} Priority scores saved to CSV.")

    return

if __name__ == "__main__":
    main()
