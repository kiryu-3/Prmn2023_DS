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

def upload_csv():
  # csvがアップロードされたとき
  if st.session_state['upload_csvfile'] is not None:
      # アップロードされたファイルデータを読み込む
      file_data = st.session_state['upload_csvfile'].read()
      # バイナリデータからPandas DataFrameを作成
      try:
          df = pd.read_csv(io.BytesIO(file_data), encoding="utf-8", engine="python")
          st.session_state["ja"] = False
      except UnicodeDecodeError:
          # UTF-8で読み取れない場合はShift-JISエンコーディングで再試行
          df = pd.read_csv(io.BytesIO(file_data), encoding="shift-jis", engine="python")
          st.session_state["ja"] = True
          
      # カラムの型を自動で適切に変換
      df = df.infer_objects() 
      try:
          for column in df.columns:
              df[column] = df[column].astype(pd.Int64Dtype(), errors='ignore')
      except:
          pass

      df = df.applymap(lambda x: str(x) if not pd.isnull(x) else x)
      st.session_state["uploaded_df"] = df.copy()
      st.session_state["all_df"] = df.copy()
      create_data = decide_dtypes(df)
      st.session_state["all_df"] = st.session_state["all_df"].applymap(lambda x: str(x) if not pd.isnull(x) else x)
      
      
      st.session_state["filtered_columns"] = st.session_state["uploaded_df"].columns

      st.session_state["column_data"] = decide_dtypes(df)

  else:
      st.session_state["uploaded_df"] = pd.DataFrame()
      st.session_state["all_df"] = pd.DataFrame()
      st.session_state["column_data"] = dict()
      st.session_state["filtered_columns"] = list()

# タブ
spk.tab1.file_uploader("CSVファイルをアップロード", 
                  type=["csv"], 
                  key="upload_csvfile", 
                  on_change=upload_csv
                )

# st.write(show_df[st.session_state["filtered_columns"]])
        

