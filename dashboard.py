# import libraries

import pandas as pd
import pandas.io.sql as psql
import plotly.express as px
import streamlit as st

from config import create_connection

# from datetime import datetime
# from scipy.ndimage.filters import gaussian_filter1d


# pandas max column settings
pd.set_option('display.max_columns', 50)

# styling
def style_negative(value, props=""):
    "Styles negative values in  a dataframe"
    try:
        return props if value < 0 else None
    except:
        pass

def style_positive(value, props=""):
    "Styles positive values in  a dataframe"
    try:
        return props if value > 0 else None
    except:
        pass

st.title("Nike Dunk Shoe Price Tracker")

# create database connection
connection, _ = create_connection()

# GOAT
query = """
                SELECT 
                    "date", 
                    sku AS style_code, 
                    value AS product_title, 
                    retail_price_cents, 
                    image_url 
                FROM goat;
            """
goat_frame = psql.read_sql(query, connection)


# read in data from database
# filter out only shoe(s) with price(s) greater than 0
goat = goat_frame.query("retail_price_cents > 0")

# convert cents to USD
goat["retail_price_cents"] = goat.retail_price_cents / 100
goat.rename(columns={"retail_price_cents": "price"}, inplace=True)


# data cleaning & transformation
goat["style_code"] = goat["style_code"].str.replace(" ", "-")
goat["date"] = goat["date"].dt.date

goat_df = goat.copy()
goat_df = goat_df.sort_values(by=["style_code", "date"])

goat_start_date = goat_df.date.min()
goat_end_date = goat_df.date.max()
goat_df = goat_df[(goat_df.date == goat_start_date)
                | (goat_df.date == goat_end_date)]

product_lst = list(
    set(zip(goat_df["style_code"].values, goat_df["product_title"].values)))
goat_data = goat_df.groupby(["style_code", "date"])[
    "price"].mean().reset_index()

new_data = goat_data[goat_data["date"] ==
                    goat_end_date][["style_code", "price"]]
old_data = goat_data[goat_data["date"] ==
                    goat_start_date][["style_code", "price"]]
merge_data = pd.merge(old_data, new_data, how="inner", on="style_code")

merge_data.rename(columns={"price_x": "prev_price",
                "price_y": "curr_price"}, inplace=True)
merge_data["pct_change"] = round(
    ((merge_data["curr_price"] - merge_data["prev_price"]) / merge_data["prev_price"]) * 100, 2)
merge_data["product_title"] = merge_data["style_code"].map(dict(product_lst))

final_data = merge_data[["product_title", "style_code", "prev_price", "curr_price",
                        "pct_change"]].sort_values(by="pct_change", ascending=False).reset_index(drop=True)

reverse_data = final_data.sort_values(by="pct_change", ascending=True).reset_index(drop=True)

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

st.write("Goat - Top 5 Price Gain")

for i in range(5):
    with columns[i]:
        st.metric(final_data.iloc[i, 0], final_data.iloc[i, -2], final_data.iloc[i, -1])

st.write("Goat - Top 5 Price Drop")

for i in range(5):
    with columns[i]:
        st.metric(reverse_data.iloc[i, 0], reverse_data.iloc[i, -2], reverse_data.iloc[i, -1])

st.write("Goat - Top 10 Shoes by Percent Price Change")
st.dataframe(final_data.head(10).style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;'))

# SOLE SUPPLIER

# read in data from database
query = """
            SELECT 
                "date",
                style_code,
                product_title,
                price,
                image_url
            FROM sole_supplier
        """
sole_supplier = psql.read_sql(query, connection)

# data cleaning & transformation
sole = sole_supplier.copy()
sole["date"] = sole["date"].dt.date
sole = sole.sort_values(by=["style_code", "date"])

sole_start_date = sole.date.min()
sole_end_date = sole.date.max()
sole = sole[(sole.date == sole_start_date) | (sole.date == sole_end_date)]

product_list = list(
    set(zip(sole["style_code"].values, sole["product_title"].values)))
sole_df = sole.groupby(["style_code", "date"])["price"].mean().reset_index()

new_df = sole_df[sole_df["date"] == sole_end_date][["style_code", "price"]]
old_df = sole_df[sole_df["date"] == sole_start_date][["style_code", "price"]]
merge_df = pd.merge(old_df, new_df, how="inner", on="style_code")

merge_df.rename(columns={"price_x": "prev_price",
                "price_y": "curr_price"}, inplace=True)
merge_df["pct_change"] = round(
    ((merge_df["curr_price"] - merge_df["prev_price"]) / merge_df["prev_price"]) * 100, 2)
merge_df["product_title"] = merge_df["style_code"].map(dict(product_list))

final_df = merge_df[["product_title", "style_code", "prev_price", "curr_price",
                    "pct_change"]].sort_values(by="pct_change", ascending=False).reset_index(drop=True)
reverse_df = final_df.sort_values(by="pct_change", ascending=True).reset_index(drop=True)


col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

st.write("Sole Supplier - Top 5 Price Gain")

for i in range(5):
    with columns[i]:
        st.metric(final_df.iloc[i, 0], final_df.iloc[i, -2], final_df.iloc[i, -1])

st.write("Sole Supplier - Top 5 Price Drop")

for i in range(5):
    with columns[i]:
        st.metric(reverse_df.iloc[i, 0], reverse_df.iloc[i, -2], reverse_df.iloc[i, -1])

st.write("Sole Supplier - Top 10 Shoes by Percent Price Change")
st.dataframe(final_df.head(10).style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;'))
