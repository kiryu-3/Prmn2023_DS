import streamlit as st
from streamlit_folium import st_folium
import folium

# Streamlitアプリケーションの設定
st.set_page_config(page_title="Folium Map Info Example")

# セッション状態を初期化
if "map_info" not in st.session_state:
    st.session_state.map_info = {
        "zoom": 10,
        "latitude": 37.7749,
        "longitude": -122.4194
    }

# ユーザーが設定した情報を表示するセクション
st.sidebar.header("Map Information")

# ズームレベルを更新
new_zoom = st.sidebar.slider("Zoom Level", min_value=1, max_value=20, value=st.session_state.map_info["zoom"])
st.session_state.map_info["zoom"] = new_zoom

# 中心座標（緯度と経度）を更新
st.sidebar.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)
new_latitude = st.sidebar.number_input("Latitude", value=st.session_state.map_info["latitude"])
new_longitude = st.sidebar.number_input("Longitude", value=st.session_state.map_info["longitude"])
st.session_state.map_info["latitude"] = new_latitude
st.session_state.map_info["longitude"] = new_longitude

# Folium Mapオブジェクトを作成
m = folium.Map(location=[st.session_state.map_info["latitude"], st.session_state.map_info["longitude"]],
               zoom_start=st.session_state.map_info["zoom"])

# StreamlitコンポーネントにFolium Mapオブジェクトを埋め込む
data = st_folium(m)

st.write(data)
