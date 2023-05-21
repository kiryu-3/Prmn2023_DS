import streamlit as st
import json
import folium

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

with st.sidebar:
  # CSVファイルのアップロード
  uploaded_csvfile = st.file_uploader("CSVファイルをアップロード", type=["csv"])

if 'map' not in st.session_state: # 初期化
    # 初めての表示時は空のマップを表示
    m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)

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
    
    st.write(df)

    
left, right = st.columns(2)


with left:

    # call to render Folium map in Streamlit
    st_data = st_folium(st.session_state['map'], width=725)     

with right:
    data = dict(st_data)
    st.subheader("地図の全データ")
    st.write(data)
    st.subheader("地図の全描画データ")
    st.write(data["all_drawings"])
    
#     st.write([data[i] for i in data["all_drawings"] if i == 0])
#     if "all_drawings" in data:
#         if data["all_drawings"][0] is not None:
#             data["all_drawings"][0]["properties"] = "0"
#             st.subheader("抜粋データ")
#             st.write(data["all_drawings"][0])
            
         
    st.subheader("最後に描画した円の半径データ")
    st.write(data["last_circle_radius"])
    st.subheader("最後に描画した円の全データ")
    st.write(data["last_circle_polygon"])
