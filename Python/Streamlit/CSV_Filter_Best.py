import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import seaborn as sns

st.set_page_config(page_title="Titanic Shows", layout="wide") 
st.title("Titanic shows analysis")

st.session_state["csv"] = sns.load_dataset('titanic')
gb = GridOptionsBuilder.from_dataframe(st.session_state["csv"])

# ---
gb.configure_pagination()
gb.configure_side_bar()
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
gridOptions = gb.build()

if st.button("update"):
    st.write("update finish")

st.session_state["grid"] = AgGrid(st.session_state["csv"], gridOptions=gridOptions, enable_enterprise_modules=True, reload_data=True, key="data")


# st.write(st.session_state["grid"].data["type"].value_counts())
# st.write(st.session_state["csv"]["type"].value_counts())

# ダウンロードボタンを追加
# st.download_button(label="Download CSV", data=st.session_state["csv"].to_csv(index=False), file_name='sorted.csv')
st.download_button(label="Download CSV", data=pd.DataFrame(st.session_state["grid"].data).to_csv(index=False), file_name='sorted.csv')
