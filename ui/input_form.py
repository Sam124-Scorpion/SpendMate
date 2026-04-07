"""
Input Form UI Component
Handles user preference selection (mood, budget, location, preferences)
"""

import streamlit as st


def render_input_form():
    """
    Renders the input form for user preferences.
    
    Returns:
        dict: User inputs with keys: budget, mood, location, preferences
    """
    st.subheader("Enter Your Preferences")
    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input(
            "Enter Your Budget (₹)",
            min_value=100,
            max_value=10000,
            step=50
        )
        mood = st.selectbox(
            "Select Your Mood",
            ["Happy 😊", "Sad 😔", "Bored 😐", "Romantic ❤️", "Stressed 😤"]
        )

    with col2:
        location = st.text_input(
            "Enter Your Location",
            value=st.session_state.get("location_input", ""),
            placeholder="Example : Kolkata",
            key="location_input"
        )
        preferences = st.selectbox(
            "What are u looking for?",
            ["Any", "Food", "Movie", "Hangout"]
        )

    st.divider()

    return {
        'budget': budget,
        'mood': mood,
        'location': location,
        'preferences': preferences
    }
