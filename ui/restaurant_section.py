"""
Restaurant Discovery Section Component
Handles restaurant discovery and display
"""

import streamlit as st
import pandas as pd
from utils.services import get_restaurants_and_hangouts


def render_restaurant_section(location, preferences):
    """
    Renders the restaurant discovery section.
    
    Args:
        location (str): User's location
        preferences (str): User's preference filter
    """
    if not location.strip() or preferences not in ["Any", "Food"]:
        return

    try:
        st.divider()
        st.subheader("Nearby Restaurants")

        # Create cache key for restaurants
        cache_key_rest = f"restaurants_{location.lower()}"

        if cache_key_rest not in st.session_state:
            print(f"\n[APP] Fetching restaurants for location: {location}")

            with st.spinner("Searching nearby restaurants..."):
                places_data = get_restaurants_and_hangouts(location)

            st.session_state[cache_key_rest] = places_data
            st.success("Restaurant data loaded!")
        else:
            print(f"[APP] Using cached restaurant data for: {location}")
            places_data = st.session_state[cache_key_rest]

        # Display Restaurant Source Status
        st.markdown("**Data Sources:**")
        col1, col2 = st.columns(2)
        with col1:
            if places_data.get('restaurant_source') == 'osm':
                st.success(f"Restaurants: OpenStreetMap (Real Data)")
            else:
                st.info(f"Restaurants: Fallback Data")
        with col2:
            st.caption(f"Location: {location}")

        # Display map and list
        _display_restaurant_map(places_data)
        _display_restaurant_list(places_data)

    except Exception as restaurant_error:
        print(f"[APP] Restaurant section error: {str(restaurant_error)}")
        st.error("Error loading restaurants. Please try again with a different location.")


def _display_restaurant_map(places_data):
    """Display restaurant locations on map."""
    if not places_data.get('restaurants') or not places_data.get('user_lat'):
        return

    st.markdown("### Restaurant Locations Map")

    try:
        map_data = []

        # Add user location
        map_data.append({
            'lat': places_data['user_lat'],
            'lon': places_data['user_lon'],
        })

        # Add restaurants
        for restaurant in places_data.get('restaurants', [])[:10]:
            map_data.append({
                'lat': restaurant['lat'],
                'lon': restaurant['lon'],
            })

        map_df = pd.DataFrame(map_data)
        st.map(map_df[['lat', 'lon']], zoom=12, use_container_width=True)

        st.caption(
            f"Your Location (Source) | Restaurants (Destinations) - "
            f"showing {min(10, len(places_data.get('restaurants', [])))} restaurants"
        )

    except Exception as map_error:
        print(f"[APP] Restaurant map error: {str(map_error)}")
        st.info("Map unavailable")


def _display_restaurant_list(places_data):
    """Display restaurant list."""
    st.markdown("### Nearby Restaurants")

    if places_data.get('restaurants'):
        for i, restaurant in enumerate(places_data['restaurants'][:10], 1):
            col_info = st.columns([3, 1])
            with col_info[0]:
                st.write(f"**{i}. {restaurant['name']}**")
                st.caption(
                    f"{restaurant['distance']} km | "
                    f"₹{restaurant.get('estimated_cost', '---')} avg | "
                    f"{restaurant.get('type', 'Restaurant')}"
                )
            with col_info[1]:
                st.metric("Distance", f"{restaurant['distance']} km")

        if len(places_data['restaurants']) > 10:
            st.caption(f"... and {len(places_data['restaurants']) - 10} more restaurants")
    else:
        st.info("No restaurants found")
