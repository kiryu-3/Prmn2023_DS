import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objs as go
import plotly.io as pio
import plotly
import matplotlib.pyplot as plt
import pandas as pd
import folium
from folium.plugins import Draw, TimestampedGeoJson
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import streamlit as st
from streamlit_folium import st_folium
import base64
import requests
from PIL import Image
import io
from io import BytesIO
import itertools

# # 画像URLを指定
# image_url = "https://imgur.com/C32lMvR.jpg"
#
# # 画像をダウンロードしPILのImageオブジェクトとして読み込む
# response = requests.get(image_url)
# image = Image.open(BytesIO(response.content))
#
# # Streamlit ページの設定
# st.set_page_config(
#     page_title="CIST-FASS",
#     page_icon=image,
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
#
# hide_menu_style = """
#     <style>
#     #MainMenu {visibility: hidden;}
#     </style>
# """
# st.markdown(hide_menu_style, unsafe_allow_html=True)

if "count" not in st.session_state:
    st.session_state['count'] = 0

if 'map2' not in st.session_state:
    lo = [39.949610, -75.150282]  # デフォルトの位置情報
    zoom_level = 10  # デフォルトのズームレベル
    st.session_state['center'] = {'lat': lo[0], 'lon': lo[1]}
    st.session_state['zoom_level'] = zoom_level
    st.session_state['map_initialized'] = True
    st.session_state['count'] += 1
    m = folium.Map()
    draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
    draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
    draw.add_to(m)

    st.session_state['map2'] = m

st.write(st.session_state['count'])
# 表示する地図
st_data = st_folium(st.session_state['map2'], width=800, height=800, zoom=st.session_state['zoom_level'],
                    center=st.session_state['center'])
st.write(st_data)
# lo = [39.949610, -75.150282]  # デフォルトの位置情報
# zoom_level = 10  # デフォルトのズームレベル
# st.session_state['center'] = {'lat': lo[0], 'lon': lo[1]}
# st.session_state['zoom_level'] = zoom_level
# st.session_state['map_initialized'] = True
# st.session_state['count'] = 0
# m = folium.Map(location=lo, zoom_start=zoom_level)
# draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
# draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
# draw.add_to(m)
#
# st.session_state['map2'] = m
#
# # 表示する地図
# st_data = st_folium(st.session_state['map2'], width=1200, height=800)
