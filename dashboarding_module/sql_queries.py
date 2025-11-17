def order_data_query():
    return "SELECT * FROM cleaned_order_data"

def all_stock_data_query():
    return "SELECT * FROM stock_data"

def monthly_stock_data_query():
    return """
    SELECT 
        "Product Name",
        strftime('%Y', Date) AS Year,
        strftime('%m', Date) AS Month,
        FIRST_VALUE("Current Stock") OVER (
            PARTITION BY "Product Name", strftime('%Y-%m', Date)
            ORDER BY Date
        ) AS "Stock at Start of Month",
        SUM("Total Sold") AS "Total Sold"
    FROM stock_data
    WHERE strftime('%d', "Date") = '01' OR strftime('%d', "Date") BETWEEN '01' AND '31'
    GROUP BY "Product Name", Year, Month;
    """

def product_info_query():
    return "SELECT * FROM product_info"

