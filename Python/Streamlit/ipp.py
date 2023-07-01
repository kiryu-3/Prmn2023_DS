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

if 'map' not in st.session_state: # Initialization
    # Display an empty map for the first time
    m = folium.Map(location=[42.793553, 141.6958724], zoom_start=16)
    # Add the Leaflet.js Draw plugin
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
    
if 'draw_data' not in st.session_state: # Initialization
    st.session_state['draw_data'] = list()  
if 'df' not in st.session_state: # Initialization
    df = pd.DataFrame()
    st.session_state['df'] = df
if 'kiseki' not in st.session_state: # Initialization
    st.session_state['kiseki'] = False
if 'kiseki_data' not in st.session_state: # Initialization
    st.session_state['kiseki_data'] = dict() 
if 'gate_data' not in st.session_state: # Initialization
    st.session_state['gate_data'] = list()     
if "line_geojson" not in st.session_state: # Initialization
    st.session_state['line_geojson'] = None
if "tuuka_list" not in st.session_state: # Initialization
    st.session_state['tuuka_list'] = list()

def are_lines_intersecting(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    # Calculate the equations of the lines
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1 * x1 + b1 * y1

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2 * x3 + b2 * y3

    # Check for intersection
    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        # The two lines are parallel
        return.
