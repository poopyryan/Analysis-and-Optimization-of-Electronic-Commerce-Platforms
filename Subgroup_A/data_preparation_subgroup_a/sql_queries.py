def add_churned_column_query():
    return """
    ALTER TABLE olist_customers_dataset ADD COLUMN churned INTEGER;
    """

def update_churned_column_query():
    return """
    UPDATE olist_customers_dataset
    SET churned = (
        SELECT 
            CASE 
                WHEN c.last_purchase_date < DATE(m.last_available_purchase_date, '-6 months') THEN 1
                ELSE 0
            END
        FROM (
            SELECT 
                cust.customer_unique_id,
                MAX(ord.order_purchase_timestamp) AS last_purchase_date
            FROM 
                olist_orders_dataset ord
            JOIN 
                olist_customers_dataset cust 
            ON 
                ord.customer_id = cust.customer_id
            GROUP BY 
                cust.customer_unique_id
        ) c,
        (
            SELECT 
                MAX(order_purchase_timestamp) AS last_available_purchase_date
            FROM 
                olist_orders_dataset
        ) m
        WHERE 
            olist_customers_dataset.customer_unique_id = c.customer_unique_id
    );
    """

def change_column_names_and_add_price_after_discount_query():
    return """CREATE TABLE olist_order_items_dataset_new AS 
    SELECT 
        `index`,
            order_id,
            order_item_id,
            product_id,
            seller_id,
            shipping_limit_date,
        price AS price_after_discount,
            freight_value,
            discount_rate
    FROM olist_order_items_dataset;
    """

def drop_order_items_table_query():
    return """DROP TABLE olist_order_items_dataset;"""

def rename_new_order_items_table_query():
    return """ALTER TABLE olist_order_items_dataset_new RENAME TO olist_order_items_dataset;"""

def add_price_before_discount_query():
    return """ALTER TABLE olist_order_items_dataset ADD COLUMN price_before_discount REAL;"""

def round_discount_rate_query():
    return """
    UPDATE olist_order_items_dataset
    SET discount_rate = ROUND(discount_rate, 2);
    """

def calculate_price_before_discount_query():
    return """
    UPDATE olist_order_items_dataset
    SET price_before_discount = ROUND(price_after_discount / (1 - discount_rate), 2);
    """
