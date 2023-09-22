import numpy as np
import pandas as pd
import streamlit as st
# import streamlit_pandas as sp
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
# 表示するカラム
# if 'selected_columns' not in st.session_state:  # 初期化
    # st.session_state["selected_columns"] = list()
# # セレクトボックスの状態
# if 'selected_item' not in st.session_state:  # 初期化
#     st.session_state["selected_item"] = "CSV Uploader"
# # CSVの状態
# if 'upload_csvfile' not in st.session_state:  # 初期化
#     st.session_state["upload_csvfile"] = None

st.title("CSV Filters")

# タブ
tab1, tab2, tab3, tab4 = st.sidebar.tabs(["Uploader", "Select_columns", "Select_Values", "Downloader"])

def filter_string(df, column, selected_list):
    final = []
    df = df[df[column].notna()]
    for idx, row in df.iterrows():
        if row[column] in selected_list:
            final.append(row)
    res = pd.DataFrame(final)
    return res

def number_widget(df, column, ss_name):
    df = df[df[column].notna()]
    # カラムを数値型に変換
    num_df = pd.DataFrame()
    # カラムをfloat型に変換
    df[f'{column}_number'] = pd.to_numeric(df[column], errors='coerce', downcast='float')
    max = float(df[f'{column}_number'].max())
    min = float(df[f'{column}_number'].min())
    temp_input = tab2.slider(f"{column.title()}", min, max, (min, max), key=f"{ss_name}_numeric")
    all_widgets.append((f"{ss_name}_numeric", "number", f"{column}_numeric"))
    return df

def datetime_widget(df, column, ss_name):
    df = df[df[column].notna()]
    # カラムを日付型に変換
    df[f'{column}_datetime'] = pd.to_datetime(df[column], errors='coerce')
    start_date = df[f'{column}_datetime'].min()
    end_date = df[f'{column}_datetime'].max()
    start_date = start_date.to_pydatetime()
    end_date = end_date.to_pydatetime()

    # ユニークな日付を取り出す
    unique_dates = df[f'{column}_datetime'].unique()
    
    # ユニークな日付をソート
    unique_dates = sorted(unique_dates)
    
    # 隣接する日付の差を計算（秒単位）
    date_diffs_seconds = [(unique_dates[i + 1] - unique_dates[i]) / np.timedelta64(1, 's') for i in range(len(unique_dates) - 1)]
    
    # 最小間隔を計算（秒単位）
    min_date_diff = min(date_diffs_seconds)

    # 関数を定義
    def format_time_interval(seconds):
        # 秒、分、時間、日、年の単位を定義
        intervals = [('year', 365*24*60*60), ('month', 6*24*60*60), ('day', 24*60*60), ('hour', 60*60), ('minute', 60), ('second', 1)]
    
        # 最小間隔とそれに対応する単位を計算
        for unit, seconds_in_unit in intervals:
            interval = seconds / seconds_in_unit
            if interval >= 1:
                interval = round(interval)
                return unit if interval > 1 else unit  # 単位名の調整

    if format_time_interval(min_date_diff) == "year":
      temp_input = tab3.slider(
          "日付範囲を選択してください",
          min_value=start_date,
          max_value=end_date,
          value=(start_date, end_date),
          step=timedelta(days=365),
          key=f"{ss_name}_datetime"
          )
    elif format_time_interval(min_date_diff) == "month":
      temp_input = tab3.slider(
        "日付範囲を選択してください",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(days=30),
        key=f"{ss_name}_datetime"
        )
    elif format_time_interval(min_date_diff) == "day":
      temp_input = tab3.slider(
        "日付範囲を選択してください",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(days=1),
        key=f"{ss_name}_datetime"
        )
    elif format_time_interval(min_date_diff) == "hour":
      temp_input = tab3.slider(
        "日付範囲を選択してください",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(hours=1),
        key=f"{ss_name}_datetime"
        )    
    elif format_time_interval(min_date_diff) == "minute":
      temp_input = tab3.slider(
        "日付範囲を選択してください",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(minutes=1),
        key=f"{ss_name}_datetime"
        )
    elif format_time_interval(min_date_diff) == "second":
      temp_input = tab3.slider(
        f"{column.title()}",
        min_value=start_date,
        max_value=end_date,
        value=(start_date, end_date),
        step=timedelta(seconds=1),
        key=f"{ss_name}_datetime"
        )
        
    all_widgets.append((f"{ss_name}_datetime", "datetime", f"{column}_datetime"))
    return df    

def text_widget(df, column, ss_name):
    df = df[df[column].notna()]
    options = df[column].unique()
    options.sort()
    temp_input = tab3.multiselect(f"{column.title()}", options, key=ss_name)
    all_widgets.append((ss_name, "text", column))
  

def create_widgets(df, create_data={}):
  global all_widgets
  all_widgets = []
  for ctype, column in zip(df.dtypes, df.columns):
      if column in create_data:
          if create_data[column] == "number":
              text_widget(df, column, column.lower())
              df = number_widget(df, column, column.lower())
          elif create_data[column] == "datetime":
              text_widget(df, column, column.lower())
              df = datetime_widget(df, column, column.lower())              
          elif create_data[column] == "object":
              text_widget(df, column, column.lower())
  return df, all_widgets

# def numeric_column(df):
    # numeric_names = list() 
    # for column_name in df.columns:
        # カラム内のすべての値が欠損値もしくは数値、または数値に変換可能な場合
        # if df[column_name].dropna().apply(lambda x: isinstance(x, (int, float)) or (str(x).replace(".", "", 1).isdigit())).all():
            # numeric_names.append(column_name)
            
    # st.session_state["numeric_columns"] = numeric_names
            # 新しい数値型カラムを作成
            # new_column_name_numeric = f"{column_name}_numeric"
            # df[new_column_name_numeric] = pd.to_numeric(df[column_name], errors="coerce")

def numeric_column(df, column_name):
    if df[column_name].dropna().apply(lambda x: isinstance(x, (int, float)) or (str(x).replace(".", "", 1).isdigit())).all():
        return True
    else:
        return False

def datetime_column(df, column_name):
    # カラム内のすべての値が日付型に変換可能な場合
    def is_date(x):
        try:
            pd.to_datetime(x)
            return True
        except (ValueError, TypeError):
            return False

    return df[column_name].dropna().apply(is_date).all()

    # if df[column_name].dropna().apply(is_date).all():
    #     return True
    # else:
    #     return False

def decide_dtypes(df):
    # 空の辞書を作成
    create_data = {}
    # データフレームの各列に対してデータ型をチェック
    for column_name in df.columns:
        if numeric_column(df, column_name):
            create_data[column_name] = "number"
            new_column_name_numeric = f"{column_name}_numeric"
            st.session_state["all_df"][new_column_name_numeric] = pd.to_numeric(st.session_state["all_df"][column_name], errors="coerce")
        elif datetime_column(df, column_name):
            create_data[column_name] = "datetime"
            new_column_name_datetime = f"{column_name}_datetime"
            st.session_state["all_df"][new_column_name_datetime] = pd.to_datetime(st.session_state["all_df"][column_name], errors="coerce")
        else:
            create_data[column_name] = "object"
    return create_data

def filter_df(df, all_widgets):
    """
    This function will take the input dataframe and all the widgets generated from
    Streamlit Pandas. It will then return a filtered DataFrame based on the changes
    to the input widgets.

    df => the original Pandas DataFrame
    all_widgets => the widgets created by the function create_widgets().
    """
    res = df
    for widget in all_widgets:
        ss_name, ctype, column = widget
        data = st.session_state[ss_name]
        try:
            if data:
                if ctype == "number":
                    min, max = data
                    res = res.loc[(res[column] >= min) & (res[column] <= max)]
                elif ctype == "datetime":
                    min, max = data
                    res = res.loc[(res[column] >= min) & (res[column] <= max)]
                elif ctype == "object":
                    res = filter_string(res, column, data)
        except Exception as e:
            st.error(e)
            st.error(all_widgets)
    return res

def upload_csv():
    # csvがアップロードされたとき
    if st.session_state['upload_csvfile'] is not None:
        # アップロードされたファイルデータを読み込む
        file_data = st.session_state['upload_csvfile'].read()
        # バイナリデータからPandas DataFrameを作成
        try:
            df = pd.read_csv(io.BytesIO(file_data), encoding="utf-8", engine="python")
        except UnicodeDecodeError:
            # UTF-8で読み取れない場合はShift-JISエンコーディングで再試行
            df = pd.read_csv(io.BytesIO(file_data), encoding="shift-jis", engine="python")
        # カラムの型を自動で適切に変換
        df = df.infer_objects()
        df = df.astype('object')
        st.session_state["uploaded_df"] = df.copy()
        st.session_state["all_df"] = df.copy()

        create_data = decide_dtypes(df)
        # df = df.astype('object')

        # for column in df.columns:
        #     if np.issubdtype(df[column].dtype, np.number):
        #         # 数値型の列は変換しない
        #         pass
        #     else:
        #         try:
        #             df[column] = pd.to_datetime(df[column])
        #         except:
        #             pass

       
        # # 各カラムのデータ型をチェックして日付型以外のカラムをオブジェクト型に変換
        # for column_name, dtype in df.dtypes.items():
        #     if dtype != 'datetime64[ns]':
        #         df[column_name] = df[column_name].astype('object')

        # for column_name, dtype in df.dtypes.items():
        #     if dtype != 'datetime64[ns]':
        #         df[column_name] = df[column_name].astype('object')

        # # 空の辞書を作成
        # create_data = {}
        # # データフレームの各列に対してデータ型をチェック
        # for column_name, dtype in df.dtypes.items():
        #     create_data[column_name] = "multiselect"

        
        # st.session_state["download_df"] = df.copy()
        # st.session_state["notnum_df"] = df.copy()
        st.session_state["column_data"] = decide_dtypes(df)
        st.session_state["filtered_columns"] = df.columns
        # numeric_column(st.session_state["uploaded_df"])

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

    # # 空の辞書を作成
    # create_data = {}
    # # データフレームの各列に対してデータ型をチェック
    # for column_name, dtype in st.session_state["uploaded_df"][st.session_state["filtered_columns"]].dtypes.items():
    #     create_data[column_name] = "multiselect"
    create_data = decide_dtypes(df[st.session_state["filtered_columns"]])

    st.session_state["column_data"] = create_data
    # numeric_column(st.session_state["uploaded_df"][st.session_state["filtered_columns"]])

# def select_numeric_column():
#     # カラム名が"_numeric"で終わるカラムを取り除く
#     st.session_state["all_df"] = st.session_state["all_df"].loc[:, ~st.session_state["all_df"].columns.str.endswith("_numeric")]
#     if len(st.session_state["selected_numeric_columns"]) != 0:
#         for column_name in st.session_state["selected_numeric_columns"]:
#             new_column_name_numeric = f"{column_name}_numeric"
#             st.session_state["all_df"][new_column_name_numeric] = pd.to_numeric(st.session_state["all_df"][column_name], errors="coerce")
    
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
    
    upload_name = st.session_state['upload_csvfile'].name
    download_name = upload_name.split(".")[0]
    tab4.write("ファイル名を入力してください")
    tab4.text_input(
        label="Press Enter to Apply",
        value=f"{download_name}_filtered",
        key="download_name"
    )
    
    df = st.session_state["all_df"][st.session_state["filtered_columns"]].copy()
    create_data = st.session_state["column_data"]
    df, all_widgets = create_widgets(df, create_data)
    show_df = filter_df(df, all_widgets)
    st.write(show_df[st.session_state["filtered_columns"]])
    
    # ダウンロードボタンを追加
    download_df = show_df.loc[:, ~show_df.columns.str.endswith("_numeric")]
    csv_file = download_df.to_csv(index=False)
    tab4.download_button(
        label="Download CSV",
        data=csv_file,
        file_name=f'{st.session_state["download_name"]}.csv'
    )    
        


# if st.session_state["upload_csvfile"] is not None:
    # col = st.columns(2)
    # col[0].multiselect(label="表示したいカラムを選択してください", 
    #               options=st.session_state["uploaded_df"].columns, 
    #               key="selected_columns", 
    #               on_change=select_column)

    # col[0].multiselect(label="数値型にしたいカラムを選択してください", 
    #               options=st.session_state["numeric_columns"], 
    #               key="selected_numeric_columns", 
    #               on_change=select_numeric_column)


    # upload_name = st.session_state['upload_csvfile'].name
    # download_name = upload_name.split(".")[0]
    # col[1].write("ファイル名を入力してください")
    # col[1].text_input(
    #     label="Press Enter to Apply",
    #     value=f"{download_name}_filtered",
    #     key="download_name"
    # )

    

# if st.session_state["upload_csvfile"] is not None:

        
