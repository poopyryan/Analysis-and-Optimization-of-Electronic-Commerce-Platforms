import sqlite3
import pandas as pd
import numpy as np

def view_table(table, limit, conn):
    query = f"""
        SELECT *
        FROM {table}
        LIMIT {limit}
    """
    return pd.read_sql_query(query, conn)

def count_nulls(table, conn):
    # Get the column names from the table
    query = f"PRAGMA table_info({table});"
    columns_info = pd.read_sql_query(query, conn)
    columns = columns_info['name'].tolist()

    # Build a dynamic query to count NULL values in each column
    null_counts_query = ", ".join(
        [f"SUM(CASE WHEN \"{col}\" IS NULL THEN 1 ELSE 0 END) AS {col}_nulls" for col in columns]
    )
    query = f"SELECT {null_counts_query} FROM {table};"

    # Execute the query and return the result as a DataFrame
    null_counts = pd.read_sql_query(query, conn)
    return null_counts

def count_unique_values(table, conn):
    # Get the column names from the table
    query = f"PRAGMA table_info({table});"
    columns_info = pd.read_sql_query(query, conn)
    columns = columns_info['name'].tolist()

    # Build a dynamic query to count unique values in each column
    unique_counts_query = ", ".join(
        [f"COUNT(DISTINCT \"{col}\") AS {col}_unique" for col in columns]
    )
    query = f"SELECT {unique_counts_query} FROM {table};"

    # Execute the query and return the result as a DataFrame
    unique_counts = pd.read_sql_query(query, conn)
    return unique_counts

# Create function to get unique values from column of a table
def get_unique_values(table, column,conn):
    query = f"""
        SELECT DISTINCT "{column}" 
        FROM {table};
    """
    unique_values = pd.read_sql_query(query, conn)
    return unique_values

def clean_clv(clv_df, df_clv_rfm, df_expected_purchases):
    clv_df['index'] = clv_df['index'].astype(str)
    clv_df['customer_unique_id'] = clv_df['index'].str.extract(r'\[(.*)\]')
    monetary_values_list = df_clv_rfm.set_index("customer_id").loc[clv_df["customer_unique_id"], "monetary_value"]
    clv_df['monetary_value'] = monetary_values_list.values
    clv_df.rename(columns={'mean' : 'expected_clv', 'hdi_3%': 'clv_estimate_hdi_3%', 'hdi_97%': 'clv_estimate_hdi_97%'}, inplace=True)
    expected_purchases_list = df_expected_purchases.set_index("customer_id").loc[clv_df["customer_unique_id"], "expected_purchases"]
    clv_df['expected_num_purchases']=expected_purchases_list.values
    return clv_df