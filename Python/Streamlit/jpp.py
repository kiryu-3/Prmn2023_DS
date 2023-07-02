import io
from io import BytesIO
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature

import streamlit as st
import json
import folium
import pandas as pd
import copy
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

if 'map' not in st.session_state: # 初期化
    # 初めての表示時は空のマップを表示
    m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)
    # Leaflet.jsのDrawプラグインを追加
    draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
    draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
    draw.add_to(m)
    
    # Custom CSS style for the export button
    st.markdown("""
        <style>
        .leaflet-draw-actions {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 5px;
            border-radius: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.session_state['map'] = m
    
 
if 'df' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df'] = df
if 'df_new' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df_new'] = df
if 'draw_data' not in st.session_state: # 初期化
    st.session_state['draw_data'] = list() 
if 'gate_data' not in st.session_state: # 初期化
    st.session_state['gate_data'] = list()  
if 'kiseki_data' not in st.session_state: # 初期化
    st.session_state['kiseki_data'] = dict() 
if "line_geojson" not in st.session_state: # 初期化
    st.session_state['line_geojson'] = None
if "tuuka_list" not in st.session_state: # 初期化
    st.session_state['tuuka_list'] = list()


def upload_csv():
    if st.session_state["upload_csvfile"] is not None:
        file_data = st.session_state["upload_csvfile"].read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data))
        # 通過時間でソート
        df.sort_values(by=[df.columns[1]], inplace=True)
        # ユニークなIDを取得
        unique_values = df.iloc[:, 0].unique()
        # IDのデータフレーム
        df_new = pd.DataFrame(unique_values, columns=["newid"])
        # 1からスタート
        df_new.index = range(1, len(df_new) + 1)
        st.session_state['df'] = df
        st.session_state['df_new'] = df_new
        st.session_state['sorted_df'] = df
        # tab2.write(st.session_state['df'])

        # ユニークなIDのリスト
        list2 = list(unique_values)
        
        # 描画するプロットデータ
        features = []
        for i, row in df.iterrows():
            indexNum = list2.index(row.iloc[0])
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
                    "time": row.iloc[1],
                    "popup": f"{indexNum+1} - {row.iloc[0]}",
                    "ID": row.iloc[0]
                }
            }
            features.append(feature)

        # 描画する軌跡データ
        line_features = []
        for itr in list2:
            st.session_state['kiseki_data'][itr] = list()
        for itr in list2:
            list3 = []
            for i, row in df.iterrows():
                if itr == row[0]:
                    list3.append(row)
            df2 = pd.DataFrame(list3)
            for i in range(len(df2) - 1):
                line_feature = {
                     'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
                                        [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
                    },
                    'properties': {
                        'time': df2.iloc[i, 1]
                    }
                }
                line_features.append(line_feature)
                # 軌跡のデータを管理する
                st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], 
                                                             '日時': df2.iloc[i, 1]})
        # tab4.write(st.session_state['kiseki_data'])
        # 軌跡のデータをまとめる
        line_geojson = {'type': 'FeatureCollection', 'features': line_features}
        st.session_state["line_geojson"] = line_geojson
        
        # プロットのデータをまとめる
        geojson = {"type": "FeatureCollection", "features": features}
            
        # レイヤーを削除
        if 'map' in st.session_state:
            layers_to_remove = []
            for key, value in st.session_state['map']._children.items():
                if isinstance(value, TimestampedGeoJson):
                    layers_to_remove.append(key)
            for key in layers_to_remove:
                del st.session_state['map']._children[key]

        # TimestampedGeoJsonの作成
        timestamped_geojson = TimestampedGeoJson(
                geojson,
                period="PT1M",
                duration="PT1S",
                auto_play=False,
                loop=False
            )
    
        # TimestampedGeoJsonをマップに追加
        timestamped_geojson.add_to(st.session_state['map'])

    else:
        # 空のデータフレームを作成
        df = pd.DataFrame()
        st.session_state['df'] = df
        st.session_state['df_new'] = df
        st.session_state['sorted_df'] = df

        # TimestampedGeoJsonレイヤーを削除
        if 'map' in st.session_state:
            layers_to_remove = []
            for key, value in st.session_state['map']._children.items():
                if isinstance(value, TimestampedGeoJson):
                    layers_to_remove.append(key)
            for key in layers_to_remove:
                del st.session_state['map']._children[key]

        # 軌跡のデータを削除
        del st.session_state['kiseki_data']

def select_data():
    # プロット・軌跡を描画するデータの選択
    selected_values = st.session_state["select_data_id"]
    # 選択されていない場合はそのままのデータ
    if len(selected_values) == 0:
        st.session_state['sorted_df'] = st.session_state['df']

    # 選択された場合はデータをソート
    else:
        st.session_state['sorted_df'] = st.session_state['df'][st.session_state['df'].iloc[:, 0].isin(selected_values)]
        
        # 線のジオJSONを削除する
        line_layers_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson):
                line_layers_to_remove.append(key)
        for key in line_layers_to_remove:
            del st.session_state['map']._children[key]

        # ユニークなIDのリスト
        list2 = selected_values
        
        # 描画するプロットデータ
        features = []
        for i, row in st.session_state['sorted_df'].iterrows():
            indexNum = list2.index(row.iloc[0])
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
                    "time": row.iloc[1],
                    "popup": f"{indexNum+1} - {row.iloc[0]}",
                    "ID": row.iloc[0]
                }
            }
            features.append(feature)

        # 描画する軌跡データ
        line_features = []
        for itr in list2:
            st.session_state['kiseki_data'][itr] = list()
        for itr in list2:
            list3 = []
            for i, row in st.session_state['df'].iterrows():
                if itr == row[0]:
                    list3.append(row)
            df2 = pd.DataFrame(list3)
            for i in range(len(df2) - 1):
                line_feature = {
                     'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
                                        [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
                    },
                    'properties': {
                        'time': df2.iloc[i, 1]
                    }
                }
                line_features.append(line_feature)
                # 軌跡データはいじらない
                # st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], '日時': df2.iloc[i, 1]})

        # 軌跡のデータをまとめる
        line_geojson = {'type': 'FeatureCollection', 'features': line_features}
        st.session_state["line_geojson"] = line_geojson
        

        # プロットのデータをまとめる
        geojson = {"type": "FeatureCollection", "features": features}

        # TimestampedGeoJsonの作成
        timestamped_geojson = TimestampedGeoJson(
                geojson,
                period="PT1M",
                duration="PT1S",
                auto_play=False,
                loop=False
            )

        # TimestampedGeoJsonレイヤーを削除
        if 'map' in st.session_state:
            layers_to_remove = []
            for key, value in st.session_state['map']._children.items():
                if isinstance(value, TimestampedGeoJson):
                    layers_to_remove.append(key)
            for key in layers_to_remove:
                del st.session_state['map']._children[key]
    
        # TimestampedGeoJsonをマップに追加
        timestamped_geojson.add_to(st.session_state['map'])

        # 軌跡の追加
        if st.session_state['kiseki_flag']:
                # 線のジオJSONを追加
                folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                               style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
    

def kiseki_draw():
    if st.session_state['kiseki_flag']:
        # 線のジオJSONを追加
        folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                       style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
    else:
        # 線のジオJSONを削除する
        line_layers_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson):
                line_layers_to_remove.append(key)
        for key in line_layers_to_remove:
            del st.session_state['map']._children[key]

        # 
        list2 = list(st.session_state['new_df']['newid'])
        
        # 描画する軌跡データ
        line_features = []
        for itr in list2:
            st.session_state['kiseki_data'][itr] = list()
        for itr in list2:
            list3 = []
            for i, row in st.session_state['df'].iterrows():
                if itr == row[0]:
                    list3.append(row)
            df2 = pd.DataFrame(list3)
            for i in range(len(df2) - 1):
                line_feature = {
                     'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
                                        [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
                    },
                    'properties': {
                        'time': df2.iloc[i, 1]
                    }
                }
                line_features.append(line_feature)
                # 軌跡データはいじらない
                # st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], '日時': df2.iloc[i, 1]})

        # 軌跡のデータをまとめる
        line_geojson = {'type': 'FeatureCollection', 'features': line_features}
        st.session_state["line_geojson"] = line_geojson

        # 線のジオJSONを追加
        folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                       style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])

def select_shape():
    if st.session_state["select_shape_id"] != "":
        select_shape_id = int(st.session_state["select_shape_id"])
        # 表示対象の図形を特定
        selected_shape = st.session_state['gate_data'][select_shape_id - 1]
        if selected_shape[0][0] == selected_shape[0][-1]:
            st.write(f"ゲート{select_shape_id}(ライン)")
        else:
            st.write(f"ゲート{select_shape_id}(ポリゴン)")
        st.write(select_shape_id)
    
def delete_shape():
    if st.session_state["delete_shape_id"] != "":
        delete_shape_id = int(st.session_state["delete_shape_id"])
        # 削除対象の図形を特定
        delete_shape = st.session_state['draw_data'][delete_shape_id - 1]
        # 図形をマップから削除するためのキーを記録
        keys_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson) and value.data == delete_shape:
                keys_to_remove.append(key)
        # マップから図形を削除
        for key in keys_to_remove:
            del st.session_state['map']._children[key]
        # draw_dataから図形を削除
        st.session_state['draw_data'].remove(delete_shape)

def are_lines_intersecting(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    # 線分の方程式を計算
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1 * x1 + b1 * y1

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2 * x3 + b2 * y3

    # 交差判定
    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        # 2つの線分が平行である場合
        return False
    else:
        intersect_x = (b2 * c1 - b1 * c2) / determinant
        intersect_y = (a1 * c2 - a2 * c1) / determinant

        # 交差点が線分の範囲内にあるかどうかをチェック
        if min(x1, x2) <= intersect_x <= max(x1, x2) and min(x3, x4) <= intersect_x <= max(x3, x4) and \
                min(y1, y2) <= intersect_y <= max(y1, y2) and min(y3, y4) <= intersect_y <= max(y3, y4):
            return True
        else:
            return False
            
def ingate(plot_point, gate_polygon):
    # plot_point = [float(plot_point)]
    point = Feature(geometry=Point(plot_point))
    polygon = Polygon(
        [gate_polygon]
    )
    return boolean_point_in_polygon(point, polygon)


    
def kousa():
    found_intersection = False           
    
    # ゲートでループ
    for idx1 in range(len(st.session_state['gate_data'])):

       # 線分それぞれをチェック
       for idx2 in range(len(st.session_state['gate_data'][idx1][0])-1):   
           line1 = [(st.session_state['gate_data'][idx1][0][idx2][0], st.session_state['gate_data'][idx1][0][idx2][1]),
                    (st.session_state['gate_data'][idx1][0][idx2+1][0], st.session_state['gate_data'][idx1][0][idx2+1][1])]
           
           # IDでループ
           for key, values in st.session_state['kiseki_data'].items():
            
               # 初期座標がゲート内にあるかどうかチェック
               data_list = []
               for item in st.session_state['gate_data'][idx1][0][:len(st.session_state['gate_data'][idx1][0])]:
                   data_list.append(item)

               st.write(data_list)
               # ポリゴンゲートのときは初期座標をチェック
               if st.session_state['gate_data'][idx1][0][0] == st.session_state['gate_data'][idx1][0][-1]:
                   if ingate(values[0]["座標"][0], data_list):
                       found_intersection = True
                       st.session_state['tuuka_list'][idx1] += 1
                       continue  # このIDのループを終了
            
               # IDの軌跡ごとループ
               for value in values:
                   line2 = [(value["座標"][0][0], value["座標"][0][1]),
                            (value["座標"][1][0], value["座標"][1][1])]
                
                   if are_lines_intersecting(line1, line2):
                       # found_intersection = True
                       st.session_state['tuuka_list'][idx1] += 1
                       break  # このIDのループを終了

# call to render Folium map in eamlit
st_data = st_folium(st.session_state['map'], width=725)  

data = copy.deepcopy(dict(st_data))

try:
    if data["all_drawings"] is not None and isinstance(data["all_drawings"], list) and len(data["all_drawings"]) > 0:
        # GeoJSONデータをマップに追加する
        if data["last_circle_polygon"] is not None:
                data["all_drawings"][0]["geometry"]["type"] = "Polygon"
                data["all_drawings"][0]["geometry"]["coordinates"] = data["last_circle_polygon"]["coordinates"]
                center_list = data["last_active_drawing"]["geometry"]["coordinates"]
                center_dict = dict()
                center_dict["lat"] = center_list[0]
                center_dict["lng"] = center_list[1]
                data["all_drawings"][0]["properties"]["center"] = center_dict
        
        if len(st.session_state['draw_data']) != 0 and data["all_drawings"][0] not in st.session_state['draw_data']:
            # データの追加
            st.session_state['draw_data'].append(data["all_drawings"][0])
                
            # 通過人数カウントの準備
            append_list = list()
            for _ in range(len(st.session_state['draw_data'])):
                append_list.append(0)
            st.session_state['tuuka_list'] = append_list
            
            for idx, sdata in enumerate(st.session_state['draw_data']):
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                if len(st.session_state['df']) != 0:
                    kousa()
                    # st.session_state['count'] += 1
                    popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                    folium.GeoJson(sdata[0], tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                else:
                    folium.GeoJson(sdata[0], tooltip=tooltip_html).add_to(st.session_state['map'])
            
    else:
        pass
            
except Exception as e:
    # st.write(e)
    pass

st.subheader("地図の全描画データ")
st.write(data["all_drawings"])
st.write(st.session_state['draw_data'])

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4 = st.tabs(["Uploader", "Data_info", "Gate_info", "Kiseki_info"])
    
    with tab1:
        # CSVファイルのアップロード
        st.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)
        
    with tab2:    
        st.write(st.session_state['df'])
            
        if len(st.session_state['df']) != 0:
            # selected_values = st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",on_change=select_data)
            st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",on_change=select_data)
       
    with tab3:
        st.selectbox("削除したい図形のIDを選択してください",
                         [""] + [str(value) for value in range(1, len(st.session_state['draw_data']) + 1)],
                         key="delete_shape_id",
                         on_change=delete_shape)
        
    with tab4:
        st.checkbox(label='軌跡の表示', key='kiseki_flag', on_change=kiseki_draw)
