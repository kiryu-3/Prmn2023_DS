import streamlit as st

def multi_file_uploader(label, key):
    uploaded_files = st.file_uploader(label, key=key, accept_multiple_files=True, type=["csv"])
    return uploaded_files

# 使用例
uploaded_files = multi_file_uploader("複数のファイルを選択してください", "file_uploader")

# 選択されたファイルを表示する例
if uploaded_files:
    for file in uploaded_files:
        file_data = file.read()
        # バイナリデータからPandas DataFrameを作成
        df = pd.read_csv(io.BytesIO(file_data))
        df.to_excel(buf := BytesIO(), index=False)
        st.download_button(
        "Download",
        buf.getvalue(),
        "sample.csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
