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

    # Display AI Advice with source indicator
    st.markdown("### Your Personalized Plan")
    source = result.get('source', 'unknown')
    source_badge = " **Gemini AI**" if source == "gemini" else " **Fallback Response**"
    st.markdown(f"**Source:** {source_badge}")
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

    # Money-Saving Tips with source indicator
    if result.get('efficiency_score', 0) > 0:
        st.divider()
        st.subheader("Money-Saving Tips")
        tips_source = result.get('tips_source', 'unknown')
        tips_badge = " **Gemini AI**" if tips_source == "gemini" else " **Fallback Response**"
        st.write(f"**Efficiency Score:** {result.get('efficiency_score', 0):.1f}/100")
        st.markdown(f"**Source:** {tips_badge}")
        st.markdown(result.get('tips', 'No tips available'))

    # Show Location Services Header
    st.divider()
    st.subheader("Location-Based Services")
    st.info("**Now discovering nearby places based on your location and preference...**")
