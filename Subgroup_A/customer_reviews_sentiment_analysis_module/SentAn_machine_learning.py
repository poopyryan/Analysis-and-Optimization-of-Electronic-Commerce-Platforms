"""
This script is used to define the functions required for sentiment analysis for Machine Learning.
More specifcally, this script contains functions for building, training and evaluating the pipeline and model
for predicting positive and negative sentiment
"""

"""
Importing ALL Libraries (Used in Final)
"""
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


# DataPrep
import re
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
import joblib
from deep_translator import GoogleTranslator

# Modeling
import itertools
import time
from datetime import datetime
from sklearn.model_selection import train_test_split, RandomizedSearchCV, cross_val_score, cross_val_predict, learning_curve
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, make_scorer
import shap
import lightgbm as lgb
from sklearn.cluster import KMeans

"""
1. Defining Functions for Feature Extraction
"""
def extract_features_from_corpus(corpus, vectorizer, df=False):
    # Extracting features
    corpus_features = vectorizer.fit_transform(corpus).toarray()
    features_names = vectorizer.get_feature_names_out()
    # Transforming into a dataframe to give interpetability to the process
    df_corpus_features = None
    if df:
        df_corpus_features = pd.DataFrame(corpus_features, columns=features_names)
    return corpus_features, df_corpus_features


"""
2. Building a Class for Analysis
"""
class ClassifierAnalysis:
    def __init__(self):
        self.results = {}

    def fit(self, classifiers, X_train, y_train, random_search=True, scoring='accuracy', cv=5):
        for name, clf_info in classifiers.items():
            model = clf_info['model']
            param_grid = clf_info['params']
            print(f"Training {name}...")

            # Perform hyperparameter tuning if parameter grid is provided
            if random_search and param_grid:
                search = RandomizedSearchCV(model, param_grid, n_iter=20, scoring=scoring, cv=cv, random_state=42, n_jobs=-1)
                start_time = time.time()
                search.fit(X_train.toarray() if hasattr(model, 'partial_fit') else X_train, y_train)
                elapsed_time = time.time() - start_time
                best_model = search.best_estimator_
            else:
                start_time = time.time()
                model.fit(X_train, y_train)
                elapsed_time = time.time() - start_time
                best_model = model

            # Cross-validation scores
            scores = cross_val_score(best_model, X_train, y_train, scoring=scoring, cv=cv)
            self.results[name] = {'model': best_model, 'cv_scores': scores, 'fit_time': elapsed_time}

            print(f"{name} completed in {elapsed_time:.2f}s with mean CV {scoring}: {np.mean(scores):.4f}")


"""
3. Functions for Colors in Model Evaluation Metrics
"""
#Plotting Test Metric Results
def get_fill_color(value, column_values):
    if value == "LogisticRegression":
        return "#F2F3F4"
    if value == "Naive Bayes":
        return "#F2F3F4"
    elif value == max(column_values):
        return "#00008C" 
    else:
        return "#F2F3F4"  

def get_font_color(fill_color):
    if fill_color == "#00008C":
        return "white"  
    else:
        return "black"



"""
3. Functions for Sentiment Analysis Prediction
"""
def sentiment_analysis_predictor_portuguese(text, pipeline, vectorizer, model):    
    # Step 1: Preprocess the text
    preprocessed_text = pipeline.transform([text])  # Assumes pipeline has a transform method
    
    # Step 2: Vectorize the text
    vectorized_text = vectorizer.transform(preprocessed_text).toarray()

    # Step 3: Predict sentiment
    prediction_proba = model.predict_proba(vectorized_text)  # Get probabilities for both classes
    pred = model.predict(vectorized_text)

    # Step 4: Display results
    fig, ax = plt.subplots(figsize=(5, 3))
    
    if pred[0] == 1:
        text = 'Positive'
        class_proba = 100 * round(prediction_proba[0][1], 2)
        color = 'green'  
    else:
        text = 'Negative'
        class_proba = 100 * round(prediction_proba[0][0], 2)
        color = 'red'  

    ax.text(0.5, 0.5, text, fontsize=50, ha='center', color=color)
    ax.text(0.5, 0.20, str(class_proba) + '%', fontsize=14, ha='center')
    
    ax.axis('off')
    ax.set_title('Sentiment Analysis', fontsize=14)
    
    plt.show()


def sentiment_analysis_predictor_english(text, pipeline, vectorizer, model):
    #Translating from Portuguese to English
    translated_text = GoogleTranslator(source='pt', target='en').translate(text)    
    
    # Step 1: Preprocess the text
    preprocessed_text = pipeline.transform([translated_text])  # Assumes pipeline has a transform method
    
    # Step 2: Vectorize the text
    vectorized_text = vectorizer.transform(preprocessed_text).toarray()

    # Step 3: Predict sentiment
    prediction_proba = model.predict_proba(vectorized_text)  # Get probabilities for both classes
    pred = model.predict(vectorized_text)

    # Step 4: Display results
    fig, ax = plt.subplots(figsize=(5, 3))
    
    if pred[0] == 1:
        text = 'Positive'
        class_proba = 100 * round(prediction_proba[0][1], 2)
        color = 'green'  
    else:
        text = 'Negative'
        class_proba = 100 * round(prediction_proba[0][0], 2)
        color = 'red'  

    ax.text(0.5, 0.5, text, fontsize=50, ha='center', color=color)
    ax.text(0.5, 0.20, str(class_proba) + '%', fontsize=14, ha='center')
    
    ax.axis('off')
    ax.set_title('Sentiment Analysis', fontsize=14)
    
    plt.show()