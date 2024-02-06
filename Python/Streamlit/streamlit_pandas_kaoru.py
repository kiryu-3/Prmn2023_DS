import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

import re
import requests
from PIL import Image
import io
from io import BytesIO

# 表示するデータフレーム
if 'main_df' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['main_df'] = df


# タブ
# tab1, tab2, tab3 = st.sidebar.tabs(["Uploader", "Select_Values", "Downloader"])

def filter_string(df, column, selected_list):
    if len(selected_list) != 0:
        res = df[df[column].isin(selected_list)]
    else:
        res = df.copy()
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
        try:
            max_value = int(max(temp_df[f'{column}_numeric'].unique()))
            min_value = int(min(temp_df[f'{column}_numeric'].unique()))
        except:
            pass
    else:
        df[f'{column}_numeric'] = pd.to_numeric(df[column], errors="coerce")
        # temp_df[f'{column}_numeric'] = temp_df[column].copy()
        # temp_df = temp_df.astype({f'{column}_numeric': float})
        temp_df[f'{column}_numeric'] = pd.to_numeric(temp_df[column], errors="coerce")
        try:
            max_value = float(max(temp_df[f'{column}_numeric'].unique()))
            min_value = float(min(temp_df[f'{column}_numeric'].unique()))
        except:
            pass

    try:
        if max_value!=min_value:
            temp_input = st.sidebar.slider(f"{column.title()}", min_value, max_value, (min_value, max_value),
                                           key=f"{ss_name}_numeric")
            all_widgets.append((f"{ss_name}_numeric", "number", f"{column}_numeric"))
    except:
        pass

    return df


def datetime_widget(df, column, ss_name):
    temp_df = pd.DataFrame()
    if df[column].isna().any():
        temp_df = df.dropna(subset=[column])
    else:
        temp_df = df.copy()
    # カラムを日付型に変換

    df[f'{column}_datetime'] = pd.to_datetime(df[column], errors='coerce')
    temp_df[f'{column}_datetime'] = pd.to_datetime(temp_df[column], errors="coerce")
    start_date = df[f'{column}_datetime'].min()
    end_date = df[f'{column}_datetime'].max()
    first_date = start_date.to_pydatetime()
    last_date = end_date.to_pydatetime()

    # 関数を定義
    def format_time_interval(seconds):
        # 秒、分、時間、日、年の単位を定義
        intervals = [('year', 365 * 24 * 60 * 60), ('month', 6 * 24 * 60 * 60), ('day', 24 * 60 * 60),
                     ('hour', 60 * 60), ('minute', 60), ('second', 1)]

        # 最小間隔とそれに対応する単位を計算
        for unit, seconds_in_unit in intervals:
            interval = seconds / seconds_in_unit
            if interval >= 1:
                interval = round(interval)
                return unit if interval > 1 else unit  # 単位名の調整

    # 日付表示方法を定義する関数
    def format_time_show(date, max_diff):
        # 秒、分、時間、日、年の表示方法を定義
        shows = [('year', ""), ('month', f" - {start_date.year}年"),
                 ('day', f" - {start_date.year}年{start_date.month}月"),
                 ('hour', f" - {start_date.year}年{start_date.month}月{start_date.day}日"),
                 ('minute', f" - {start_date.year}年{start_date.month}月{start_date.day}日"),
                 ('second', f" - {start_date.year}年{start_date.month}月{start_date.day}日")]

        # 最小間隔とそれに対応する単位を計算
        for unit, show_unit in shows:
            if format_time_interval(max_diff) == unit:
                return show_unit

    # 関数を定義
    def format_time_range(max_diff, min_diff):
        max_unit = format_time_interval(max_diff)
        min_unit = format_time_interval(min_diff)
        # 秒、分、時間、日、年の単位を定義
        units = [('year', 'year', 'YYYY'), ('year', 'month', 'YYYY-MM'), ('year', 'day', 'YYYY-MM-DD'),
                 ('year', 'hour', 'YYYY-MM-DD HH'), ('year', 'minute', 'YYYY-MM-DD HH:mm'),
                 ('year', 'second', 'YYYY-MM-DD HH:mm:ss'),
                 ('month', 'month', 'MM'), ('month', 'day', 'MM-DD'), ('month', 'hour', 'MM-DD HH'),
                 ('month', 'minute', 'MM-DD HH:mm'), ('month', 'second', 'YYYY-MM-DD HH:mm:ss'),
                 ('day', 'day', 'DD'), ('day', 'hour', 'DD HH'), ('day', 'minute', 'DD HH:mm'),
                 ('day', 'second', 'DD HH:mm:ss'),
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
    date_diffs_seconds = [(unique_dates[i + 1] - unique_dates[i]) / np.timedelta64(1, 's') for i in
                          range(len(unique_dates) - 1)]

    # 最小間隔を計算（秒単位）
    min_date_diff = min(date_diffs_seconds)

    # 最初と最後の日付の差を計算（秒単位）
    max_date_diff = (end_date - start_date) / np.timedelta64(1, 's')

    # 日付情報を表示するための変数を用意
    show_date = format_time_show(start_date, max_date_diff)
    range_unit = format_time_range(max_date_diff, min_date_diff)

    if format_time_interval(min_date_diff) == "year" and end_date != start_date:
        temp_input = st.sidebar.slider(
            f"{column.title()}{show_date}",
            min_value=first_date,
            max_value=last_date,
            value=(first_date, last_date),
            step=timedelta(days=365),
            key=f"{ss_name}_datetime",
            format=range_unit
        )
    elif format_time_interval(min_date_diff) == "month" and end_date != start_date:
        temp_input = st.sidebar.slider(
            f"{column.title()}{show_date}",
            min_value=first_date,
            max_value=last_date,
            value=(first_date, last_date),
            step=timedelta(days=30),
            key=f"{ss_name}_datetime",
            format=range_unit
        )
    elif format_time_interval(min_date_diff) == "day" and end_date != start_date:
        temp_input = st.sidebar.slider(
            f"{column.title()}{show_date}",
            min_value=first_date,
            max_value=last_date,
            value=(first_date, last_date),
            step=timedelta(days=1),
            key=f"{ss_name}_datetime",
            format=range_unit
        )
    elif format_time_interval(min_date_diff) == "hour" and end_date != start_date:
        temp_input = st.sidebar.slider(
            f"{column.title()}{show_date}",
            min_value=first_date,
            max_value=last_date,
            value=(first_date, last_date),
            step=timedelta(hours=1),
            key=f"{ss_name}_datetime",
            format=range_unit
        )
    elif format_time_interval(min_date_diff) == "minute" and end_date != start_date:
        temp_input = st.sidebar.slider(
            f"{column.title()}{show_date}",
            min_value=first_date,
            max_value=last_date,
            value=(first_date, last_date),
            step=timedelta(minutes=1),
            key=f"{ss_name}_datetime",
            format=range_unit
        )
    elif format_time_interval(min_date_diff) == "second" and end_date != start_date:
        temp_input = st.sidebar.slider(
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
    
    # 欠損値を除外してソート
    options = sorted(temp_df[column].unique().tolist())

    # None（欠損値）をリストの最初に追加
    if df[column].isna().any():
        options.insert(0, np.nan)

       
    temp_input = st.sidebar.multiselect(f"{column.title()}", options=options, default=list(),  key=ss_name)
    all_widgets.append((ss_name, "text", column))
    # temp_df = df.dropna(subset=[column])
    # temp_df = temp_df.astype(str)
    # options = df[column].unique().tolist()
    # # options = temp_df[column].unique().tolist()

    
        
    # # st.write(options[:10])
    # # if temp_df[column].apply(is_integer).sum() == len(temp_df[column]):
    # #     options = [int(float(value)) for value in options]
    # #     options = [str(value) for value in options]
    
    # options.sort()
    # temp_input = st.sidebar.multiselect(f"{column.title()}", options, key=ss_name)
    # all_widgets.append((ss_name, "text", column))


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
        data = st.session_state[ss_name]
        if ctype == "number":
            min_value, max_value = data
            temp_df = df.dropna(subset=[column])
            if (float(max(temp_df[column].unique())) == max_value) & (float(min(temp_df[column].unique())) == min_value):
                pass
            else:
                res = res.loc[(res[column] >= min_value) & (res[column] <= max_value)]
            # res[column] = res[column].astype('object')
        elif ctype == "datetime":
            min_value, max_value = data
            temp_df = df.dropna(subset=[column])
            first_date = temp_df[column].min().to_pydatetime()
            last_date = temp_df[column].max().to_pydatetime()
            if (last_date == max_value) & (first_date == min_value):
                pass
            else:
                res = res.loc[(res[column] >= min_value) & (res[column] <= max_value)]
            # res[column] = res[column].astype('object')
        elif ctype == "text":
            res = filter_string(res, column, data)
    return res
