import arviz as az
import pymc as pm 
import pandas as pd
import numpy as np
from arviz.labels import MapLabeller
from IPython.display import Image
from pymc_marketing import clv



# 1. Using BetaGeoModel to predict customers' expected number of purchases across a specified future time period
def df_clv_rfm(df):
    return clv.utils.rfm_summary(df, "customer_unique_id","order_purchase_timestamp", "payment_value")

def build_and_sample_bgm_model(data, draws=1000, tune=500, target_accept=0.95):
    """
    Build and sample from a BetaGeoModel for CLV prediction.
    
    Parameters:
        data (pd.DataFrame): The RFM dataset to train the model.
        draws (int): Number of posterior samples to draw.
        tune (int): Number of tuning steps (burn-in).
        target_accept (float): The target acceptance rate for sampling.
    
    Returns:
        bgm (BetaGeoModel): The trained BetaGeoModel.
        trace (arviz.InferenceData): The posterior samples.
    """
    # Step 1: Initialize the BetaGeoModel
    bgm = clv.BetaGeoModel(data=data)
    bgm.build_model()
    bgm.fit()

    # Step 2: Sample from the posterior within the model context
    with bgm.model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            target_accept=target_accept,
            return_inferencedata=True
        )
    
    return bgm, trace

def clv_expected_purchases(model, data, future_t=365):
    """
    Calculate the expected number of purchases over a specified future time period.
    
    Parameters:
        model (BetaGeoModel): The trained BetaGeoModel.
        data (pd.DataFrame): The RFM dataset used to predict future purchases.
        future_t (int): The time period (in days) for future purchases prediction.
    
    Returns:
        pd.DataFrame: A DataFrame with the expected future purchases added.
    """
    # Calculate expected purchases over `future_t` days
    num_purchases = model.expected_purchases(future_t=future_t, data=data)

    # Create a copy of the data with the expected purchases added
    df_expected_purchases = data.copy()
    df_expected_purchases["expected_purchases"] = num_purchases.mean(("chain", "draw")).values

    return df_expected_purchases

# 2. Using the Gamma-Gamma model to predict how much customers spend in each transaction across a specified future time period
def filter_non_zero_purchases(data):
    """
    Filter customers with non-zero purchase frequency and monetary value.
    
    Parameters:
        data (pd.DataFrame): The RFM dataset.
    
    Returns:
        pd.DataFrame: A filtered DataFrame with non-zero frequency and monetary value.
    """
    # Filter data for non-zero frequency and monetary value
    df_non_zero_purchases = data[
        (data["frequency"] > 0) & (data["monetary_value"] > 0)
    ][["customer_id", "monetary_value", "frequency"]]
    
    return df_non_zero_purchases

def build_gg_model(data):
    gg = clv.GammaGammaModel(data=data)
    gg.build_model
    gg.fit()
    return gg

def calculate_expected_spending(model, data):
    """
    Calculate the expected spending for each customer using a Gamma-Gamma model.
    
    Parameters:
        model (GammaGammaModel): The trained Gamma-Gamma model for expected spending.
        data (pd.DataFrame): The RFM dataset filtered for non-zero purchases.
    
    Returns:
        pd.DataFrame: A DataFrame with customer IDs and their expected spending.
    """
    # Calculate expected spending for each customer
    expected_spending = model.expected_customer_spend(data=data)
    
    # Average across chains and draws
    expected_spending_mean = expected_spending.mean(axis=(0, 1))  # Average across chains and draws

    # Create DataFrame with customer IDs and expected spending
    df_expected_spending = pd.DataFrame({
        "customer_id": data["customer_id"],
        "expected_spending": expected_spending_mean
    })

    return df_expected_spending

def calculate_clv_estimate(gamma_gamma_model, beta_geo_model, data, future_t=12, discount_rate=0.01):
    """
    Calculate the expected customer lifetime value using a Gamma-Gamma and Beta-Geometric model.
    
    Parameters:
        gamma_gamma_model (GammaGammaModel): The trained Gamma-Gamma model for monetary value.
        beta_geo_model (BetaGeoModel): The transaction model to estimate purchase frequency.
        data (pd.DataFrame): The RFM dataset used for prediction.
        future_t (int): Time horizon in months for CLV estimation.
        discount_rate (float): Discount rate for future cash flows.
    
    Returns:
        pd.DataFrame: A DataFrame with customer IDs and their estimated CLV.
    """
    # Calculate expected CLV
    clv_estimate = gamma_gamma_model.expected_customer_lifetime_value(
        data=data,
        transaction_model=beta_geo_model,
        future_t=future_t,
        discount_rate=discount_rate
    )

    df_clv_estimate = az.summary(clv_estimate, kind = 'stats').reset_index()

    return df_clv_estimate





