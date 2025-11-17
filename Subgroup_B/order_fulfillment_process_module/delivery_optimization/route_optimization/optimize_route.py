import pandas as pd
import sqlite3
import os
import click 
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from math import radians, sin, cos, sqrt, atan2
import folium

def nowtime():

    time = pd.Timestamp('now').strftime('%Y-%m-%d %H:%M:%S')

    return f"[{time}]"

##### SQL FUNCTIONS #####

def open_connection(database_path):

    conn = sqlite3.connect(database_path)

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

##### ROUTE OPTIMIZATION PREPROCESSING #####

# Function to load the orders from a CSV file
def get_orders(file_path):
    
    df = pd.read_csv(file_path)
    print(f"{nowtime()} Orders loaded from {file_path}")

    return df

# Function to filter the data for today's deliveries
def filter_data(df, num_vehicles, vehicle_capacity):
    """
    Filter the data to include only the orders that can be delivered today.
    """
    max_packages = num_vehicles * vehicle_capacity
    buffer = int(max_packages * 0.1)
    filtered_df = df.head(max_packages - buffer)

    print(f"{nowtime()} Data filtered for today's deliveries based on the no. of available vehicles.")

    return filtered_df

# Function to add latitude and longitude to the data frame
def add_lat_long(df, database_path):
    """
    Add latitude and longitude to the data frame.
    """
    conn = open_connection(database_path)
    query = f"SELECT * FROM city_lat_long;"
    lat_long = query_data(conn, query)
    close_connection(conn)

    df = df.merge(lat_long, on=["Order Country", "Order City", "Order State"], how='left')

    print(f"{nowtime()} Latitude and longitude added to the data.")

    return df

# Function to calculate the haversine distance between two geographic coordinates
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the haversine distance between two geographic coordinates.
    """
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Function to build a distance matrix for the given locations
def build_distance_matrix(df):
    """
    Create a symmetrical distance matrix for the given locations.
    """
    num_locations = len(df) + 1  # +1 for the supplier location
    distance_matrix = [[0] * num_locations for _ in range(num_locations)]
    supplier_lat = df['Warehouse Latitude'].unique()[0]
    supplier_lon = df['Warehouse Longitude'].unique()[0]

    for i in range(num_locations):
        for j in range(i, num_locations): # Start from i to ensure symmetry
            if i == 0:  # Distance from supplier to customers
                distance = haversine(supplier_lat, supplier_lon,
                                     df.iloc[j - 1]['latitude'],
                                     df.iloc[j - 1]['longitude']) if j > 0 else 0
            else:  # Distance between customers
                if i == j:
                    distance = 0
                else:
                    distance = haversine(df.iloc[i - 1]['latitude'],
                                         df.iloc[i - 1]['longitude'],
                                         df.iloc[j - 1]['latitude'],
                                         df.iloc[j - 1]['longitude'])
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance

    print(f"{nowtime()} Distance matrix created.")

    return distance_matrix

# Function to create the routing model
def create_routing_model(num_locations, num_vehicles, distance_matrix):
    """
    Create and configure the routing model.
    """
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    print(f"{nowtime()} Routing model created.")

    return routing, manager

# Function to add capacity constraints to the routing model
def add_capacity_constraints(routing, num_vehicles, vehicle_capacity):
    """
    Add capacity constraints to the routing model.
    """
    def demand_callback(from_index):
        return 1  # Each order has a demand of 1

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [vehicle_capacity] * num_vehicles,
        True,
        "Capacity"
    )

    print(f"{nowtime()} Capacity constraints added to the routing model.")

    return routing

# Function to solve the routing problem
def solve_routing_problem(routing):
    """
    Solve the routing problem.
    """
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)

    return solution

# Function to print the solution
# def print_solution(routing, manager, solution, num_vehicles):
#     """
#     Print the solution, including routes and total distance.
#     """
#     total_distance = 0
#     print("\nRoutes and Distances per Vehicle:\n" + "-" * 33)
#     for vehicle_id in range(num_vehicles):
#         index = routing.Start(vehicle_id)
#         route_distance = 0
#         route = []
#         while not routing.IsEnd(index):
#             route.append(manager.IndexToNode(index))
#             previous_index = index
#             index = solution.Value(routing.NextVar(index))
#             route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
#         route.append(manager.IndexToNode(index))  # Add end of route
#         total_distance += route_distance
        
#         # Format route output for readability
#         route_str = " → ".join(map(str, route))
#         print(f"Vehicle {vehicle_id + 1}:\n  Route: {route_str}\n  Distance: {route_distance}\n")

#     print(f"Total Distance: {total_distance}")

def print_solution(routing, manager, solution, num_vehicles, output_dir):
    """
    Print the solution, including routes and total distance, and save it to a file.
    """
    total_distance = 0
    output_lines = []
    
    # Header
    output_lines.append("\nRoutes and Distances per Vehicle:\n" + "-" * 33)
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route_distance = 0
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        route.append(manager.IndexToNode(index))  # Add end of route
        total_distance += route_distance

        # Format route output for readability
        route_str = " → ".join(map(str, route))
        vehicle_output = f"Vehicle {vehicle_id + 1}:\n  Route: {route_str}\n  Distance: {route_distance}\n"
        
        # Append the output to the list
        output_lines.append(vehicle_output)
        
    # Total distance
    output_lines.append(f"Total Distance: {total_distance}")
    
    # Print to console
    print("\n".join(output_lines))

    output_file = f"{output_dir}/Optimized_Route.txt"
    
    # Write to file
    with open(output_file, "w") as file:
        file.write("\n".join(output_lines))
        
    print(f"\nSolution saved to {output_file}")

# Function to find the most optimal route
def find_solution(df, num_vehicles, vehicle_capacity, database_path, output_dir):

    filtered_df = filter_data(df, num_vehicles, vehicle_capacity)

    filtered_df = add_lat_long(filtered_df, database_path)

    distance_matrix = build_distance_matrix(filtered_df)
    
    routing, manager = create_routing_model(len(distance_matrix), num_vehicles, distance_matrix)
    routing = add_capacity_constraints(routing, num_vehicles, vehicle_capacity)
    
    solution = solve_routing_problem(routing)
    if solution:
        print(f"{nowtime()} Routing problem solved. Solution found!")
        print_solution(routing, manager, solution, num_vehicles, output_dir)
    else:
        print(f"{nowtime()} No solution found!")

    return filtered_df, routing, manager, solution

##### FUNCTION FOR PLOTTING THE ROUTE #####

# Function to create a base map
def create_base_map(supplier_lat, supplier_lon, zoom_start=8):
    """
    Create a base map centered around the supplier's location.
    """
    return folium.Map(location=[supplier_lat, supplier_lon], zoom_start=zoom_start)

# Function to plot a single route on the base map for a given vehicle
def plot_route(base_map, route, vehicle_id, filtered_df, supplier_lat, supplier_lon, vehicle_colors):
    """Plot a single route on the base map for a given vehicle."""
    for i in range(len(route) - 1):
        start_node = route[i]
        end_node = route[i + 1]

        # Get latitudes and longitudes for the start and end nodes
        start_lat, start_lon = (supplier_lat, supplier_lon) if start_node == 0 else (
            filtered_df.iloc[start_node - 1]['latitude'], filtered_df.iloc[start_node - 1]['longitude']
        )
        end_lat, end_lon = (supplier_lat, supplier_lon) if end_node == 0 else (
            filtered_df.iloc[end_node - 1]['latitude'], filtered_df.iloc[end_node - 1]['longitude']
        )

        # Create a line between points
        folium.PolyLine(
            locations=[[start_lat, start_lon], [end_lat, end_lon]],
            color=vehicle_colors[vehicle_id - 1],  # Different colors for different vehicles
            weight=2.5,
            opacity=1
        ).add_to(base_map)

    # Mark the route points
    for node in route:
        if node == 0:
            folium.Marker(
                location=[supplier_lat, supplier_lon],
                popup='Supplier',
                icon=folium.Icon(color='red')
            ).add_to(base_map)
        else:
            lat = filtered_df.iloc[node - 1]['latitude']
            lon = filtered_df.iloc[node - 1]['longitude']
            folium.Marker(
                location=[lat, lon],
                popup=f'Order {node}',
                icon=folium.Icon(color='blue')
            ).add_to(base_map)

# Function to plot all routes on the base map
def plot_all_routes(base_map, routing, manager, solution, num_vehicles, filtered_df, supplier_lat, supplier_lon):
    """
    Plot all routes for each vehicle on the base map.
    """
    vehicle_colors = ['blue', 'green', 'orange', 'purple', 'black', 'red', 'yellow']
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # Add end of route
        plot_route(base_map, route, vehicle_id + 1, filtered_df, supplier_lat, supplier_lon, vehicle_colors)

# Function to save the base map as an HTML file
def save_map(base_map, output_dir, filename="map.html"):
    """
    Save the base map as an HTML file.
    """
    file_path = os.path.join(output_dir, filename)
    
    base_map.save(file_path)

    print(f"Map saved as {file_path}")

# Function to generate the route map
def generate_route_map(filtered_df, routing, manager, solution, num_vehicles, output_dir):

    supplier_lat = filtered_df['Warehouse Latitude'].unique()[0]
    supplier_lon = filtered_df['Warehouse Longitude'].unique()[0]
    base_map = create_base_map(supplier_lat, supplier_lon)

    # Plot all routes on the map
    plot_all_routes(base_map, routing, manager, solution, num_vehicles, filtered_df, supplier_lat, supplier_lon)

    # Save map as HTML
    save_map(base_map, output_dir, "route_map.html")

    return

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('num_vehicles', type=int)
@click.argument('vehicle_capacity', type=int)
@click.argument('database_path', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(exists=True))

def main(file_path, num_vehicles, vehicle_capacity, database_path, output_dir):

    df = get_orders(file_path)

    # Find most optimal route
    filtered_df, routing, manager, solution = find_solution(df, num_vehicles, vehicle_capacity, database_path, output_dir)

    # Generate route map
    generate_route_map(filtered_df, routing, manager, solution, num_vehicles, output_dir)

    return

if __name__ == "__main__":
    main()
