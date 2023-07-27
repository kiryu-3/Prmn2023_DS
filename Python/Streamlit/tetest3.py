import streamlit as st
import folium
from folium.plugins import Draw, TimestampedGeoJson
from streamlit_folium import st_folium

# 地図の初期ズームレベル
initial_zoom_level = 16

# 地図のズームレベルを記録するキー
zoom_level_key = 'map_zoom_level'

# 前回のセッションで設定されたズームレベルを取得する
previous_zoom_level = st.session_state.get(zoom_level_key, initial_zoom_level)

# 地図を表示する
if 'map' not in st.session_state:
    m = folium.Map(location=[42.793553, 141.6958724], zoom_start=previous_zoom_level)
    st.session_state['map'] = m
else:
    m = st.session_state['map']

# 地図の表示とズームレベルの更新
m = folium.Map(location=[42.793553, 141.6958724], zoom_start=previous_zoom_level)
# Leaflet.jsのDrawプラグインを追加
draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
draw.add_to(m)

# ユーザーが地図のズームレベルを変更した場合、新しいズームレベルを記録する
if 'zoom' in m.to_dict():
    st.session_state[zoom_level_key] = m.to_dict()['zoom']

# 地図を表示する
st_folium(m)
