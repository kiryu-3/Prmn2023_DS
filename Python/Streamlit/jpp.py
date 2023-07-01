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
    
    
if 'csv' not in st.session_state: # 初期化
    st.session_state['csv'] = None
if 'draw_data' not in st.session_state: # 初期化
    st.session_state['draw_data'] = list()  
if 'df' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df'] = df
if 'kiseki' not in st.session_state: # 初期化
    st.session_state['kiseki'] = False
if 'kiseki_data' not in st.session_state: # 初期化
    st.session_state['kiseki_data'] = dict() 
if 'gate_data' not in st.session_state: # 初期化
    st.session_state['gate_data'] = list()     
if "line_geojson" not in st.session_state: # 初期化
    st.session_state['line_geojson'] = None
if "tuuka_list" not in st.session_state: # 初期化
    st.session_state['tuuka_list'] = list()


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
    if len(st.session_state['df']) != 0:      
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

                   # if found_intersection:
                       # break # このIDのループを終了

        # # IDでループ
        # for key, values in st.session_state['kiseki_data'].items():
        #     # IDの軌跡ごとループ
        #     for value in values:

        #         line1 = [(value["座標"][0][0], value["座標"][0][1]),
        #                  (value["座標"][1][0], value["座標"][1][1])]
                
        #         # ゲートでループ
        #         for idx1 in range(len(st.session_state['gate_data'])):
        #            # 初期座標がゲート内にあるかどうかチェック
        #            data_list = []
        #            for item in st.session_state['gate_data'][idx1][0][:len(st.session_state['gate_data'][idx1][0])]:
        #                data_list.append(item)
        
        #            # 初期座標を取得
        #            first_value = next(iter(st.session_state['kiseki_data'].values()))
    
        #            # ポリゴンゲートのときは初期座標をチェック
        #            if st.session_state['gate_data'][idx1][0][0] == st.session_state['gate_data'][idx1][0][-1]:
        #                if ingate(first_value["座標"][0], data_list):
        #                    found_intersection = True
        #                    break  # このゲートのループを終了
    
        #            # 線分それぞれをチェック
        #            for idx2 in range(len(st.session_state['gate_data'][idx1][0])-1):   
        #                line2 = [(st.session_state['gate_data'][idx1][0][idx2][0], st.session_state['gate_data'][idx1][0][idx2][1]),
        #                         (st.session_state['gate_data'][idx1][0][idx2+1][0], st.session_state['gate_data'][idx1][0][idx2+1][1])]
        #                if are_lines_intersecting(line1, line2):
        #                    found_intersection = True
        #                    st.session_state['tuuka_list'][idx1] += 1
        #                    break  # このゲートのループを終了

        #            if found_intersection:
                       

# call to render Folium map in Streamlit
st_data = st_folium(st.session_state['map'], width=725)  

data = copy.deepcopy(dict(st_data))
# st.subheader("地図の全描画データ")
# st.write(data["all_drawings"])
# st.write(st.session_state['draw_data'])
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

        st.session_state['draw_data'].append(data["all_drawings"])
        if len(st.session_state['draw_data']) != 0:
            append_list = list()
            for _ in range(len(st.session_state['draw_data'])):
                append_list.append(0)
            st.session_state['tuuka_list'] = append_list
    else:
        pass
            
except Exception as e:
    # st.write(e)
    pass

st.subheader("地図の全描画データ")
st.write(len(st.session_state['draw_data']))
# st.write(data["all_drawings"])
st.write(st.session_state['draw_data'])
# st.write(len(st.session_state['draw_data'])

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Uploader", "Data_info", "Gate_info", "Kiseki_info", "Plus"])
    with tab1:
        # CSVファイルのアップロード
        uploaded_csvfile = st.file_uploader("CSVファイルをアップロード", type=["csv"])
        st.session_state['csv'] = uploaded_csvfile
        st.write(st.session_state['csv'])

        # def multi_file_uploader(label, key):
        #     uploaded_files = st.file_uploader(label, key=key, accept_multiple_files=True)
        #     return uploaded_files

        # # 使用例
        # uploaded_csvfiles = multi_file_uploader("複数のファイルを選択してください", "file_uploader")
        # st.write(uploaded_csvfiles)
        
        
        
        
    with tab2:    
        # st.write(st.session_state['df'])
        # excel_df = st.session_state['df']

        if st.session_state['csv'] is not None:
            file_data = st.session_state['csv'].read()
            # バイナリデータからPandas DataFrameを作成
            df = pd.read_csv(io.BytesIO(file_data))
            df.sort_values(by=[df.columns[1]], inplace=True)
            # st.write(df)
            unique_values = df.iloc[:, 0].unique()
            df_new = pd.DataFrame(unique_values, columns=["newid"])
            df_new.index = range(1, len(df_new) + 1)
            st.session_state['df'] = df_new
            st.write(st.session_state['df'])
            if len(df_new) != 0:
                selected_values = st.multiselect("選択してください", df.iloc[:, 0].unique())
                if len(selected_values) == 0:
                    sorted_df = df
                    st.session_state["kiseki"] = False
                else:
                    sorted_df = df[df.iloc[:, 0].isin(selected_values)]
                    st.session_state['kiseki'] = False
            else:
                sorted_df = df
        
            # df.sort_values(by=[df.columns[1]], inplace=True)
            kiseki = tab4.checkbox(label='軌跡の表示', key='kiseki2')
            list2 = list()
            for i, row in df.iterrows():
                if row.iloc[0] not in list2:
                    list2.append(row.iloc[0])
            features = []
            for i, row in sorted_df.iterrows():
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
            
            line_features = []
            for itr in list2:
                st.session_state['kiseki_data'][itr] = list()
            for itr in list2:
                list3 = []
                for i, row in sorted_df.iterrows():
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
                    st.session_state['kiseki_data'][itr].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], '日時': df2.iloc[i, 1]})
            tab4.write(st.session_state['kiseki_data'])
            line_geojson = {'type': 'FeatureCollection', 'features': line_features}
            st.session_state["line_geojson"] = line_geojson
        
            # 線のジオJSONを追加
            if kiseki and not st.session_state["kiseki"]:
                # 線のジオJSONを削除する
                line_layers_to_remove = []
                for key, value in st.session_state['map']._children.items():
                    if isinstance(value, folium.features.GeoJson):
                        line_layers_to_remove.append(key)
                for key in line_layers_to_remove:
                    del st.session_state['map']._children[key]
                # 線のジオJSONを追加
                folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                           style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
                st.session_state["kiseki"] = True
            
            elif not kiseki:
                # 線のジオJSONを削除する
                line_layers_to_remove = []
                for key, value in st.session_state['map']._children.items():
                    if isinstance(value, folium.features.GeoJson):
                        line_layers_to_remove.append(key)
                for key in line_layers_to_remove:
                    del st.session_state['map']._children[key]
            
                st.session_state["kiseki"] = False
            
            geojson = {"type": "FeatureCollection", "features": features}
        
            # レイヤーを削除
            if 'map' in st.session_state:
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
        
            # TimestampedGeoJsonをマップに追加
            timestamped_geojson.add_to(st.session_state['map'])
        
            # DataFrameをサイドバーに表示
            st.session_state['df'] = df_new
        
            for idx, sdata in enumerate(st.session_state['draw_data']):
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                if len(st.session_state['df']) != 0 and len(st.session_state['tuuka_list']) != 0:
                    kousa()
                    popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                    # folium.GeoJson(sdata[0], tooltip=tooltip_html).add_to(st.session_state['map'])
                    folium.GeoJson(sdata[0], tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                else:
                    folium.GeoJson(sdata[0], tooltip=tooltip_html).add_to(st.session_state['map'])

            delete_shape_id = st.selectbox("削除したい図形のIDを選択してください",
                                   [""] + [str(value) for value in range(1, len(st.session_state['draw_data']) + 1)])
            # tab4.write(st.session_state['tuuka_list'])
            # Deleteボタンがクリックされた場合
            if delete_shape_id != "":
                st.info("Deleteボタンをダブルクリックしてください")
                if st.button("Delete"):
                    delete_shape_id = int(delete_shape_id)
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
                    # tab5.write("削除しました")

                    # st.write(st.session_state['df'])
        else:
            df = pd.DataFrame()
            st.session_state['df'] = df
        
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
            st.session_state['kiseki_data'] = dict()
        
            for idx, sdata in enumerate(st.session_state['draw_data']):
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                if len(st.session_state['df']) != 0 and len(st.session_state['tuuka_list']) != 0:
                    kousa()
                    popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                    folium.GeoJson(sdata[0], tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                else:
                    folium.GeoJson(sdata[0], tooltip=tooltip_html).add_to(st.session_state['map'])
            
        # delete_shape_id = st.selectbox("削除したい図形のIDを選択してください",
        #                            [""] + [str(value) for value in range(1, len(st.session_state['draw_data']) + 1)])
        # # tab4.write(st.session_state['tuuka_list'])
        # # Deleteボタンがクリックされた場合
        # if delete_shape_id != "":
        #     st.info("Deleteボタンをダブルクリックしてください")
        #     if st.button("Delete"):
        #         delete_shape_id = int(delete_shape_id)
        #         # 削除対象の図形を特定
        #         delete_shape = st.session_state['draw_data'][delete_shape_id - 1]
        #         # 図形をマップから削除するためのキーを記録
        #         keys_to_remove = []
        #         for key, value in st.session_state['map']._children.items():
        #             if isinstance(value, folium.features.GeoJson) and value.data == delete_shape:
        #                 keys_to_remove.append(key)
        #             # マップから図形を削除
        #         for key in keys_to_remove:
        #             del st.session_state['map']._children[key]
        #         # draw_dataから図形を削除
        #         st.session_state['draw_data'].remove(delete_shape)
        #         # tab5.write("削除しました")

        #         # st.write(st.session_state['df'])
    with tab3:
        try:
            if len(st.session_state['draw_data']) == 0: 
                st.session_state['gate_data'] = list()
            else:
                # st.session_state['gate_data'] = list()
                # 最初の要素のみを取得してst.session_state['gate_data']に追加
                gate_append_list = list()
                for idx, sdata in enumerate(st.session_state['draw_data']):
                    gate_append_list.append(sdata[0]["geometry"]["coordinates"])
                st.session_state['gate_data'] = gate_append_list 
                st.write(st.session_state['gate_data'])
                # st.write(st.session_state['gate_data'])
                # zukei_area = tab3.empty()
                zukei_id = st.selectbox("表示したい図形のIDを選択してください", [""]
                                       + [str(value) for value in range(1, len(st.session_state['draw_data']) + 1)])
                if zukei_id != "":
                    zukei_id = int(zukei_id)
                    # 表示対象の図形を特定
                    delete_shape = st.session_state['gate_data'][zukei_id - 1]
                    if delete_shape[0][0] == delete_shape[0][-1]:
                        st.write(f"ゲート{zukei_id}(ライン)")
                    else:
                        st.write(f"ゲート{zukei_id}(ポリゴン)")
                    st.write(delete_shape)

            st.write(st.session_state['tuuka_list'])
        except:
            pass
