import streamlit as st
import json

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)


left, right = st.columns(2)


with left:
    with st.echo():

        import folium
        import streamlit as st

        from streamlit_folium import st_folium
        from folium import plugins
        from folium.plugins import Draw, TimestampedGeoJson

        # center on Liberty Bell, add marker
        m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)
        folium.Marker(
            [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
        ).add_to(m)
        # Leaflet.jsのDrawプラグインを追加
        draw_options = {'polyline': True, 'rectangle': True, 'circle': True, 'marker': True, 'circlemarker': True}
        draw = folium.plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=draw_options)
        draw.add_to(m)

        # call to render Folium map in Streamlit
        st_data = st_folium(m, width=725)

with right:
    data = dict(st_data)
    st.subheader("地図の全データ")
    st.write(data)
    st.subheader("地図の全描画データ")
    st.write(data["all_drawings"])
    if "all_drawings" in st_data:
        if 0 in st_data["all_drawings"][0]:
            st_data["all_drawings"][0][0]["properties"] = "0"
            st_data["all_drawings"][0]
         
    st.subheader("最後に描画した円の半径データ")
    st.write(data["last_circle_radius"])
    st.subheader("最後に描画した円の全データ")
    st.write(data["last_circle_polygon"])
