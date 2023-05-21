import io
import streamlit as st
import json
import folium
import pandas as pd

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

@st.cache(allow_output_mutation=True)
def initialize_map():
    m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)
    draw_options = {'polyline': True, 'rectangle': True, 'circle': False, 'marker': False, 'circlemarker': False}
    draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
    draw.add_to(m)
    return m

if 'df' not in st.session_state:
    df = pd.DataFrame()
    st.session_state['df'] = df

with st.sidebar:
    uploaded_csvfile = st.file_uploader("CSVファイルをアップロード", type=["csv"])
    st.write(st.session_state['df'])

if 'map' not in st.session_state:
    st.session_state['map'] = initialize_map()

if uploaded_csvfile is not None:
    file_data = uploaded_csvfile.read()
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

    layers_to_remove = []
    for key, value in st.session_state['map']._children.items():
        if isinstance(value, TimestampedGeoJson):
            layers_to_remove.append(key)
    for key in layers_to_remove:
        del st.session_state['map']._children[key]

    timestamped_geojson = TimestampedGeoJson(
        geojson,
        period="PT1M",
        duration="PT1S",
        auto_play=False,
        loop=False
    )

    timestamped_geojson.add_to(st.session_state['map'])
    st.session_state['df'] = df

left, right = st.columns(2)

with left:
    st_data = st_folium(st.session_state['map'], width=725)

with right:
    data = dict(st_data.copy())
    st.subheader("地図の全データ")
    st.write(st_data)
    st.subheader("地図の全描画データ")
    st.write(data["all_drawings"])

    try:
        if data["all_drawings"][0] is not None:
            for idx in range(len(data["all_drawings"])):
                data["all_drawings"][idx]["properties"] = str(idx)
                tooltip_html = '<div style="font-size: 16px;">gateid:{}</div>'.format(data["all_drawings"][idx]["properties"])
                folium.GeoJson(data["all_drawings"][idx], tooltip=tooltip_html).add_to(st.session_state['map'])

            data["all_drawings"][0]["properties"] = "0"
            st.subheader("抜粋データ")
            st.write(data["all_drawings"][0])
            st.write(len(data["all_drawings"]))
    except Exception as e:
        pass

    st.subheader("最後に描画した円の半径データ")
    st.write(data["last_circle_radius"])
    st.subheader("最後に描画した円の全データ")
    st.write(data["last_circle_polygon"])

    # import io
# import streamlit as st
# import json
# import folium
# import pandas as pd

# from streamlit_folium import st_folium
# from folium import plugins
# from folium.plugins import Draw, TimestampedGeoJson

# st.set_page_config(
#     page_title="streamlit-folium documentation",
#     page_icon=":world_map:️",
#     layout="wide",
# )

# hide_menu_style = """
#     <style>
#     #MainMenu {visibility: hidden;}
#     </style>
# """

# st.markdown(hide_menu_style, unsafe_allow_html=True)

# if 'df' not in st.session_state: # 初期化
#     df = pd.DataFrame()
#     st.session_state['df'] = df
    
# with st.sidebar:
  
#   # CSVファイルのアップロード
#   uploaded_csvfile = st.file_uploader("CSVファイルをアップロード", type=["csv"])
#   st.write(st.session_state['df'])


# if 'map' not in st.session_state: # 初期化
#     # 初めての表示時は空のマップを表示
#     m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)

#     # Leaflet.jsのDrawプラグインを追加
#     draw_options = {'polyline': True, 'rectangle': True, 'circle': False, 'marker': False, 'circlemarker': False}
#     draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
#     draw.add_to(m)
    
    
    
#     st.session_state['map'] = m
    
   

    
# if uploaded_csvfile is not None:
#     file_data = uploaded_csvfile.read()

#     # バイナリデータからPandas DataFrameを作成
#     df = pd.read_csv(io.BytesIO(file_data))

#     features = []
#     for i, row in df.iterrows():
#         feature = {
#             "type": "Feature",
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [row.iloc[3], row.iloc[2]]
#             },
#             "properties": {
#                 "icon": "circle",
#                 "iconstyle": {
#                     "color": "#4169e1",
#                     "fillColor": "#01bfff",
#                     "weight": 10,
#                     "radius": 3
#                 },
#                 "time": row.iloc[1]
#             }
#         }
#         features.append(feature)

#     geojson = {
#         "type": "LineString",
#         "features": features
#     }

#     # レイヤーを削除
#     if 'map' in st.session_state:
#         layers_to_remove = []
#         for key, value in st.session_state['map']._children.items():
#             if isinstance(value, TimestampedGeoJson):
#                 layers_to_remove.append(key)
#         for key in layers_to_remove:
#             del st.session_state['map']._children[key]


#     timestamped_geojson = TimestampedGeoJson(
#         geojson,
#         period="PT1M",
#         duration="PT1S",
#         auto_play=False,
#         loop=False
#     )

#     # TimestampedGeoJsonをマップに追加
#     timestamped_geojson.add_to(st.session_state['map'])
    
#     # DataFrameをサイドバーに表示
#     st.session_state['df'] = df

# left, right = st.columns(2)
    
# with left:

#     # call to render Folium map in Streamlit
#     st_data = st_folium(st.session_state['map'], width=725)     

# with right:
#     data = dict(st_data.copy())
#     st.subheader("地図の全データ")
#     st.write(st_data)
#     st.subheader("地図の全描画データ")
#     st.write(data["all_drawings"])
    
#     try:
#         if data["all_drawings"][0] is not None:
            
#             for idx in range(len(data["all_drawings"])):
#                     data["all_drawings"][idx]["properties"] = str(idx)
#                     tooltip_html = '<div style="font-size: 16px;">gateid:{}</div>'.format(data["all_drawings"][idx]["properties"])
#                     # GeoJSONデータをマップに追加する
#                     folium.GeoJson(data["all_drawings"][idx], tooltip=tooltip_html).add_to(st.session_state['map'])
    
                             
#             data["all_drawings"][0]["properties"] = "0"
#             st.subheader("抜粋データ")
#             st.write(data["all_drawings"][0])
#             st.write(len(data["all_drawings"]))
#     except Exception as e:
#         pass
            
         
#     st.subheader("最後に描画した円の半径データ")
#     st.write(data["last_circle_radius"])
#     st.subheader("最後に描画した円の全データ")
#     st.write(data["last_circle_polygon"])
