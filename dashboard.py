import numpy as np
import pandas as pd
import pandas.io.sql as psql
import plotly.express as px
import streamlit as st
from config import create_connection
from datetime import timedelta
from forex_python.converter import CurrencyRates
from utils import fillna_mode, style_negative, style_positive


c = CurrencyRates()

rate = c.get_rate('GBP', 'USD')

pd.options.display.float_format = "${:,.2f}".format


def home():
    unit = "$"
    st.write(
        "The sneaker retail market is a huge market where people invest in buying sneakers and sell them for a considerable profit. There are various strategies used when operating in such a market. The long-term investment strategy involves buying sneakers and holding unto them for a significant period to make a profit. In consignment, you get stores to sell the sneakers for you for a percentage of your profit. The final strategy called quick flip means you sell the sneakers immediately after you buy them for a slight profit. This is common for people who need quick cash or are new to the market. This dashboard helps track the prices of some of these sneakers to help make informed decisions when investing.")
    st.subheader("sole_supplier Supplier")
    # -------------- sole_supplier SUPPLIER --------------

    # create database connection
    connection, _ = create_connection()

    # read in data from database
    query = """
                SELECT 
                    "date",
                    style_code,
                    product_title,
                    ROUND(price,2) AS price,
                    image_url
                FROM sole_supplier
            """
    sole_supplier = psql.read_sql(query, connection)

    # close connection
    connection.close()

    # data cleaning & transformation
    sole_supplier["date"] = pd.to_datetime(sole_supplier["date"])
    sole_supplier["date"] = sole_supplier["date"].dt.date
    sole_supplier["price"] = sole_supplier["price"] * rate

    sole_supplier_start_date = sole_supplier.date.min()
    sole_supplier_end_date = sole_supplier.date.max()

    # data analysis
    sole_supplier.drop_duplicates(inplace=True)
    sole_supplier.sort_values(by=["style_code", "date"], inplace=True)

    sole_supplier_product_lst = list(
        set(zip(sole_supplier["style_code"].values,
            sole_supplier["product_title"].values))
    )

    sole_supplier_agg = sole_supplier.groupby(["style_code", "date"])[
        "price"].mean().unstack().fillna(method="backfill", axis=1)

    num_days = (sole_supplier_end_date - sole_supplier_start_date).days

    sole_supplier_agg["volatility"] = sole_supplier_agg.apply(
        lambda x: (x.std()) / (num_days ** 0.5), axis=1)
    # volatility = std / (365/T)**0.5
    sole_supplier_agg["price_change"] = sole_supplier_agg.apply(
        lambda x: round(
            ((x[sole_supplier_end_date] - x[sole_supplier_start_date])),
            2,
        ),
        axis=1,
    )
    try:
        sole_supplier_agg["daily_pct"] = sole_supplier_agg.apply(
            lambda x: round(
                (
                    (
                        (x[sole_supplier_end_date] -
                         x[sole_supplier_end_date - timedelta(days=1)])
                        / x[sole_supplier_end_date - timedelta(days=1)]
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
        sole_supplier_agg["weekly_pct"] = sole_supplier_agg.apply(
            lambda x: round(
                (
                    (
                        (x[sole_supplier_end_date] -
                         x[sole_supplier_end_date - timedelta(days=7)])
                        / x[sole_supplier_end_date - timedelta(days=7)]
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
        sole_supplier_agg["total_pct"] = sole_supplier_agg.apply(
            lambda x: round(
                (((x[sole_supplier_end_date] - x[sole_supplier_start_date]
                   ) / x[sole_supplier_start_date]) * 100),
                2,
            ),
            axis=1,
        )
    except:
        pass
    sole_supplier_agg = sole_supplier_agg.sort_values(
        by="volatility", ascending=False).reset_index()
    sole_supplier_agg.columns.name = ""
    sole_supplier_agg["volatility"] = sole_supplier_agg.volatility.astype(
        np.float32)
    sole_supplier_agg["volatility"] = round(
        np.log(sole_supplier_agg["volatility"]), 2)
    sole_supplier_agg = sole_supplier_agg.sort_values(
        by="volatility", ascending=False).reset_index(drop=True)
    sole_supplier_agg["product_title"] = sole_supplier_agg["style_code"].map(
        dict(sole_supplier_product_lst))

    if "daily_pct" not in list(sole_supplier_agg.columns):
        sole_supplier_agg = sole_supplier_agg.drop(
            columns=list(sole_supplier_agg.columns)[1:-6], axis=1)
        sole_supplier_agg.rename(
            columns={list(sole_supplier_agg.columns)[1]: "price"}, inplace=True)
        sole_supplier_agg = sole_supplier_agg[
            [
                "product_title",
                "style_code",
                "price",
                "price_change",
                # "daily_pct",
                "weekly_pct",
                "total_pct",
                "volatility",
            ]
        ]

    elif "weekly_pct" not in list(sole_supplier_agg.columns):
        sole_supplier_agg = sole_supplier_agg.drop(
            columns=list(sole_supplier_agg.columns)[1:-6], axis=1)
        sole_supplier_agg.rename(
            columns={list(sole_supplier_agg.columns)[1]: "price"}, inplace=True)
        sole_supplier_agg = sole_supplier_agg[
            [
                "product_title",
                "style_code",
                "price",
                "price_change",
                "daily_pct",
                # "weekly_pct",
                "total_pct",
                "volatility",
            ]
        ]
    elif (("weekly_pct") not in list(sole_supplier_agg.columns)) & (("daily_pct") not in list(sole_supplier_agg.columns)):
        sole_supplier_agg = sole_supplier_agg.drop(
            columns=list(sole_supplier_agg.columns)[1:-6], axis=1)
        sole_supplier_agg.rename(
            columns={list(sole_supplier_agg.columns)[1]: "price"}, inplace=True)
        sole_supplier_agg = sole_supplier_agg[
            [
                "product_title",
                "style_code",
                "price",
                "price_change",
                # "daily_pct",
                # "weekly_pct",
                "total_pct",
                "volatility",
            ]
        ]
    else:
        sole_supplier_agg = sole_supplier_agg.drop(
            columns=list(sole_supplier_agg.columns)[1:-7], axis=1)
        sole_supplier_agg.rename(
            columns={list(sole_supplier_agg.columns)[1]: "price"}, inplace=True)
        sole_supplier_agg = sole_supplier_agg[
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

    final_pct = sole_supplier_agg.sort_values(by="price_change", ascending=False).reset_index(
        drop=True
    )

    reverse_pct = sole_supplier_agg.sort_values(by="price_change", ascending=True).reset_index(
        drop=True
    )

    st.subheader("Top 5 Sneakers Price Gain & Price Drop")

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

    st.subheader("Top 10 Most Volatile Nike Dunk Sneakers")
    st.markdown(
        "$Volatility$ measures how the price of a sneaker varies from its average price over time. Fluctuation in price is a good indicator of sneakers that are relatively unstable. The sneakers with the highest volatility should be avoided to avert risk."
    )
    st.markdown(
        "- `style_code` represents a  unique identifier for each sneaker.")
    st.markdown(
        f"- `price` represents the  price on `{sole_supplier_end_date}`.")
    st.markdown(
        f"- `price_change` represents the  difference in price from `{sole_supplier_start_date}` to `{sole_supplier_end_date}`."
    )
    st.markdown("- `daily_pct` represents the percentage change in price daily.")
    st.markdown(
        "- `weekly_pct` represents the percentage change in price weekly.")
    st.markdown(
        f"- `total_pct` represents the percentage change in price from `{sole_supplier_start_date}` to `{sole_supplier_end_date}`."
    )
    st.markdown("- `volatility` represents the rate of fluctuation in price.")

    st.dataframe(
        sole_supplier_agg.head(10)
        .style.hide()
        .applymap(style_negative, props="color:red;")
        .applymap(style_positive, props="color:green;")
    )

    st.subheader("Goat")
    # -------------- GOAT --------------
    # create database connection
    connection, _ = create_connection()

    query = """
                    SELECT 
                        "date", 
                        sku AS style_code, 
                        value AS product_title, 
                        ROUND(retail_price_cents, 2) AS retail_price_cents 
                    FROM goat;
                """
    goat_frame = psql.read_sql(query, connection)

    # close connection
    connection.close()

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
    goat.drop_duplicates(inplace=True)
    goat.sort_values(by=["style_code", "date"], inplace=True)
    goat_agg = goat.groupby(["style_code", "date"])[
        "price"].mean().unstack().fillna(method="backfill", axis=1)

    goat_product_lst = list(
        set(zip(goat["style_code"].values, goat["product_title"].values))
    )

    num_days = (goat_end_date - goat_start_date).days

    goat_agg["volatility"] = goat_agg.apply(
        lambda x: (x.std()) / (num_days ** 0.5), axis=1)  # volatility = std / (T)**0.5

    goat_agg["price_change"] = goat_agg.apply(
        lambda x: round(
            ((x[goat_end_date] - x[goat_start_date])),
            2,
        ),
        axis=1,
    )

    goat_agg["daily_pct"] = goat_agg.apply(
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

    goat_agg["weekly_pct"] = goat_agg.apply(
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

    goat_agg["total_pct"] = goat_agg.apply(
        lambda x: round(
            (((x[goat_end_date] - x[goat_start_date]) / x[goat_start_date]) * 100), 2
        ),
        axis=1,
    )
    goat_agg = goat_agg.sort_values(
        by="volatility", ascending=False).reset_index()
    goat_agg.columns.name = ""
    goat_agg["volatility"] = goat_agg.volatility.astype(np.float32)
    goat_agg["volatility"] = round(np.log(goat_agg["volatility"]), 2)
    goat_agg = goat_agg.sort_values(
        by="volatility", ascending=False).reset_index(drop=True)
    goat_agg["product_title"] = goat_agg["style_code"].map(
        dict(goat_product_lst))
    goat_agg = goat_agg.drop(
        columns=list(goat_agg.columns)[1:-7], axis=1)
    goat_agg.rename(
        columns={list(goat_agg.columns)[1]: "price"}, inplace=True)
    goat_agg = goat_agg[
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

    final_pct_2 = goat_agg.sort_values(by="price_change", ascending=False).reset_index(
        drop=True
    )

    reverse_pct_2 = goat_agg.sort_values(by="price_change", ascending=True).reset_index(
        drop=True
    )

    st.subheader("Top 5 Sneakers Price Gain & Price Drop")

    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    for i in range(5):
        with columns[i]:
            st.metric(
                final_pct_2.iloc[i, 0],
                f"{unit}{final_pct_2.iloc[i, 2]:,.2f}",
                f"{final_pct_2.iloc[i, 3]:,.2f}",
            )

    for i in range(5):
        with columns[i]:
            st.metric(
                reverse_pct_2.iloc[i, 0],
                f"{unit}{reverse_pct_2.iloc[i, 2]:,.2f}",
                f"{reverse_pct_2.iloc[i, 3]:,.2f}",
            )

    st.subheader("Top 10 Most Volatile Nike Dunk Sneakers")
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
        goat_agg.head(10)
        .style.hide()
        .applymap(style_negative, props="color:red;")
        .applymap(style_positive, props="color:green;")
    )


def search():
    st.write("All original NIke sneakers have tags attached to them with their sizes, barcodes, and model numbers. The model number of the sneaker is usually located under the size and above the barcode. Most times, it is a 6-digit number / alphabet followed by a 3-digit number / alphabet (e.g. DJ0950-113).  You can also find it in the description on retail sites or on the box.")
    with st.form("sneaker_form", clear_on_submit=True):

        stores = ["sole_supplier Supplier", "Goat"]
        user_input = st.text_input(
            label="Model Number",
            max_chars=30,
            key="unique_code",
            placeholder="Enter your model number here ...",
        )
        stores = st.selectbox("Choose a retail store", stores)
        submitted = st.form_submit_button("Submit")
        style_code = st.session_state["unique_code"].upper()

        if submitted & (len(style_code) > 0):
            st.success("valid input")

            # data validation
            if (
                isinstance(user_input, str)
                & ("-" in style_code)
                & (10 >= len(style_code) < 30)
            ):
                # create database connection
                connection, _ = create_connection()

                if stores == "sole_supplier Supplier":
                    st.subheader("sole_supplier Supplier")
                    # read in data from database
                    query = f'''
                                SELECT 
                                    "date",
                                    product_title,
                                    price,
                                    image_url
                                FROM sole_supplier
                                WHERE style_code='{style_code}'
                            '''
                    df = psql.read_sql(query, connection)

                    # close connection
                    connection.close()

                    if (df.shape[0]) > 0:
                        df["date"] = pd.to_datetime(df["date"])
                        df["date"] = df["date"].dt.date
                        df["price"] = df["price"].round(2) * rate
                        title = df["product_title"].unique()[0]
                        img = df["image_url"].unique()[0]
                        data = df.sort_values(
                            by="date", ascending=False).copy()
                        # st.markdown(f"![{style_code} {title}]({img})")
                        st.image(img)
                        frame = data.describe().T
                        frame["initial"] = list(data["price"])[0]
                        frame["current"] = list(data["price"])[-1]
                        frame["change"] = list(
                            data["price"])[-1] - list(data["price"])[0]
                        frame.rename(
                            columns={
                                "mean": "average",
                                "std": "standard deviation",
                                "max": "maximum",
                                "min": "minimum",
                            },
                            inplace=True,
                        )
                        st.subheader("Summary Statistics")
                        st.dataframe(
                            frame.style.hide()
                            .applymap(style_negative, props="color:red;")
                            .applymap(style_positive, props="color:green;")
                        )
                        data = data[["date", "price"]]
                        data = data.set_index("date")
                        fig = px.line(
                            data,
                            y="price",
                            line_shape="spline",
                            render_mode="svg",
                            color_discrete_sequence=px.colors.qualitative.G10,
                        )
                        fig.update_layout(
                            title_text=f"{title} Price Change Over Time")
                        # fig.update_layout(
                        #     {"plot_bgcolor": "rgba(106, 245, 39, 0.96)"})
                        fig.update_traces(
                            line={"color": "Black", "width": 2.5})
                        fig.update_xaxes(
                            minor=dict(ticks="inside", showgrid=True),
                            rangeslider_visible=True,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.markdown(f"### {style_code} not found in database")
                elif stores == "Goat":
                    st.subheader("Goat")
                    # read in data from database
                    query = f'''
                                SELECT 
                                    "date",
                                    product_title,
                                    (retail_price_cents/100) AS price,
                                    image_url
                                FROM goat
                                WHERE REPLACE(sku, '', '-')='{style_code}'
                            '''
                    df = psql.read_sql(query, connection)

                    # close connection
                    connection.close()

                    if (df.shape[0]) > 0:
                        df["date"] = pd.to_datetime(df["date"])
                        df["date"] = df["date"].dt.date
                        df["price"] = df["price"].round(2)
                        title = df["product_title"].unique()[0]
                        img = df["image_url"].unique()[0]
                        data = df.sort_values(
                            by="date", ascending=False).copy()
                        # st.markdown(f"![{style_code} {title}]({img})")
                        st.image(img)
                        frame = data.describe().T
                        frame["initial"] = list(data["price"])[0]
                        frame["current"] = list(data["price"])[-1]
                        frame["change"] = list(
                            data["price"])[-1] - list(data["price"])[0]
                        frame.rename(
                            columns={
                                "mean": "average",
                                "std": "standard deviation",
                                "max": "maximum",
                                "min": "minimum",
                            },
                            inplace=True,
                        )
                        st.subheader("Summary Statistics")
                        st.dataframe(
                            frame.style.hide()
                            .applymap(style_negative, props="color:red;")
                            .applymap(style_positive, props="color:green;")
                        )
                        data = data[["date", "price"]]
                        data = data.set_index("date")
                        fig = px.line(
                            data,
                            y="price",
                            line_shape="spline",
                            render_mode="svg",
                            color_discrete_sequence=px.colors.qualitative.G10,
                        )
                        fig.update_layout(
                            title_text=f"{title} Price Change Over Time")
                        # fig.update_layout(
                        #     {"plot_bgcolor": "rgba(106, 245, 39, 0.96)"})
                        fig.update_traces(
                            line={"color": "Black", "width": 2.5})
                        fig.update_xaxes(
                            minor=dict(ticks="inside", showgrid=True),
                            rangeslider_visible=True,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.markdown(f"### {style_code} not found in database")
