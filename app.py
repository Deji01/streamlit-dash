# import libraries
import streamlit as st
from streamlit_option_menu import option_menu
from dashboard import home, search

# -------------- SETTINGS --------------
page_title = "Nike Dunk Sneakers Price Tracker"
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
page_icon = ":shoe:"
layout = "wide"
# --------------------------------------


st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title)

# Option Menu
selected = option_menu(
    None,
    ["Home", "Search"],
    icons=["house", "search"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

st.write(
    "The sneaker retail market is a huge market where people invest in buying sneakers and sell them for a considerable profit. There are various strategies used when operating in such a market. The long-term investment strategy involves buying sneakers and holding unto them for a significant period to make a profit. In consignment, you get stores to sell the sneakers for you for a percentage of your profit. The final strategy called quick flip means you sell the sneakers immediately after you buy them for a slight profit. This is common for people who need quick cash or are new to the market. This dashboard helps track the prices of some of these sneakers to help make informed decisions when investing."
)
if selected == "Home":
    home()

if selected == "Search":
    search()
