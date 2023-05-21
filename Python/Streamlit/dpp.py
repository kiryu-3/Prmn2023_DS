import io
import sys
import pandas as pd
import folium

import streamlit as st
import json
from folium import plugins
from streamlit_folium import folium_static
from folium.plugins import Draw, TimestampedGeoJson

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
"""

st.markdown(hide_menu_style, unsafe_allow_html=True)

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)

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
    
left, right = st.columns(2)


with left:
    with st.echo():    
        
        # st_data = folium_static(st.session_state['map'], width=st.session_state['width'], height=st.session_state['height'])
        st_data = folium_static(st.session_state['map'], width=725)
    with right:
        data = dict(st_data)
        st.subheader("地図の全データ")
        st.write(data)
