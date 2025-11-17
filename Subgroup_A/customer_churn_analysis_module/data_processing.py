import pandas as pd
from scipy.stats import pearsonr

def count_total_unique_churned(df):
    return df['customer_unique_id'].nunique()

def count_total_unique_churned_group_by(df, group):
    return df.groupby(group)['customer_unique_id'].nunique().unstack(fill_value=0)

def count_total_unique_churned_group_by_size(df, group):
    return df.groupby(group).size().unstack(fill_value=0)

def churn_rate_overall(first_data, second_data):
    return (first_data / second_data) * 100

def churn_rate_count_by_segment(df, segment):
    return df.groupby(segment)['churned'].mean() * 100

def churn_count_by_segment(df, segment):
    return df.groupby(segment)['churned'].mean()

def churn_rate_count_by_segment_sum(df):
    df['churned'] = (df[1] / df.sum(axis=1)) * 100
    return df

def pearsonr_correlation(df):
    return pearsonr(df.index, df.values)

def percentage_churned_by_count_fillna(total, df, column_name, number):
    if number == 0:
        df[column_name] = (total / total.sum() * 100).fillna(0)
    else:
        df[column_name] = (df[number] / total * 100).fillna(0)
    return df


def reset_index(df):
    return df.reset_index()

def remove_duplicates(df, group):
    return df.drop_duplicates(subset=group)

def segment_bin(df, new_name, existing_name, desired_bins, labels):
    df[new_name] = pd.cut(df[existing_name], bins=desired_bins, labels=labels, right=False)
    return df

def segment_bin_right(df, new_name, existing_name, desired_bins, labels):
    df[new_name] = pd.cut(df[existing_name], bins=desired_bins, labels=labels)
    return df

def map_category(df):
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

    df['category'] = df['product_category_name_english'].map(category_mapping)
    return df

def convert_to_datetime(df, columns):
    for column in columns:
        df[column] = pd.to_datetime(df[column])
    return df

def number_of_days(df, name, first, second):
    df[name] = (df[first] - df[second]).dt.days
    return df
