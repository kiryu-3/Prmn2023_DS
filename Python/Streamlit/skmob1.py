import streamlit as st
import folium
from streamlit_folium import folium_static
import skmob
from datetime import datetime
import pandas as pd

# Streamlitアプリケーションの設定
st.title("移動データ可視化アプリ")

# CSVファイルをアップロード
uploaded_file = st.file_uploader("CSVファイルをアップロード", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # scikit-mobilityのTrajDataFrameを作成
    traj_df = skmob.TrajDataFrame(df, timestamp=True)

    # 地図の初期設定
    m = folium.Map(location=[traj_df.columns[3].mean(), traj_df.columns[2].mean()], zoom_start=12)

    # 移動経路のプロット（streamlit-foliumを使用）
    for _, row in traj_df.iterrows():
        folium.CircleMarker(location=(row.columns[3], row.columns[2]), radius=5, color='blue').add_to(m)

    # 地図の表示
    folium_static(m)
