"""
API-Only Recommendation System - Uses only Gemini API
No CSV fallback data - pure API-driven recommendations
"""

import os
from dotenv import load_dotenv
from .ai_recommender import create_ai_recommender

load_dotenv()

def get_recommendations_from_api(mood, budget, location):
    """
    Get recommendations ONLY from Gemini API
    No CSV fallback, pure API response
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        print("[RECOMMENDER] ❌ GEMINI_API_KEY not found")
        return None
    
    try:
        # Initialize AI recommender
        ai_recommender = create_ai_recommender(gemini_key)
        
        print(f"[RECOMMENDER] 🤖 Fetching recommendations from Gemini API...")
        print(f"[RECOMMENDER] Mood: {mood}, Budget: ₹{budget}, Location: {location}")
        
        # Create a simple initial recommendation structure to pass
        initial_recommendations = {
            "food": {"name": "Food", "cost": budget // 3},
            "movie": {"name": "Movie", "cost": budget // 3},
            "place": {"name": "Place", "cost": budget // 3}
        }
        
        # Get AI-powered budget balanced recommendations
        ai_result = ai_recommender.get_budget_balanced_recommendations(
            mood=mood,
            budget=budget,
            location=location,
            current_recommendations=initial_recommendations
        )
        
        if not ai_result.get('success'):
            print(f"[RECOMMENDER] ❌ API failed: {ai_result.get('error', 'Unknown error')}")
            return None
        
        # Get Gemini AI tips/suggestions
        tips_result = ai_recommender.get_personalized_tips(
            mood=mood,
            budget=budget,
            current_spending=budget,
            location=location
        )
        
        recommendation = {
            "mood": mood,
            "budget": budget,
            "location": location,
            "ai_advice": ai_result.get('ai_advice', ''),
            "budget_used_percentage": ai_result.get('budget_used_percentage', 0),
            "savings_potential": ai_result.get('savings_potential', 0),
            "efficiency_score": tips_result.get('efficiency_score', 0) if tips_result.get('success') else 0,
            "tips": tips_result.get('tips', '') if tips_result.get('success') else '',
            "source": "api",
            "status": "success"
        }
        
        print(f"[RECOMMENDER] ✅ Successfully got API recommendations")
        return recommendation
        
    except Exception as e:
        print(f"[RECOMMENDER] ❌ Error: {str(e)}")
        return None
