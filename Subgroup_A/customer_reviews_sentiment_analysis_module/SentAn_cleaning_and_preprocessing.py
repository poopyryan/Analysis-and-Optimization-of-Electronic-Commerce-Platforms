"""
This script is used to define the functions required for cleaning and processing the datasets, more specifically,
used to process the text reviews for customer sentiment analysis
"""

"""
Importing ALL Libraries (Used in Final)
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
pd.set_option('display.max_columns', 100)
import plotly.offline as py
import plotly.express as px
import plotly.graph_objs as go
import json
import requests
import folium
from folium.plugins import FastMarkerCluster, Fullscreen, MiniMap, HeatMap, HeatMapWithTime, LocateControl
from wordcloud import WordCloud
from collections import Counter
from PIL import Image
import sqlite3

# DataPrep
import re
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
import joblib

#For English Translation
from deep_translator import GoogleTranslator
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_result, RetryError

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
 3. Dictionary for Category Mapping
"""
#Defining a dictionary to generalise some categories 
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

"""
 4. Functions for Applying Englsish Translation
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

# Class for regular expressions application
class ApplyRegex(BaseEstimator, TransformerMixin):
    def __init__(self, regex_transformers):
        self.regex_transformers = regex_transformers
    def fit(self, X, y=None):
        return self
    def transform(self, X, y=None):
        # Applying all regex functions in the regex_transformers dictionary
        for regex_name, regex_function in self.regex_transformers.items():
            X = regex_function(X)
        return X

# Class for stopwords removal from the corpus
class StopWordsRemoval(BaseEstimator, TransformerMixin):
    def __init__(self, text_stopwords):
        self.text_stopwords = text_stopwords
    def fit(self, X, y=None):
        return self
    def transform(self, X, y=None):
        return [' '.join(stopwords_removal(comment, self.text_stopwords)) for comment in X]

# Class for apply the stemming process
class StemmingProcess(BaseEstimator, TransformerMixin):
    def __init__(self, stemmer):
        self.stemmer = stemmer
    def fit(self, X, y=None):
        return self
    def transform(self, X, y=None):
        return [' '.join(stemming_process(comment, self.stemmer)) for comment in X]
    
# Class for extracting features from corpus
class TextFeatureExtraction(BaseEstimator, TransformerMixin):
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer
    def fit(self, X, y=None):
        return self
    def transform(self, X, y=None):
        return self.vectorizer.fit_transform(X).toarray()

