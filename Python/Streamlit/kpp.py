import io
from io import BytesIO
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature 
import itertools 

import streamlit as st
import json
import folium
import pandas as pd
import copy
from streamlit_folium import st_folium
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

ccssvv = st.file_uploader("CSVファイルをアップロード", type=["csv"])

if ccssvv != None:
        # アップロードされたファイルデータを読み込む
        file_data = ccssvv.read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data))
        # 通過時間でソート
        df.sort_values(by=[df.columns[1]], inplace=True)
      
        # ユニークなIDを取得
        unique_values = df.iloc[:, 0].unique()

        st.write(unique_values)
