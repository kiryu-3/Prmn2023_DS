import streamlit as st
import folium
from streamlit_folium import folium_static
import copy

# 初期の中心座標を設定
initial_center = {"lat": 35.6895, "lng": 139.6917}
if "center" not in st.session_state:
    st.session_state.center = initial_center

# 地図を作成
if not hasattr(st.session_state, "draw_added"):
    draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
    draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
    st.session_state.map = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=16)
    draw.add_to(st.session_state.map)
    st.session_state.draw_added = True
else:
    st.session_state.map = folium.Map(location=[st.session_state.center["lat"], st.session_state.center["lng"]], zoom_start=16)

# 地図をStreamlitコンポーネントに追加
st_data = folium_static(st.session_state.map, width=725)

# 地図の中心座標を保存
data = copy.deepcopy(dict(st_data))
st.session_state.center["lat"] = data["center"]["lat"]
st.session_state.center["lng"] = data["center"]["lng"]
