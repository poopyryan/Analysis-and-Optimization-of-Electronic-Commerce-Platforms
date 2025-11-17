
def supply_chain_query():
    return """
    SELECT * 
    FROM cleaned_order_data
    """

def olist_query1():
    return """
    SELECT * 
    FROM olist_order_items_dataset
    """

def olist_query2():
    return """
    SELECT * 
    FROM olist_products_dataset
    """

def olist_query3():
    return """
    SELECT * 
    FROM product_category_name_translation
    """

def olist_query4():
    return """
    SELECT * 
    FROM olist_orders_dataset
    """