import json
import random
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objs as go
import plotly.io as pio
import plotly

import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import folium
from folium import plugins
from folium.plugins import Draw, TimestampedGeoJson
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import streamlit as st
from streamlit_folium import st_folium
import io
from io import BytesIO
import itertools
import copy

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

# 読み込んだデータフレームを管理する
if 'center' not in st.session_state:  # 初期化
    st.session_state['center'] = dict()
    st.session_state['center']["lat"] = 42.80961703023506
    st.session_state['center']["lng"] = 141.69487953186038

# if 'map' not in st.session_state:  # 初期化
#     # 初めての表示時は空のマップを表示
#     m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)
#     # Leaflet.jsのDrawプラグインを追加
#     draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
#     draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
#     draw.add_to(m)

#     st.session_state['map'] = m

# else:
#     m = folium.Map(location=[st.session_state['center']["lat"], st.session_state['center']["lng"]], zoom_start=16)
#     # Leaflet.jsのDrawプラグインを追加
#     draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
#     draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
#     draw.add_to(m)

#     st.session_state['map'] = m

# 読み込んだデータフレームを管理する
if 'df' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['df'] = df
# 特定のIDの情報を管理する
if 'sorted_df' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['sorted_df'] = df
# tab2に実際に表示するデータフレーム
if 'df_new' not in st.session_state:  # 初期化
    df = pd.DataFrame()
    st.session_state['df_new'] = df
# 地図上に描画された図形情報を管理する
if 'draw_data' not in st.session_state:  # 初期化
    st.session_state['draw_data'] = list()
# それぞれの緯度経度のみの図形情報を管理する
if 'gate_data' not in st.session_state:  # 初期化
    st.session_state['gate_data'] = list()
# 軌跡の情報を管理する
if 'kiseki_data' not in st.session_state:  # 初期化
    st.session_state['kiseki_data'] = dict()
# 軌跡を描画するモードか管理する
if 'kiseki_flag' not in st.session_state:  # 初期化
    st.session_state['kiseki_flag'] = False
# 実際に地図に追加する形で軌跡の情報を管理する
if "line_geojson" not in st.session_state:  # 初期化
    st.session_state['line_geojson'] = None
# 当たり判定のゲートごとの人数を管理する
if "tuuka_list" not in st.session_state:  # 初期化
    st.session_state['tuuka_list'] = list()
# tab3に表示する選択された図形の緯度経度情報を管理する
if "selected_shape" not in st.session_state:  # 初期化
    st.session_state["selected_shape"] = list()
# tab3に表示する選択された図形のタイプを管理する
if "selected_shape_type" not in st.session_state:  # 初期化
    st.session_state["selected_shape_type"] = ""
# グラフデータを管理する
if "graph_data" not in st.session_state:  # 初期化
    st.session_state["graph_data"] = dict()


# 描画するプロットデータの作成
def features_maker(list2):
    features = []
    coordinates = st.session_state['sorted_df'][['longitude', 'latitude']].values  # 座標データのみを抽出

    index_map = {value: index for index, value in enumerate(list2)}
    for i, row in st.session_state['sorted_df'].iterrows():
        indexNum = index_map[row[0]]
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row[3], row[2]]
            },
            "properties": {
                "icon": "circle",
                "iconstyle": {
                    "color": "#4169e1",
                    "fillColor": "#01bfff",
                    "weight": 10,
                    "radius": 3
                },
                "time": row[1],
                "popup": f"{indexNum + 1} - {row[0]}",
                "ID": row[0]
            }
        }
        features.append(feature)
    return features


# 描画する軌跡データの作成
def line_features_maker(list2, kiseki):
    line_features = []

    index_map = {value: index for index, value in enumerate(list2)}

    # データをIDでグループ化する
    grouped_data = st.session_state['sorted_df'].groupby(st.session_state['sorted_df'].columns[0])

    for itr in list2:
        if itr in grouped_data.groups:
            indexNum = index_map[itr]
            group_df = grouped_data.get_group(itr)
            coords = group_df[[group_df.columns[3], group_df.columns[2]]].values.tolist()
            times = group_df[group_df.columns[1]].values.tolist()

            # 各行の座標データから軌跡データを作成
            for i in range(len(coords) - 1):
                line_feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [coords[i], coords[i + 1]]
                    },
                    'properties': {
                        'time': times[i],
                        "popup": f"{indexNum + 1} - {itr}"
                    }
                }
                line_features.append(line_feature)

                if kiseki:
                    # 軌跡データをセッションの状態に保存
                    st.session_state['kiseki_data'][str(itr)].append({'座標': [coords[i], coords[i + 1]],
                                                                      '日時': times[i]})
    return line_features


# csvのuploaderの状態が変化したときに呼ばれるcallback関数
def upload_csv():
    # csvがアップロードされたとき
    if st.session_state["upload_csvfile"] is not None:
        # アップロードされたファイルデータを読み込む
        file_data = st.session_state["upload_csvfile"].read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data))
        df.loc[df["newid"] == 20230403156, "daytime"] = df.loc[df["newid"] == 20230403156, "daytime"].str.replace(
            "2023/4/3", "2023/4/4")
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

        st.session_state['kiseki_data'] = {str(itr): [] for itr in unique_values}

        features = features_maker(unique_values)
        line_features = line_features_maker(unique_values, True)

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
        if len(st.session_state['draw_data']) != 0:
            for idx, sdata in enumerate(st.session_state['draw_data']):

                # 通過人数カウントの準備
                append_list = [dict() for _ in range(len(st.session_state['draw_data']))]
                st.session_state['tuuka_list'] = append_list

                # ゲートとIDの組み合わせごとにループ
                for idx1, gates in enumerate(st.session_state['gate_data']):
                    for key, values in st.session_state['kiseki_data'].items():

                        # ポリゴンゲートのときは初期座標をチェック
                        if gates[0] == gates[-1]:
                            if ingate(values[0]["座標"][0], gates):
                                st.session_state['tuuka_list'][idx1][key] = values[0]["日時"]
                                continue  # このIDのループを終了
                            else:
                                pass

                        kekka = cross_judge(gates, values)
                        if kekka[0]:
                            st.session_state['tuuka_list'][idx1][key] = values[kekka[1]]["日時"]
                            continue  # このIDのループを終了

                # 図形IDを表示するツールチップを設定
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
                # 通過人数を表示するポップアップを指定
                popup_html = '<div style="font-size: 16px; font-weight: bold; width: 110px; height: 20px;  color: #27b9cc;">通過人数：{}人</div>'.format(
                    len(st.session_state['tuuka_list'][idx]))
                # 地図にツールチップとポップアップを追加する
                folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(
                    st.session_state['map'])

    else:
        # 空のデータフレームを作成
        df = pd.DataFrame()
        st.session_state['df'] = df
        st.session_state['df_new'] = df
        st.session_state['sorted_df'] = df

        st.session_state["graph_data"] = dict()

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
        line_layers_to_remove = []
        for key, value in st.session_state['map']._children.items():
            if isinstance(value, folium.features.GeoJson):
                line_layers_to_remove.append(key)
        for key in line_layers_to_remove:
            del st.session_state['map']._children[key]


def select_data():
    # プロット・軌跡を描画するデータの選択
    selected_values = st.session_state["select_data_id"]

    # 選択されていない場合はそのままのデータ
    if len(selected_values) == 0:
        st.session_state['sorted_df'] = st.session_state['df']
        # ユニークなIDを取得
        unique_values = st.session_state['sorted_df'].iloc[:, 0].unique()

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
        unique_values = selected_values

    # 描画するプロットデータ
    features = features_maker(unique_values)
    line_features = line_features_maker(unique_values, False)

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
            append_list = [dict() for _ in range(len(st.session_state['draw_data']))]
            st.session_state['tuuka_list'] = append_list

            # ゲートとIDの組み合わせごとにループ
            for idx1, gates in enumerate(st.session_state['gate_data']):
                for key, values in st.session_state['kiseki_data'].items():

                    # ポリゴンゲートのときは初期座標をチェック
                    if gates[0] == gates[-1]:
                        if ingate(values[0]["座標"][0], gates):
                            st.session_state['tuuka_list'][idx1][key] = values[0]["日時"]
                            continue  # このIDのループを終了
                        else:
                            pass

                    kekka = cross_judge(gates, values)
                    if kekka[0]:
                        st.session_state['tuuka_list'][idx1][key] = values[kekka[1]]["日時"]
                        continue  # このIDのループを終了
                    else:
                        pass

            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
            # 通過人数を表示するポップアップを指定
            popup_html = '<div style="font-size: 16px; font-weight: bold; width: 110px; height: 20px;  color: #27b9cc;">通過人数：{}人</div>'.format(
                len(st.session_state['tuuka_list'][idx]))
            folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(st.session_state['map'])

        else:
            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
            folium.GeoJson(sdata, tooltip=tooltip_html).add_to(st.session_state['map'])

    # 軌跡の追加
    if st.session_state['kiseki_flag']:
        # 線のジオJSONを追加
        # folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
        #                style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
        folium.GeoJson(
            st.session_state["line_geojson"],
            name='線の表示/非表示',
            style_function=lambda x: {"weight": 2, "opacity": 1},
            popup=folium.GeoJsonPopup(fields=['popup'], labels=False)
        ).add_to(st.session_state['map'])


def select_graph():
    # st.session_state["cols"][1].selectbox("グラフを表示したい図形のIDを選択してください", [""]+ [str(value) for value in range(1, len(st.session_state['gate_data']) + 1)],
    #                        key="select_graph_id",
    #                        on_change=select_graph)

    # if len(st.session_state["graph_data"]) < len(st.session_state['select_graph_ids']):
    st.session_state["graph_data"] = dict()
    if len(st.session_state['select_graph_ids']) != 0:
        for idx in st.session_state['select_graph_ids']:
            data = st.session_state['tuuka_list'][int(idx) - 1]
            dates = data.values()
            first_date_str = next(iter(dates))
            start_date = datetime.strptime(first_date_str, '%Y/%m/%d %H:%M').date()

            # 日付と時間帯ごとに人数をカウントする辞書を初期化
            hourly_counts = defaultdict(lambda: defaultdict(int))

            # 日付ごとにデータを処理して人数をカウント
            for date_str in dates:
                dt = datetime.strptime(date_str, '%Y/%m/%d %H:%M')
                date = dt.date()
                hour = dt.hour
                hourly_counts[date][hour] += 1

            # print(hourly_counts.items())
            # 結果を表示
            counts_dict = dict()
            for date, counts in hourly_counts.items():
                for hour in range(24):
                    counts_dict[f"{date.strftime('%m/%d')} {hour:02d}時"] = counts[hour]

            # データを時刻順にソート
            sorted_data = sorted(counts_dict.items())

            # 折れ線グラフのトレースを作成
            trace = go.Scatter(x=[f"{start_date.strftime('%m/%d')} {hour:02d}:00" for hour in range(24)],
                               y=[counts for hour, counts in sorted_data],
                               mode='lines', name='通過人数[人]')

            # グラフのレイアウトを設定
            layout = go.Layout(
                title='通過人数',
                xaxis=dict(title='日時'),
                yaxis=dict(
                    title='通過人数[人]',
                    tickvals=list(range(max([counts for hour, counts in sorted_data]) + 1)),  # 整数のリストを設定
                    tickformat='d',  # 整数表示に設定
                )
            )

            # グラフオブジェクトを作成
            fig = go.Figure(data=[trace], layout=layout)

            # グラフをJSON形式に変換
            graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

            # JSONをst.session_stateに保存
            st.session_state["graph_data"][idx] = graph_json

        # グラフを表示
        # st.plotly_chart(fig)

        # # 時刻と値をリストに分ける
        # time_points, values = zip(*sorted_data)

        # # 最終日の日付を取得
        # last_date_str = time_points[-1].split()[0]
        # last_date = datetime.strptime(last_date_str, '%m/%d')

        # # 最終日のデータが24時まであるか確認
        # if last_date.hour != 23:
        #     # 24時までのデータを追加
        #     last_date += timedelta(days=1)
        #     time_points = tuple(list(time_points) + [f"{last_date.strftime('%m/%d')} 00時"])
        #     values = tuple(list(values) + [0])

        # # グラフの作成
        # fig, ax = plt.subplots(figsize=(725/96, 6))
        # ax.plot(time_points, values)

        # # x軸とy軸のラベル、タイトルを設定
        # # ax.set_xlabel('時間')
        # ax.set_ylabel('通過人数[人]')
        # # ax.set_title('通過人数')

        # # x軸の目盛りを6時間ごとに設定
        # ax.set_xticks(range(0, len(time_points), 6))
        # ax.set_xticklabels(time_points[::6])

        # # y軸のスケールを整数値に設定
        # count_per_group = 5

        # # スケールが1ずつの条件を追加
        # if max(values) <= 5:
        #     count_per_group = 1

        # ax.set_yticks(list(range(0, max(values) + count_per_group, count_per_group)) + [max(values)])

        # # グラフをバイトストリームに変換
        # buffer = BytesIO()
        # plt.savefig(buffer, format='png')
        # buffer.seek(0)

        # # バイトストリームをst.session_stateに保存
        # st.session_state['graph_image'] = buffer.getvalue()

        # # グラフを表示
        # # tab4.image(st.session_state['graph_image'], use_column_width=True)

    else:
        # グラフを空にする
        st.session_state["graph_data"] = dict()


def kiseki_draw():
    if st.session_state['kiseki_flag']:
        # 線のジオJSONを追加
        # folium.GeoJson(st.session_state["line_geojson"], name='線の表示/非表示',
        #                style_function=lambda x: {"weight": 2, "opacity": 1}).add_to(st.session_state['map'])
        folium.GeoJson(
            st.session_state["line_geojson"],
            name='線の表示/非表示',
            style_function=lambda x: {"weight": 2, "opacity": 1},
            popup=folium.GeoJsonPopup(fields=['popup'], labels=False)
        ).add_to(st.session_state['map'])

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
            append_list = [dict() for _ in range(len(st.session_state['draw_data']))]
            st.session_state['tuuka_list'] = append_list

            # ゲートとIDの組み合わせごとにループ
            for idx1, gates in enumerate(st.session_state['gate_data']):
                for key, values in st.session_state['kiseki_data'].items():

                    # ポリゴンゲートのときは初期座標をチェック
                    if gates[0] == gates[-1]:
                        if ingate(values[0]["座標"][0], gates):
                            st.session_state['tuuka_list'][idx1][key] = values[0]["日時"]
                            continue  # このIDのループを終了
                        else:
                            pass

                    kekka = cross_judge(gates, values)
                    if kekka[0]:
                        st.session_state['tuuka_list'][idx1][key] = values[kekka[1]]["日時"]
                        continue  # このIDのループを終了

            # 図形IDを表示するツールチップを設定
            tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
            # 通過人数を表示するポップアップを指定
            popup_html = '<div style="font-size: 16px; font-weight: bold; width: 110px; height: 20px;  color: #27b9cc;">通過人数：{}人</div>'.format(
                len(st.session_state['tuuka_list'][idx]))
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
        st.session_state['gate_data'].pop(delete_shape_id - 1)
        if len(st.session_state['tuuka_list']) != 0:
            st.session_state['tuuka_list'].pop(delete_shape_id - 1)
        if len(st.session_state['selected_shape']) != 0:
            st.session_state["selected_shape"].pop(delete_shape_id - 1)

        for idx, sdata in enumerate(st.session_state['draw_data']):
            if len(st.session_state['df_new']) != 0:
                # 通過人数カウントの準備
                append_list = [dict() for _ in range(len(st.session_state['draw_data']))]
                st.session_state['tuuka_list'] = append_list

                # ゲートとIDの組み合わせごとにループ
                for idx1, gates in enumerate(st.session_state['gate_data']):
                    for key, values in st.session_state['kiseki_data'].items():

                        # ポリゴンゲートのときは初期座標をチェック
                        if gates[0] == gates[-1]:
                            if ingate(values[0]["座標"][0], gates):
                                st.session_state['tuuka_list'][idx1][key] = values[0]["日時"]
                                continue  # このIDのループを終了
                            else:
                                pass

                        kekka = cross_judge(gates, values)
                        if kekka[0]:
                            st.session_state['tuuka_list'][idx1][key] = values[kekka[1]]["日時"]
                            continue  # このIDのループを終了

                # 図形IDを表示するツールチップを設定
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
                # 通過人数を表示するポップアップを指定
                popup_html = '<div style="font-size: 16px; font-weight: bold; width: 110px; height: 20px;  color: #27b9cc;">通過人数：{}人</div>'.format(
                    len(st.session_state['tuuka_list'][idx]))
                folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(
                    st.session_state['map'])


            else:
                # 図形IDを表示するツールチップを設定
                tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
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
    idx = -1
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
            if tc1 * tc2 <= 0 and td1 * td2 <= 0:
                flag = True
                idx = idx2
                break
        if flag:
            break
    return (flag, idx)


# プロットの初期座標がゲート内にあるか判定
def ingate(plot_point, gate_polygon):
    # plot_point = [float(plot_point)]
    point = Feature(geometry=Point(plot_point))
    polygon = Polygon(
        [gate_polygon]
    )
    return boolean_point_in_polygon(point, polygon)


# 表示する地図

m = folium.Map(location=[st.session_state['center']["lat"], st.session_state['center']["lng"]], zoom_start=16)
# Leaflet.jsのDrawプラグインを追加
draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': False, 'circlemarker': False}
draw = folium.plugins.Draw(export=False, position='topleft', draw_options=draw_options)
draw.add_to(m)

st.session_state['map'] = m
st_data = st_folium(st.session_state['map'], width=725)

# 地図のデータをコピー
data = copy.deepcopy(dict(st_data))
st.session_state["center"] = data["center"]

# st.write(data)

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
                    append_list = [dict() for _ in range(len(st.session_state['draw_data']))]
                    st.session_state['tuuka_list'] = append_list

                    # ゲートとIDの組み合わせごとにループ
                    for idx1, gates in enumerate(st.session_state['gate_data']):
                        for key, values in st.session_state['kiseki_data'].items():

                            # ポリゴンゲートのときは初期座標をチェック
                            if gates[0] == gates[-1]:
                                if ingate(values[0]["座標"][0], gates):
                                    st.session_state['tuuka_list'][idx1][key] = values[0]["日時"]
                                    continue  # このIDのループを終了
                                else:
                                    pass

                            kekka = cross_judge(gates, values)
                            if kekka[0]:
                                st.session_state['tuuka_list'][idx1][key] = values[kekka[1]]["日時"]
                                continue  # このIDのループを終了

                    # 図形IDを表示するツールチップを設定
                    tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
                    # 通過人数を表示するポップアップを指定
                    popup_html = '<div style="font-size: 16px; font-weight: bold; width: 110px; height: 20px;  color: #27b9cc;">通過人数：{}人</div>'.format(
                        len(st.session_state['tuuka_list'][idx]))
                    folium.GeoJson(sdata, tooltip=tooltip_html, popup=folium.Popup(popup_html)).add_to(
                        st.session_state['map'])

                else:
                    # 図形IDを表示するツールチップを設定
                    tooltip_html = '<div style="font-size: 16px;">gateid：{}</div>'.format(idx + 1)
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

# st.session_state["cols"][0].subheader("地図の全描画データ")
# st.session_state["cols"][0].write(st.session_state['draw_data'])
# st.session_state["cols"][0].write(st.session_state['gate_data'])
if len(st.session_state['df']) != 0 and len(st.session_state['gate_data']):
    # マルチセレクトに加えるIDリストを生成
    available_ids = [str(value) for value in range(1, len(st.session_state['gate_data']) + 1) if
                     len(st.session_state['tuuka_list'][value - 1]) > 0]

    # st.multiselectを呼び出し
    st.multiselect(
        "グラフを表示したい図形のIDを選択してください",
        available_ids,  # 上記で生成したリストを使用
        key="select_graph_ids",
        on_change=select_graph
    )

    if len(st.session_state["select_graph_ids"]) != 0:
        fig = go.Figure()
        diff = len(st.session_state['tuuka_list']) - len(st.session_state["select_graph_ids"])
        y_values = []  # 全折れ線のy値を保持するリストを初期化
        for idx in st.session_state["select_graph_ids"]:
            # st.session_stateから選択された図形のIDに対応するグラフのJSONデータを取得
            graph_json = st.session_state['graph_data'][idx]

            # JSONデータをPythonオブジェクトに変換
            fig_dict = json.loads(graph_json)

            # 折れ線のy値をリストに追加
            y_values.extend(trace['y'] for trace in fig_dict['data'])

            # PlotlyのFigureオブジェクトにトレースを追加
            for trace in fig_dict['data']:
                # 凡例を変更する場合は、nameプロパティを設定する
                name = f"図形{idx}"
                fig.add_trace(go.Scatter(x=trace['x'], y=trace['y'], mode=trace['mode'], name=name))

            # PlotlyのFigureオブジェクトに戻す
            # fig = go.Figure(fig_dict)

            # fig_list.append(fig)

        # 全折れ線のy値の最大値を取得
        max_y_value = max(max(y) for y in y_values)

        # 目盛りの間隔を設定
        if max_y_value > 5:
            dtick_value = 5
        else:
            dtick_value = 1

        # グラフのレイアウトを設定
        layout = go.Layout(
            title='通過人数',
            xaxis=dict(title='日時', dtick=6),
            yaxis=dict(
                title='通過人数[人]',
                tickvals=list(range(0, max_y_value + 1, dtick_value)) + [max_y_value],  # 目盛りの間隔を設定
                tickformat='d',  # 整数表示に設定
            )
        )

        fig.update_layout(layout)

        # グラフを表示
        st.plotly_chart(fig)
        st.write(max_y_value)
        st.write(len(st.session_state['graph_data']))

with st.sidebar:
    # タブ
    tab1, tab2, tab3, tab4 = st.tabs(["Uploader", "Data_info", "Gate_info", "Kiseki_info"])

    # csvのuploader
    with tab1:
        # CSVファイルのアップロード
        st.file_uploader("CSVファイルをアップロード", type=["csv"], key="upload_csvfile", on_change=upload_csv)
        st.write(st.session_state["upload_csvfile"])

    # csvから読み込んだIDの表示とプロットするマーカー・軌跡の選択
    with tab2:
        st.write(st.session_state['df_new'])
        if len(st.session_state['df']) != 0:
            st.multiselect("選択してください", st.session_state['df'].iloc[:, 0].unique(), key="select_data_id",
                           on_change=select_data)

    # 図形の情報の選択と削除
    with tab3:
        if len(st.session_state['draw_data']) != 0:
            st.selectbox("表示したい図形のIDを選択してください",
                         [""] + [str(value) for value in range(1, len(st.session_state['gate_data']) + 1)],
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