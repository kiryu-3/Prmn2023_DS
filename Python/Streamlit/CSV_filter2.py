import pandas as pd
import streamlit as st
import streamlit_pandas as sp

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
# 表示するカラム
# if 'selected_columns' not in st.session_state:  # 初期化
    # st.session_state["selected_columns"] = list()
# # セレクトボックスの状態
# if 'selected_item' not in st.session_state:  # 初期化
#     st.session_state["selected_item"] = "CSV Uploader"
# # CSVの状態
# if 'upload_csvfile' not in st.session_state:  # 初期化
#     st.session_state["upload_csvfile"] = None

def numeric_column(df):
    numeric_names = list()
    for column_name in df.columns:
        # カラム内のすべての値が欠損値もしくは数値、または数値に変換可能な場合
        if df[column_name].dropna().apply(lambda x: isinstance(x, (int, float)) or (str(x).replace(".", "", 1).isdigit())).all():
            numeric_names.append(column_name)
            
    st.session_state["numeric_columns"] = numeric_names
            # 新しい数値型カラムを作成
            # new_column_name_numeric = f"{column_name}_numeric"
            # df[new_column_name_numeric] = pd.to_numeric(df[column_name], errors="coerce")

def upload_csv():
    # csvがアップロードされたとき
    if st.session_state['upload_csvfile'] is not None:
        # アップロードされたファイルデータを読み込む
        file_data = st.session_state['upload_csvfile'].read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data), encoding="utf-8", engine="python")
        # カラムの型を自動で適切に変換
        df = df.infer_objects()

       
        # 各カラムのデータ型をチェックして日付型以外のカラムをオブジェクト型に変換
        for column_name, dtype in df.dtypes.items():
            if dtype != 'datetime64[ns]':
                df[column_name] = df[column_name].astype('object')

        # 空の辞書を作成
        create_data = {}
        # データフレームの各列に対してデータ型をチェック
        for column_name, dtype in df.dtypes.items():
            create_data[column_name] = "multiselect"

        st.session_state["uploaded_df"] = df.copy()
        # st.session_state["download_df"] = df.copy()
        # st.session_state["notnum_df"] = df.copy()
        st.session_state["all_df"] = df.copy()
        st.session_state["column_data"] = create_data
        st.session_state["filtered_columns"] = df.columns
        numeric_column(st.session_state["uploaded_df"])

    else:
        st.session_state["uploaded_df"] = pd.DataFrame()
        # st.session_state["download_df"] = pd.DataFrame()
        # st.session_state["notnum_df"] = pd.DataFrame()
        st.session_state["all_df"] = pd.DataFrame()
        st.session_state["column_data"] = dict()
        st.session_state["filtered_columns"] = list()
        

def select_column():
    # 数値型のカラム以外の、指定したリストの管理
    if len(st.session_state["selected_columns"]) == 0:
        st.session_state["filtered_columns"] = st.session_state["uploaded_df"].columns
    else:
        st.session_state["filtered_columns"] = st.session_state["selected_columns"]


    # 空の辞書を作成
    create_data = {}
    # データフレームの各列に対してデータ型をチェック
    for column_name, dtype in st.session_state["uploaded_df"][st.session_state["filtered_columns"]].dtypes.items():
        create_data[column_name] = "multiselect"

    st.session_state["column_data"] = create_data
    numeric_column(st.session_state["uploaded_df"][st.session_state["filtered_columns"]])

def select_numeric_column():
    # カラム名が"_numeric"で終わるカラムを取り除く
    st.session_state["all_df"] = st.session_state["all_df"].loc[:, ~st.session_state["all_df"].columns.str.endswith("_numeric")]
    if len(st.session_state["selected_numeric_columns"]) != 0:
        for column_name in st.session_state["selected_numeric_columns"]:
            new_column_name_numeric = f"{column_name}_numeric"
            st.session_state["all_df"][new_column_name_numeric] = pd.to_numeric(st.session_state["all_df"][column_name], errors="coerce")


st.title("CSV Filters")
# CSVファイルのアップロード
st.file_uploader("CSVファイルをアップロード", 
                  type=["csv"], 
                  key="upload_csvfile", 
                  on_change=upload_csv
                )
if st.session_state["upload_csvfile"] is not None:
    col = st.columns(2)
    col[0].multiselect(label="表示したいカラムを選択してください", 
                  options=st.session_state["uploaded_df"].columns, 
                  key="selected_columns", 
                  on_change=select_column)

    col[0].multiselect(label="数値型にしたいカラムを選択してください", 
                  options=st.session_state["numeric_columns"], 
                  key="selected_numeric_columns", 
                  on_change=select_numeric_column)


    upload_name = st.session_state['upload_csvfile'].name
    download_name = upload_name.split(".")[0]
    col[1].write("ファイル名を入力してください")
    col[1].text_input(
        label="Press Enter to Apply",
        value=f"{download_name}_filtered",
        key="download_name"
    )

    

# if st.session_state["upload_csvfile"] is not None:
    df = st.session_state["all_df"].copy()
    create_data = st.session_state["column_data"]
    all_widgets = sp.create_widgets(df, create_data)
    show_df = sp.filter_df(df, all_widgets)
    st.write(show_df[st.session_state["filtered_columns"]])
    
    # ダウンロードボタンを追加
    show_df = show_df.loc[:, ~show_df.columns.str.endswith("_numeric")]
    csv_file = show_df.to_csv(index=False)
    # col[1].write(csv_file)
    col[1].download_button(
        label="Download CSV",
        data=csv_file,
        file_name=f'{st.session_state["download_name"]}.csv'
    )
        
