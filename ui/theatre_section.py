"""
Theatre Discovery Section Component
Handles theatre and movie display
"""

import streamlit as st
import pandas as pd
from utils.services import get_theatres_with_movies


def render_theatre_section(location, preferences):
    """
    Renders the theatre discovery section.
    
    Args:
        location (str): User's location
        preferences (str): User's preference filter
    """
    if not location.strip() or preferences not in ["Any", "Movie"]:
        return

    try:
        st.divider()
        st.subheader("Nearby Theatres & Now Playing Movies")

        # Create cache key for this location
        cache_key = f"theatre_data_{location.lower()}"

        # Check if we already have this data cached
        if cache_key not in st.session_state:
            print(f"\n[APP] Fetching theatres for location: {location}")

            with st.spinner("Searching nearby theatres and movies..."):
                theatre_data = get_theatres_with_movies(location)

            # Cache the data in session state
            st.session_state[cache_key] = theatre_data
            st.success("Theatre data loaded!")
        else:
            print(f"[APP] Using cached theatre data for: {location}")
            theatre_data = st.session_state[cache_key]

        # Show data source and error status
        if 'error' in theatre_data:
            st.warning(f"{theatre_data['error']}")

        # Display Theatre Source Status
        st.markdown("**Data Sources:**")
        col1, col2 = st.columns(2)
        with col1:
            if theatre_data['theatre_source'] == 'osm':
                st.success(f"Theatres: OpenStreetMap (Overpass API)")
            elif theatre_data['theatre_source'] == 'nominatim':
                st.success(f"Theatres: Nominatim API (Fallback)")
            else:
                st.info(f"Theatres: Hardcoded Fallback Data")
        with col2:
            if theatre_data['movie_source'] == 'api':
                st.success(f"Movies: Live TMDB API")
            else:
                st.info(f"Movies: Fallback Data")

        # Display Theatres with Map
        _display_theatre_map(theatre_data)
        _display_theatre_list(theatre_data)
        _display_movies(theatre_data)

    except Exception as theatre_error:
        print(f"[APP] Theatre section error: {str(theatre_error)}")
        st.error("Error loading theatres. Please try again with a different location.")


def _display_theatre_map(theatre_data):
    """Display theatre locations on map."""
    if not theatre_data['theatres'] or not theatre_data['user_lat'] or not theatre_data['user_lon']:
        return

    st.markdown("### Theatre Locations Map")

    try:
        map_data = []

        # Add user location
        map_data.append({
            'lat': theatre_data['user_lat'],
            'lon': theatre_data['user_lon'],
            'name': 'Your Location'
        })

        # Add theatre locations
        for theatre in theatre_data['theatres'][:10]:
            map_data.append({
                'lat': theatre['lat'],
                'lon': theatre['lon'],
                'name': f"{theatre['name']} ({theatre['distance']} km)"
            })

        # Display map
        map_df = pd.DataFrame(map_data)
        st.map(map_df[['lat', 'lon']], zoom=12, use_container_width=True)

        st.caption(
            f"Your Location (Source) | Theatres (Destinations) - "
            f"showing {min(10, len(theatre_data['theatres']))} of {len(theatre_data['theatres'])} found"
        )

    except Exception as map_error:
        print(f"[APP] Map error: {str(map_error)}")
        st.info("Map unavailable - showing theatre list instead")


def _display_theatre_list(theatre_data):
    """Display theatre list."""
    if not theatre_data['theatres']:
        return

    st.markdown("### Nearby Theatres")

    for i, theatre in enumerate(theatre_data['theatres'][:10], 1):
        st.write(
            f"**{i}. {theatre['name']}** • {theatre['distance']} km • "
            f"{theatre['lat']:.4f}, {theatre['lon']:.4f}"
        )

    if len(theatre_data['theatres']) > 10:
        st.caption(f"... and {len(theatre_data['theatres']) - 10} more theatres")


def _display_movies(theatre_data):
    """Display now playing movies."""
    st.markdown("### Now Playing Movies")

    if not theatre_data['movies']:
        st.info("No movies found")
        return

    try:
        st.caption(f"Found {len(theatre_data['movies'])} movies")

        # Create columns for movie grid
        cols = st.columns(3)

        for idx, movie in enumerate(theatre_data['movies'][:9]):
            with cols[idx % 3]:
                st.write(f"**{movie['name']}**")
                st.metric("Rating", f"{movie['rating']}/10")

                if movie['release_date']:
                    st.caption(f"{movie['release_date']}")

                if movie['overview']:
                    st.caption(movie['overview'][:60] + "...")

        if len(theatre_data['movies']) > 9:
            st.info(f"Showing 9 of {len(theatre_data['movies'])} movies")

    except Exception as movie_error:
        print(f"[APP] Movie rendering error: {str(movie_error)}")
        st.warning("Error displaying movies")

        # Simple fallback list
        for i, movie in enumerate(theatre_data['movies'][:5], 1):
            st.write(f"{i}. **{movie['name']}** - {movie['rating']}/10")
