"""
Hangout Discovery Section Component
Handles hangout place discovery and display
"""

import streamlit as st
import pandas as pd
from utils.services import get_restaurants_and_hangouts


def render_hangout_section(location, preferences):
    """
    Renders the hangout place discovery section.
    
    Args:
        location (str): User's location
        preferences (str): User's preference filter
    """
    if not location.strip() or preferences not in ["Any", "Hangout"]:
        return

    try:
        st.divider()
        st.subheader("Nearby Hangout Places")

        # Create cache key for hangouts
        cache_key_hang = f"hangouts_{location.lower()}"

        if cache_key_hang not in st.session_state:
            print(f"\n[APP] Fetching hangout places for location: {location}")

            with st.spinner("Searching nearby hangout places..."):
                places_data = get_restaurants_and_hangouts(location)

            st.session_state[cache_key_hang] = places_data
            st.success("Hangout data loaded!")
        else:
            print(f"[APP] Using cached hangout data for: {location}")
            places_data = st.session_state[cache_key_hang]

        # Display Hangout Source Status
        st.markdown("**Data Sources:**")
        col1, col2 = st.columns(2)
        with col1:
            if places_data.get('hangout_source') == 'osm':
                st.success(f"Hangouts: OpenStreetMap (Real Data)")
            else:
                st.info(f"Hangouts: Fallback Data")
        with col2:
            st.caption(f"Location: {location}")

        # Display map and list
        _display_hangout_map(places_data)
        _display_hangout_list(places_data)

    except Exception as hangout_error:
        print(f"[APP] Hangout section error: {str(hangout_error)}")
        st.error("Error loading hangout places. Please try again with a different location.")


def _display_hangout_map(places_data):
    """Display hangout locations on map."""
    if not places_data.get('hangouts') or not places_data.get('user_lat'):
        return

    st.markdown("### Hangout Locations Map")

    try:
        map_data = []

        # Add user location
        map_data.append({
            'lat': places_data['user_lat'],
            'lon': places_data['user_lon'],
        })

        # Add hangouts
        for hangout in places_data.get('hangouts', [])[:10]:
            map_data.append({
                'lat': hangout['lat'],
                'lon': hangout['lon'],
            })

        map_df = pd.DataFrame(map_data)
        st.map(map_df[['lat', 'lon']], zoom=12, use_container_width=True)

        st.caption(
            f"Your Location (Source) | Hangout Places (Destinations) - "
            f"showing {min(10, len(places_data.get('hangouts', [])))} places"
        )

    except Exception as map_error:
        print(f"[APP] Hangout map error: {str(map_error)}")
        st.info("Map unavailable")


def _display_hangout_list(places_data):
    """Display hangout place list."""
    st.markdown("### Nearby Hangout Places")

    if places_data.get('hangouts'):
        for i, hangout in enumerate(places_data['hangouts'][:10], 1):
            col_info = st.columns([3, 1])
            with col_info[0]:
                st.write(f"**{i}. {hangout['name']}**")
                st.caption(
                    f"{hangout['distance']} km | "
                    f"{hangout.get('type', 'Attraction')}"
                )
            with col_info[1]:
                st.metric("Distance", f"{hangout['distance']} km")

        if len(places_data['hangouts']) > 10:
            st.caption(f"... and {len(places_data['hangouts']) - 10} more places")
    else:
        st.info("No hangout places found")
