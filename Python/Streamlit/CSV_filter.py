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
tab1, tab2, tab3 = st.sidebar.tabs(["Uploader", "Select_Values", "Downloader"])

# def filter_string(df, column, selected_list):
#     final = []
#     try:
#         selected_list = [float(item) for item in selected_list]
#         selected_list = [str(item) for item in selected_list]
#     except:
#         pass
#     df = df[df[column].notna()]
#     for idx, row in df.iterrows():
#         if row[column] in selected_list:
#             final.append(row)
#     res = pd.DataFrame(final)
    
#     return res
def filter_string(df, column, selected_list):
    # # リスト内の各要素をfloat型に変換する関数
    # def convert_to_float(value):
    #     try:
    #         return str(float(value))
    #     except (ValueError, TypeError):
    #         return value
            
    # # map関数を使用してリスト内のすべての要素をfloat型に変換する
    # selected_list = list(map(convert_to_float, selected_list))
    # try:
    #     tab3.write(column)
    #     tab3.write(type(selected_list[0]))
    #     tab3.write(type(df[column].unique()[0]))
    # except:
    #     tab3.write(column)
        
    # 'hello'列の値がselected_list内の値に含まれている行を選択
    if len(selected_list) != 0:
        res = df[df[column].isin(selected_list)]
    else:
        res = df.copy()
    # if len(res) == 0:
    #     res = df.copy()
    return res

def is_integer(n):
      try:
          float(n)
      except ValueError:
          return False
      else:
          return float(n).is_integer()

def number_widget(df, column, ss_name):
    temp_df = pd.DataFrame()
    temp_df = df.dropna(subset=[column])

    

    if temp_df[column].apply(is_integer).sum() == len(temp_df[column]):
        df[f'{column}_numeric'] = pd.to_numeric(df[column], errors="coerce")
        # temp_df[f'{column}_numeric'] = temp_df[column].copy()
        # temp_df = temp_df.astype({f'{column}_numeric': float})
        temp_df[f'{column}_numeric'] = pd.to_numeric(temp_df[column], errors="coerce")
        max_value = int(max(temp_df[f'{column}_numeric'].unique()))
        min_value = int(min(temp_df[f'{column}_numeric'].unique()))
    else:
        df[f'{column}_numeric'] = pd.to_numeric(df[column], errors="coerce")
        # temp_df[f'{column}_numeric'] = temp_df[column].copy()
        # temp_df = temp_df.astype({f'{column}_numeric': float})
        temp_df[f'{column}_numeric'] = pd.to_numeric(temp_df[column], errors="coerce")
        max_value = float(temp_df[f'{column}_numeric'].max())
        min_value = float(temp_df[f'{column}_numeric'].min())
    
    if max!=min:
        temp_input = tab2.slider(f"{column.title()}", min_value, max_value, (min_value, max_value), key=f"{ss_name}_numeric")
    all_widgets.append((f"{ss_name}_numeric", "number", f"{column}_numeric"))
    return df

def datetime_widget(df, column, ss_name):
    temp_df = pd.DataFrame()
    if df[column].isna().any():
        temp_df = df.dropna(subset=[column])
    else:
        temp_df = df.copy()
    # カラムを日付型に変換
    
    df[f'{column}_datetime'] = pd.to_datetime(df[column], errors='coerce')
    # temp_df[f'{column}_datetime'] = temp_df[column].copy()
    # temp_df = temp_df.astype({f'{column}_datetime': datetime})
    temp_df[f'{column}_datetime'] = pd.to_datetime(temp_df[column], errors="coerce")
    start_date = df[f'{column}_datetime'].min()
    end_date = df[f'{column}_datetime'].max()
    first_date = start_date.to_pydatetime()
    last_date = end_date.to_pydatetime()

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

    # 日付表示方法を定義する関数
    def format_time_show(date, max_diff):
        # 秒、分、時間、日、年の表示方法を定義
        shows = [('year', ""), ('month', f" - {start_date.year}年"), ('day', f" - {start_date.year}年{start_date.month}月"), 
                 ('hour', f" - {start_date.year}年{start_date.month}月{start_date.day}日"), ('minute', f" - {start_date.year}年{start_date.month}月{start_date.day}日"), ('second', f" - {start_date.year}年{start_date.month}月{start_date.day}日")]

        # 最小間隔とそれに対応する単位を計算
        for unit, show_unit in shows:
            if format_time_interval(max_diff) == unit:
                return show_unit

    # 関数を定義
    def format_time_range(max_diff, min_diff):
        max_unit = format_time_interval(max_diff)
        min_unit = format_time_interval(min_diff)
        # 秒、分、時間、日、年の単位を定義
        units = [('year', 'year', 'YYYY'), ('year', 'month', 'YYYY-MM'), ('year', 'day', 'YYYY-MM-DD'), ('year', 'hour', 'YYYY-MM-DD HH'), ('year', 'minute', 'YYYY-MM-DD HH:mm'), ('year', 'second', 'YYYY-MM-DD HH:mm:ss'),
                     ('month', 'month', 'MM'), ('month', 'day', 'MM-DD'), ('month', 'hour', 'MM-DD HH'), ('month', 'minute', 'MM-DD HH:mm'), ('month', 'second', 'YYYY-MM-DD HH:mm:ss'),
                     ('day', 'day', 'DD'), ('day', 'hour', 'DD HH'), ('day', 'minute', 'DD HH:mm'), ('day', 'second', 'DD HH:mm:ss'),
                     ('hour', 'hour', 'HH'), ('hour', 'minute', 'HH:mm'), ('hour', 'second', 'HH:mm:ss'),
                     ('minute', 'minute', 'HH:mm'), ('minute', 'second', 'HH:mm:ss'), ('second', 'second', 'HH:mm:ss')]
    
        # 最小間隔とそれに対応する単位を計算
        for unit1, unit2, unit in units:
            if unit1 == max_unit and unit2 == min_unit:
                return unit  # 単位名の調整

    # ユニークな日付を取り出す
    unique_dates = temp_df[f'{column}_datetime'].unique()
    
    # ユニークな日付をソート
    unique_dates = sorted(unique_dates)
    
    # 隣接する日付の差を計算（秒単位）
    date_diffs_seconds = [(unique_dates[i + 1] - unique_dates[i]) / np.timedelta64(1, 's') for i in range(len(unique_dates) - 1)]
    
    # 最小間隔を計算（秒単位）
    min_date_diff = min(date_diffs_seconds)
    
    # 最初と最後の日付の差を計算（秒単位）            
    max_date_diff = (end_date - start_date) / np.timedelta64(1, 's')
    
    # 日付情報を表示するための変数を用意
    show_date = format_time_show(start_date, max_date_diff) 
    range_unit = format_time_range(max_date_diff, min_date_diff)
    
    if format_time_interval(min_date_diff) == "year" and end_date!=start_date:
      temp_input = tab2.slider(
          f"{column.title()}{show_date}",
          min_value=first_date,
          max_value=last_date,
          value=(first_date, last_date),
          step=timedelta(days=365),
          key=f"{ss_name}_datetime",
          format=range_unit
          )
    elif format_time_interval(min_date_diff) == "month" and end_date!=start_date:
      temp_input = tab2.slider(
        f"{column.title()}{show_date}",
        min_value=first_date,
        max_value=last_date,
        value=(first_date, last_date),
        step=timedelta(days=30),
        key=f"{ss_name}_datetime",
        format=range_unit
        )
    elif format_time_interval(min_date_diff) == "day" and end_date!=start_date:
      temp_input = tab2.slider(
        f"{column.title()}{show_date}",
        min_value=first_date,
        max_value=last_date,
        value=(first_date, last_date),
        step=timedelta(days=1),
        key=f"{ss_name}_datetime",
        format=range_unit
        )
    elif format_time_interval(min_date_diff) == "hour" and end_date!=start_date:
      temp_input = tab2.slider(
        f"{column.title()}{show_date}",
        min_value=first_date,
        max_value=last_date,
        value=(first_date, last_date),
        step=timedelta(hours=1),
        key=f"{ss_name}_datetime",
        format=range_unit
        )    
    elif format_time_interval(min_date_diff) == "minute" and end_date!=start_date:
      temp_input = tab2.slider(
        f"{column.title()}{show_date}",
        min_value=first_date,
        max_value=last_date,
        value=(first_date, last_date),
        step=timedelta(minutes=1),
        key=f"{ss_name}_datetime",
        format=range_unit
        )
    elif format_time_interval(min_date_diff) == "second" and end_date!=start_date:
      temp_input = tab2.slider(
        f"{column.title()}{show_date}",
        min_value=first_date,
        max_value=last_date,
        value=(first_date, last_date),
        step=timedelta(seconds=1),
        key=f"{ss_name}_datetime",
        format=range_unit
        )

    all_widgets.append((f"{ss_name}_datetime", "datetime", f"{column}_datetime"))
    return df    

def text_widget(df, column, ss_name):
    temp_df = df.dropna(subset=[column])
    temp_df = temp_df.astype(str)
    options = temp_df[column].unique().tolist()
    # st.write(options[:10])
    if temp_df[column].apply(is_integer).sum() == len(temp_df[column]):
        options = [int(float(value)) for value in options]
        options = [str(value) for value in options]
    # if all(value.isdigit() for value in options):
    #     options = [int(value) for value in options]
    #     options = [str(value) for value in options]
    # if temp_df[column].apply(is_integer).sum() == len(temp_df[column]):
    #     temp_df[column] = temp_df[column].astype(int) 
    #     temp_df[column] = temp_df[column].astype("object") 
    # else:
    #     temp_df[column] = temp_df[column].astype("object") 
    
    # options = list(temp_df[column].unique())
    # if nan:
    #     options.append("NaN")
    options.sort()
    temp_input = tab2.multiselect(f"{column.title()}", options, key=ss_name)
    all_widgets.append((ss_name, "text", column))
  

def create_widgets(df, create_data={}):
  global all_widgets
  all_widgets = []
  for ctype, column in zip(df.dtypes, df.columns):
      if column in create_data:
          if create_data[column] == "number":
              
              text_widget(df, column, column.lower())
              number_widget(df, column, column.lower())
          elif create_data[column] == "datetime":
              text_widget(df, column, column.lower())
              datetime_widget(df, column, column.lower())              
          elif create_data[column] == "text":
              text_widget(df, column, column.lower())
  return all_widgets

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
    for value in df[column_name]:
        try:
            # 文字列を数値型に変換を試みる
            float_value = float(value)
        except :
            # ValueErrorが発生した場合は変換できない
            return False
    return True

# def (df, column_name):
#     # カラム内のすべての値が日付型に変換可能な場合
#     def is_date(x):
#         try:
#             pd.to_datetime(x)
#             return True
#         except (ValueError, TypeError):
#             return False

#     return df[column_name].dropna().apply(is_date).all()

def datetime_column(df, column_name):
    for value in df[column_name]:
        try:
            # 文字列を日付型に変換を試みる
            pd.to_datetime(value)
        except (ValueError, pd.errors.OutOfBoundsDatetime):
            # ValueErrorやOutOfBoundsDatetimeが発生した場合は変換できない
            return False
    return True

def decide_dtypes(df):
    df = df.dropna()
    # 空の辞書を作成
    create_data = {}
    # データフレームの各列に対してデータ型をチェック
    for column_name in df.columns:
        if numeric_column(df, column_name):
            create_data[column_name] = "number"
            new_column_name_number = f"{column_name}_number2"
            st.session_state["all_df"][new_column_name_number] = pd.to_numeric(st.session_state["all_df"][column_name], errors="coerce")
        elif datetime_column(df, column_name):
            create_data[column_name] = "datetime"
            new_column_name_datetime = f"{column_name}_datetime2"
            st.session_state["all_df"][new_column_name_datetime] = pd.to_datetime(st.session_state["all_df"][column_name], errors="coerce")
        else:
            create_data[column_name] = "text"
    return create_data

def filter_df(df, all_widgets):
    """
    This function will take the input dataframe and all the widgets generated from
    Streamlit Pandas. It will then return a filtered DataFrame based on the changes
    to the input widgets.

    df => the original Pandas DataFrame
    all_widgets => the widgets created by the function create_widgets().
    """
    res = df.copy()
    
    for widget in all_widgets:
        ss_name, ctype, column = widget
        tab3.write(st.session_state[ss_name])
        data = st.session_state[ss_name]
        if ctype == "number":
            min, max = data
            res = res.loc[(res[column] >= min) & (res[column] <= max)]
            # res[column] = res[column].astype('object')
        elif ctype == "datetime":
            min, max = data
            res = res.loc[(res[column] >= min) & (res[column] <= max)]
            # res[column] = res[column].astype('object')
        elif ctype == "text":
            res = filter_string(res, column, data)

    return res

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
        
        # for column_name in df.columns:
        #     # カラムがfloat型で、欠損値以外の値がすべて整数であるかを確認
        #     if df[column_name].dtype in [int, float] and df[column_name].isna().any():
        #         replacement_value = -334334
        #         df[column_name] = df[column_name].fillna(replacement_value)

        #     def is_integer(n):
        #       try:
        #           float(n)
        #       except ValueError:
        #           return False
        #       else:
        #           return float(n).is_integer()

        #     if df[column_name].apply(is_integer).sum() == len(df[column_name])
        
        # 
        df = df.applymap(lambda x: str(x) if not pd.isnull(x) else x)
        st.session_state["uploaded_df"] = df.copy()
        st.session_state["all_df"] = df.copy()
        create_data = decide_dtypes(df)
        st.session_state["all_df"] = st.session_state["all_df"].applymap(lambda x: str(x) if not pd.isnull(x) else x)
        
        
        st.session_state["filtered_columns"] = st.session_state["uploaded_df"].columns
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

        
        # st.session_state["download_df"] = df
        # st.session_state["notnum_df"] = df
        st.session_state["column_data"] = decide_dtypes(df)
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
    create_data = decide_dtypes(st.session_state["uploaded_df"][st.session_state["filtered_columns"]])

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
    all_widgets = create_widgets(df, create_data)
    # st.write(create_data)
    show_df = filter_df(df, all_widgets)
    
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

        
