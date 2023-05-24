import streamlit as st
import pandas as pd

# サンプルのDataFrameを作成します
data = {
    'Name': ['John', 'Emily', 'Michael'],
    'Age': [25, 30, 35],
    'City': ['New York', 'London', 'Paris']
}
df = pd.DataFrame(data)

# DataFrameを表示します
st.write(df)

# ユーザーが行をクリックしたときに実行される関数
def process_row(row):
    # 選択された行のデータを表示します
    st.write("選択された行のデータ:")
    st.write(row)

    # 選択された行に対して処理を施す例（ここでは年齢を2倍にします）
    processed_age = row['Age'] * 2
    st.write("処理後の年齢:", processed_age)

# 行のクリックイベントを処理するコールバック関数
def on_click(row):
    process_row(row)

# DataFrameの各行に対してクリックイベントを設定します
for index, row in df.iterrows():
    # クリックイベントを設定するために一意のキーを作成します
    key = f"row-{index}"
    # 行を表示します
    st.write(row, key=key)
    # クリックイベントを設定します
    st.button(label="処理する", key=key, on_click=on_click, args=(row,))

