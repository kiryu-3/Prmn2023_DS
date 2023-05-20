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
        m = folium.Map(location=[39.949610, -75.150282], zoom_start=16)
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
    st_data
    st.write(st_data.get("center"))
    data = dict(st_data)
    st.write(type(data))

