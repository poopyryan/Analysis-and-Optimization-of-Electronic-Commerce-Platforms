import pandas as pd
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

##### PRIORITY METRICS FUNCTIONS #####

def extract_late_delivery_summary(df):
    """
    Calculate the risk of late delivery based on a specified date and grouped by Product Name and Shipping Mode.
    
    Parameters:
    - df: DataFrame containing the supply chain data.
    
    Returns:
    - DataFrame summarizing late delivery probabilities for each product and shipping mode.
    """

    # Group by 'Product Name' and 'Shipping Mode', calculate total orders and late deliveries
    late_delivery_summary = df.groupby(['Product Name', 'Shipping Mode']).agg(
        total_orders=('Index', 'size'),  # Count all orders per product and shipping mode
        late_deliveries=('Delivery Status', lambda x: (x == 'Late delivery').sum())  # Count late deliveries
    ).reset_index()

    # Calculate % of late deliveries
    late_delivery_summary['late_delivery_probability'] = late_delivery_summary['late_deliveries'] / late_delivery_summary['total_orders']

    # Select relevant columns
    late_delivery_summary = late_delivery_summary[['Product Name', 'Shipping Mode', 'late_delivery_probability']]

    print(f"{nowtime()} Late delivery summary extracted.")

    return late_delivery_summary

def extract_avg_shipping_time(df):
    """
    Calculate the average shipping time for each product by order region based on a specified date.
    
    Parameters:
    - df: DataFrame containing the supply chain data.
    
    Returns:
    - DataFrame summarizing average shipping time for each product by order region.
    """

    # Group by 'Product Name' and 'Order Region' to calculate the average 'Days for shipping (real)'
    avg_shipping_days_per_product_region = df.groupby(['Product Name', 'Shipping Mode'])['Days for shipment (real)'].mean()
    
    # Reset index and rename the column
    avg_shipping_days_per_product_region_df = avg_shipping_days_per_product_region.reset_index().rename(columns={'Days for shipment (real)': 'Avg Shipping Time'})

    # Drop duplicates
    avg_shipping_days_per_product_region_df = avg_shipping_days_per_product_region_df.drop_duplicates()

    # Select relevant columns
    avg_shipping_days_per_product_region_df = avg_shipping_days_per_product_region_df[['Product Name', 'Shipping Mode', 'Avg Shipping Time']]

    print(f"{nowtime()} Average shipping time extracted.")

    return avg_shipping_days_per_product_region_df

@click.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.argument('database_path', type=click.Path(exists=True))
@click.argument('query', type=str)

def main(output_dir, database_path, query):

    # Connect to the database
    conn = open_connection(database_path)

    # Extract data between specified timeframe
    print(f"{nowtime()} Extracting data for priority metrics...")
    df = query_data(conn, query)

    # Extract summaries
    print(f"{nowtime()} Extracting late delivery summaries...")
    late_delivery_summary = extract_late_delivery_summary(df)

    print(f"{nowtime()} Extracting average shipping time...")
    avg_shipping_time = extract_avg_shipping_time(df)
                                                                     
    # Save summaries to CSV
    late_delivery_summary.to_csv(os.path.join(output_dir, 'late_delivery_summary.csv'), index=False)
    print(f"{nowtime()} Late delivery summary saved to CSV.")
    avg_shipping_time.to_csv(os.path.join(output_dir, 'avg_shipping_time.csv'), index=False)
    print(f"{nowtime()} Average shipping time saved to CSV.")\
    
    print(f"{nowtime()} Priority metrics saved to CSV.")

    # Close the connection
    close_connection(conn)

    return 

if __name__ == "__main__":
    main()