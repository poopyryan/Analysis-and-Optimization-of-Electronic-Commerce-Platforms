import sqlite3
import pandas as pd
import os
from sdv.metadata import Metadata

def load_data(database_path, query):
    connection = sqlite3.connect(database_path)
    df = pd.read_sql_query(query, connection)
    connection.close()
    return df

def merge_data(first_df, second_df, column):
    return pd.merge(first_df, second_df, on=column)

def load_metadata(metadata_filename, df):
    if not os.path.isfile(metadata_filename):
        metadata = Metadata.detect_from_dataframe(df)
        metadata.save_to_json(metadata_filename)
    else:
        metadata = Metadata.load_from_json(metadata_filename)
    return metadata

def drop_column(df, list_of_columns):
    return df.drop(columns=list_of_columns)
