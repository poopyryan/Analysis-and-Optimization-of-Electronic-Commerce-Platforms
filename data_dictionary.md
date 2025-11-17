# Data Dictionary 

## Overview
This data dictionary describes the datasets used in this project, including their purpose, data types, and any relevant details.
We have stored our datasets in 2 databases: `supply_chain.db` and `brazil_dataset.db`

## Dataset 1: cleaned_order_data 
- **Description**: This dataset comprises order information in a Time series format collected by DataCo Global from an e-commerce platform. 
- **Source**: https://data.mendeley.com/datasets/8gx2fvg2k6/5, stored in supply_chain.db
- **Last Updated**: 13 March 2019 (Raw data)

| Column Name                         | Data Type | Description                                                                 |
|--------------------------------------|-----------|-----------------------------------------------------------------------------|
| **Transaction Type**                   | `object`  | Payment method used. Sample Values: ['DEBIT', 'TRANSFER', 'CASH', 'PAYMENT'] |
| **Days for shipment (real)**           | `int64`   | Number of days taken for an order to reach the customer's doorstep (Order Date - Real Shipping Date) |
| **Days for shipment (scheduled)**      | `int64`   | Scheduled Delivery Time frame based on Shipping Mode (Order Date - Scheduled Shipping Date) |
| **Sales per customer**                 | `float64` | Total sales per customer                                                    |
| **Delivery Status**                    | `object`  | The status of the delivery (e.g., delivered, pending, etc.)                  |
| **Late_delivery_risk**                 | `object`  | The binary risk prediction (calculated by DataCo) for late delivery. Values: ['Late', 'Not Late']  |
| **Product Category**                   | `object`  | Category of the product (e.g., electronics, clothing).                       |
| **Customer City**                      | `object`  | City where the customer resides.                                            |
| **Customer Country**                   | `object`  | Country where the customer resides.                                         |
| **Customer Fname**                     | `object`  | First name of the customer.                                                  |
| **Customer Id**                        | `int64`   | Unique identifier for each customer.                                         |
| **Customer Lname**                     | `object`  | Last name of the customer.                                                   |
| **Customer Segment**                   | `object`  | The segment of the customer. Values: ['Consumer' 'Home Office' 'Corporate'] |
| **Customer State**                     | `object`  | State where the customer resides.                                            |
| **Customer Street**                    | `object`  | Street address where the customer resides. (Synthetic)                       |
| **Warehouse Id**                       | `int64`   | Unique identifier for the Supplier's warehouse.                              |
| **Warehouse Name**                     | `object`  | Name of the Supplier's warehouse. This value is also used as Supplier Name. Each Supplier has only 1 Warehouse |
| **Market**                             | `object`  | The market in which the product is sold (e.g., North America, Europe).       |
| **Order City**                         | `object`  | City where the order is being shipped to.                                    |
| **Order Country**                      | `object`  | Country where the order is being shipped to.                                 |
| **Order Date**                         | `object`  | Date when the order was placed.                                              |
| **Order Id**                           | `int64`   | Unique identifier for each order.                                            |
| **Order Item Discount**                | `float64` | Discount applied to a specific order item.                                   |
| **Order Item Discount Rate**           | `float64` | Discount rate applied to a specific order item (as a percentage).            |
| **Order Item Id**                      | `int64`   | Unique identifier for the order item.                                        |
| **Order Item Profit Ratio**            | `float64` | Profit ratio for a specific order item (Order Profit / Sales).               |
| **Total Quantity Purchased**           | `int64`   | The total number of items purchased in the order.                            |
| **Sales**                              | `float64` | Total sales amount for the order.                                            |
| **Order Item Total**                   | `float64` | Total cost of the specific order item.                                       |
| **Order Profit**                       | `float64` | Profit made from the order after all expenses.                               |
| **Order Region**                       | `object`  | Region where the order is being shipped to                                   |
| **Order State**                        | `object`  | State where the order is being shipped to.                                   |
| **Order Status**                       | `object`  | Status of the order. Values: ['COMPLETE' 'PENDING' 'CLOSED' 'PENDING_PAYMENT' 'CANCELED'] This value is changed when status is updated. |
| **Product Id**                         | `int64`   | Unique identifier for each product.                                          |
| **Product Category Id**                | `int64`   | Unique identifier for the product category.                                  |
| **Product Name**                       | `object`  | Name of the product.                                                         |
| **Product Price**                      | `float64` | Price of the product.                                                        |
| **Product Status**                     | `object`  | Status of the product.                                                      |
| **Shipping Date**                      | `datetime`| Date when the product reaches the customer's doorstep.                      |
| **Shipping Mode**                      | `object`  | Mode of shipping chosen by customer. Values: ['Standard Class', 'First Class', 'Second Class', 'Same Day'] |
| **Order Timestamp**                    | `datetime`| Timestamp when the order was placed, including time. Sample Value: '2018-01-31 22:56:00' |
| **Order Year**                         | `int64`   | The year when the order was placed.                                          |
| **Order Month**                        | `object`  | The month when the order was placed.                                         |
| **Order Day**                          | `int64`   | The day of the month when the order was placed.                              |
| **Order Year-Month**                   | `object`  | A combination of the order year and month.                                  |
| **Order Day of Week**                  | `object`  | The day of the week when the order was placed.                              |
| **Shipping Year**                      | `int64`   | The year when the product was shipped.                                       |
| **Shipping Month**                     | `object`  | The month when the product was shipped.                                      |
| **Shipping Day**                       | `int64`   | The day of the month when the product was shipped.                           |
| **Shipping Year-Month**                | `object`  | A combination of the shipping year and month.                               |
| **Shipping Day of Week**               | `object`  | The day of the week when the product was shipped.                            |
| **difference in shipment days**        | `int64`   | Difference between the actual shipping days and the scheduled shipping days. |
| **Index**                              | `int64`   | The index for the row in the dataset.                                        |
| **Warehouse Latitude**                 | `float64` | Latitude coordinate of the warehouse location.                              |
| **Warehouse Longitude**                | `float64` | Longitude coordinate of the warehouse location.                             |


## Dataset 2: stock_data 
- **Description**: This dataset is a synthetically generated time series Inventory data, using `faker` library. It has been synthesized on real hypothetical scenarios, and based on products sold in the DataCo order data. This dataset allows us to monitor changes in stock levels on a daily basis.
- **Source**: Synthetically Generated, stored in supply_chain.db
- **Last Updated**: 7 Nov 2024

| Column Name      | Data Type | Description                                                                 |
|------------------|-----------|-----------------------------------------------------------------------------|
| **Product Name** | `object`  | Name of the product. |
| **Date**         | `object`  | Date |
| **Current Stock**| `int64`   | The number of items currently available in stock as of the end of the day. |
| **Total Sold**   | `int64`   | The total number of items sold on that day. |


## Dataset 3: product_info
- **Description**:  This dataset is synthetically generated. It contains product information such as product weight and manufacture time. 
- **Source**: Synthetically Generated, stored in supply_chain.db
- **Last Updated**: 7 Nov 2024

 Column Name            | Data Type | Description                                                                 |
|------------------------|-----------|-----------------------------------------------------------------------------|
| **Product Name**        | `object`  | Name of the product. |
| **Weight (kg)**         | `float64` | The weight of the product in kilograms. |
| **Product Id**          | `int64`   | Unique identifier for each product. |
| **Warehouse Id**        | `int64`   | Unique identifier for the warehouse storing the product. |
| **Daily Storage Rate**  | `float64` | The daily rate for storing a product, kept at a constant value of 0.02 |
| **Daily Storage Cost**  | `float64` | The daily cost for storing a product. |
| **Manufacturing Time**  | `int64`   | The number of days required to manufacture the product.|
| **Manufacturing Cost**  | `float64` | The cost price of the product. |
| **Price**               | `float64` | The Average selling price of the product. |

## Dataset 4: olist_customers_dataset
- **Description**: This dataset contains information about customers such as their address.

- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_customers_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **customer_id**        | `object`   | Non-unique identifier for customers. |
| **customer_unique_id** | `object` | Unique indentifier for each customer. |
| **customer_zip_code_prefix** | `int64` | The zip code of customer's registered address. |
| **customer_city** | `object` | The city in customer's registered address. |
| **customer_state** | `object` | The state in customer's registered address. |
| **churned** | `int64` | Indicates whether the customer has been churned or not, where 1 means churned and 0 means not churned. |

## Dataset 5: olist_geolocation_dataset
- **Description**: The dataset contains geographic information.
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_geolocation_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **geolocation_zip_code_prefix** | `int64` | The zip code of the location. |
| **geolocation_lat** | `float24` | The latitude coordinate of the location. |
| **geolocation_lng** | `float24` | The longitude coordinate of the location.|
| **geolocation_city** | `object` | The city of the location.| 
| **geolocation_state** | `object` | The state of the location.|

## Dataset 6: olist_marketing_dataset
- **Description**: This dataset is synthetically generated. It was synthesised based on a dataset taken from Kaggle, and has been modified to fit our e-commerce scenario. It contains marketing information.
- **Source**: https://www.kaggle.com/datasets/sinderpreet/analyze-the-marketing-spending/data modified and stored in brazil_dataset.db
- **Last Updated**: 12 Nov 2024

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **id**                     | `int64`   | The campaign id.                                                                              |
| **start_date**             | `object`  | When the campaign started, in `YYYY-MM-DD` format.                                                                    |
| **end_date**               | `object`  | When the campaign ended, in `YYYY-MM-DD` format.                                                                      |
| **campaign_type**          | `object`  | The type of campaign.                                                                         | 
| **channel**                | `object`  | The outlet used to promote the campaign.                                                      |
| **campaign_budget**        | `float24` | The cost of the campaign.                                                                     |
| **campaign_revenue**       | `float24` | The revenue earned from the campaign.                                                         |
| **impressions**            | `int64`   | The number of times the campaign is displayed to users.                                       |
| **clicks**                 | `int64`   | The number of times the campaign was clicked by users.                                        |

## Dataset 7: olist_order_items_dataset
- **Description**: This dataset includes data about the items purchased within each order.
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_items_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **order_id**               | `object`  | Unique identifier for each order.                                                             |
| **order_item_id**          | `int64`   | Number of items included in the same order.                                                   |
| **product_id**             | `object`  | Unique identifier for each product.                                                           |
| **seller_id**              | `object`  | Unique identifier for each seller.                                                            |
| **shipping_limit_date**    | `object`  | The shipping limit date for the seller to hand over the order to the logistic partner.        |
| **price_after_discount**   | `float24` | Price of each item after discount.                                                            |
| **freight_value**          | `float24` | Item freight value. If an order has more than one items, freight value is split between items.|
| **discount_rate**          | `float24` | The discount rate of each item.                                                               |
| **price_before_discount**  | `float24` | Price of each item before discount.                                                           |

## Dataset 8: olist_order_payments_dataset
- **Description**: This dataset contains payment information from orders. 
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_payments_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **order_id**               | `object`  | Unique identifier for each order.                                                             |
| **payment_sequential** | `int64`| The sequence number of a payment made for a specific purchase.|
| **payment_type** | `object` | The method of payment. |
| **payment_installments** | `int64` | The number of payments customer must make to pay off their purchase. |
| **payment_value** | `float64`| The value of each payment.|

## Dataset 9: olist_order_reviews_dataset
- **Description**: This dataset contains customer order reviews and their ratings 
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_reviews_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                | Data Type | Description                                                                                   |
|----------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **review_id**              | `object`  | Unique ID for each review.                                                                    |
| **order_id**               | `object`  | Unique identifier for each order.                                                             |
| **product_id**             | `object`  | Unique identifier for each product.                                                           |
| **review_score**           | `int64`   | Given score of the review (from a score of 1 (Lowest Score) to 5 (Highest Score)).            |
| **review_comment_title**   | `object`  | The title of given to each review.                                                            |
| **review_comment_message** | `object`  | The review comment message of each individual review.                                         |
| **review_creation_date**   | `object`  | The date and time when the review was created in `YYYY/MM/DD HH:MM:SS` format.                |
| **review_answer_timestamp**| `object`  | The date and time when the review was resolved in `YYYY/MM/DD HH:MM:SS` format.               |

## Dataset 10: olist_orders_dataset
- **Description**: This dataset contains information about the orders and their stages. 
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_orders_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                      | Data Type | Description                                                                                         |
|----------------------------------|-----------|-----------------------------------------------------------------------------------------------------|
| **order_id**                     | `object`  | Unique identifier for each order.                                                                   |
| **customer_id**                  | `object`  | Non-unique identifier for customers.                                                                |
| **order_status**                 | `object`  | The current state of the order.                                                                     |
| **order_purchase_timestamp**     | `object`  | The date and time when the order was purchased in `YYYY/MM/DD HH:MM:SS` format.                     |
| **order_approved_at**            | `object`  | The date and time when the order purchase was approved in `YYYY/MM/DD HH:MM:SS` format.             |
| **order_delivered_carrier_date** | `object`  | The date and time when the order was picked up by the carrier in `YYYY/MM/DD HH:MM:SS` format.      |
| **order_delivered_customer_date**| `object`  | The date and time when the order was delivered to the customer's address in `YYYY/MM/DD HH:MM:SS` format. |

## Dataset 11: olist_products_dataset
- **Description**: This dataset includes data about the products sold.
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_products_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                   | Data Type | Description                                                                                   |
|-------------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **product_id**                | `object`  | Unique identifier for each product.                                                           |
| **product_category_name**     | `object`  | Category of each product, in Portuguese.                                                      |
| **product_name_lenght**       | `float24` | Number of characters of each product name.                                                    |
| **product_description_lenght**| `float24` | Number of characters of each product description.                                             |
| **product_photos_qty**        | `float24` | Number of published photos for each product.                                                  |
| **product_weight_g**          | `float24` | Product weight measured in grams.                                                             |
| **product_length_cm**         | `float24` | Product length measured in centimeters.                                                       |
| **product_height_cm**         | `float24` | Product height measured in centimeters.                                                       |
| **product_width_cm**          | `float24` | Product width measured in centimeters.                                                        |

## Dataset 12: olist_sellers_dataset
- **Description**: This dataset includes data about the sellers that fulfilled orders made.
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_sellers_dataset.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                   | Data Type | Description                                                                                   |
|-------------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **seller_id**                 | `object`  | Unique identifier of each seller.                                                             |
| **seller_zip_code_prefix**    | `int64`   | First 5 digits of seller zip code.                                                            |
| **seller_city**               | `object`  | Seller's city name.                                                                           |
| **seller_state**              | `object`  | Seller's state.                                                                               |

## Dataset 13: product_category_name_translation
- **Description**: This dataset translates the `product_category_name` from `olist_products_dataset` to English.
- **Source**: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=product_category_name_translation.csv stored in brazil_dataset.db
- **Last Updated**: 02 Oct 2021 (Raw data)

| Column Name                      | Data Type | Description                                                                                   |
|----------------------------------|-----------|-----------------------------------------------------------------------------------------------|
| **product_category_name**        | `object`  | Category name, in Portuguese.                                                                 |
| **product_category_name_english**| `object`  | Category name, in English.                                                                    |
