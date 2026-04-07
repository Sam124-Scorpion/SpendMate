"""
Map Helper Functions
Reusable utilities for displaying location maps
"""

import streamlit as st
import pandas as pd


def create_location_map(locations_data, title="Map"):
    """
    Create and display a location map.
    
    Args:
        locations_data (list): List of dicts with 'lat', 'lon', 'name' keys
        title (str): Map section title
        
    Returns:
        bool: True if map displayed successfully, False otherwise
    """
    try:
        st.markdown(f"### {title}")
        
        map_df = pd.DataFrame(locations_data)
        st.map(map_df[['lat', 'lon']], zoom=12, use_container_width=True)
        return True
        
    except Exception as map_error:
        print(f"[APP] Map error: {str(map_error)}")
        st.info("Map unavailable - showing list instead")
        return False


def display_data_source_status(source_dict, columns=2):
    """
    Display data source status badges.
    
    Args:
        source_dict (dict): Dictionary with source information (e.g., 'osm', 'nominatim')
        columns (int): Number of columns for layout
    """
    st.markdown("**Data Sources:**")
    cols = st.columns(columns)
    
    source_items = list(source_dict.items())
    for idx, (label, source) in enumerate(source_items):
        with cols[idx % columns]:
            if source == 'osm':
                st.success(f"{label.title()}: OpenStreetMap (Real Data)")
            elif source == 'nominatim':
                st.success(f"{label.title()}: Nominatim API (Fallback)")
            elif source == 'api':
                st.success(f"{label.title()}: Live API")
            else:
                st.info(f"{label.title()}: Fallback Data")
