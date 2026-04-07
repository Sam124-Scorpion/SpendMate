"""
SpendMate - AI Smart Spending Companion
Main Application Entry Point (Simplified)

This app provides personalized spending recommendations based on:
- Mood and budget
- Current location
- Real-time theatre, restaurant, and hangout discoveries
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Import modular UI components
from ui import (
    render_input_form,
    render_recommendations,
    render_theatre_section,
    render_restaurant_section,
    render_hangout_section
)

# Import API modules
from utils.ai import get_recommendations_from_api

# Load environment variables
load_dotenv()


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="SpendWise - AI Smart Spending Companion",
    page_icon="💰",
    layout="centered"
)

gemini_key = os.getenv("GEMINI_API_KEY")

st.title("💰 SpendWise – AI Smart Spending Companion")
st.write("Get smart spending suggestions based on your mood, budget and location")
st.divider()


# ==========================================
# USER INPUT
# ==========================================

user_input = render_input_form()
budget = user_input['budget']
mood = user_input['mood']
location = user_input['location']
preferences = user_input['preferences']

# Submit Button
if st.button("Get Smarter Suggestions"):
    print(f"\n{'='*60}")
    print(f"[APP] User clicked 'Get Smarter Suggestions'")
    print(f"[APP] Input - Mood: {mood}, Budget: {budget}, Location: {location}, Preference: {preferences}")
    print(f"{'='*60}\n")

    # Get recommendations from Gemini API
    result = get_recommendations_from_api(mood.split(" ")[0], budget, location)

    if result and result.get("status") == "success":
        print(f"[APP] Got API recommendations successfully")

        # ==========================================
        # DISPLAY RECOMMENDATIONS
        # ==========================================
        render_recommendations(result, budget)

        # ==========================================
        # DISPLAY LOCATION-BASED DISCOVERIES
        # ==========================================

        render_theatre_section(location, preferences)
        render_restaurant_section(location, preferences)
        render_hangout_section(location, preferences)

        # ==========================================
        # FINAL STATUS
        # ==========================================

        st.divider()

        if gemini_key:
            print(f"\n[APP] AI recommendations already provided at top of page")
        else:
            print(f"[APP] No Gemini API key found in .env")
            st.error("Gemini API key not found. Add GEMINI_API_KEY to .env file to enable AI features.")

        print(f"\n{'='*60}")
        print(f"[APP] API-only recommendation flow completed successfully!")
        print(f"{'='*60}\n")

    else:
        print(f"\n[APP] Failed to get API recommendations")
        st.error('Could not generate recommendations from API. Please check your Gemini API key.')
