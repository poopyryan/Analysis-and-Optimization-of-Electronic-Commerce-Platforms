import pandas as pd
import numpy as np
import sqlite3
import os
import click
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
import joblib
import matplotlib.pyplot as plt

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

##### MODEL DATA PREPROCESSING FUNCTIONS #####

def get_train_data(input_year, conn):

    if input_year == 2015:
        print(f"{nowtime()} Unable to forecast for 2015 as this is the first year of sales data.")
        exit()
    if input_year == 2016 or input_year == "2016":
        start_year_month = "2015-01"
    else:
        start_year_month = f"{input_year-2}-12"

    train_data_query = f'''
    SELECT "Order Year", "Order Month", "Product Id", SUM("Total Quantity Purchased") AS "Total Quantity Purchased"
    FROM cleaned_order_data
    WHERE "Order Year-Month" BETWEEN "{start_year_month}" AND "{input_year-1}-12"
    GROUP BY "Product Id", "Order Year-Month";
    '''
    try:
        train_data = query_data(conn, train_data_query)

        if train_data.empty:
            print(f"{nowtime()} No sales data available for training model.")
            exit()
    
    except Exception as e:
        print(f"{nowtime()} Query Failed: {e}")
        exit()

    return train_data

def preprocess_train_data(train_data):

    # Encode Order Month as numeric and convert to account for cyclic features
    month_mapping = {month: i+1 for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 
                                                        'July', 'August', 'September', 'October', 'November', 'December'])}
    train_data['Order Month'] = train_data['Order Month'].map(month_mapping)

    # Ensure that train_data is sorted in order of Product Id and month
    train_data = train_data.sort_values(['Product Id', 'Order Year', 'Order Month'])

    # Get the previous month's quantity for each product
    train_data['Quantity from previous month'] = train_data.groupby('Product Id')['Total Quantity Purchased'].shift(1)
    print(f"{nowtime()} Previous month's quantity added.")
    
    # Remove rows with NaN values
    train_data = train_data.dropna()

    # Add in cyclic features for Order Month
    train_data['Month_sin'] = np.sin(2 * np.pi * train_data['Order Month'] / 12)
    train_data['Month_cos'] = np.cos(2 * np.pi * train_data['Order Month'] / 12)
    print(f"{nowtime()} Cyclic Features Added.")

    # Sort and one hot encode the data
    train_data = train_data.sort_values(by=['Order Year', 'Order Month', 'Product Id'])
    train_data = train_data.join(pd.get_dummies(train_data['Product Id'], prefix='Product')).drop('Product Id', axis=1)
    print(f"{nowtime()} Data sorted and one-hot encoded.")

    X_train = train_data.drop(columns=["Total Quantity Purchased", "Order Year", "Order Month"])
    Y_train = train_data["Total Quantity Purchased"]
    print(f"{nowtime()} Training Data preprocessed.")

    return X_train, Y_train

##### MODEL TRAINING FUNCTIONS #####

# Function to read in the model
def read_model(model_path):

    model = joblib.load(model_path)
    print(f"{nowtime()} Model loaded from {model_path}")

    return model

# Function to create the model
def create_GB_model(X_train, Y_train, param_grid=None):

    if param_grid is None:
        param_grid = {
            'n_estimators': [100, 200, 300],                # Number of boosting stages
            'learning_rate': [0.01, 0.05, 0.1, 0.2],        # Controls the contribution of each tree
            'max_depth': [3, 5, 7],                     # Controls the depth of each tree
            'min_samples_split': [2, 5, 10],                # Minimum samples required to split a node
            'min_samples_leaf': [1, 2, 4],                  # Minimum samples required at a leaf node
            'subsample': [0.7, 0.85, 1.0],                  # Fraction of samples used for each tree
            'max_features': ['sqrt', 'log2', None]          # Number of features to consider at each split
        }

    # Create the model
    model = GradientBoostingRegressor(random_state=42)
    print(f"{nowtime()} Model created. Begin Hyperparameter Tuning...")

    grid_search_gb = GridSearchCV(model, param_grid, cv=5, verbose=2, n_jobs=-1)
    grid_search_gb.fit(X_train, Y_train)
    print(f"{nowtime()} Beginning hyperparameter tuning...")

    # Display best parameters
    best_model = grid_search_gb.best_estimator_
    print(f"{nowtime()} Best parameters: {grid_search_gb.best_params_}")

    return best_model

def evaluate_model(model, X_train, Y_train):

    # Get the model score
    score = model.score(X_train, Y_train)
    print(f"{nowtime()} Model Score: {score}")

    return

##### DEMAND FORECASTING FUNCTIONS #####

def convert_to_month(month_sin, month_cos):

    angle = np.arctan2(month_sin, month_cos)
    month = (angle / (2 * np.pi) * 12) % 12
    month = np.round(month).astype(int)
    month[month == 0] = 12  # Adjust for 0 to be December

    return month

def prepare_forecast_data(queried_train_data, input_year):

    carried_over_quantities = queried_train_data.groupby('Product Id')['Total Quantity Purchased'].last().reset_index()

    carried_over_quantities["Order Month"] = 1
    carried_over_quantities["Order Year"] = input_year+1
    carried_over_quantities.rename(columns={"Total Quantity Purchased": "Quantity from previous month"}, inplace=True)

    # Generate new rows for each Product Id for months 2 to 12, setting Quantity from previous month to 0
    new_rows = []
    for product_id in carried_over_quantities['Product Id'].unique():
        for month in range(2, 13):
            new_rows.append({'Product Id': product_id, 'Quantity from previous month': 0, 'Order Month': month, 'Order Year': 2016})

    # Append new rows to the original DataFrame
    forecast_data = pd.concat([carried_over_quantities, pd.DataFrame(new_rows)], ignore_index=True)

    # Sort the DataFrame for readability
    forecast_data.sort_values(by=['Order Month', 'Product Id'], inplace=True)
    forecast_data.reset_index(drop=True, inplace=True)

    # Add in cyclic features for Order Month
    forecast_data['Month_sin'] = np.sin(2 * np.pi * forecast_data['Order Month'] / 12)
    forecast_data['Month_cos'] = np.cos(2 * np.pi * forecast_data['Order Month'] / 12)
    print(f"{nowtime()} Cyclic Features Added.")

    # One hot encode the data
    forecast_data = forecast_data.join(pd.get_dummies(forecast_data['Product Id'], prefix='Product')).drop('Product Id', axis=1)
    print(f"{nowtime()} Data sorted and one-hot encoded.")

    # Remove columns
    forecast_data = forecast_data.drop(columns=["Order Year", "Order Month"])
    print(f"{nowtime()} Training Data preprocessed.")

    return forecast_data

# Forecasting for the next year
def forecast_demand(model, data, tolerance=1e-6):
    results = pd.DataFrame()
    previous_month_quantity = [None] * len(data[data['Month_sin'] == np.sin(2 * np.pi * (1 / 12))])

    for month in range(1, 13):
        month_sin = np.sin(2 * np.pi * (month / 12))
        month_cos = np.cos(2 * np.pi * (month / 12))

        # Filter data for the current month based on cyclical encoding with tolerance
        current_month_data = data[(np.abs(data['Month_sin'] - month_sin) < tolerance) & 
                                  (np.abs(data['Month_cos'] - month_cos) < tolerance)].copy()
        
        if month != 1:
            current_month_data['Quantity from previous month'] = previous_month_quantity

        prediction = model.predict(current_month_data)
        prediction = np.round(prediction)

        temp = pd.concat([current_month_data.reset_index(drop=True), pd.Series(prediction, name='Predicted Quantity')], axis=1)
        previous_month_quantity = prediction
        results = pd.concat([results, temp], ignore_index=True)

    results['Order Month'] = convert_to_month(results['Month_sin'], results['Month_cos'])

    # Find the column names that start with 'Product_'
    product_columns = [col for col in results.columns if col.startswith('Product_')]
    
    # Create the 'Product Id' column by finding the column with True (or 1) for each row
    results['Product Id'] = results[product_columns].idxmax(axis=1)
    
    # Extract the numeric Product Id from the column name (e.g., 'Product_37' -> 37)
    results['Product Id'] = results['Product Id'].str.extract('(\d+)').astype(float)
    
    # Drop the one-hot encoded columns
    results = results.drop(columns=product_columns)

    results = results[['Order Month', 'Product Id', 'Predicted Quantity']]

    print(f"{nowtime()} Demand Forecasted.")

    return results

def plot_forecast(forecasted_data, output_dir, input_year):

    forecast = forecasted_data.groupby('Order Month')['Predicted Quantity'].sum().reset_index()

    print(f"{nowtime()} Plotting forecasted data...")
    plt.figure(figsize=(12, 6))
    plt.plot(forecast['Order Month'].astype(str), forecast['Predicted Quantity'], label='Predicted Quantity', color='red', linestyle='--')
    plt.xlabel('Month')
    plt.ylabel('Predicted Quantity')
    plt.title(f'Total Predicted Quantity for {input_year}')
    plt.xticks(rotation=45)
    plt.grid(True)
    
    plt.savefig(os.path.join(output_dir, f'{input_year}_demand_forecast.png'))
    print(f"{nowtime()} Forecast plot saved!")

    return

@click.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.argument('input_year', type=int)
@click.argument('model_dir', type=click.Path(exists=True))
@click.argument('database_path', type=click.Path(exists=True))

def main(output_dir, input_year, model_dir, database_path):

    # Connect to the database
    conn = open_connection(database_path)

    # Get the training data
    train_data = get_train_data(input_year, conn)

    # Prepare inputs for forecasting
    input_for_forecast = prepare_forecast_data(train_data, input_year)

    # Preprocess the training data to obtain X_train and Y_train
    X_train, Y_train = preprocess_train_data(train_data)

    # Load the model
    model_path = os.path.join(model_dir, f"{input_year}_demand_forecasting_model.pkl")

    if os.path.exists(model_path):
        model = read_model(model_path)
    else:
        # Create the model
        model = create_GB_model(X_train, Y_train)
        joblib.dump(model, model_path)
        print(f"{nowtime()} Model saved to {model_path}")
        evaluate_model(model, X_train, Y_train)

    # Forecast the demand
    forecasted_data = forecast_demand(model, input_for_forecast)

    # Plot the forecasted data
    plot_forecast(forecasted_data, output_dir, input_year)

    # Save forecasted data to a csv file
    forecasted_data.to_csv(os.path.join(output_dir, 'demand_forecast.csv'), index=False)

    # Close the connection to the database
    close_connection(conn)

    return

if __name__ == "__main__":
    main()
