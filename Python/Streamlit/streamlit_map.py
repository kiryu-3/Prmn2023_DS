import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objs as go 
import plotly.io as pio
import plotly 
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import folium
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import skmob
from skmob import TrajDataFrame 
import streamlit as st
from streamlit_folium import st_folium
import base64
import requests
from PIL import Image
import io
from io import BytesIO
import itertools
# import copy

# 画像URLを指定
image_url = "https://imgur.com/okIhGTb.jpg"

# 画像をダウンロードしPILのImageオブジェクトとして読み込む
response = requests.get(image_url)
image = Image.open(BytesIO(response.content))

# Streamlit ページの設定
st.set_page_config(
    page_title="cist-mobmap",
    page_icon=image,
    layout="wide",
    initial_sidebar_state="expanded"
)

# st.set_page_config(
#     page_title="cist-mobmap",
#     page_icon=":world_map:️",
#     layout="wide",
# )
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

if 'map' not in st.session_state:  # 初期化
    # 初めての表示時は空のマップを表示
    # m = folium.Map(location=[42.793553, 141.6958724])
    m = folium.Map()
    # Leaflet.jsのDrawプラグインを追加
    draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
    draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
    draw.add_to(m)

    st.session_state['map'] = m

if 'data' not in st.session_state:  # 初期化
    st.session_state["data"] = dict()
    change_dict = dict()
    change_dict["lat"] = 42.79355312
    change_dict["lng"] = 141.695872412
    st.session_state["center"] = change_dict
    st.session_state["zoom"] = 16

# def change_mapinfo():
#     change_dict = dict()
#     try:
#         change_dict["lat"] = st.session_state["data"]["center"]["lat"]
#         change_dict["lng"] = st.session_state["data"]["center"]["lng"]
#         st.session_state["center"] = change_dict
#         st.session_state['zoom_level'] = st.session_state["data"]["zoom"]
#     except:
#         pass

# 表示する地図
# st_data = st_folium(st.session_state['map'], width=800, height=800, zoom=st.session_state["zoom"], center=st.session_state["center"])

# 地図のデータをコピー
# st.session_state["data"] = st_data
# # st.session_state["data"] = copy.deepcopy(dict(st_data))

st.subheader("全体データ")
st.write(st.session_state["data"])
st.subheader("最後にクリックした座標")
st.write(st.session_state["zoom"])
st.subheader("地図のズームレベル")
st.write(st.session_state["zoom"])
st.subheader("地図の中心座標")
st.write(st.session_state["center"])
