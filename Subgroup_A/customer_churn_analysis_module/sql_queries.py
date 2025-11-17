def supply_chain_query():
    return """SELECT `Order Item Discount Rate` FROM raw_order_data"""

def order_items_table_query():
    return """SELECT * FROM olist_order_items_dataset"""

def orders_table_query():
    return """SELECT order_id, order_purchase_timestamp FROM olist_orders_dataset"""

def overall_churn_rate_query():
    return """
        SELECT customer_unique_id, churned
        FROM olist_customers_dataset
    """

def churn_order_count_query():
    return """
        SELECT 
            customer_unique_id,
            COUNT(order_id) AS order_count,
            MAX(churned) AS churned  -- Use MAX to get the churned status for customers with multiple orders
        FROM 
            olist_orders_dataset 
        JOIN 
            olist_customers_dataset ON olist_orders_dataset.customer_id = olist_customers_dataset.customer_id
        GROUP BY 
            customer_unique_id
    """

def churn_review_score_query():
    return """
        SELECT o.order_id, c.customer_unique_id, c.churned, r.review_score
        FROM olist_customers_dataset c
        JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
        JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
    """

def churn_discount_rate_query():
    return """
        SELECT o.order_id, o.customer_id, c.churned, i.discount_rate
        FROM olist_orders_dataset o
        JOIN olist_order_items_dataset i ON o.order_id = i.order_id
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    """

def churn_product_category_query():
    return """
        SELECT
            p.product_id,
            t.product_category_name_english,
            c.churned
        FROM
            olist_customers_dataset c
        JOIN
            olist_orders_dataset o ON c.customer_id = o.customer_id
        JOIN 
            olist_order_items_dataset i ON o.order_id = i.order_id
        JOIN 
            olist_products_dataset p ON i.product_id = p.product_id
        JOIN 
            product_category_name_translation t ON p.product_category_name = t.product_category_name
    """

def churn_customer_city_query():
    return """
        SELECT customer_unique_id, churned, customer_state
        FROM olist_customers_dataset
    """

def churn_orders_date_query():
    return """
        SELECT 
            o.order_id,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date,
            o.order_estimated_delivery_date,
            c.churned
        FROM 
            olist_orders_dataset AS o
        JOIN
            olist_customers_dataset AS c on o.customer_id = c.customer_id
    """
    
    
