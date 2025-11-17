# Import necessary packages
import pandas as pd
from fuzzywuzzy import process
from unidecode import unidecode
import sqlite3
import json
import click

def nowtime():

    time = pd.Timestamp('now').strftime('%Y-%m-%d %H:%M:%S')

    return f"[{time}]"

# Function to extract country mapping dictionary
def retrieve_country_mappings(country_mapping_input):

    country_mappings = json.loads(country_mapping_input)

    print(f"{nowtime()} Country mappings loaded.")

    return country_mappings

##### SQL FUNCTIONS #####

# Function to connect to a database
def connect_to_database(database_path):

    conn = sqlite3.connect(database_path)
    print(f"{nowtime()} Connected to database at {database_path}")

    return conn

# Function to query data from a database
def query_data(conn, query):

    df = pd.read_sql_query(query, conn)
    print(f"{nowtime()} Data extracted from database.")

    return df

# Function to add a table to a database
def add_table_to_database(df, table_name, conn):
    
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.commit()
    print(f"{nowtime()} Table added to database.")

    return

# Function to close the sql connection
def close_connection(conn):
    
    conn.close()
    print(f"{nowtime()} Connection to database closed.")

    return

# Function to check if check if all occurences of Order Country, Order City, and Order State from order_data are city_lat_long table in the db
def check_city_data(df, conn):

    # Check if table city_lat_long exists
    check_table = pd.read_sql_query('SELECT name FROM sqlite_master WHERE type="table" AND name="city_lat_long"', conn)

    if not check_table.empty:
        data = pd.read_sql_query('SELECT "Order Country", "Order City", "Order State" FROM city_lat_long', conn)

        # Check if all occurences of Order Country, Order City, and Order State from order_data are present in database
        missing_locations = df[~df[['country', 'city', 'state']].apply(tuple, 1).isin(data[['Order Country', 'Order City', 'Order State']].apply(tuple, 1))]

        if not missing_locations.empty:
            print(f"{nowtime()} New Order City identified. Mapping for new countries...")
            return False
        else:
            print(f"{nowtime()} All Order Cities and their locations are present in the database.")
            return True
    else:
        print(f"{nowtime()} Order City data not found in the database. Mapping for new countries...")
        return False

##### PREPROCESSING STEPS #####

# Function to clean location names
def clean_location_name(location_name):

    if isinstance(location_name, str):
        location_name = unidecode(location_name).lower().strip().lstrip('`')

    return location_name

# Function to clean city, state, and country columns
def clean_locations(df):

    df['clean_city'] = df['city'].apply(clean_location_name)
    df['clean_state'] = df['state'].apply(clean_location_name)
    df['clean_country'] = df['country'].apply(clean_location_name)

    return df

# Function to extract world city data
def extract_world_city_data(file_path):
    
    # Extract world city data
    world_city_data = pd.read_csv(file_path)
    world_city_data = world_city_data[['city_ascii', 'country', 'admin_name','lat', 'lng']]
    world_city_data = world_city_data.rename(columns={'city_ascii': 'city', 'admin_name': 'state','lat': 'latitude', 'lng': 'longitude'})

    print(f"{nowtime()} World city data extracted.")

    return world_city_data

##### MAPPING CITIES TO WORLD CITY DATA #####

# Function to replace country names
def replace_country_names(country_dictionary, order_data):

    order_data['original_country_name'] = order_data['country']
    order_data['country'] = order_data['country'].replace(country_dictionary)

    print(f"{nowtime()} Country names replaced.")

    return order_data

# Function to map cities to world city data
def map_cities(order_data, world_city_data):

    # Dictionary to store mapped unique cities
    mapped_cities = []

    for _, row in order_data.iterrows():

        original_country_name, city, clean_city, country, state, clean_state = row['original_country_name'], row['city'], row['clean_city'], row['country'], row['state'], row['clean_state']
        
        print(f"Mapping city: {city}, state: {state}, country: {country}")

        # Filter world_city_data to only include entries from the same country
        country_filtered = world_city_data[world_city_data['country'] == country]
        filtered_cities = country_filtered['clean_city'].dropna()

        mapped_city = None
        mapped_state = None
        
        # If there are matching cities in the filtered set, perform fuzzy matching
        if not country_filtered.empty:
            result = process.extractOne(clean_city, filtered_cities, score_cutoff=50)
            if result:
                mapped_city = result[0]  # Get the matched state name

        filtered_states = country_filtered['clean_state'].dropna()

        # If there are matching states in the filtered set, perform fuzzy matching
        if not country_filtered.empty:
            city_result = process.extractOne(state, filtered_cities, score_cutoff=50)
            state_result = process.extractOne(state, filtered_states, score_cutoff=50)

            if state_result:
                mapped_state = state_result[0]
            elif city_result:
                mapped_state = country_filtered[country_filtered['clean_city'] == city_result[0]]['clean_state'].values[0]

        mapped_cities.append({
            'original_country_name': original_country_name,
            'country': country,
            'city': city,
            'clean_city': clean_city,
            'mapped_city': mapped_city,
            'state': state,
            'clean_state': clean_state,
            'mapped_state': mapped_state

        })

    # Display or analyze mapped cities as needed
    mapped_cities_df = pd.DataFrame(mapped_cities)

    print(f"{nowtime()} Cities mapped.")

    return mapped_cities_df

# Function to extract latitude and longitude to mapped cities
def map_lat_long(mapped_cities, world_city_data):
    
    mapped_cities = mapped_cities[['original_country_name', 'country', 'city', 'state', 'mapped_city', 'mapped_state']]
    world_city_data = world_city_data[['country', 'clean_city', 'clean_state', 'latitude', 'longitude']]
    world_city_data = world_city_data.rename(columns={'clean_city': 'mapped_city', 'clean_state': 'mapped_state'})

    merged_cities = mapped_cities.merge(world_city_data, how='left', on=['country', 'mapped_city', 'mapped_state'])

    print(f"{nowtime()} Latitude and longitude extracted.")

    return merged_cities

# Function to create a dictionary of latitude and longitude for each country
def get_lat_long_dictionary(merged_cities, world_city_data):

    # Create a dictionary to store the first found latitude and longitude for each country based on order data
    order_country_lat_long = {}

    # Iterate through the city_data to populate the dictionary
    for _, row in merged_cities.iterrows():
        country = row['country']
        if country not in order_country_lat_long:
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                order_country_lat_long[country] = (row['latitude'], row['longitude'])

    # Create a dictionary to store the first found latitude and longitude for each country based on world city data
    world_country_lat_long = {}

    # Iterate through the city_data to populate the dictionary
    for _, row in world_city_data.iterrows():
        country = row['country']
        if country not in world_country_lat_long:
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                world_country_lat_long[country] = (row['latitude'], row['longitude'])

    # Add countries not in order_country_lat_long from world_country_lat_long
    for country, lat_long in world_country_lat_long.items():
        if country not in order_country_lat_long:
            order_country_lat_long[country] = lat_long

    return order_country_lat_long

# Function to update latitude and longitude in merged_cities for missing values
def update_lat_long(merged_cities, order_country_lat_long):

    # Fill NaN values in merged_cities with the corresponding country's latitude and longitude
    merged_cities['latitude'] = merged_cities.apply(
        lambda x: order_country_lat_long[x['country']][0] if pd.isna(x['latitude']) else x['latitude'], axis=1)
    
    merged_cities['longitude'] = merged_cities.apply(
        lambda x: order_country_lat_long[x['country']][1] if pd.isna(x['longitude']) else x['longitude'], axis=1)
    
    print(f"{nowtime()} Latitude and longitude updated.")

    # Drop unnecessary columns
    merged_cities = merged_cities.drop(columns=['country', 'mapped_city', 'mapped_state'])

    # Rename columns
    merged_cities = merged_cities.rename(columns={'original_country_name': 'Order Country', 'city': 'Order City', 'state': 'Order State'})

    return merged_cities

@click.command()
@click.argument('city_data_file_path', type=click.Path(exists=True))
@click.argument('database_path', type=click.Path(exists=True))
@click.argument('order_query', type=str)
@click.argument('country_mapping_input', type=str)

def main(city_data_file_path, database_path, order_query, country_mapping_input):

    country_mapping = retrieve_country_mappings(country_mapping_input)

    # Connect to the database
    conn = connect_to_database(database_path)

    # Extract order data
    order_data = query_data(conn, order_query)

     # Check if all occurences of Order Country, Order City, and Order State from order_data are present in database
    if check_city_data(order_data, conn):
       close_connection(conn)
       return

    # Extract world city data
    world_city_data = extract_world_city_data(city_data_file_path)

    # Replace country names
    order_data = replace_country_names(country_mapping, order_data)

    # Clean location names
    order_data = clean_locations(order_data)
    world_city_data = clean_locations(world_city_data)

    # Map cities
    mapped_cities_df = map_cities(order_data, world_city_data)

    # Extract latitude and longitude to mapped cities
    merged_cities = map_lat_long(mapped_cities_df, world_city_data)

    # Create a dictionary of latitude and longitude for each country
    order_country_lat_long = get_lat_long_dictionary(merged_cities, world_city_data)

    # Update latitude and longitude in merged_cities for missing values
    updated_cities = update_lat_long(merged_cities, order_country_lat_long)

    # Save the output
    add_table_to_database(updated_cities, "city_lat_long", conn)

    # Close the connection
    close_connection(conn)

    return

if __name__ == '__main__':
    main()
