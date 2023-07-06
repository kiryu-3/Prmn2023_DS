import io
from io import BytesIO
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import itertools

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
if 'sorted_df' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['sorted_df'] = df
if 'df_new' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df_new'] = df
if 'draw_data' not in st.session_state: # 初期化
    st.session_state['draw_data'] = list() 
if 'gate_data' not in st.session_state: # 初期化
    st.session_state['gate_data'] = list()  
if 'kiseki_data' not in st.session_state: # 初期化
    st.session_state['kiseki_data'] = dict() 
if 'kiseki' not in st.session_state: # 初期化
    st.session_state['kiseki'] = False
if "line_geojson" not in st.session_state: # 初期化
    st.session_state['line_geojson'] = None
if "tuuka_list" not in st.session_state: # 初期化
    st.session_state['tuuka_list'] = list()
if "ingate_count" not in st.session_state: # 初期化
    st.session_state['ingate_count'] = 0   
if "non_ingate_count" not in st.session_state: # 初期化
    st.session_state['non_ingate_count'] = 0 
if "cross_judge_count" not in st.session_state: # 初期化
    st.session_state['cross_judge_count'] = 0   
if "non_cross_judge_count" not in st.session_state: # 初期化
    st.session_state['non_cross_judge_count'] = 0 
if "count" not in st.session_state: # 初期化
    st.session_state['count'] = 0
if "selected_shape" not in st.session_state: # 初期化
    st.session_state["selected_shape"] = list()
if "selected_shape_type" not in st.session_state: # 初期化
    st.session_state["selected_shape_type"] = ""
if "select_mode" not in st.session_state: # 初期化
    st.session_state["select_mode"] = False
if "sorted_index" not in st.session_state: # 初期化
    st.session_state["sorted_index"] = list()

def plot(df):
    # 描画するプロットデータ
    features = []
    for i, row in df.iterrows():
        indexNum = st.session_state['sorted_index'].index(str(row.iloc[0]))
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
    return features

def kiseki_maker(df):
    # 描画する軌跡データ
    line_features = []
    for itr in st.session_state['sorted_index']:
        st.session_state['kiseki_data'][str(itr)] = list()
    for itr in st.session_state['sorted_index']:
        list3 = []
        for i, row in df.iterrows():
            if itr == str(row[0]):
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
            if itr not in st.session_state['kiseki_data']:
                st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], 
                                                             '日時': df2.iloc[i, 1]})
                
    return line_features
    
def zukei_draw():
    gate_append_list = list()
    for idx, sdata in enumerate(st.session_state['draw_data']):
        if sdata["geometry"]["coordinates"][0][0] == sdata["geometry"]["coordinates"][0][-1]:
            gate_append_list.append(sdata["geometry"]["coordinates"][0])
        else:
            gate_append_list.append(sdata["geometry"]["coordinates"])
        tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
        if len(st.session_state['df_new']) != 0:
            kousa()
            st.session_state['count'] += 1
            popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
            folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
        else:
            folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])


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
        st.session_state['sorted_index'] = [str(value) for value in unique_values]
        features = plot(df)
        line_features = kiseki_maker(df)
        
        # # 描画するプロットデータ
        # features = []
        # for i, row in df.iterrows():
        #     indexNum = list2.index(str(row.iloc[0]))
        #     feature = {
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [row.iloc[3], row.iloc[2]]
        #         },
        #         "properties": {
        #             "icon": "circle",
        #             "iconstyle": {
        #                 "color": "#4169e1",
        #                 "fillColor": "#01bfff",
        #                 "weight": 10,
        #                 "radius": 3
        #             },
        #             "time": row.iloc[1],
        #             "popup": f"{indexNum+1} - {row.iloc[0]}",
        #             "ID": row.iloc[0]
        #         }
        #     }
        #     features.append(feature)

        # # 描画する軌跡データ
        # line_features = []
        # for itr in list2:
        #     st.session_state['kiseki_data'][str(itr)] = list()
        # for itr in list2:
        #     list3 = []
        #     for i, row in df.iterrows():
        #         if itr == str(row[0]):
        #             list3.append(row)
        #     df2 = pd.DataFrame(list3)
        #     for i in range(len(df2) - 1):
        #         line_feature = {
        #              'type': 'Feature',
        #             'geometry': {
        #                 'type': 'LineString',
        #                 'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
        #                                 [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
        #             },
        #             'properties': {
        #                 'time': df2.iloc[i, 1]
        #             }
        #         }
        #         line_features.append(line_feature)
        #         # 軌跡のデータを管理する
        #         st.session_state['kiseki_data'][str(itr)].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], 
        #                                                      '日時': df2.iloc[i, 1]})
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

        # # 線のジオJSONを削除する
        # line_layers_to_remove = []
        # for key, value in st.session_state['map']._children.items():
        #     if isinstance(value, folium.features.GeoJson):
        #         line_layers_to_remove.append(key)
        # for key in line_layers_to_remove:
        #     del st.session_state['map']._children[key]

        # for idx, sdata in enumerate(st.session_state['draw_data']):
        #     tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
        #     if len(st.session_state['df_new']) != 0:
        #         kousa()
        #         # st.session_state['count'] += 1
        #         popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
        #         folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
        #     else:
        #         folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])

    else:
        # 空のデータフレームを作成
        df = pd.DataFrame()
        st.session_state['df'] = df
        st.session_state['df_new'] = df
        st.session_state['sorted_df'] = df
        # st.session_state["line_geojson"] = dict()

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
        del st.session_state["line_geojson"]

def select_data():
    # プロット・軌跡を描画するデータの選択
    selected_values = st.session_state["select_data_id"]
    st.session_state['sorted_index'] = [str(value) for value in selected_values]
    # 選択されていない場合はそのままのデータ
    if len(selected_values) == 0:
        st.session_state['sorted_df'] = st.session_state['df']

    # 選択された場合はデータをソート
    else:
        st.session_state['sorted_df'] = st.session_state['df'][st.session_state['df'].iloc[:, 0].isin(selected_values)]
        st.session_state['sorted_df'] = st.session_state['sorted_df'].reset_index(drop=True)
        
        # 線のジオJSONを削除する
        line_layers_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson):
                line_layers_to_remove.append(key)
        for key in line_layers_to_remove:
            del st.session_state['map']._children[key]

        # ユニークなIDのリスト
        # リストの全ての要素を文字列型に変換する
        features = plot(st.session_state['sorted_df'])
        line_features = kiseki_maker(st.session_state['sorted_df'])
        # list2 = selected_values
        
        # 描画するプロットデータ
        # features = []
        # for i, row in st.session_state['sorted_df'].iterrows():
        #     indexNum = list2.index(row.iloc[0])
        #     feature = {
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [row.iloc[3], row.iloc[2]]
        #         },
        #         "properties": {
        #             "icon": "circle",
        #             "iconstyle": {
        #                 "color": "#4169e1",
        #                 "fillColor": "#01bfff",
        #                 "weight": 10,
        #                 "radius": 3
        #             },
        #             "time": row.iloc[1],
        #             "popup": f"{indexNum+1} - {row.iloc[0]}",
        #             "ID": row.iloc[0]
        #         }
        #     }
        #     features.append(feature)

        # # 描画する軌跡データ
        # line_features = []
        # for itr in list2:
        #     st.session_state['kiseki_data'][str(itr)] = list()
        # for itr in list2:
        #     list3 = []
        #     for i, row in st.session_state['df'].iterrows():
        #         if itr == row[0]:
        #             list3.append(row)
        #     df2 = pd.DataFrame(list3)
        #     for i in range(len(df2) - 1):
        #         line_feature = {
        #              'type': 'Feature',
        #             'geometry': {
        #                 'type': 'LineString',
        #                 'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
        #                                 [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
        #             },
        #             'properties': {
        #                 'time': df2.iloc[i, 1]
        #             }
        #         }
        #         line_features.append(line_feature)
        #         # 軌跡データはいじらない
        #         # st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], '日時': df2.iloc[i, 1]})

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

        if len(st.session_state['draw_data']) != 0:
            zukei_draw()
    

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
        # list2 = [str(value) for value in st.session_state['new_df']['newid']]
        
        # 描画する軌跡データ
        # line_features = []
        # for itr in list2:
        #     st.session_state['kiseki_data'][str(itr)] = list()
        # for itr in list2:
        #     list3 = []
        #     for i, row in st.session_state['df'].iterrows():
        #         if itr == str(row[0]):
        #             list3.append(row)
        #     df2 = pd.DataFrame(list3)
        #     for i in range(len(df2) - 1):
        #         line_feature = {
        #              'type': 'Feature',
        #             'geometry': {
        #                 'type': 'LineString',
        #                 'coordinates': [[df2.iloc[i, 3], df2.iloc[i, 2]],
        #                                 [df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]]
        #             },
        #             'properties': {
        #                 'time': df2.iloc[i, 1]
        #             }
        #         }
        #         line_features.append(line_feature)
        #         # 軌跡データはいじらない
        #         # st.session_state['kiseki_data'][str(itr)].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], '日時': df2.iloc[i, 1]})

        line_features = kiseki_maker(st.session_state['sorted_df'])
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
        if selected_shape[0] != selected_shape[-1]:
            st.session_state["selected_shape_type"] = f"ゲート{select_shape_id}(ライン)"
            # tab3.write(f"ゲート{select_shape_id}(ライン)")
            converted_shape = [{"経度": row[0], "緯度": row[1]} for row in selected_shape]
        else:
            st.session_state["selected_shape_type"] = f"ゲート{select_shape_id}(ポリゴン)"
            # tab3.write(f"ゲート{select_shape_id}(ポリゴン)")
            converted_shape = [{"経度": row[0], "緯度": row[1]} for row in selected_shape]
        st.session_state["selected_shape"] = converted_shape
    else:
         st.session_state["selected_shape_type"] = ""
         st.session_state["selected_shape"] = list()
    
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

        # gate_append_list = list()
        # for idx, sdata in enumerate(st.session_state['draw_data']):
        #     if sdata["geometry"]["coordinates"][0][0] == sdata["geometry"]["coordinates"][0][-1]:
        #         gate_append_list.append(sdata["geometry"]["coordinates"][0])
        #     else:
        #         gate_append_list.append(sdata["geometry"]["coordinates"])
        #     tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
        #     if len(st.session_state['df_new']) != 0:
        #         kousa()
        #         st.session_state['count'] += 1
        #         popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
        #         folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
        #     else:
        #         folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])

def max_min_cross(p1, p2, p3, p4):
    min_ab, max_ab = min(p1, p2), max(p1, p2)
    min_cd, max_cd = min(p3, p4), max(p3, p4)

    if min_ab > max_cd or max_ab < min_cd:
        return False

    return True


def cross_judge(gates, values):
    flag = False
    # ゲートとIDの組み合わせごとにループ
    for idx1 in range(len(gates) - 1):
        line1 = [
                (gates[idx1][0], gates[idx1][1]),
                (gates[idx1 + 1][0], gates[idx1 + 1][1])
            ]
        for idx2 in range(len(values)):
            line2 = [
                        (values[idx2]["座標"][0][0], values[idx2]["座標"][0][1]),
                        (values[idx2]["座標"][1][0], values[idx2]["座標"][1][1])
                    ]
            (a, b, c, d) = (line1[0], line1[1], line2[0], line2[1])

            
            # x座標による判定
            if not max_min_cross(a[0], b[0], c[0], d[0]):
                continue
        
            # y座標による判定
            if not max_min_cross(a[1], b[1], c[1], d[1]):
                continue
        
            tc1 = (a[0] - b[0]) * (c[1] - a[1]) + (a[1] - b[1]) * (a[0] - c[0])
            tc2 = (a[0] - b[0]) * (d[1] - a[1]) + (a[1] - b[1]) * (a[0] - d[0])
            td1 = (c[0] - d[0]) * (a[1] - c[1]) + (c[1] - d[1]) * (c[0] - a[0])
            td2 = (c[0] - d[0]) * (b[1] - c[1]) + (c[1] - d[1]) * (c[0] - b[0])
            if tc1 * tc2 <= 0 and td1 * td2 <= 0 :
                flag = True
                break
        if flag:
            break
    return flag

def ingate(plot_point, gate_polygon):
    # plot_point = [float(plot_point)]
    point = Feature(geometry=Point(plot_point))
    polygon = Polygon(
        [gate_polygon]
    )
    return boolean_point_in_polygon(point, polygon)

def kousa():
    # 通過人数カウントの準備
    append_list = list()
    for _ in range(len(st.session_state['draw_data'])):
        append_list.append(0)
    st.session_state['tuuka_list'] = append_list
    
    # ゲートとIDの組み合わせごとにループ
    for idx1, gates in enumerate(st.session_state['gate_data']):
        for key, values in st.session_state['kiseki_data'].items():  

           if "gates" not in st.session_state:
               st.session_state['gates'] = gates
           if "values" not in st.session_state:
               st.session_state['values'] = values
            
           # ポリゴンゲートのときは初期座標をチェック
           if gates[0] == gates[-1]:
               try:
                   if ingate(values[0]["座標"][0], gates):
                       st.session_state['tuuka_list'][idx1] += 1
                       st.session_state['ingate_count'] += 1
                       continue  # このIDのループを終了
                   else:
                       st.session_state['non_ingate_count'] += 1
               except:
                   pass
                    #  tab4.write(values)

           if cross_judge(gates, values):
               # found_intersection = True
               st.session_state['tuuka_list'][idx1] += 1
               st.session_state['cross_judge_count'] += 1
               continue  # このIDのループを終了
           else:
               st.session_state['non_cross_judge_count'] += 1

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
        
        if (data["all_drawings"][0] not in st.session_state['draw_data'] or len(st.session_state['draw_data']) == 0):

            # データの追加
            st.session_state['draw_data'].append(data["all_drawings"][0])
            
                
            # # 通過人数カウントの準備
            # append_list = list()
            # for _ in range(len(st.session_state['draw_data'])):
            #     append_list.append(0)
            # st.session_state['tuuka_list'] = append_list

            # 線のジオJSONを削除する
            # line_layers_to_remove = []
            # for key, value in st.session_state['map']._children.items():
            #     if isinstance(value, folium.features.GeoJson):
            #         line_layers_to_remove.append(key)
            # for key in line_layers_to_remove:
            #     del st.session_state['map']._children[key]

            gate_append_list = list()
            for idx, sdata in enumerate(st.session_state['draw_data']):
                if sdata["geometry"]["coordinates"][0][0] == sdata["geometry"]["coordinates"][0][-1]:
                    gate_append_list.append(sdata["geometry"]["coordinates"][0])
                else:
                    gate_append_list.append(sdata["geometry"]["coordinates"]) 
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                if len(st.session_state['df_new']) != 0:
                    kousa()
                    st.session_state['count'] += 1
                    popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                    folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                else:
                    folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])

            
                    

            # 最初の要素のみを取得してst.session_state['gate_data']に追加
            st.session_state['gate_data'] = gate_append_list
            
            # 線のジオJSONを追加
            folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                       style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
    
            # raise st.experimental_rerun()
    else:
        # st.write(e)
        pass
            
except Exception as e:
    st.write(e)
    pass

st.subheader("地図の全描画データ")
st.write(data["all_drawings"])
st.write(st.session_state['draw_data'])
# st.write(st.session_state['count'])

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4 = st.tabs(["Uploader", "Data_info", "Gate_info", "Kiseki_info"])
    
    with tab1:
        # CSVファイルのアップロード
        st.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)
        
    with tab2:    
        st.write(st.session_state['df_new'])
        tab2.write(st.session_state['sorted_df'])
            
        if len(st.session_state['df']) != 0:
            # selected_values = st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",on_change=select_data)
            st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",on_change=select_data)
       
    with tab3:
        if len(st.session_state['draw_data']) != 0:
            st.write(st.session_state['gate_data'])
            st.selectbox("表示したい図形のIDを選択してください", [""]+ [str(value) for value in range(1, len(st.session_state['gate_data']) + 1)],
                         key="select_shape_id",
                         on_change=select_shape)

            st.selectbox("削除したい図形のIDを選択してください",
                         [""] + [str(value) for value in range(1, len(st.session_state['draw_data']) + 1)],
                         key="delete_shape_id",
                         on_change=delete_shape)

            st.write(st.session_state['tuuka_list'])
            st.write(st.session_state["selected_shape_type"])
            st.write(st.session_state["selected_shape"])
            # st.write(st.session_state['count'])
        
    with tab4:
        if len(st.session_state['df']) != 0:
            st.checkbox(label='軌跡の表示', key='kiseki_flag', on_change=kiseki_draw)

            # st.write(st.session_state['kiseki_data'])
            # st.write(st.session_state['tuuka_list'])
            # st.subheader("count")
            # st.write(st.session_state['count'])
            # st.subheader("ingate_count")
            # st.write(st.session_state['ingate_count'])
            # st.subheader("non_ingate_count")
            # st.write(st.session_state['non_ingate_count'])
            # st.subheader("cross_judge_count")
            # st.write(st.session_state['cross_judge_count'])  
            # st.subheader("non_cross_judge_count")
            # st.write(st.session_state['non_cross_judge_count'])

