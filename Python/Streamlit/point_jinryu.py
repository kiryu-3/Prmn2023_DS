import io
from io import BytesIO
import json
import itertools
import pandas as pd
import copy

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature

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
    
    st.session_state['map'] = m
    
# 読み込んだデータフレームを管理する 
if 'df' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df'] = df
# 特定のIDの情報を管理する
if 'sorted_df' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['sorted_df'] = df
# tab2に実際に表示するデータフレーム
if 'df_new' not in st.session_state: # 初期化
    df = pd.DataFrame()
    st.session_state['df_new'] = df
# 地図上に描画された図形情報を管理する
if 'draw_data' not in st.session_state: # 初期化
    st.session_state['draw_data'] = list() 
# それぞれの緯度経度のみの図形情報を管理する
if 'gate_data' not in st.session_state: # 初期化
    st.session_state['gate_data'] = list()  
# 軌跡の情報を管理する
if 'kiseki_data' not in st.session_state: # 初期化
    st.session_state['kiseki_data'] = dict() 
# 軌跡を描画するモードか管理する
if 'kiseki_flag' not in st.session_state: # 初期化
    st.session_state['kiseki_flag'] = False
# 実際に地図に追加する形で軌跡の情報を管理する
if "line_geojson" not in st.session_state: # 初期化
    st.session_state['line_geojson'] = None
# 当たり判定のゲートごとの人数を管理する
if "tuuka_list" not in st.session_state: # 初期化
    st.session_state['tuuka_list'] = list()
# tab3に表示する選択された図形の緯度経度情報を管理する
if "selected_shape" not in st.session_state: # 初期化
    st.session_state["selected_shape"] = list()
# tab3に表示する選択された図形のタイプを管理する  
if "selected_shape_type" not in st.session_state: # 初期化
    st.session_state["selected_shape_type"] = ""

# 描画するプロットデータの作成
def features_maker(list2):
    # 描画するプロットデータ
    features = []
    for i, row in st.session_state['sorted_df'].iterrows():
        indexNum = list2.index(str(row.iloc[0]))
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

# 描画する軌跡データの作成
def line_features_maker(list2, kiseki):
    # 描画する軌跡データのリスト
    line_features = []
    # 各IDごとにループ
    for itr in list2:
        # IDに対応する行のデータを抽出
        list3 = []
        for i, row in st.session_state['sorted_df'].iterrows():
            if itr == str(row[0]):
                list3.append(row)
        df2 = pd.DataFrame(list3)
        # 各行の座標データから軌跡データを作成
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
            if kiseki:
                # 軌跡データをセッションの状態に保存
                st.session_state['kiseki_data'][str(itr)].append({'座標': [[df2.iloc[i, 3], df2.iloc[i, 2]],[df2.iloc[i + 1, 3], df2.iloc[i + 1, 2]]], 
                                                                  '日時': df2.iloc[i, 1]})
    return line_features

# csvのuploaderの状態が変化したときに呼ばれるcallback関数
def upload_csv():
    # csvがアップロードされたとき
    if st.session_state["upload_csvfile"] is not None:
        # アップロードされたファイルデータを読み込む
        file_data = st.session_state["upload_csvfile"].read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data))
        # 通過時間でソート
        df.sort_values(by=[df.columns[1]], inplace=True)
      
        # ユニークなIDを取得
        unique_values = df.iloc[:, 0].unique()
        # IDのデータフレームを作成
        df_new = pd.DataFrame(unique_values, columns=["newid"])
      
        # 1からスタートするようにインデックスを設定
        df_new.index = range(1, len(df_new) + 1)

        # データフレームをセッションの状態に保存
        st.session_state['df'] = df
        st.session_state['df_new'] = df_new
        st.session_state['sorted_df'] = df

        # ユニークなIDのリスト
        list2 = [str(value) for value in unique_values]
        for itr in list2:
          st.session_state['kiseki_data'][str(itr)] = list()

        features = features_maker(list2)
        line_features = line_features_maker(list2, True)
        
        # プロットデータをまとめる
        geojson = {"type": "FeatureCollection", "features": features}
        # 軌跡データをまとめる
        line_geojson = {'type': 'FeatureCollection', 'features': line_features}
        st.session_state["line_geojson"] = line_geojson
            
        # 地図のレイヤーを削除
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

        # 軌跡のGeoJSONを削除する
        line_layers_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson):
                line_layers_to_remove.append(key)
        for key in line_layers_to_remove:
            del st.session_state['map']._children[key]

        # 地図に図形情報を追加
        for idx, sdata in enumerate(st.session_state['draw_data']):
            
            # 通過人数カウントの準備
            append_list = list()
            for _ in range(len(st.session_state['draw_data'])):
                append_list.append(0)
            # 最初は各ゲートの通過人数は0人とする
            st.session_state['tuuka_list'] = append_list
            
            # ゲートとIDの組み合わせごとにループ
            for idx1, gates in enumerate(st.session_state['gate_data']):
                for key, values in st.session_state['kiseki_data'].items():  
                    
                   # ポリゴンゲートのときは初期座標をチェック
                   if gates[0] == gates[-1]:
                       if ingate(values[0]["座標"][0], gates):
                           st.session_state['tuuka_list'][idx1] += 1
                           continue  # このIDのループを終了
                       else:
                           pass
        
                   if cross_judge(gates, values):
                       st.session_state['tuuka_list'][idx1] += 1
                       continue  # このIDのループを終了
                   else:
                       pass

            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
            # 通過人数を表示するポップアップを指定
            popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
            # 地図にツールチップとポップアップを追加する
            folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
  
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
        st.session_state['kiseki_data'] = dict()

def select_data():
  
    # プロット・軌跡を描画するデータの選択
    selected_values = st.session_state["select_data_id"]
  
    # 選択されていない場合はそのままのデータ
    if len(selected_values) == 0:
        st.session_state['sorted_df'] = st.session_state['df']
        # ユニークなIDを取得
        unique_values = st.session_state['sorted_df'].iloc[:, 0].unique()
        list2 = [str(value) for value in unique_values]

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
        list2 = [str(value) for value in selected_values]
    
    # 描画するプロットデータ
    features = features_maker(list2)
    line_features = line_features_maker(list2, False)

    # プロットデータをまとめる
    geojson = {"type": "FeatureCollection", "features": features}
    # 軌跡データをまとめる
    line_geojson = {'type': 'FeatureCollection', 'features': line_features}
    st.session_state["line_geojson"] = line_geojson

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

    # 地図に図形情報を追加
    for idx, sdata in enumerate(st.session_state['draw_data']):
        if len(st.session_state['df_new']) != 0: 
            # 通過人数カウントの準備
            append_list = list()
            for _ in range(len(st.session_state['draw_data'])):
                append_list.append(0)
            st.session_state['tuuka_list'] = append_list
            
            # ゲートとIDの組み合わせごとにループ
            for idx1, gates in enumerate(st.session_state['gate_data']):
                for key, values in st.session_state['kiseki_data'].items():  
                   
                   # ポリゴンゲートのときは初期座標をチェック
                   if gates[0] == gates[-1]:
                       if ingate(values[0]["座標"][0], gates):
                           st.session_state['tuuka_list'][idx1] += 1
                           continue  # このIDのループを終了
                       else:
                           pass
        
                   if cross_judge(gates, values):
                       st.session_state['tuuka_list'][idx1] += 1
                       continue  # このIDのループを終了
                   else:
                       pass
            
            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
            # 通過人数を表示するポップアップを指定
            popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
            folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
        else:
            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
            folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])
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

        # 地図に図形情報を追加
        for idx, sdata in enumerate(st.session_state['draw_data']):
            # 通過人数カウントの準備
            append_list = list()
            for _ in range(len(st.session_state['draw_data'])):
                append_list.append(0)
            st.session_state['tuuka_list'] = append_list
            
            # ゲートとIDの組み合わせごとにループ
            for idx1, gates in enumerate(st.session_state['gate_data']):
                for key, values in st.session_state['kiseki_data'].items():  
                    
                   # ポリゴンゲートのときは初期座標をチェック
                   if gates[0] == gates[-1]:
                       if ingate(values[0]["座標"][0], gates):
                           st.session_state['tuuka_list'][idx1] += 1
                           continue  # このIDのループを終了
                       else:
                           pass
        
                   if cross_judge(gates, values):
                       st.session_state['tuuka_list'][idx1] += 1
                       continue  # このIDのループを終了
                   else:
                       pass
            
            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
            # 通過人数を表示するポップアップを指定
            popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
            folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                
# 図形情報を表示する図形の選択・加工        
def select_shape():
    # 図形IDが指定されているとき
    if st.session_state["select_shape_id"] != "":
        select_shape_id = int(st.session_state["select_shape_id"])
        # 表示対象の図形を特定
        selected_shape = st.session_state['gate_data'][select_shape_id - 1]
      
        # 図形の最初と最後の座標が違うときはライン
        if selected_shape[0] != selected_shape[-1]:
            st.session_state["selected_shape_type"] = f"ゲート{select_shape_id}(ライン)"
            converted_shape = [{"経度": row[0], "緯度": row[1]} for row in selected_shape]
          
        # 図形の最初と最後の座標が同じときはポリゴン
        else:
            st.session_state["selected_shape_type"] = f"ゲート{select_shape_id}(ポリゴン)"
            converted_shape = [{"経度": row[0], "緯度": row[1]} for row in selected_shape]
        st.session_state["selected_shape"] = converted_shape

    # 図形IDが指定されていないとき
    else:
         st.session_state["selected_shape_type"] = ""
         st.session_state["selected_shape"] = list()

# 地図から図形を削除する
def delete_shape():
    # 図形IDが指定されているとき
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
        if len(st.session_state['tuuka_list']) != 0:
            st.session_state['tuuka_list'].pop(delete_shape_id - 1)

        for idx, sdata in enumerate(st.session_state['draw_data']):
            if len(st.session_state['df_new']) != 0:  
                # 通過人数カウントの準備
                append_list = list()
                for _ in range(len(st.session_state['draw_data'])):
                    append_list.append(0)
                st.session_state['tuuka_list'] = append_list
                
                # ゲートとIDの組み合わせごとにループ
                for idx1, gates in enumerate(st.session_state['gate_data']):
                    for key, values in st.session_state['kiseki_data'].items():  
                        
                       # ポリゴンゲートのときは初期座標をチェック
                       if gates[0] == gates[-1]:
                           try:
                               if ingate(values[0]["座標"][0], gates):
                                   try:
                                       st.session_state['tuuka_list'][idx1] += 1
                                       continue  # このIDのループを終了
                                   except Exception as e:
                                       st.write(st.session_state['tuuka_list'])
                               else:
                                   pass
                           except:
                                tab4.write(values)
            
                       if cross_judge(gates, values):
                           st.session_state['tuuka_list'][idx1] += 1
                           continue  # このIDのループを終了
                       else:
                           pass
                
                # 図形IDを表示するツールチップを設定
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                # 通過人数を表示するポップアップを指定
                popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])

            else:
                # 図形IDを表示するツールチップを設定
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])            

# x座標、y座標ごとに座標が一切被っていない場合はfalseを返す
def max_min_cross(p1, p2, p3, p4):
    min_ab, max_ab = min(p1, p2), max(p1, p2)
    min_cd, max_cd = min(p3, p4), max(p3, p4)

    # それぞれの最大値と最小値を比較
    # 最大値 < 最小値の時にfalseを返す
    if min_ab > max_cd or max_ab < min_cd:
        return False

    return True

# 2つの線分の交差判定
def cross_judge(gates, values):
    flag = False
    # ゲートとIDの組み合わせごとにループ
    for idx1 in range(len(gates) - 1):
        # ゲートを構成する線分の一つ
        line1 = [
                (gates[idx1][0], gates[idx1][1]),
                (gates[idx1 + 1][0], gates[idx1 + 1][1])
            ]
        for idx2 in range(len(values)):
            # 軌跡の線分の一つ
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

# プロットの初期座標がゲート内にあるか判定
def ingate(plot_point, gate_polygon):
    # plot_point = [float(plot_point)]
    point = Feature(geometry=Point(plot_point))
    polygon = Polygon(
        [gate_polygon]
    )
    return boolean_point_in_polygon(point, polygon)

# 表示する地図
st_data = st_folium(st.session_state['map'], width=725)  

# 地図のデータをコピー
data = copy.deepcopy(dict(st_data))

try:
    # data["all_drawings"]が有効なリストであるかどうか判定
    # 値が入っていたら値を追加する
    if data["all_drawings"] is not None and isinstance(data["all_drawings"], list) and len(data["all_drawings"]) > 0:
        
        # サークルのデータを加工
        if data["last_circle_polygon"] is not None:
            data["all_drawings"][0]["geometry"]["type"] = "Polygon"
            data["all_drawings"][0]["geometry"]["coordinates"] = data["last_circle_polygon"]["coordinates"]
            center_list = data["last_active_drawing"]["geometry"]["coordinates"]
            center_dict = dict()
            center_dict["lat"] = center_list[0]
            center_dict["lng"] = center_list[1]
            data["all_drawings"][0]["properties"]["center"] = center_dict

        # data["all_drawings"][0]が追加できそうなら追加
        if (data["all_drawings"][0] not in st.session_state['draw_data'] or len(st.session_state['draw_data']) == 0):

            # st.session_state['draw_data']に追加
            st.session_state['draw_data'].append(data["all_drawings"][0])

            # 線のジオJSONを削除する
            line_layers_to_remove = []
            for key, value in st.session_state['map']._children.items():
                if isinstance(value, folium.features.GeoJson):
                    line_layers_to_remove.append(key)
            for key in line_layers_to_remove:
                del st.session_state['map']._children[key]

            # st.session_state['gate_data']に追加するための加工
            gate_append_list = list()
            for idx, sdata in enumerate(st.session_state['draw_data']):
                # 図形の最初と最後の座標が違うとき（ライン）
                if sdata["geometry"]["coordinates"][0][0] == sdata["geometry"]["coordinates"][0][-1]:
                    gate_append_list.append(sdata["geometry"]["coordinates"][0])
                # 図形の最初と最後の座標が同じとき（ポリゴン）
                else:
                    gate_append_list.append(sdata["geometry"]["coordinates"])
                  
            # st.session_state['gate_data']に追加
            st.session_state['gate_data'] = gate_append_list
          
            for idx, sdata in enumerate(st.session_state['draw_data']):
                # データがあるときは当たり判定を行う
                if len(st.session_state['df_new']) != 0:
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
                               if ingate(values[0]["座標"][0], gates):
                                   st.session_state['tuuka_list'][idx1] += 1
                                   continue  # このIDのループを終了
                               else:
                                   pass
                
                           if cross_judge(gates, values):
                               st.session_state['tuuka_list'][idx1] += 1
                               continue  # このIDのループを終了
                           else:
                               pass
                    
                    # 図形IDを表示するツールチップを設定 
                    tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                    # 通過人数を表示するポップアップを指定
                    popup_html = '<div style="font-size: 16px;">通過人数：{}人</div>'.format(st.session_state['tuuka_list'][idx])
                    folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])
                else: 
                    # 図形IDを表示するツールチップを設定
                    tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(st.session_state['draw_data'].index(sdata) + 1)
                    folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])

            if st.session_state["kiseki_flag"]:
                # 線のジオJSONを追加
                folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
                               style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
                                                                                          
    # 地図に新たな図形が描画されていないなら何もしない
    else:
        pass

                                                                                        
except Exception as e:
    pass

st.subheader("地図の全描画データ")
st.write(st.session_state['draw_data'])

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4 = st.tabs(["Uploader", "Data_info", "Gate_info", "Kiseki_info"])

    # csvのuploader
    with tab1:
        # CSVファイルのアップロード
        st.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)

    # csvから読み込んだIDの表示とプロットするマーカー・軌跡の選択
    with tab2:    
        st.write(st.session_state['df_new'])
            
        if len(st.session_state['df']) != 0:
            st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",on_change=select_data)

    # 図形の情報の選択と削除
    with tab3:
        if len(st.session_state['draw_data']) != 0:
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

    # 軌跡を描画するか選択
    with tab4:
        if len(st.session_state['df']) != 0:
            st.checkbox(label='軌跡の表示', key='kiseki_flag', on_change=kiseki_draw)
