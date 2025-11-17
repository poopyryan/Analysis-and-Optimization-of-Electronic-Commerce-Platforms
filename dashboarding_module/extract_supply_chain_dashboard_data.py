import sqlite3
import pandas as pd
import os
import sql_queries
import click

#################### SUPPLY CHAIN DATA ####################

##### SUPPLIER PERFORMANCE DATA #####

def extract_supply_chain_data(supply_chain_database_path):

    supply_chain_conn = sqlite3.connect(supply_chain_database_path)

    # Order Data #
    order_data = pd.read_sql_query(sql_queries.order_data_query(), supply_chain_conn)

    # All stock Data #
    stock_data = pd.read_sql_query(sql_queries.all_stock_data_query(), supply_chain_conn)

    # Monthly stock Data #
    monthly_stock_data = pd.read_sql_query(sql_queries.monthly_stock_data_query(), supply_chain_conn)

    # Product Info #
    product_info = pd.read_sql_query(sql_queries.product_info_query(), supply_chain_conn)

    supply_chain_conn.close()

    return order_data, stock_data, monthly_stock_data, product_info

##### INVENTORY MANAGEMENT DATA #####

def inventory_management_data(inventory_management_dir, input_year):

    # Forecasted Demand Data #
    forecasted_data = pd.read_csv(os.path.join(inventory_management_dir, input_year, "demand_forecast.csv"))

    # EOQ ROP Data #
    eoq_rop_data = pd.read_csv(os.path.join(inventory_management_dir, input_year, "product_EOQ_ROP.csv"))

    return forecasted_data, eoq_rop_data

def write_subgroup_b_data(order_data, stock_data, monthly_stock_data, product_info, eoq_rop_data, forecasted_data, output_dir):

    with pd.ExcelWriter(f"{output_dir}/subgroup_b_dashboard.xlsx") as writer:
        order_data.to_excel(writer, sheet_name="order_data", index=False)
        stock_data.to_excel(writer, sheet_name="stock_data", index=False)
        monthly_stock_data.to_excel(writer, sheet_name="stock_data_by_month", index=False)
        product_info.to_excel(writer, sheet_name="product_info", index=False)
        eoq_rop_data.to_excel(writer, sheet_name="product_eoq_rop_data", index=False)
        forecasted_data.to_excel(writer, sheet_name="predicted_demand", index=False)

    return

@click.command()
@click.argument("supply_chain_database_path", type=click.Path())
@click.argument("output_dir", type=click.Path())
@click.argument("inventory_management_dir", type=click.Path(exists=True))
@click.argument("input_year", type=click.STRING)

def main(supply_chain_database_path, output_dir, inventory_management_dir, input_year):

    # Supply Chain Data #
    order_data, stock_data, monthly_stock_data, product_info = extract_supply_chain_data(supply_chain_database_path)

    # Inventory Management Data #
    forecasted_data, eoq_rop_data = inventory_management_data(inventory_management_dir, input_year)

    # Write Data #
    write_subgroup_b_data(order_data, stock_data, monthly_stock_data, product_info, eoq_rop_data, forecasted_data, output_dir)

    return

if __name__ == "__main__":
    main()