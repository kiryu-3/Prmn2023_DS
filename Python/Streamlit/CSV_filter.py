import streamlit as st
import pandas as pd

import io
from io import BytesIO
import copy

# 読み込んだデータフレームを管理する
if 'data' not in st.session_state:  # 初期化
    st.session_state['data'] = dict()

# 読み込んだデータフレームを管理する
if 'df' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['df'] = df
    st.session_state['new_df'] = df
    st.session_state["download_df"] = df

# 読み込んだデータフレームを管理する
if 'unique_values' not in st.session_state:  # 初期化
    st.session_state['unique_values'] = dict()

# 読み込んだデータフレームを管理する
if 'select_loc_columns' not in st.session_state:  # 初期化
    st.session_state['select_loc_columns'] = list()

# 読み込んだデータフレームを管理する
if 'select_show_columns' not in st.session_state:  # 初期化
    st.session_state['select_show_columns'] = list()


st.header("CIST-CSV-Filtered-System")
if len(st.session_state['select_show_columns']) == 0:
    st.write(st.session_state['new_df'])
else:
    st.write(st.session_state['new_df'][st.session_state['select_show_columns']])
# st.write(st.session_state["select_loc_columns"])
# st.write(st.session_state['unique_values'])
# st.write(st.session_state['data'])

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4 = st.tabs(["Uploader", "Select_columns", "Select_Values", "Downloader"])

    # csvのuploaderの状態が変化したときに呼ばれるcallback関数
    def upload_csv():
        # csvがアップロードされたとき
        if st.session_state["upload_csvfile"] is not None:
            # アップロードされたファイルデータを読み込む
            file_data = st.session_state["upload_csvfile"].read()
            # バイナリデータからPandas DataFrameを作成
            st.session_state["df"] = pd.read_csv(io.BytesIO(file_data))
    
            st.session_state['new_df'] = st.session_state["df"].copy()
    
            st.session_state['download_df'] = st.session_state["df"].copy()
        else:
            df = pd.DataFrame()
            st.session_state['df'] = df
            st.session_state['new_df'] = df
            st.session_state["download_df"] = df
            st.session_state['unique_values'] = dict()
            st.session_state['data'] = dict()

    # csvのuploader
    with tab1:
        # CSVファイルのアップロード
        st.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)

    # csvのuploader
    with tab2:
        def select_loc_column():
            if len(st.session_state["select_loc_columns"]) == 0:
                st.session_state['new_df'] = st.session_state["df"].copy()
                if len(st.session_state["data"].items()) != 0:
                    st.session_state['unique_values'] = dict()
                    st.session_state['data'] = dict()
            else:
                # st.session_state['data'] = {
                #     key: value
                #     for key, value in st.session_state['data'].items()
                #     if key in st.session_state["select_loc_columns"]
                # }
                st.session_state['unique_values'] = dict()
                st.session_state['data'] = dict()

                # 選択されたカラムごとにユニークな値を取得
                for column in st.session_state["select_loc_columns"]:
                    st.session_state['data'][column] = st.session_state['new_df'][column].unique()
                    st.session_state['unique_values'][column] = st.session_state['df'][column].unique()

        if st.session_state["upload_csvfile"] is not None:
            # st.multiselectを呼び出し
            st.multiselect(
                "フィルタリングしたいカラムの値を選択してください",
                st.session_state["df"].columns,  # 上記で生成したリストを使用
                key="select_loc_columns",
                on_change=select_loc_column
            )

            # st.multiselectを呼び出し
            st.multiselect(
                "表示したいカラムの値を選択してください",
                st.session_state["df"].columns,  # 上記で生成したリストを使用
                key="select_show_columns",
            )
            

    with tab3:
        def select_values(selected_column):
            if len(st.session_state[f"{selected_column}_selected_values"]) == 0:
                # del st.session_state['unique_values'][selected_column]
                del st.session_state['data'][selected_column]
            else:
                st.session_state['data'][selected_column] = st.session_state[f"{selected_column}_selected_values"]

            # 条件式を格納するリストを初期化
            filtered_df = st.session_state['df'].copy()
            for column, values in st.session_state['data'].items():
                filtered_df = filtered_df[filtered_df[column].isin(values)]

            st.session_state['new_df'] = filtered_df.copy()


            # ユニークな値を表示するためのマルチセ
        # レクトを作成
        if len(st.session_state['unique_values'].items()) != 0:
            for selected_column, values in st.session_state['unique_values'].items():
                st.multiselect(
                    f"{selected_column} の値を選択してください",
                    values,
                    key=f"{selected_column}_selected_values",
                    on_change=select_values,
                    args=(selected_column,)
                )

    with tab4:
        def select_downloaded_value():
            if len(st.session_state['selected_download_values']) != 0:
                st.session_state['download_df'] = st.session_state['new_df'][st.session_state['selected_download_values']]

        st.multiselect(
            f"ダウンロードしたいカラムを選択してください",
            st.session_state['new_df'].columns,
            key=f"selected_download_values",
            on_change=select_downloaded_value,
        )

        csv_file = st.session_state['download_df'].to_csv(index=False)

        # ダウンロードボタンを追加
        st.download_button(label="Download CSV", data=csv_file, file_name='sorted.csv')

