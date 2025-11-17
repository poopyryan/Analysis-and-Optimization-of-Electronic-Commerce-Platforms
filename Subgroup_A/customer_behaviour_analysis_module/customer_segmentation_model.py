import sqlite3
import pandas as pd
import queries
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def drop_na(df):
    """
    Drops rows with missing values from the DataFrame.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values dropped.
    """
    # Do not use inplace=True; return the modified DataFrame instead
    return df.dropna()

def coerce_date(df):
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], errors = 'coerce')
    return df

def get_latest_date(df):
    latest_date = df['order_delivered_customer_date'].max() +pd.Timedelta(days=1)
    return latest_date

# Calculate Recency (most recent purchase from each customer)
def calculate_recency(orders_payments_df, latest_date):
    """
    Calculate Recency for each customer based on the most recent purchase.

    Parameters:
        orders_payments_df (pd.DataFrame): The DataFrame containing order information with columns:
                                           'customer_unique_id' and 'order_delivered_customer_date'.
        latest_date (pd.Timestamp): The latest date to calculate recency against (e.g., current date).

    Returns:
        pd.DataFrame: DataFrame with 'customer_unique_id' and 'Recency' columns.
    """
    df_segm_rec = orders_payments_df.groupby('customer_unique_id')['order_delivered_customer_date'].max().reset_index()
    df_segm_rec.columns = ['customer_unique_id', 'most_recent_purchase']

    # Convert the most recent purchase date to datetime format
    df_segm_rec['most_recent_purchase'] = pd.to_datetime(df_segm_rec['most_recent_purchase'], errors='coerce')

    # Step 2: Calculate Recency in days
    df_segm_rec['Recency'] = (latest_date - df_segm_rec['most_recent_purchase']).dt.days

    return df_segm_rec[['customer_unique_id', 'Recency']]

# Calculate Frequency (how many times a customer has visited the platform)
def calculate_frequency(orders_payments_df):
    """
    Calculate the purchase frequency for each customer.

    Parameters:
        orders_payments_df (pd.DataFrame): The DataFrame containing order information with columns:
                                           'customer_unique_id' and 'order_delivered_customer_date'.

    Returns:
        pd.DataFrame: DataFrame with 'customer_unique_id' and 'Frequency' columns.
    """
    # Calculate the frequency of purchases for each customer
    df_segm_freq = orders_payments_df.groupby('customer_unique_id')['order_delivered_customer_date'].count().reset_index()
    df_segm_freq.columns = ['customer_unique_id', 'Frequency']

    return df_segm_freq

# Calculate Monetary Value (how much a customer has spent on the platform)
def calculate_monetary_value(orders_payments_df):
    """
    Calculate the total monetary value (sum of payments) for each customer.

    Parameters:
        orders_payments_df (pd.DataFrame): DataFrame containing order information with columns:
                                           'customer_unique_id' and 'payment_value'.

    Returns:
        pd.DataFrame: DataFrame with 'customer_unique_id' and 'Monetary Value' columns.
    """
    # Calculate total payment value for each customer
    df_segm_mon = orders_payments_df.groupby('customer_unique_id')['payment_value'].sum().reset_index()
    df_segm_mon.columns = ['customer_unique_id', 'Monetary Value']

    return df_segm_mon

def merge_rfm_data(df_recency, df_frequency, df_monetary):
    """
    Merge Recency, Frequency, and Monetary Value DataFrames into a single RFM DataFrame.

    Parameters:
        df_recency (pd.DataFrame): DataFrame containing 'customer_unique_id' and 'Recency'.
        df_frequency (pd.DataFrame): DataFrame containing 'customer_unique_id' and 'Frequency'.
        df_monetary (pd.DataFrame): DataFrame containing 'customer_unique_id' and 'Monetary Value'.

    Returns:
        pd.DataFrame: Merged RFM DataFrame with 'customer_unique_id', 'Recency', 'Frequency', and 'Monetary Value'.
    """
    # Merge Recency and Frequency DataFrames
    df_rfm = pd.merge(df_recency, df_frequency, on='customer_unique_id', how='inner')

    # Merge with Monetary Value DataFrame
    df_rfm = pd.merge(df_rfm, df_monetary, on='customer_unique_id', how='inner')

    return df_rfm


def scale_rfm_features(df_rfm):
    """
    Standardize the Recency, Frequency, and Monetary Value features in the RFM DataFrame.

    Parameters:
        df_rfm (pd.DataFrame): DataFrame containing 'Recency', 'Frequency', and 'Monetary Value'.

    Returns:
        pd.DataFrame: DataFrame with scaled 'Recency', 'Frequency', and 'Monetary Value' columns.
    """
    # Initialize the StandardScaler
    scaler = StandardScaler()

    # Fit and transform the RFM features
    scaled_features = scaler.fit_transform(df_rfm[['Recency', 'Frequency', 'Monetary Value']])

    # Create a new DataFrame with the scaled features
    df_rfm_scaled = pd.DataFrame(scaled_features, columns=['Recency', 'Frequency', 'Monetary Value'])

    return df_rfm_scaled

def order_cluster(cluster_field_name, target_field_name, df, ascending):
    # Calculate the mean of the target field for each cluster
    cluster_order = df.groupby(cluster_field_name)[target_field_name].mean().sort_values(ascending=ascending).index

    # Create a mapping from old cluster labels to new ordered labels
    cluster_mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_order)}

    # Apply the mapping to the original cluster field
    df[cluster_field_name] = df[cluster_field_name].map(cluster_mapping)

    return df


def calculate_sse(df_rfm_scaled, feature_column, max_k=10):
    """
    Calculate the Sum of Squared Errors (SSE) for K-means clustering with different values of k.

    Parameters:
        df_rfm_scaled (pd.DataFrame): The scaled RFM DataFrame.
        feature_column (str): The column to use for clustering (e.g., 'Recency').
        max_k (int): The maximum number of clusters to evaluate (default is 10).

    Returns:
        dict: A dictionary with the number of clusters (k) as keys and SSE as values.
    """
    # Initialize an empty dictionary to store SSE values
    sse = {}

    # Select the feature column for clustering
    df_feature = df_rfm_scaled[[feature_column]].copy()

    # Iterate over the range of k values (1 to max_k)
    for k in range(1, max_k + 1):
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=k, max_iter=1000, random_state=42).fit(df_feature)

        # Assign the cluster labels to the DataFrame (for evaluation purposes)
        df_feature['clusters'] = kmeans.labels_

        # Store the SSE (inertia) for the current number of clusters
        sse[k] = kmeans.inertia_

    return sse

import pandas as pd

def calculate_customer_score(df_rfm, recency_cluster_col, freq_cluster_col, money_cluster_col):
    """
    Calculate the customer score and return the grouped mean values of RFM features.

    Parameters:
        df_rfm (pd.DataFrame): The RFM DataFrame with clustering labels.
        recency_cluster_col (str): Column name for the Recency cluster labels.
        freq_cluster_col (str): Column name for the Frequency cluster labels.
        money_cluster_col (str): Column name for the Monetary Value cluster labels.

    Returns:
        pd.DataFrame: DataFrame grouped by 'customer_score' with mean values of 'Recency', 'Frequency', and 'Monetary Value'.
    """
    # Calculate the customer score
    df_rfm['customer_score'] = (
        df_rfm[recency_cluster_col] +
        df_rfm[freq_cluster_col] +
        df_rfm[money_cluster_col]
    )

    # Group by customer_score and calculate the mean of RFM features
    rfm_summary = df_rfm.groupby('customer_score')[['Recency', 'Frequency', 'Monetary Value']].mean()

    return rfm_summary

def assign_customer_segments(df_rfm, score_column):
    """
    Assign customer segments based on the customer score.

    Parameters:
        df_rfm (pd.DataFrame): The RFM DataFrame containing the customer score.
        score_column (str): The column name for the customer score.

    Returns:
        pd.DataFrame: DataFrame with an additional 'customer_segment' column.
    """
    # Define the segmentation function
    def customer_segment(score):
        if score <= 2:
            return 'Low Value'
        elif score <= 5:
            return 'Mid Value'
        else:
            return 'High Value'

    # Apply the segmentation function to the DataFrame
    df_rfm['customer_segment'] = df_rfm[score_column].apply(customer_segment)

    return df_rfm

