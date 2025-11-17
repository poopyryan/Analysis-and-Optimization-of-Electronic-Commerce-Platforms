import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv

# Reviews Data Prep
import nltk
import re
import tenacity
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
nltk.download('stopwords')
nltk.download('rslp')
nltk.download('punkt')
import time
# For English Translation
from deep_translator import GoogleTranslator
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_result, RetryError

load_dotenv()

brazil_database_path = os.getenv("brazil_database_path")
output_dir = os.getenv("output_dir")
input_dir = os.getenv("input_dir")

connection = sqlite3.connect(brazil_database_path)

product_category_query = """
    SELECT 
        p.product_id,
        p.product_category_name,
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
product_category_df = pd.read_sql_query(product_category_query, connection)

# Define the mapping of unique categories to broader categories (e.g. Home & Living, Fashion, Electronics & Appliances)
category_mapping = {
    'housewares': 'Home & Living',
    'perfumery': 'Health & Beauty',
    'auto': 'Automotive & Industry',
    'pet_shop': 'Miscellaneous',
    'stationery': 'Miscellaneous',
    'furniture_decor': 'Home & Living',
    'office_furniture': 'Home & Living',
    'garden_tools': 'Home & Living',
    'computers_accessories': 'Electronics & Appliances',
    'bed_bath_table': 'Home & Living',
    'toys': 'Toys & Games',
    'construction_tools_construction': 'Automotive & Industry',
    'telephony': 'Electronics & Appliances',
    'health_beauty': 'Health & Beauty',
    'electronics': 'Electronics & Appliances',
    'baby': 'Miscellaneous',
    'cool_stuff': 'Toys & Games',
    'watches_gifts': 'Miscellaneous',
    'air_conditioning': 'Electronics & Appliances',
    'sports_leisure': 'Sports & Leisure',
    'books_general_interest': 'Books & Media',
    'small_appliances': 'Electronics & Appliances',
    'food': 'Food & Drink',
    'luggage_accessories': 'Miscellaneous',
    'fashion_underwear_beach': 'Fashion',
    'christmas_supplies': 'Miscellaneous',
    'fashion_bags_accessories': 'Fashion',
    'musical_instruments': 'Toys & Games',
    'construction_tools_lights': 'Automotive & Industry',
    'books_technical': 'Books & Media',
    'costruction_tools_garden': 'Automotive & Industry',
    'home_appliances': 'Home & Living',
    'market_place': 'Miscellaneous',
    'agro_industry_and_commerce': 'Automotive & Industry',
    'party_supplies': 'Sports & Leisure',
    'home_confort': 'Home & Living',
    'cds_dvds_musicals': 'Books & Media',
    'industry_commerce_and_business': 'Automotive & Industry',
    'consoles_games': 'Electronics & Appliances',
    'furniture_bedroom': 'Home & Living',
    'construction_tools_safety': 'Automotive & Industry',
    'fixed_telephony': 'Electronics & Appliances',
    'drinks': 'Food & Drink',
    'kitchen_dining_laundry_garden_furniture': 'Home & Living',
    'fashion_shoes': 'Fashion',
    'home_construction': 'Home & Living',
    'audio': 'Electronics & Appliances',
    'home_appliances_2': 'Home & Living',
    'fashion_male_clothing': 'Fashion',
    'cine_photo': 'Miscellaneous',
    'furniture_living_room': 'Home & Living',
    'art': 'Miscellaneous',
    'food_drink': 'Food & Drink',
    'tablets_printing_image': 'Electronics & Appliances',
    'fashion_sport': 'Fashion',
    'la_cuisine': 'Food & Drink',
    'flowers': 'Miscellaneous',
    'computers': 'Electronics & Appliances',
    'home_comfort_2': 'Home & Living',
    'small_appliances_home_oven_and_coffee': 'Electronics & Appliances',
    'dvds_blu_ray': 'Books & Media',
    'costruction_tools_tools': 'Automotive & Industry',
    'fashio_female_clothing': 'Fashion',
    'furniture_mattress_and_upholstery': 'Home & Living',
    'signaling_and_security': 'Miscellaneous',
    'diapers_and_hygiene': 'Health & Beauty',
    'books_imported': 'Books & Media',
    'fashion_childrens_clothes': 'Fashion',
    'music': 'Books & Media',
    'arts_and_craftmanship': 'Miscellaneous',
    'security_and_services': 'Miscellaneous'
}

# Apply the mapping to create a new column for broader categories
product_category_df['broader_category_english'] = product_category_df['product_category_name_english'].map(category_mapping)

churn_rate_by_category = product_category_df.groupby('broader_category_english')['churned'].mean() * 100

churn_rate_by_category = pd.DataFrame(churn_rate_by_category.reset_index())

orders_query = """
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

orders_df = pd.read_sql_query(orders_query, connection)

# Convert columns to datetime format
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])

orders_df['delivery_days'] = (orders_df['order_delivered_customer_date'] - orders_df['order_purchase_timestamp']).dt.days
orders_df['delivery_diff_days'] = (orders_df['order_delivered_customer_date'] - orders_df['order_estimated_delivery_date']).dt.days

# Define bins and labels for visualization
delivery_days_bins = [0, 5, 10, 15, 20, 25, orders_df['delivery_days'].max() + 1]
delivery_days_labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25+']

delivery_diff_bins = [orders_df['delivery_diff_days'].min() - 1, -1, 1, 5, 10, 15, orders_df['delivery_diff_days'].max() + 1]
delivery_diff_labels = ['Earlier than 1 day','On time (Within 1 day of expected date)', '2-5 days late', '5-10 days late', '10-15 days late', '15+ days late']

# Apply bins
orders_df['delivery_days_range'] = pd.cut(orders_df['delivery_days'], bins=delivery_days_bins, labels=delivery_days_labels)
orders_df['delivery_diff_range'] = pd.cut(orders_df['delivery_diff_days'], bins=delivery_diff_bins, labels=delivery_diff_labels)

# Calculate churn rate for each range
delivery_days_churn_rate = orders_df.groupby('delivery_days_range')['churned'].mean() * 100
delivery_diff_churn_rate = orders_df.groupby('delivery_diff_range')['churned'].mean() * 100

delivery_days_churn_rate = pd.DataFrame(delivery_days_churn_rate.reset_index())
delivery_diff_churn_rate = pd.DataFrame(delivery_diff_churn_rate.reset_index())

### Calculate churn rate by discount_rate

discount_rate_query = """
    SELECT o.order_id, o.customer_id, c.churned, i.discount_rate
    FROM olist_orders_dataset o
    JOIN olist_order_items_dataset i ON o.order_id = i.order_id
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
"""
discount_rate_df = pd.read_sql_query(discount_rate_query, connection)

discount_rate_bins = [0, 0.10, 0.20, 0.30]
labels = ['0-10%', '10-20%', '20-30%'] # Max discount rate is 0.25

discount_rate_df['discount_rate_bin'] = pd.cut(discount_rate_df['discount_rate'], bins=discount_rate_bins, labels=labels, right=False)
churn_rate_by_discount_bin = discount_rate_df.groupby('discount_rate_bin')['churned'].mean() * 100

churn_rate_by_discount_bin = pd.DataFrame(churn_rate_by_discount_bin.reset_index())

churn_rate_by_discount_bin.rename(columns={'churned':'churned_percentage'}, inplace=True)

# Calculate Month-Month Revenue and Customer Growth Data

mom_revenue_customer_query ='''

SELECT
    DATE(o.order_delivered_customer_date) AS delivered_date,
    strftime('%Y-%m', o.order_delivered_customer_date) AS month,
    COUNT(DISTINCT o.customer_id) AS daily_unique_customers,
    SUM(p.payment_value) AS daily_total_revenue
FROM
    olist_orders_dataset o
JOIN
    olist_order_payments_dataset p ON o.order_id = p.order_id
WHERE
    o.order_status = 'delivered'  -- Only consider completed (delivered) orders
GROUP BY
    delivered_date
ORDER BY
    delivered_date;
'''

mom_revenue_customer_df = pd.read_sql(mom_revenue_customer_query, connection)
mom_revenue_customer_df = pd.DataFrame(mom_revenue_customer_df.reset_index())

# Customer Score and Segmentation Table
orders_payments_query = """
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
"""

orders_payments_df = pd.read_sql(orders_payments_query, connection)
orders_payments_df.dropna(inplace=True)

orders_payments_df['order_delivered_customer_date'] = pd.to_datetime(
    orders_payments_df['order_delivered_customer_date'], errors='coerce'
)


latest_date = orders_payments_df['order_delivered_customer_date'].max() + pd.Timedelta(days=1)

# Calculate Recency (Most recent purchase for each customer)
df_segmentation_rfm = orders_payments_df.groupby('customer_unique_id')['order_delivered_customer_date'].max().reset_index()
df_segmentation_rfm.columns = ['customer_unique_id', 'most_recent_purchase']
df_segmentation_rfm['most_recent_purchase'] = pd.to_datetime(
    df_segmentation_rfm['most_recent_purchase'], errors='coerce'
)

df_segmentation_rfm['Recency'] = (latest_date - df_segmentation_rfm['most_recent_purchase']).dt.days
df_segmentation_rfm

df_segmentation_freq = orders_payments_df.groupby('customer_unique_id')['order_delivered_customer_date'].count().reset_index()
df_segmentation_freq.columns = ['customer_unique_id', 'Frequency']

df_segmentation_money = orders_payments_df.groupby('customer_unique_id')['payment_value'].sum().reset_index()
df_segmentation_money.columns = ['customer_unique_id', 'Monetary Value']

df_segmentation_rfm = pd.merge(df_segmentation_rfm, df_segmentation_freq, on='customer_unique_id')
df_segmentation_rfm = pd.merge(df_segmentation_rfm, df_segmentation_money, on='customer_unique_id')

def assign_recency_cluster(df):
    df['recency_cluster'] = np.where(df['Recency'] <= 155, 3,
                              np.where(df['Recency'] <= 279, 2,
                              np.where(df['Recency'] <= 431, 1, 0)))
    return df

df_segmentation_rfm = assign_recency_cluster(df_segmentation_rfm)

def assign_freq_cluster(df):
    df['freq_cluster'] = np.where(df['Frequency'] <=1,0,
                                  np.where(df['Frequency'] <=4,1,
                                           np.where(df['Frequency']<=11,2,3)))
    return df

df_segmentation_rfm = assign_freq_cluster(df_segmentation_rfm)

def assign_money_cluster(df):
    df['money_cluster'] = np.where(df['Monetary Value'] <=199.49,0,
                                  np.where(df['Monetary Value'] <=584.42,1,
                                           np.where(df['Monetary Value']<=1570.79,2,3)))
    return df

df_segmentation_rfm = assign_money_cluster(df_segmentation_rfm)

def assign_customer_score(df):
    df['customer_score'] = df['recency_cluster'] + df['freq_cluster'] + df['money_cluster']
    return df

df_segmentation_rfm = assign_customer_score(df_segmentation_rfm)

def customer_segment(score):
    if score <= 2:
        return 'Low Value'
    elif score <= 5:
        return 'Mid Value'
    else:
        return 'High Value'

# Apply the segmentation function to the DataFrame
df_segmentation_rfm['customer_segment'] = df_segmentation_rfm['customer_score'].apply(customer_segment)

df_segmentation_rfm = pd.DataFrame(df_segmentation_rfm.reset_index())

# Calculate Churn Rate over Time
churn_rate_over_time_query = '''WITH last_purchase AS (
    SELECT
        customer_id,
        MAX(order_purchase_timestamp) AS last_purchase_date
    FROM
        olist_orders_dataset
    GROUP BY
        customer_id
),

churned_customers AS (
    SELECT
        lp.customer_id,
        lp.last_purchase_date,
        DATE(lp.last_purchase_date, '+6 months') AS churn_date
    FROM
        last_purchase lp
    LEFT JOIN
        olist_orders_dataset o ON lp.customer_id = o.customer_id
        AND o.order_purchase_timestamp > lp.last_purchase_date
        AND o.order_purchase_timestamp <= DATE(lp.last_purchase_date, '+6 months')
    WHERE
        o.order_id IS NULL  -- No purchases within 6 months after last purchase
)

SELECT
    churn_date,
    COUNT(customer_id) AS churned_customers
FROM
    churned_customers
GROUP BY
    churn_date
ORDER BY
    churn_date;

'''

churn_rate_over_time_df = pd.read_sql_query(churn_rate_over_time_query, connection)

churn_rate_over_time_df = pd.DataFrame(churn_rate_over_time_df.reset_index())

olist_customers_dataset = pd.read_sql_query(f"SELECT * FROM olist_customers_dataset", connection)

olist_orders_dataset = pd.read_sql_query(f"SELECT * FROM olist_orders_dataset", connection)

olist_marketing_dataset = pd.read_sql_query(f"SELECT * FROM olist_marketing_dataset", connection)

print("Finished non sentiment analysis data extraction")

#### REVIEWS TABLE #####
#Defining Functions
"""
 1. Functions to Remove Regular Expressions (RegEx) on Portugese Reviews
"""
#Function to check the results of the same index of 2 lists (Difference Between Columns)
def print_step_result(list1, list2, idx_list):
    text_num = 0
    for idx in idx_list:
        if idx < len(list1) and idx < len(list2):
            before = list1[idx]
            after = list2[idx]
            print(f"--- Text {text_num + 1} ---\n")
            print(f"Before:\n{before}\n")
            print(f"After:\n{after}\n")
        else:
            print(f"Index {idx} is out of range for the provided lists.")
        text_num += 1

#Function to remove linebreaks between different lines of texts in reviews
def re_breakline(text_list, text_sub=' '):
    return [re.sub('[\n\r]', text_sub, r) for r in text_list]

#Funtion to remove hyperlinks from reviews
def re_hyperlinks(text_list):
    # Applying regex
    pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return [re.sub(pattern, ' link ', r) for r in text_list]

#Function for removing dates
def re_dates(text_list):    
    # Applying regex
    pattern = '([0-2][0-9]|(3)[0-1])(\/|\.)(((0)[0-9])|((1)[0-2]))(\/|\.)\d{2,4}'
    return [re.sub(pattern, ' data ', r) for r in text_list]

#Function for removing money symbols and values
def re_money(text_list):
    # Applying regex
    pattern = r'R?\$\s?\d+([.,]\d{1,2})?'
    return [re.sub(pattern, ' dinheiro ', r) for r in text_list]

#Function foe Removing Remaining Numbers
def re_numbers(text_list):
    # Applying regex
    return [re.sub('[0-9]+', ' numero ', r) for r in text_list]

#Function for removing negatively related words to a more common one
def re_negation(text_list):  
    # Applying regex
    return [re.sub('([nN][ãÃaA][oO]|[ñÑ]| [nN] )', ' negação ', r) for r in text_list]

#Function to remove special characters like punctuation or emojis
def re_special_chars(text_list):
    # Applying regex
    return [re.sub('\W', ' ', r) for r in text_list]

#Function to Remove Whitespaces created by co
def re_whitespaces(text_list):
    # Applying regex
    white_spaces = [re.sub('\s+', ' ', r) for r in text_list]
    white_spaces_end = [re.sub('[ \t]+$', '', r) for r in white_spaces]
    return white_spaces_end

"""
 2. Functions to Apply Extra Functions on Portugese Reviews
"""
#Function to Remove Stopwords
def stopwords_removal(text, cached_stopwords=stopwords.words('portuguese')):
    return [c.lower() for c in text.split() if c.lower() not in cached_stopwords]

#Function to Stem the comments
def stemming_process(text, stemmer=RSLPStemmer()):
    return [stemmer.stem(c) for c in text.split()]

"""
 3. Functions for Applying Englsish Translation
"""
# Define the retry condition function for tenacity
def is_translation_empty(result):
    return result == "" or result is None

## Function that will be retried on empty results
@retry(retry=retry_if_result(is_translation_empty), stop=stop_after_attempt(20), wait=wait_fixed(2))
def translate_text(text, source_lang='pt', target_lang='en'):
    try:
        # Perform the translation
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return ""  # Return empty to trigger retry

# Final function to apply the translation with retries to each element in the column
def apply_translation_with_retry(text):
    try:
        return translate_text(text)
    except RetryError:
        print(f"Max retries exceeded for text: {text}")
        return None  # Return None if all retries fail

#Removing Stopwords for English Translations
def stopwords_removal_en(text, cached_stopwords=stopwords.words('english')):
    return [c.lower() for c in text.split() if c.lower() not in cached_stopwords]


def process_sentiments(connection):

    ### START OF CLEANING AND PROCESSING
    #Importing the main reviews dataset
    df = pd.read_sql_query("SELECT * FROM olist_order_reviews_dataset;", connection)
    df = pd.DataFrame(df)
    #Dropping index columns for now
    df = df.drop('index', axis=1)

    #1) Importing the order_items dataset
    df_order = pd.read_sql_query("SELECT * FROM olist_order_items_dataset;", connection)
    df_order = pd.DataFrame(df_order)

    # Selecting the relevant columns, 'order_id' and 'product_id'
    df_order = df_order[['order_id', 'product_id']]

    #2) Importing the olist_products_datasets
    df_products = pd.read_sql_query("SELECT * FROM olist_products_dataset;", connection)
    df_products = pd.DataFrame(df_products)

    # Selecting the relevant columns, 'product_id' and 'product_category_name'
    df_products = df_products[['product_id','product_category_name']]

    #3) Converting Portugese product_category_names into English
    df_category_translation = pd.read_sql_query("SELECT * FROM product_category_name_translation;", connection)
    df_category_translation  = pd.DataFrame(df_category_translation)

    # Selecting the relevant columns, 'product_category_name' and 'product_category_name_english'
    df_category_translation = df_category_translation[['product_category_name','product_category_name_english']]

    # Step 1: Merge df and df_order on 'order_id'
    df_1 = df.merge(df_order, on='order_id', how='inner')

    # Step 2: Merge df_1 with df_products on 'product_id'
    df_2 = df_1.merge(df_products, on='product_id', how='inner', suffixes=('', '_product'))

    # Step 3: Merge df_2 with df_category_translation on 'product_category_name'
    df_comments = df_2.merge(df_category_translation, on='product_category_name', how='inner')

    # Combining 'review_comment_title' into 'review_comment_message' only if 'review_comment_title' is not null, doing this because, there is value in doing sentiment analysis on the words in the titles as well
    df_comments['review_comment_message'] = np.where(
        df_comments['review_comment_title'].notna(),
        df_comments['review_comment_title'] + " " + df_comments['review_comment_message'] ,
        df_comments['review_comment_message']
    )

    #Since we have merged multiple tables, duplicates might have arisen, therefore, we can remove duplicates on `order_id` as such
    df_comments = df_comments.drop_duplicates(subset=['order_id'])

    #Selecting the relevant columns for analysis
    df_comments = df_comments[['product_id','product_category_name','product_category_name_english','review_score','review_comment_message','review_creation_date', 'review_answer_timestamp']]

    #Dropping NaN values of 'Review Comment Message'
    df_comments.dropna(subset=['review_comment_message'])

    #Adding corresponding Index to each review score and their respective comment, and changing variable name to df_comments for efficient analysis.
    df_comments = df_comments.reset_index(drop=True)

    print(df_comments)

    ### RegEx Removal
    #1) Line Beak
    # Creating a list of comment reviews
    reviews= list(df_comments['review_comment_message'].values)

    print(reviews)

    # Applying RegEx
    reviews_breakline = re_breakline(reviews)
    df_comments['re_breakline'] = reviews_breakline

    # 2) Remove Hyperlinks
    # Applying RegEx
    reviews_hyperlinks = re_hyperlinks(reviews_breakline)
    df_comments['re_hyperlinks'] = reviews_hyperlinks

    # 3) Remove Dates
    # Applying RegEx
    reviews_dates = re_dates(reviews_hyperlinks)
    df_comments['re_dates'] = reviews_dates

    # 4) Removing Money Values
    # Applying RegEx
    reviews_money = re_money(reviews_dates)
    df_comments['re_money'] = reviews_money

    # 5) Remove Numbers
    # Applying RegEx
    reviews_numbers = re_numbers(reviews_money)
    df_comments['re_numbers'] = reviews_numbers

    # 6) Replace Negations
    # Applying RegEx
    reviews_negation = re_negation(reviews_numbers)
    df_comments['re_negation'] = reviews_negation

    # 7) Remove Special Characters
    # Applying RegEx
    reviews_special_chars = re_special_chars(reviews_negation)
    df_comments['re_special_chars'] = reviews_special_chars

    # 8) Remove Whitspaces
    # Applying RegEx
    reviews_whitespaces = re_whitespaces(reviews_special_chars)
    df_comments['re_whitespaces'] = reviews_whitespaces

    # 9) Remove Stopwords
    pt_stopwords = stopwords.words('portuguese')
    reviews_stopwords = [' '.join(stopwords_removal(review)) for review in reviews_whitespaces]
    df_comments['stopwords_removed'] = reviews_stopwords

    # 10) Stemming
    # Applying stemming
    reviews_stemmer = [' '.join(stemming_process(review)) for review in reviews_stopwords]
    df_comments['stemming'] = reviews_stemmer

    # 11) Parsing Dates
    df_comments['review_creation_date'] = pd.to_datetime(df_comments['review_creation_date'])
    df_comments['review_answer_timestamp'] = pd.to_datetime(df_comments['review_answer_timestamp'])
    #Creating a column of difference between review creation and review response
    df_comments['response_time'] = df_comments['review_answer_timestamp'] - df_comments['review_creation_date']
    df_comments['response_time_hours'] = df_comments['response_time'].dt.days * 24 + df_comments['response_time'].dt.components['hours'] + df_comments['response_time'].dt.components['minutes'] / 60 + df_comments['response_time'].dt.components['seconds'] / 3600
    df_comments['response_time_hours'] = df_comments['response_time_hours'].round(2)

    # Mapping English Categories 
    #Mapping the dictionary of 'category_mapping' to 'product_category_name_english 
    df_comments['broader_category_english'] = df_comments['product_category_name_english'].map(category_mapping)

    # Labelling data with a sentiment label 
    score_map = {
        1: 'negative',
        2: 'negative',
        3: 'positive',
        4: 'positive',
        5: 'positive'
    }
    df_comments['sentiment_label'] = df_comments['review_score'].map(score_map)

    #### THIS BLOCK RUNS FOR 7HRS, UHH TRY NOT TO RUN, I HAVE A FINALISED VERSION OF IT 'reviews_table_for_sentiment_analysis' #######
    #########

    # Apply the English translation to each row in the dataframe
    df_comments['review_en'] = df_comments['stopwords_removed'].apply(apply_translation_with_retry)
    #########

    #Selecting Relevant Columns for Analysis
    df_sentiment_analysis = df_comments.loc[:, ['product_id', 'product_category_name', 'product_category_name_english', 'broader_category_english', 'review_comment_message', 'stopwords_removed', 'stemming', 'review_en', 'review_score', 'sentiment_label','review_creation_date', 'review_answer_timestamp', 'response_time_hours']].rename(columns={
        'stopwords_removed': 'processed_review_comment_message', #Renaming 'stopwords_removed' to 'processed_review_comment_message'
        'stemming': 'stemmed_reviews'                            #Renaming 'stemming' to 'stemmed'
    })

    df_sentiment_analysis = df_sentiment_analysis.dropna(subset=['review_en'])

    # Examples of some english stopwords
    en_stopwords = stopwords.words('english')
    #Defining English Review List for Transformation
    review_en = df_sentiment_analysis['review_en'].tolist()
    # Removing stopwords
    review_en_cleaned = [' '.join(stopwords_removal_en(review)) for review in review_en]
    df_sentiment_analysis['review_en_cleaned'] = review_en_cleaned

    #Defining Cleaned English Review List for Transformation
    review_en_cleaned = df_sentiment_analysis['review_en_cleaned'].tolist()
    # Applying RegEx
    review_en_cleaned_special_chars = re_special_chars(review_en_cleaned)
    df_sentiment_analysis['review_en_cleaned_special_chars'] = review_en_cleaned_special_chars

    # Moving an existing column to a new position
    column_pop = df_sentiment_analysis.pop('review_en_cleaned_special_chars')
    df_sentiment_analysis.insert(8,'review_en_final', column_pop)

    #Finalzing the Dataset, dropping the irrelevant 'review_en_cleaned' column
    df_sentiment_analysis = df_sentiment_analysis.drop('review_en_cleaned', axis=1)

    return df_sentiment_analysis

def extract_sentiments(input_dir, connection):

    df_sentiment_analysis_path = os.path.join(input_dir, "reviews_sentiment_analysis.xlsx")

    if os.path.exists(df_sentiment_analysis_path):
        print("Reading from existing sentiment analysis file")
        # exit()
        df_sentiment_analysis = pd.read_excel(df_sentiment_analysis_path)
    else:
        print("Extracting sentiment analysis data with translator")
        df_sentiment_analysis = process_sentiments(connection)

    return df_sentiment_analysis

df_sentiment_analysis = extract_sentiments(input_dir, connection)

with pd.ExcelWriter(os.path.join(output_dir, 'subgroup_a_dashboard.xlsx'), engine='xlsxwriter') as writer:
    # Write each DataFrame to a specific sheet
    print("Writing to Excel...")
    churn_rate_by_category.to_excel(writer, sheet_name="churn_rate_category_viz", index=False)
    delivery_days_churn_rate.to_excel(writer, sheet_name="churn_rate_delivery_days_viz", index=False)
    delivery_diff_churn_rate.to_excel(writer, sheet_name="churn_rate_delivery_diff_viz", index=False)
    churn_rate_by_discount_bin.to_excel(writer, sheet_name="churn_rate_discount_rate_viz", index=False)
    mom_revenue_customer_df.to_excel(writer, sheet_name="daily_revenue_customers_viz", index=False)
    df_segmentation_rfm.to_excel(writer, sheet_name="customer_rfm_segment_score_viz", index=False)
    churn_rate_over_time_df.to_excel(writer, sheet_name="churn_rate_over_time_line_viz", index=False)
    olist_customers_dataset.to_excel(writer, sheet_name="olist_customers_dataset", index=False)
    olist_orders_dataset.to_excel(writer, sheet_name="olist_orders_dataset", index=False)
    olist_marketing_dataset.to_excel(writer, sheet_name="olist_marketing_dataset", index=False)
    df_sentiment_analysis.to_excel(writer, sheet_name="sentiment_analysis_viz", index=False)
    print("Finished writing to Excel")

