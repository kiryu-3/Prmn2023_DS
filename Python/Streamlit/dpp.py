import io
import sys
import pandas as pd
import folium

import streamlit as st
import json
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""

st.markdown(hide_menu_style, unsafe_allow_html=True)

with st.sidebar:
  # CSVファイルのアップロード
  uploaded_csvfile = st.file_uploader("CSVファイルをアップロード", type=["csv"])

  valuew = st.slider(
    label="Width: from 800 to 1000",
    min_value=800, 
    max_value=1000,
    key="width_slider"
  )
  st.session_state['width'] = valuew

  valueh = st.slider(
    label="Height: from 600 to 1000",
    min_value=600, 
    max_value=1000,
    key="height_slider"
  )
  st.session_state['height'] = valueh
  
if 'map' not in st.session_state: # 初期化
  # 初めての表示時は空のマップを表示
  m = folium.Map(location=[34.797345395117546, 137.5804696201213], zoom_start=13)

  # Leaflet.jsのDrawプラグインを追加
  draw_options = {'polyline': True, 'rectangle': True, 'circle': False, 'marker': False, 'circlemarker': False}
  draw = folium.plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=draw_options)
  draw.add_to(m)

  # 地図をフルスクリーンに切り替えボタン設置
  plugins.Fullscreen(
    position="topright",  # bottomleft 
    title="拡大する",      
    title_cancel="元に戻す",
    force_separate_button=True,
  ).add_to(m)

  st.session_state['map'] = m

if 'geojson_added' not in st.session_state:
    st.session_state['geojson_added'] = False
    
if uploaded_csvfile is not None:
    file_data = uploaded_csvfile.read()

    # バイナリデータからPandas DataFrameを作成
    df = pd.read_csv(io.BytesIO(file_data))

    features = []
    for i, row in df.iterrows():
        feature = {
