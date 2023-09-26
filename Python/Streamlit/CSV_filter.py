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

# 表示するデータフレーム
if 'main_df' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['main_df'] = df

st.title("CSV Filters")

# タブ
tab1, tab2, tab3 = st.sidebar.tabs(["Uploader", "Select_Values", "Downloader"])

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
        create_data = spk.decide_dtypes(df)
        st.session_state["all_df"] = st.session_state["all_df"].applymap(lambda x: str(x) if not pd.isnull(x) else x)
        
        
        st.session_state["filtered_columns"] = st.session_state["uploaded_df"].columns

        st.session_state["column_data"] = spk.decide_dtypes(df)

    else:
        st.session_state["uploaded_df"] = pd.DataFrame()
        st.session_state["all_df"] = pd.DataFrame()
        st.session_state["column_data"] = dict()
        st.session_state["filtered_columns"] = list()
        

def select_column():
    # 数値型のカラム以外の、指定したリストの管理
    if len(st.session_state["selected_columns"]) == 0:
        st.session_state["filtered_columns"] = st.session_state["uploaded_df"].columns
    else:
        st.session_state["filtered_columns"] = st.session_state["selected_columns"]

    create_data = spk.decide_dtypes(st.session_state["uploaded_df"][st.session_state["filtered_columns"]])

    st.session_state["column_data"] = create_data
    
# CSVファイルのアップロード
tab1.file_uploader("CSVファイルをアップロード", 
                  type=["csv"], 
                  key="upload_csvfile", 
                  on_change=upload_csv
                )

if st.session_state["upload_csvfile"] is not None:
    tab2.multiselect(label="表示したいカラムを選択してください", 
                         options=st.session_state["uploaded_df"].columns, 
                         key="selected_columns", 
                         on_change=select_column)
    tab2.header("")
    
    upload_name = st.session_state['upload_csvfile'].name
    download_name = upload_name.split(".")[0]
    tab3.write("ファイル名を入力してください")
    tab3.text_input(
        label="Press Enter to Apply",
        value=f"{download_name}_filtered",
        key="download_name"
    )
    
    df = st.session_state["all_df"][st.session_state["filtered_columns"]].copy()
    
    create_data = st.session_state["column_data"]
    all_widgets = spk.create_widgets(df, create_data)
    # st.write(create_data)
    show_df = spk.filter_df(df, all_widgets)
    
    for column in show_df[st.session_state["filtered_columns"]].columns:
        if create_data[column] == "datetime":
            st.session_state["all_df"][column] = pd.to_datetime(st.session_state["all_df"][column], errors="coerce")
            
    st.write(show_df[st.session_state["filtered_columns"]])
    
    # ダウンロードボタンを追加
    download_df = show_df[st.session_state["filtered_columns"]].copy()
    if st.session_state["ja"]:
        csv_file = download_df.to_csv(index=False, encoding="shift-jis")
    else:
        csv_file = download_df.to_csv(index=False, encoding="utf-8")
    tab3.download_button(
        label="Download CSV",
        data=csv_file,
        file_name=f'{st.session_state["download_name"]}.csv'
    ) 
        

