import streamlit as st
import pandas as pd

# サンプルのDataFrameを作成
data = {'Name': ['John', 'Emily', 'Sam', 'Alice'],
        'Age': [25, 30, 35, 40]}
df = pd.DataFrame(data)

# DataFrameを表示
selected_index = st.table(df)

# 選択された行のインデックスを取得
if selected_index is not None:
    selected_row = df.loc[selected_index]
    st.write("Selected Row:")
    st.write(selected_row)

    # 選択された行に対して処理を施す関数
    def process_selected_row(row):
        # ここで行に対する処理を行う
        # 例えば、行の特定の列の値を取得するなど
        name = row['Name']
        age = row['Age']
        st.write(f"Name: {name}, Age: {age}")

    # 選択された行に対して処理を施す
    process_selected_row(selected_row)
