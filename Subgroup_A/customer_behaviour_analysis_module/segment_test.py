import sqlite3
import queries
import customer_segmentation_model as segmodel

def segment_main():
    conn = sqlite3.connect("/Users/becky/Repositories/Campus-Security/brazil_dataset.db")

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

    sse_rec = segmodel.calculate_sse(df_segm_rfm_scaled, "Recency", 10)
    print("sse_rec calculated")

    sse_freq = segmodel.calculate_sse(df_segm_rfm_scaled, "Frequency", 10)
    print("sse_freq calculated")

    sse_mon = segmodel.calculate_sse(df_segm_rfm_scaled, "Monetary Value", 10)
    print("sse_mon calculated")

    return orders_payments_df, latest_date, df_segm_rfm, df_segm_rfm_scaled, sse_rec, sse_freq, sse_mon





