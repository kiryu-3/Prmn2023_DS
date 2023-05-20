import io
import sys
import pandas as pd
import folium

from streamlit_folium import folium_static
import streamlit as st
import json
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson

css = """
<style>
#MainMenu {visibility: hidden;}
.github-corner {display: none;}
</style>
"""
st.markdown(css, unsafe_allow_html=True)



with st.sidebar:
  # GeoJSONファイルのアップロード
  uploaded_geojsonfile = st.file_uploader("GeoJSONファイルをアップロード", type=["geojson"])
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
    
# GeoJSONファイルがアップロードされた場合
if uploaded_geojsonfile is not None and not st.session_state['geojson_added']:
    # GeoJSONデータの読み込み
    geojson_data = json.load(uploaded_geojsonfile)

    # GeoJSONデータを表示
    folium.GeoJson(geojson_data).add_to(st.session_state['map'])

if uploaded_csvfile is not None:
    file_data = uploaded_csvfile.read()

    # バイナリデータからPandas DataFrameを作成
    df = pd.read_csv(io.BytesIO(file_data))

    features = []
    for i, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.iloc[3], row.iloc[2]]
            },
            "properties": {
                "icon": "circle",
                "iconstyle": {
                    "color": "#4169e1",
                    "fillColor": "#01bfff",
                    "weight": 10,
                    "radius": 3
                },
                "time": row.iloc[1]
            }
        }
        features.append(feature)

    geojson = {
        "type": "LineString",
        "features": features
    }

    # レイヤーを削除
    layers_to_remove = []
    for layer in st.session_state['map']._children.values():
        if isinstance(layer, TimestampedGeoJson):
            layers_to_remove.append(layer.get_name())

    for layer_name in layers_to_remove:
        del st.session_state['map']._children[layer_name]
       
    

    timestamped_geojson = TimestampedGeoJson(
        geojson,
        period="PT1M",
        duration="PT1S",
        auto_play=False,
        loop=False
    )

    # TimestampedGeoJsonをマップに追加
    timestamped_geojson.add_to(st.session_state['map'])

 # ボタンを表示し、クリックイベントを処理
if st.button("描画図形の削除"):
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
    
# ボタンを表示し、クリックイベントを処理
if st.button("GeoJSONデータの削除"):
    # GeoJSONデータを削除
    layers_to_remove = []
    for layer in st.session_state['map']._children.values():
        if isinstance(layer, folium.GeoJson):
            layers_to_remove.append(layer)

    for layer in layers_to_remove:
        del st.session_state['map']._children[layer.get_name()]
        
    st.session_state['geojson_added'] = True
    
# ボタンを表示し、クリックイベントを処理
if st.button("GeoJSONデータの復活"):
    st.session_state['geojson_added'] = False
    st.experimental_rerun()
    
# Streamlitでマップを表示
folium_static(st.session_state['map'], width=st.session_state['width'], height=st.session_state['height'])
