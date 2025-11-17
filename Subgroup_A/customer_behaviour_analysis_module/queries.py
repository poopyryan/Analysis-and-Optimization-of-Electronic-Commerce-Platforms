import pandas as pd
import sqlite3
import numpy as np

# Question 1.1 Analyse historical sales data to identify patterns and trends

# SQL Query to get the distributions of locations of customers
def get_customer_location_dist(conn):
    query = '''
    SELECT 
        customer_zip_code_prefix AS zip_code_prefix,
        COUNT(customer_id) AS customer_count,
        geolocation_lat AS latitude,
        geolocation_lng AS longitude 

    FROM 
        olist_customers_dataset
    JOIN olist_geolocation_dataset ON olist_customers_dataset.customer_zip_code_prefix = olist_geolocation_dataset.geolocation_zip_code_prefix

    GROUP BY zip_code_prefix'''

    return pd.read_sql(query, conn)

# SQL query to get the top 10 cities with the most customers
def get_most_customers_by_cities(conn):
    query = '''
    SELECT 
        COUNT(customer_id) AS customer_count,
        customer_city
    FROM 
        olist_customers_dataset
    GROUP BY
        customer_city
    ORDER BY
        customer_count DESC

    LIMIT 10
    '''
    return pd.read_sql(query, conn)

# SQL query to get the monthly customer growth trend in the top 10 cities
def customer_monthly_growth_by_cities(conn):
    query ='''
    WITH top_10_cities AS (
        SELECT 
            customer_city,
            COUNT(customer_id) AS customer_count
        FROM 
            olist_customers_dataset
        GROUP BY 
            customer_city
        ORDER BY 
            customer_count DESC
        LIMIT 10
    )
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month_year,
        c.customer_city,
        COUNT(c.customer_id) AS customer_count
    FROM 
        olist_customers_dataset c
    JOIN 
        olist_orders_dataset o ON c.customer_id = o.customer_id
    JOIN 
        top_10_cities t ON c.customer_city = t.customer_city
    WHERE 
        o.order_purchase_timestamp <= '2018-08-31'
    GROUP BY 
        c.customer_city, month_year
    ORDER BY 
        c.customer_city, month_year;
    '''
    return pd.read_sql(query, conn)

# SQL query to get the monthly trend of new customers
def get_monthly_new_customers(conn):
    query = '''
    WITH first_order AS (
        SELECT 
            customer_id,
            MIN(order_purchase_timestamp) AS first_order_date
        FROM 
            olist_orders_dataset
        GROUP BY 
            customer_id
    )
    SELECT 
        STRFTIME('%Y-%m', first_order_date) AS month_year,
        COUNT(customer_unique_id) AS new_customers
    FROM 
        first_order
    GROUP BY 
        month_year
    ORDER BY 
        month_year ASC;
    '''
    return pd.read_sql(query, conn)

# SQL query to get the number of orders each day
def get_orders_per_day(conn):
    query ='''
    SELECT
        DATE(order_purchase_timestamp) AS day,
        COUNT(DISTINCT(order_id)) AS order_count
    FROM 
        olist_orders_dataset
    WHERE 
        order_purchase_timestamp <= '2018-08-31'
    GROUP BY 
        day
    '''
    return pd.read_sql(query,conn)

#SQL query to get the most popular day and time to make a purchase MIGHT HAVE A PROBLEM HERE
# def get_most_popular_day_time(conn):
#     per_day_hour = '''
#         SELECT
#         CASE STRFTIME('%w', order_purchase_timestamp)
#                 WHEN '1' THEN 'Mon'
#                 WHEN '2' THEN 'Tue'
#                 WHEN '3' THEN 'Wed'
#                 WHEN '4' THEN 'Thu'
#                 WHEN '5' THEN 'Fri'
#                 WHEN '6' THEN 'Sat'
#                 WHEN '0' THEN 'Sun'
#                 END AS day_of_week_name,
#         CAST(STRFTIME('%w', order_purchase_timestamp) AS INTEGER) AS day_of_week_int,
#         CAST(STRFTIME("%H", order_purchase_timestamp) AS INTEGER) AS hour

#         FROM 
#             olist_orders_dataset
#             '''
#         num_orders_per_hour = ',\n    '.join([
#         f'COUNT(CASE WHEN hour = {i} THEN 1 END) AS "{i}"' \
#         for i in range(24)])

#         orders_per_day_hour ='''
#         WITH PerDayHour AS (
#         {per_day_hour}
#         )
#         SELECT
#             day_of_week_name,
#             {num_orders_per_hour}
#         FROM PerDayHour
#         GROUP BY day_of_week_name
#         ORDER BY day_of_week_name;
#         '''
#         return pd.read_sql(orders_per_day_hour, conn)


def get_orders_per_day_hour(conn):
    """
    This function retrieves the number of orders per hour for each day of the week from the database.

    Parameters:
    - conn: SQLite connection object

    Returns:
    - A Pandas DataFrame with the number of orders for each hour (0-23) across each day of the week.
    """
    # SQL query to extract day of the week and hour from order timestamps
    per_day_hour_query = """
    SELECT
        CASE STRFTIME('%w', order_purchase_timestamp)
            WHEN '1' THEN 'Mon'
            WHEN '2' THEN 'Tue'
            WHEN '3' THEN 'Wed'
            WHEN '4' THEN 'Thu'
            WHEN '5' THEN 'Fri'
            WHEN '6' THEN 'Sat'
            WHEN '0' THEN 'Sun'
        END AS day_of_week_name,
        CAST(STRFTIME('%w', order_purchase_timestamp) AS INTEGER) AS day_of_week_int,
        CAST(STRFTIME("%H", order_purchase_timestamp) AS INTEGER) AS hour
    FROM 
        olist_orders_dataset
    """

    # Generate COUNT queries for each hour (0-23)
    num_orders_per_hour = ',\n    '.join([
        f'COUNT(CASE WHEN hour = {i} THEN 1 END) AS "{i}"' for i in range(24)
    ])

    # SQL query to aggregate the number of orders per hour for each day of the week
    orders_per_day_hour_query = f"""
    WITH PerDayHour AS (
        {per_day_hour_query}
    )
    SELECT
        day_of_week_name,
        {num_orders_per_hour}
    FROM PerDayHour
    GROUP BY day_of_week_name
    ORDER BY day_of_week_int;
    """

    # Execute the query and read the result into a DataFrame
    df = pd.read_sql(orders_per_day_hour_query, conn)

    # Set the day of the week as the index
    df = df.set_index('day_of_week_name')

    return df

# Example usage (assuming `conn` is your database connection):
# df_orders_per_day_hour = get_orders_per_day_hour(conn)
# print(df_orders_per_day_hour.head())


# SQL query to get the monthly revenue and number of orders
def get_monthly_orders_revenues(conn):
    query ='''
        SELECT
            CASE STRFTIME('%m', o.order_purchase_timestamp)
                WHEN '01' THEN 'Jan'
                WHEN '02' THEN 'Feb'
                WHEN '03' THEN 'Mar'
                WHEN '04' THEN 'Apr'
                WHEN '05' THEN 'May'
                WHEN '06' THEN 'Jun'
                WHEN '07' THEN 'Jul'
                WHEN '08' THEN 'Aug'
                WHEN '09' THEN 'Sep'
                WHEN '10' THEN 'Oct'
                WHEN '11' THEN 'Nov'
                WHEN '12' THEN 'Dec'
            END AS month_name,
            CAST(STRFTIME('%m', o.order_purchase_timestamp) AS INTEGER) AS month_int,
            CAST(STRFTIME('%Y', o.order_purchase_timestamp) AS INTEGER) AS year,
            COUNT(o.order_id) AS order_count,
            SUM(p.payment_value) AS total_revenue,
            -- Combine month and year into one string
            (CASE STRFTIME('%m', o.order_purchase_timestamp)
                WHEN '01' THEN 'Jan'
                WHEN '02' THEN 'Feb'
                WHEN '03' THEN 'Mar'
                WHEN '04' THEN 'Apr'
                WHEN '05' THEN 'May'
                WHEN '06' THEN 'Jun'
                WHEN '07' THEN 'Jul'
                WHEN '08' THEN 'Aug'
                WHEN '09' THEN 'Sep'
                WHEN '10' THEN 'Oct'
                WHEN '11' THEN 'Nov'
                WHEN '12' THEN 'Dec'
            END || ' ' || STRFTIME('%Y', o.order_purchase_timestamp)) AS month_year
        FROM 
            olist_orders_dataset o
        JOIN 
            olist_order_payments_dataset p ON o.order_id = p.order_id
        WHERE 
            o.order_purchase_timestamp <= '2018-08-31'
        GROUP BY 
            year, month_int
        ORDER BY 
            year, month_int;
        '''
    return pd.read_sql(query,conn)

# SQL query to get the monthly freight values
def get_avg_monthly_freight(conn):
    query ='''
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month_year,
        AVG(i.freight_value) AS avg_freight_value 
    FROM 
        olist_orders_dataset o
    JOIN   
        olist_order_items_dataset i ON o.order_id = i.order_id
    GROUP BY
        month_year 
    ORDER BY
        month_year ASC
    '''
    return pd.read_sql(query,conn)

# SQL query to get the mean item price and total revenue by state
def get_mean_price_revenue_by_state(conn):
    query ='''
    SELECT
        c.customer_state,
        AVG(i.price_after_discount) AS avg_item_price,
        SUM(p.payment_value) AS total_revenue
    FROM 
        olist_order_items_dataset i
    JOIN 
        olist_order_payments_dataset p ON i.order_id = p.order_id
    JOIN 
        olist_orders_dataset o ON o.order_id = i.order_id
    JOIN 
        olist_customers_dataset c ON o.customer_id = c.customer_id
    GROUP BY 
        c.customer_state
    ORDER BY 
        total_revenue DESC;
    '''
    return pd.read_sql(query,conn)

# SQL query to get the mean freight value and total revenue by state
def get_mean_freight_revenue_by_state(conn):
    query = '''
    SELECT
        c.customer_state,
        AVG(i.freight_value) AS avg_freight_value,
        SUM(p.payment_value) AS total_revenue
    FROM 
        olist_order_items_dataset i
    JOIN 
        olist_order_payments_dataset p ON i.order_id = p.order_id
    JOIN 
        olist_orders_dataset o ON o.order_id = i.order_id
    JOIN 
        olist_customers_dataset c ON o.customer_id = c.customer_id
    GROUP BY 
        c.customer_state
    ORDER BY 
        total_revenue DESC;
    '''
    return pd.read_sql(query,conn)

# SQL query to get the monthly trend in mode of payments
def get_monthly_payment_type(conn):
    query = '''
    SELECT
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month_year,
        p.payment_type,
        COUNT(p.payment_type) AS payment_type_count
    FROM 
        olist_order_payments_dataset p
    JOIN 
        olist_orders_dataset o ON p.order_id = o.order_id
    WHERE 
            o.order_purchase_timestamp <= '2018-08-31'
    GROUP BY 
        month_year, p.payment_type
    ORDER BY 
        month_year ASC, payment_type_count DESC;
    '''
    return pd.read_sql(query, conn)

# SQL query to get the proportions of payment types
def get_payment_type_prop(conn):
    query = '''
    SELECT
        p.payment_type,
        COUNT(p.payment_type) AS payment_type_count
    FROM 
        olist_order_payments_dataset p
    JOIN 
        olist_orders_dataset o ON p.order_id = o.order_id
        
    GROUP BY payment_type;
'''
    return pd.read_sql(query,conn)

# SQL query to get the number of cancelled orders each month based on order purchase date
def get_monthly_cancelled_orders(conn):
    query ='''
    SELECT
    CASE STRFTIME('%m', o.order_purchase_timestamp)
        WHEN '01' THEN 'Jan'
        WHEN '02' THEN 'Feb'
        WHEN '03' THEN 'Mar'
        WHEN '04' THEN 'Apr'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'Jun'
        WHEN '07' THEN 'Jul'
        WHEN '08' THEN 'Aug'
        WHEN '09' THEN 'Sep'
        WHEN '10' THEN 'Oct'
        WHEN '11' THEN 'Nov'
        WHEN '12' THEN 'Dec'
    END AS month_name,
    CAST(STRFTIME('%m', o.order_purchase_timestamp) AS INTEGER) AS month_int,
    CAST(STRFTIME('%Y', o.order_purchase_timestamp) AS INTEGER) AS year,
    COUNT(o.order_id) AS cancelled_order_count,
    (CASE STRFTIME('%m', o.order_purchase_timestamp)
        WHEN '01' THEN 'Jan'
        WHEN '02' THEN 'Feb'
        WHEN '03' THEN 'Mar'
        WHEN '04' THEN 'Apr'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'Jun'
        WHEN '07' THEN 'Jul'
        WHEN '08' THEN 'Aug'
        WHEN '09' THEN 'Sep'
        WHEN '10' THEN 'Oct'
        WHEN '11' THEN 'Nov'
        WHEN '12' THEN 'Dec'
    END || ' ' || STRFTIME('%Y', o.order_purchase_timestamp)) AS month_year
FROM 
    olist_orders_dataset o
WHERE 
    o.order_status = 'canceled'
    AND o.order_purchase_timestamp <= '2018-08-31'
GROUP BY 
    year, month_int
ORDER BY 
    year, month_int;
'''
    return pd.read_sql(query,conn)


# Question 1.2 Develop customer segmentation models based on purchasing behaviour
# Predicting Customer Lifetime Value

# SQL query to get the necessary data for customer lifetime value prediction
def get_clv_data(conn):
    query = '''
    SELECT 
        o.order_purchase_timestamp,
        c.customer_unique_id, 
        c.customer_state, 
        p.payment_value
    FROM 
        olist_orders_dataset o
    JOIN 
        olist_customers_dataset c ON o.customer_id = c.customer_id
    JOIN 
        olist_order_payments_dataset p ON o.order_id = p.order_id;
    '''
    return pd.read_sql(query,conn)

# SQL query to get customers' city and state
def get_customer_city_state(conn):
    query ='''
    SELECT 
        customer_unique_id, customer_city, customer_state 
    FROM 
        olist_customers_dataset
    '''
    return pd.read_sql(query,conn)

# Segmenting existing customer base

# SQL query to get customers' orders and payment information
def get_orders_payments(conn):
    query ='''
    SELECT 
        o.*,
        p.*,
        c.customer_unique_id
    FROM
        olist_orders_dataset o
    INNER JOIN
        olist_order_payments_dataset p ON o.order_id = p.order_id
    INNER JOIN
        olist_customers_dataset c ON o.customer_id = c.customer_id
    '''
    return pd.read_sql(query,conn)

def get_top_products_revenue(conn):
    query = '''
    SELECT 
        SUM(i.price_after_discount) AS revenue,
        t.product_category_name_english AS product_category
    FROM
        olist_order_items_dataset i
    JOIN 
        olist_products_dataset pr ON pr.product_id = i.product_id
    JOIN
        product_category_name_translation t ON pr.product_category_name = t.product_category_name
    GROUP BY
        t.product_category_name_english
    ORDER BY
        revenue DESC
    LIMIT 5
    '''
    return pd.read_sql(query,conn)

def get_top_products_orders(conn):
    query = '''
        SELECT 
            COUNT(i.order_id) AS order_count,
            t.product_category_name_english AS product_category
        FROM
            olist_order_items_dataset i
        JOIN 
            olist_products_dataset pr ON pr.product_id = i.product_id
        JOIN
            product_category_name_translation t ON pr.product_category_name = t.product_category_name
        GROUP BY
            t.product_category_name_english
        ORDER BY
            order_count DESC
        LIMIT 5
        '''
    return pd.read_sql(query,conn)

def get_top_product_categories_revenue_trend(conn):
    query = '''
    SELECT
    t.product_category_name_english AS product_category,
    SUM(i.price_after_discount) AS revenue,
    CASE STRFTIME('%m', o.order_purchase_timestamp)
        WHEN '01' THEN 'Jan'
        WHEN '02' THEN 'Feb'
        WHEN '03' THEN 'Mar'
        WHEN '04' THEN 'Apr'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'Jun'
        WHEN '07' THEN 'Jul'
        WHEN '08' THEN 'Aug'
        WHEN '09' THEN 'Sep'
        WHEN '10' THEN 'Oct'
        WHEN '11' THEN 'Nov'
        WHEN '12' THEN 'Dec'
    END AS month_name,
    CAST(STRFTIME('%m', o.order_purchase_timestamp) AS INTEGER) AS month_int,
    CAST(STRFTIME('%Y', o.order_purchase_timestamp) AS INTEGER) AS year,
    COUNT(o.order_id) AS cancelled_order_count,
    (CASE STRFTIME('%m', o.order_purchase_timestamp)
        WHEN '01' THEN 'Jan'
        WHEN '02' THEN 'Feb'
        WHEN '03' THEN 'Mar'
        WHEN '04' THEN 'Apr'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'Jun'
        WHEN '07' THEN 'Jul'
        WHEN '08' THEN 'Aug'
        WHEN '09' THEN 'Sep'
        WHEN '10' THEN 'Oct'
        WHEN '11' THEN 'Nov'
        WHEN '12' THEN 'Dec'
    END || ' ' || STRFTIME('%Y', o.order_purchase_timestamp)) AS month_year
FROM
    olist_order_items_dataset i
    JOIN 
        olist_products_dataset pr ON pr.product_id = i.product_id
    JOIN
        product_category_name_translation t ON pr.product_category_name = t.product_category_name
    JOIN
        olist_orders_dataset o ON i.order_id = o.order_id
    
    WHERE 
    product_category_name_english IN ('bed_bath_table', 'health_beauty', 'computers_accessories')
    AND o.order_purchase_timestamp <= '2018-08-31'
    GROUP BY
        year, month_int, t.product_category_name_english
    ORDER BY
        year, month_int

'''
    return pd.read_sql(query, conn)

def get_product_category_avg_price_num_orders(conn):
    query = '''
SELECT 
    COUNT(i.order_id) AS order_count,
    t.product_category_name_english AS product_category,
    AVG(i.price_after_discount) AS avg_price
FROM
    olist_order_items_dataset i
JOIN 
    olist_products_dataset pr ON pr.product_id = i.product_id
JOIN
    product_category_name_translation t ON pr.product_category_name = t.product_category_name
GROUP BY
    t.product_category_name_english
ORDER BY
    order_count DESC
'''
    return pd.read_sql(query, conn)

def get_top_product_category_undelivered(conn):
    query = '''
SELECT
    COUNT(o.order_status) AS undelivered_orders_count,
    t.product_category_name_english AS product_category
FROM
    olist_order_items_dataset i
JOIN 
    olist_products_dataset pr ON pr.product_id = i.product_id
JOIN
    product_category_name_translation t ON pr.product_category_name = t.product_category_name
JOIN
    olist_orders_dataset o ON i.order_id = o.order_id
WHERE o.order_status != "delivered"
GROUP BY
    t.product_category_name_english
ORDER BY
    undelivered_orders_count DESC
'''
    return pd.read_sql(query, conn)


