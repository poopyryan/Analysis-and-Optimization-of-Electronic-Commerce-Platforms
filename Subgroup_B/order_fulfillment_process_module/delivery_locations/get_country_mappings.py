# Import necessary packages
# PYTHON 3.10
import pandas as pd
from fuzzywuzzy import process
from unidecode import unidecode
import sqlite3
import click

def nowtime():

    time = pd.Timestamp('now').strftime('%Y-%m-%d %H:%M:%S')

    return f"[{time}]"

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

# Function to close the sql connection
def close_connection(conn):
    
    conn.close()
    print(f"{nowtime()} Connection to database closed.")

    return

# Function to check if check if all occurences of Order Country, Order City, and Order State from order_data are city_lat_long table in the db
def check_city_data(order_data, conn):

    query = '''
        SELECT *
        FROM city_lat_long
    '''

    try:
        city_lat_long = query_data(conn, query)
    except Exception as e:
        print(f"{nowtime()} Order City data not found in the database. Mapping for new countries...")
        return False

    # Extract unique rows of city, country, and state from order_data
    unique_order_locations = order_data[['country', 'city', 'state']].drop_duplicates()

    # Merge to find missing locations
    merged_data = pd.merge(unique_order_locations, city_lat_long[['Order Country', 'Order City', 'Order State']], 
                           left_on=['country', 'city', 'state'], 
                           right_on=['Order Country', 'Order City', 'Order State'], how='left', indicator=True)

    missing_locations = merged_data[merged_data['_merge'] == 'left_only']

    if not missing_locations.empty:
        print(f"{nowtime()} New Order City identified. Mapping for new countries...")
        return False
    else:
        print(f"{nowtime()} All Order Cities and their locations are present in the database.")
        return True

##### PREPROCESSING STEPS #####

# Function to extract world city data
def extract_world_city_data(file_path):
    
    # Extract world city data
    world_city_data = pd.read_csv(file_path)
    world_city_data = world_city_data[['city_ascii', 'country', 'admin_name','lat', 'lng']]
    world_city_data = world_city_data.rename(columns={'city_ascii': 'city', 'admin_name': 'state','lat': 'latitude', 'lng': 'longitude'})

    print(f"{nowtime()} World city data extracted.")

    return world_city_data

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

# Function to identify mismatched countries
def identify_mismatched_countries(order_data, world_city_data):

    print(f"{nowtime()} Identifying mismatched countries...")

    # Convert order_data to a set for faster lookup
    order_countries_set = set(order_data['clean_country'].dropna())

    # Convert country column to a set for faster lookup
    world_countries_set = set(world_city_data['clean_country'].dropna())

    # Find countries that are in both sets
    countries_in_world_countries = order_countries_set.intersection(world_countries_set)

    # Find countries that are in order_data but not in world_cities
    countries_not_in_world_countries = order_countries_set.difference(world_countries_set)

    print(f"{nowtime()} No. of mapped countries found in world_city_data: {len(countries_in_world_countries)}")
    print(f"{nowtime()} No. of mapped countries not found in world_city_data: {len(countries_not_in_world_countries)}")
    print(f"{nowtime()} Countries not found in world_city_data:", countries_not_in_world_countries)

    return world_countries_set, countries_not_in_world_countries

# Function to map names of clean countries
def map_missing_countries(world_countries_set, countries_not_in_world_countries):

    # Dictionary to store possible mappings
    mapped_countries = []

    for country in countries_not_in_world_countries:
        # Find best match in world_countries_set with a minimum similarity score (e.g., 50)
        print(f"\nFinding best matches for {country}...")
        results = process.extract(country, world_countries_set, limit=5)
        filtered_results = [(match, score) for match, score in results if score >= 50]

        if filtered_results:
            print("Possible mappings: [country, score]")
            for match, score in filtered_results:
                print(f"{country} -> {match}, {score}")
                mapped_countries.append((country, match, score))
            print("\n")

    print(f"{nowtime()} Mapping countries completed.")

    return mapped_countries

##### OUTPUT FUNCTIONS #####

# Function to save the output to a txt file
def save_output(output_dir, file_name, data):

    with open(f"{output_dir}/{file_name}.results", "w") as file:
        file.write(f"country, mapped_country, score\n")
        for country1, country2, value in data:
            file.write(f"{country1}, {country2}, {value}\n")

    print(f"{nowtime()} Output saved to {output_dir}/{file_name}.results")

    return

@click.command()
@click.argument('output_dir', type=click.Path(exists=True))
@click.argument('city_data_file_path', type=click.Path(exists=True))
@click.argument('database_path', type=click.Path(exists=True))
@click.argument('order_query', type=str)

def main(output_dir, city_data_file_path, database_path, order_query):

    # Connect to the database
    conn = connect_to_database(database_path)

    # Extract order data
    order_data = query_data(conn, order_query)
   
    # Extract world city data
    world_city_data = extract_world_city_data(city_data_file_path)

    # Clean location names
    order_data = clean_locations(order_data)
    world_city_data = clean_locations(world_city_data)

    # Identify mismatched countries
    world_countries_set, countries_not_in_world_countries = identify_mismatched_countries(order_data, world_city_data)

    # Map missing countries
    mapped_countries = map_missing_countries(world_countries_set, countries_not_in_world_countries)

    # Save the output
    save_output(output_dir, "mapped_countries", mapped_countries)

    # Close the connection
    close_connection(conn)

    return

if __name__ == "__main__":
    main()