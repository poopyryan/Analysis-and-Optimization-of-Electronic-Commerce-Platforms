"""
This script is used to define the functions required visualisations of the customer reviews and sentiment analysis
"""

"""
Importing ALL Libraries (Used in Final)
"""
# Standard libs
import sqlite3
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

import re
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
import joblib

from collections import Counter
from plotly.subplots import make_subplots
import nltk
nltk.download('punkt')


"""
1. Functions to create N-grams
"""
# Define a function to extract n-grams
def get_top_ngrams(corpus, ngram_range=(1, 1), n=None):
    vec = CountVectorizer(ngram_range=ngram_range).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

# Helper function to convert to data format for plotting
def ngram_data(ngrams):
    words = [i[0] for i in ngrams]
    counts = [i[1] for i in ngrams]
    return words, counts

# Function to create color gradient based on counts
def color_gradient(counts, color_start, color_end):
    max_count = max(counts)
    min_count = min(counts)
    normalized_counts = [(count - min_count) / (max_count - min_count) for count in counts]
    colors = [
        f'rgba({(color_end[0] - color_start[0]) * nc + color_start[0]},'
        f'{(color_end[1] - color_start[1]) * nc + color_start[1]},'
        f'{(color_end[2] - color_start[2]) * nc + color_start[2]}, 1)'
        for nc in normalized_counts
    ]
    return colors

"""
2. Functions to create table for review score averages
"""
# Define color ranges, excluding the overall average row
def get_color(score):
    if score >= 4.00:
        return '#c6f7e2'  # light green
    elif score >= 3.80:
        return '#d9f0c3'  # light yellow-green
    elif score >= 3.70:
        return '#fef4c3'  # light yellow
    elif score >= 3.60:
        return '#fde0c5'  # light orange
    else:
        return '#f9c2c2'  # light red

