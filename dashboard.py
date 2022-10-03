# import libraries
import pandas as pd 
import pandas.io.sql as psql
import plotly.express as px
import streamlit as st

from config import create_connection
from datetime import datetime
from scipy.ndimage.filters import gaussian_filter1d


# pandas max column settings
pd.set_option('display.max_columns', 50)

from config import create_connection
from datetime import datetime

st.title("Nike Dunk Shoe Price Tracker")

# create database connection
connection, _ = create_connection()

## GOAT

# read in data from database
query = """
            SELECT 
                "date", 
                sku AS style_code, 
                value AS product_title, 
                retail_price_cents, 
                image_url 
            FROM goat;
        """
goat = psql.read_sql(query, connection)

# filter out only shoe(s) with price(s) greater than 0
goat = goat.query("retail_price_cents > 0")

# convert cents to USD
goat["retail_price_cents"] = goat.retail_price_cents / 100
goat.rename(columns={"retail_price_cents" : "price"}, inplace=True)


# data cleaning & transformation
goat["style_code"] = goat["style_code"].str.replace(" ", "-")
goat["date"] = goat["date"].dt.date

goat_df = goat.copy()
goat_df = goat_df.sort_values(by=["style_code", "date"])

goat_start_date = goat_df.date.min()
goat_end_date = goat_df.date.max()
goat_df = goat_df[(goat_df.date == goat_start_date) | (goat_df.date == goat_end_date)]

product_lst = list(set(zip(goat_df["style_code"].values, goat_df["product_title"].values)))
goat_data = goat_df.groupby(["style_code", "date"])["price"].mean().reset_index()

new_data = goat_data[goat_data["date"] == end_date][["style_code", "price"]]
old_data = goat_data[goat_data["date"] == start_date][["style_code", "price"]]
merge_data = pd.merge(old_data, new_data, how="inner", on="style_code")

merge_data.rename(columns={"price_x":"prev_price", "price_y":"curr_price"}, inplace=True)
merge_data["pct_change"] = round(((merge_data["curr_price"] - merge_data["prev_price"])/ merge_data["prev_price"]) * 100, 2)
merge_data["product_title"] = merge_data["style_code"].map(dict(product_lst))

final_data = merge_data[["product_title", "style_code" , "prev_price", "curr_price", "pct_change"]].sort_values(by="pct_change", ascending=False).reset_index(drop=True)

st.write("Goat Price Change")
st.write(final_data)

## SOLE SUPPLIER

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

product_list = list(set(zip(sole["style_code"].values, sole["product_title"].values)))
sole_df = sole.groupby(["style_code", "date"])["price"].mean().reset_index()

new_df = sole_df[sole_df["date"] == end_date][["style_code", "price"]]
old_df = sole_df[sole_df["date"] == start_date][["style_code", "price"]]
merge_df = pd.merge(old_df, new_df, how="inner", on="style_code")

merge_df.rename(columns={"price_x":"prev_price", "price_y":"curr_price"}, inplace=True)
merge_df["pct_change"] = round(((merge_df["curr_price"] - merge_df["prev_price"])/ merge_df["prev_price"]) * 100, 2)
merge_df["product_title"] = merge_df["style_code"].map(dict(product_list))

final_df = merge_df[["product_title", "style_code" , "prev_price", "curr_price", "pct_change"]].sort_values(by="pct_change", ascending=False).reset_index(drop=True)

st.write("Sole Supplier Price Change")
st.write(final_df)
