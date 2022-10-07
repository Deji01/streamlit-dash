import numpy as np
import pandas as pd
import pandas.io.sql as psql
import streamlit as st
from config import create_connection
from datetime import timedelta
from utils import fillna_mode, style_negative, style_positive

# pandas max column settings
pd.set_option("display.max_columns", 50)
pd.options.display.float_format = "${:,.2f}".format


def home():
    unit = "$"
    # create database connection
    connection, _ = create_connection()

    st.markdown("## Sole Supplier")
    # -------------- SOLE SUPPLIER --------------

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
    sole["date"] = pd.to_datetime(sole["date"])
    sole["date"] = sole["date"].dt.date

    sole_start_date = sole.date.min()
    sole_end_date = sole.date.max()

    # data analysis
    sole_df = sole.copy()
    sole_df = sole_df.sort_values(by=["style_code", "date"])

    sole_product_lst = list(
        set(zip(sole_df["style_code"].values, sole_df["product_title"].values))
    )

    sole_df = sole_df.groupby(["style_code", "date"])[
        "price"].mean().reset_index()
    sole_df = sole_df.pivot_table("style_code", "date", "style_code")
    sole_df = sole_df.T

    sole_data = fillna_mode(sole_df)

    num_days = (sole_end_date - sole_start_date).days

    sole_data["volatility"] = sole_data.apply(
        lambda x: (x.std()) / ((365 / num_days) ** 0.5), axis=1
    )  # volatility = std / (365/T)**0.5

    sole_data["price_change"] = sole_data.apply(
        lambda x: round(
            ((x[sole_end_date] - x[sole_start_date])),
            2,
        ),
        axis=1,
    )
    try:
        sole_data["daily_pct"] = sole_data.apply(
            lambda x: round(
                (
                    (
                        (x[sole_end_date] - x[sole_end_date - timedelta(days=1)])
                        / x[sole_end_date - timedelta(days=1)]
                    )
                    * 100
                ),
                2,
            ),
            axis=1,
        )
    except:
        pass

    try:
        sole_data["weekly_pct"] = sole_data.apply(
            lambda x: round(
                (
                    (
                        (x[sole_end_date] - x[sole_end_date - timedelta(days=7)])
                        / x[sole_end_date - timedelta(days=7)]
                    )
                    * 100
                ),
                2,
            ),
            axis=1,
        )
    except:
        pass

    try:
        sole_data["total_pct"] = sole_data.apply(
            lambda x: round(
                (((x[sole_end_date] - x[sole_start_date]) / x[sole_start_date]) * 100),
                2,
            ),
            axis=1,
        )
    except:
        pass

    final_data = sole_data.sort_values(
        by="volatility", ascending=False).reset_index()
    final_data.columns.name = ""
    final_data["product_title"] = final_data["style_code"].map(
        dict(sole_product_lst))
    final_data = final_data.drop(
        columns=list(final_data.columns)[1:-7], axis=1)
    final_data.rename(
        columns={list(final_data.columns)[1]: "price"}, inplace=True)
    final_data = final_data[
        [
            "product_title",
            "style_code",
            "price",
            "price_change",
            "daily_pct",
            "weekly_pct",
            "total_pct",
            "volatility",
        ]
    ]

    final_pct = final_data.sort_values(by="price_change", ascending=False).reset_index(
        drop=True
    )

    reverse_pct = final_data.sort_values(by="price_change", ascending=True).reset_index(
        drop=True
    )

    st.markdown("#### Top 5 Sneakers Price Gain & Price Drop")

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i in range(5):
        with columns[i]:
            st.metric(
                final_pct.iloc[i, 0],
                f"{unit}{final_pct.iloc[i, 2]:,.2f}",
                f"{final_pct.iloc[i, 3]:,.2f}",
            )

    for i in range(5):
        with columns[i]:
            st.metric(
                reverse_pct.iloc[i, 0],
                f"{unit}{reverse_pct.iloc[i, 2]:,.2f}",
                f"{reverse_pct.iloc[i, 3]:,.2f}",
            )

    st.markdown("#### Top 10 Most Volatile Nike Dunk Sneakers")
    st.markdown(
        "$Volatility$ measures how the price of a sneaker varies from its average price over time. Fluctuation in price is a good indicator of sneakers that are relatively unstable. The sneakers with the highest volatility should be avoided to avert risk."
    )
    st.markdown(
        "- `style_code` represents a  unique identifier for each sneaker.")
    st.markdown(f"- `price` represents the  price on `{sole_end_date}`.")
    st.markdown(
        f"- `price_change` represents the  difference in price from `{sole_start_date}` to `{sole_end_date}`."
    )
    st.markdown("- `daily_pct` represents the percentage change in price daily.")
    st.markdown(
        "- `weekly_pct` represents the percentage change in price weekly.")
    st.markdown(
        f"- `total_pct` represents the percentage change in price from `{sole_start_date}` to `{sole_end_date}`."
    )
    st.markdown("- `volatility` represents the rate of fluctuation in price.")

    st.dataframe(
        final_data.head(10)
        .style.hide()
        .applymap(style_negative, props="color:red;")
        .applymap(style_positive, props="color:green;")
    )

    st.markdown("## Goat")
    # -------------- GOAT --------------

    query = """
                    SELECT 
                        "date", 
                        sku AS style_code, 
                        value AS product_title, 
                        retail_price_cents 
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
    goat["date"] = pd.to_datetime(goat["date"])
    goat["date"] = goat["date"].dt.date

    goat_start_date = goat.date.min()
    goat_end_date = goat.date.max()

    # data analysis
    goat_df = goat.copy()
    goat_df = goat_df.sort_values(by=["style_code", "date"])

    goat_product_lst = list(
        set(zip(goat_df["style_code"].values, goat_df["product_title"].values))
    )

    goat_df = goat_df.groupby(["style_code", "date"])[
        "price"].mean().reset_index()
    goat_df = goat_df.pivot_table("style_code", "date", "style_code")
    goat_df = goat_df.T

    goat_data = fillna_mode(goat_df)

    num_days = (goat_end_date - goat_start_date).days

    goat_data["volatility"] = goat_data.apply(
        lambda x: (x.std()) / ((365 / num_days) ** 0.5), axis=1
    )  # volatility = std / (T)**0.5

    goat_data["price_change"] = goat_data.apply(
        lambda x: round(
            ((x[goat_end_date] - x[goat_start_date])),
            2,
        ),
        axis=1,
    )

    goat_data["daily_pct"] = goat_data.apply(
        lambda x: round(
            (
                (
                    (x[goat_end_date] - x[goat_end_date - timedelta(days=1)])
                    / x[goat_end_date - timedelta(days=1)]
                )
                * 100
            ),
            2,
        ),
        axis=1,
    )

    goat_data["weekly_pct"] = goat_data.apply(
        lambda x: round(
            (
                (
                    (x[goat_end_date] - x[goat_end_date - timedelta(days=7)])
                    / x[goat_end_date - timedelta(days=7)]
                )
                * 100
            ),
            2,
        ),
        axis=1,
    )

    goat_data["total_pct"] = goat_data.apply(
        lambda x: round(
            (((x[goat_end_date] - x[goat_start_date]) / x[goat_start_date]) * 100), 2
        ),
        axis=1,
    )

    final_data = goat_data.sort_values(
        by="volatility", ascending=False).reset_index()
    final_data.columns.name = ""
    final_data["product_title"] = final_data["style_code"].map(
        dict(goat_product_lst))
    final_data = final_data.drop(
        columns=list(final_data.columns)[1:-7], axis=1)
    final_data.rename(
        columns={list(final_data.columns)[1]: "price"}, inplace=True)
    final_data = final_data[
        [
            "product_title",
            "style_code",
            "price",
            "price_change",
            "daily_pct",
            "weekly_pct",
            "total_pct",
            "volatility",
        ]
    ]

    final_pct = final_data.sort_values(by="price_change", ascending=False).reset_index(
        drop=True
    )

    reverse_pct = final_data.sort_values(by="price_change", ascending=True).reset_index(
        drop=True
    )

    st.markdown("#### Top 5 Sneakers Price Gain & Price Drop")

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i in range(5):
        with columns[i]:
            st.metric(
                final_pct.iloc[i, 0],
                f"{unit}{final_pct.iloc[i, 2]:,.2f}",
                f"{final_pct.iloc[i, 3]:,.2f}",
            )

    for i in range(5):
        with columns[i]:
            st.metric(
                reverse_pct.iloc[i, 0],
                f"{unit}{reverse_pct.iloc[i, 2]:,.2f}",
                f"{reverse_pct.iloc[i, 3]:,.2f}",
            )

    st.markdown("#### Top 10 Most Volatile Nike Dunk Sneakers")
    st.markdown(
        "$Volatility$ measures how the price of a sneaker varies from its average price over time. Fluctuation in price is a good indicator of sneakers that are relatively unstable. The sneakers with the highest volatility should be avoided to avert risk."
    )
    st.markdown(
        "- `style_code` represents a  unique identifier for each sneaker.")
    st.markdown(f"- `price` represents the  price on `{goat_end_date}`.")
    st.markdown(
        f"- `price_change` represents the  difference in price from `{goat_start_date}` to `{goat_end_date}`."
    )
    st.markdown("- `daily_pct` represents the percentage change in price daily.")
    st.markdown(
        "- `weekly_pct` represents the percentage change in price weekly.")
    st.markdown(
        f"- `total_pct` represents the percentage change in price from `{goat_start_date}` to `{goat_end_date}`."
    )
    st.markdown("- `volatility` represents the rate of fluctuation in price.")
    st.dataframe(
        final_data.head(10)
        .style.hide()
        .applymap(style_negative, props="color:red;")
        .applymap(style_positive, props="color:green;")
    )
