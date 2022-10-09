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

if selected == "Home":
    home()

elif selected == "Search":
    search()
