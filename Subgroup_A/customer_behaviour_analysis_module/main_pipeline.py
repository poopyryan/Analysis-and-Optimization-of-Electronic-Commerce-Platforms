import sqlite3
import queries 
import customer_lifetime_value_model as clvmodel
import customer_segmentation_model as segmodel
import os
from dotenv import load_dotenv

load_dotenv()

FILE_PATH = os.getenv('FILE_PATH')
TEST_SIZE = float(os.getenv('TEST_SIZE'))
RANDOM_STATE = int(os.getenv('RANDOM_STATE'))

def clv_main():
    conn = sqlite3.connect(FILE_PATH)

    clv_data = queries.get_clv_data(conn)
    print("CLV_DATA READY")
    df_clv_rfm = clvmodel.df_clv_rfm(clv_data)
    
    print("CLV RFM DATA READY")
    bgm, trace = clvmodel.build_and_sample_bgm_model(df_clv_rfm, draws=1000, tune=500,target_accept=0.95)

    print("BGM MODEL READY")
    df_clv_expected_purchases = clvmodel.clv_expected_purchases(bgm,df_clv_rfm, future_t=365)

    print("EXTRACT EXPECTED PURCHASES FORM BGM READY")
    df_clv_non_zero_purchases = clvmodel.filter_non_zero_purchases(df_clv_rfm)

    print("NON ZERO PURCHASES FILTERED")
    gg = clvmodel.build_gg_model(df_clv_non_zero_purchases)

    print("GG MODEL BUILT")
    df_clv_expected_spending = clvmodel.calculate_expected_spending(gg, df_clv_non_zero_purchases)

    print("EXTRACTED EXPECTED SPENDING FROM GG MODEL")
    df_clv_estimate = clvmodel.calculate_clv_estimate(gg, bgm,df_clv_rfm, 12, 0.01)
    print("CLV READY LGNLDFNG")
    
    return clv_data, df_clv_rfm, bgm, trace, df_clv_expected_purchases, df_clv_non_zero_purchases, gg, df_clv_expected_spending,df_clv_estimate  

    
def segment_main():
    conn = sqlite3.connect(FILE_PATH)

    orders_payments_df = queries.get_orders_payments(conn)
    print("orders_payments_df loaded")

    orders_payments_df = segmodel.drop_na(orders_payments_df)
    print("orders_payments_df dropped")

    orders_payments_df = segmodel.coerce_date(orders_payments_df)
    print("orders_payments_df's dates coereced")

    latest_date = segmodel.get_latest_date(orders_payments_df)
    print("latest date acquired")

    df_segm_rec = segmodel.calculate_recency(orders_payments_df, latest_date)
    print("dr_segm_rec ready")

    df_segm_freq = segmodel.calculate_frequency(orders_payments_df)
    print("df_segm_freq ready")

    df_segm_mon = segmodel.calculate_monetary_value(orders_payments_df)
    print("df_segm_mon ready")

    df_segm_rfm = segmodel.merge_rfm_data(df_segm_rec, df_segm_freq, df_segm_mon)
    print("df_segm_rfm merged successfully")

    df_segm_rfm_scaled = segmodel.scale_rfm_features(df_segm_rfm)
    print("df_segm_rfm successfully scaled")
    print(df_segm_rfm_scaled.columns)


    sse_rec = segmodel.calculate_sse(df_segm_rfm_scaled, "Recency", 10)
    print("sse_rec calculated")

    sse_freq = segmodel.calculate_sse(df_segm_rfm_scaled, "Frequency", 10)
    print("sse_freq calculated")

    sse_mon = segmodel.calculate_sse(df_segm_rfm_scaled, "Monetary Value", 10)
    print("sse_mon calculated")

    return orders_payments_df, latest_date, df_segm_rfm, df_segm_rfm_scaled, sse_rec, sse_freq, sse_mon
