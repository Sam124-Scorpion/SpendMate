"""
AI Recommendations Display Component
Shows personalized plan, budget analysis, and money-saving tips
"""

import streamlit as st


def render_recommendations(result, budget):
    """
    Renders AI-powered recommendations section.
    
    Args:
        result (dict): Recommendation data from Gemini API
        budget (int): User's budget in rupees
    """
    st.divider()
    st.subheader("AI-Powered Recommendations")

    # Show source badge
    st.info("**ALL recommendations powered by Gemini API (No CSV data)**")

    # Display AI Advice
    st.markdown("### Your Personalized Plan")
    st.markdown(result.get('ai_advice', 'No advice available'))

    # Budget Analysis
    st.divider()
    st.subheader("Budget Analysis")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Budget", f"₹{budget}")
    with col2:
        st.metric("Budget Used", f"{result.get('budget_used_percentage', 0):.1f}%")
    with col3:
        st.metric("Savings", f"₹{result.get('savings_potential', 0)}")

    # Money-Saving Tips
    if result.get('efficiency_score', 0) > 0:
        st.divider()
        st.subheader("Money-Saving Tips")
        st.write(f"**Efficiency Score:** {result.get('efficiency_score', 0):.1f}/100")
        st.markdown(result.get('tips', 'No tips available'))

    # Show Location Services Header
    st.divider()
    st.subheader("Location-Based Services")
    st.info("**Now discovering nearby places based on your location and preference...**")
