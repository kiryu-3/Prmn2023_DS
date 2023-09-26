import numpy as np
import pandas as pd
import streamlit as st
import streamlit_pandas_kaoru as spk
from datetime import datetime, timedelta

import re
import requests
from PIL import Image
import io
from io import BytesIO

# 画像URLを指定
image_url = "https://imgur.com/okIhGTb.jpg"

# 画像をダウンロードしPILのImageオブジェクトとして読み込む
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))

# Streamlit ページの設定
st.set_page_config(
    page_title="CSV Filters",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# タブ
# tab1, tab2, tab3 = spk.sidebar.tabs(["Uploader", "Select_Values", "Downloader"])

st.title("CSV Filters")

# タブ
spk.tab1.file_uploader("CSVファイルをアップロード", 
                  type=["csv"], 
                  key="upload_csvfile", 
                  on_change=upload_csv
                )

# st.write(show_df[st.session_state["filtered_columns"]])
        

