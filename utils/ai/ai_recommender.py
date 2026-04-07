import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class AIRecommender:
    """AI-powered recommendation engine using Google Gemini API with fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        # Using gemini-2.5-flash for better compatibility
        self.model = "gemini-2.5-flash"  # Updated to a more recent model for better performance
        self.base_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 3600  # 1 hour cache duration
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached response is still valid."""
        if cache_key not in self.cache:
            return False
        cached_time, _ = self.cache[cache_key]
        return datetime.now() - cached_time < timedelta(seconds=self.cache_duration)
    
    def _get_fallback_advice(self, mood: str, budget: int, total: int) -> str:
        """Generate fallback advice when API is unavailable."""
        status = self._get_budget_status(total, budget)
        remaining = budget - total
        
        fallback_tips = {
            "Happy": f"Great mood for spending! You have ₹{remaining} left - consider rewarding yourself with your favorite activity.",
            "Sad": f"Cheer up! Spending ₹{total} on activities you enjoy can help lift your mood. Consider saving ₹{remaining} for a special treat.",
            "Bored": f"Breaking the monotony! Your plan costs ₹{total}. Try mixing up the order of activities to maximize enjoyment.",
            "Romantic": f"Perfect for a memorable experience! You're spending ₹{total} with ₹{remaining} flexibility. Make it special.",
            "Stressed": f"Self-care matters! Your spending of ₹{total} is {status}. Don't forget to relax and enjoy the experience."
        }
        
        return fallback_tips.get(mood, f"Your spending is {status}. Budget used: ₹{total}/{budget}. {remaining} remaining.")
    
    def _call_gemini_api(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7, cache_key: str = None) -> Dict:
        """Make API call to Gemini with caching and fallback."""
        # Check cache first
        if cache_key and self._is_cache_valid(cache_key):
            _, cached_response = self.cache[cache_key]
            return cached_response
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "success": True,
                    "content": data['candidates'][0]['content']['parts'][0]['text']
                }
                # Cache successful response
                if cache_key:
                    self.cache[cache_key] = (datetime.now(), result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"API error {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_budget_balanced_recommendations(
        self, mood: str, budget: int, location: str, current_recommendations: Dict
    ) -> Dict:
        """AI budget balancing advice with fallback."""
        food = current_recommendations.get('food', {})
        movie = current_recommendations.get('movie', {})
        place = current_recommendations.get('place', {})
        total = food.get('cost', 0) + movie.get('cost', 0) + place.get('cost', 0)
        
        # Use mood-based cache key
        cache_key = f"budget_{mood}_{budget}_{location}"
        
        prompt = f"""Smart spending advisor for SpendMate app. Analyze and provide budget balancing advice.

User: Mood={mood}, Budget=₹{budget}, Location={location}
Current: Food {food.get('name')} ₹{food.get('cost')}, Movie {movie.get('name')} ₹{movie.get('cost')}, Place {place.get('name')} ₹{place.get('cost')}
Total: ₹{total} | Status: {self._get_budget_status(total, budget)}

Provide: (1) Within budget? (2) Budget allocation balance? (3) Mood-based suggestions (4) Alternatives (5) Spending health tips
Keep concise and practical."""

        result = self._call_gemini_api(prompt, max_tokens=500, temperature=0.7, cache_key=cache_key)
        
        if result['success']:
            return {
                "success": True,
                "ai_advice": result['content'],
                "current_total": total,
                "budget": budget,
                "budget_status": self._get_budget_status(total, budget),
                "savings_potential": max(0, budget - total),
                "budget_used_percentage": (total / budget * 100) if budget > 0 else 0
            }
        
        # Fallback when API fails
        fallback = self._get_fallback_advice(mood, budget, total)
        return {
            "success": True,  # Return as success to show fallback
            "ai_advice": fallback,
            "current_total": total,
            "budget": budget,
            "budget_status": self._get_budget_status(total, budget),
            "savings_potential": max(0, budget - total),
            "budget_used_percentage": (total / budget * 100) if budget > 0 else 0,
            "is_fallback": True
        }
    
    def optimize_for_budget(
        self, mood: str, budget: int, location: str, available_options: Dict[str, List[Dict]]
    ) -> Dict:
        """AI-powered budget optimization with fallback."""
        options_text = "\n".join([
            f"{cat.upper()}: " + ", ".join([f"{item.get('name')} ₹{item.get('cost')}" for item in items])
            for cat, items in available_options.items()
        ])
        
        cache_key = f"optimize_{mood}_{budget}_{location}"
        
        prompt = f"""Budget optimizer for {location}. Find best combination for mood "{mood}" and budget ₹{budget}.

Available:
{options_text}

Select 1 food, 1 movie, 1 place within ₹{budget}. Format: Food: name (₹X), Movie: name (₹X), Place: name (₹X), Total: ₹X, Why: brief reason"""

        result = self._call_gemini_api(prompt, max_tokens=400, temperature=0.7, cache_key=cache_key)
        
        if result['success']:
            return {"success": True, "optimization": result['content']}
        
        # Fallback - simple recommendation
        fallback = "Unable to optimize right now. Choose items that match your mood and stay within your budget. Mix high, medium, and low-cost options for variety."
        return {"success": True, "optimization": fallback, "is_fallback": True}
    
    def _get_fallback_tips(self, mood: str, budget: int, spending: int) -> str:
        """Generate fallback money-saving tips when API is unavailable."""
        remaining = budget - spending
        generic_tips = f"""
1. **Smart Category Split**: Allocate 30% to food, 40% to entertainment, 30% to experiences.

2. **Timing is Money**: Visit restaurants during off-peak hours for better deals. Matinee shows cost less than evening shows.

3. **Group Discounts**: Invite friends! Many places offer group discounts or couple packages.

4. **Review Before You Go**: Check ratings and reviews to avoid high-cost regrets. Spend ₹{remaining} wisely on quality over quantity.

5. **Set Limits**: Decide on a per-category budget upfront. You have ₹{budget} total - stick to it!
"""
        return generic_tips
    
    def get_personalized_tips(self, mood: str, budget: int, current_spending: int, location: str) -> Dict:
        """Get personalized money-saving tips with fallback."""
        remaining = budget - current_spending
        cache_key = f"tips_{mood}_{budget}_{current_spending}"
        
        prompt = f"""Finance advisor tips for {location}. User: Mood={mood}, Budget=₹{budget}, Spending=₹{current_spending}, Remaining=₹{remaining}

Provide 3-4 practical, mood-appropriate money-saving tips (1-2 sentences each). No budget exceeded."""

        result = self._call_gemini_api(prompt, max_tokens=300, temperature=0.8, cache_key=cache_key)
        
        if result['success']:
            return {
                "success": True,
                "tips": result['content'],
                "remaining_budget": remaining,
                "efficiency_score": self._calculate_efficiency(current_spending, budget)
            }
        
        # Fallback tips
        return {
            "success": True,  # Return as success to show fallback
            "tips": self._get_fallback_tips(mood, budget, current_spending),
            "remaining_budget": remaining,
            "efficiency_score": self._calculate_efficiency(current_spending, budget),
            "is_fallback": True
        }
    
    @staticmethod
    def _get_budget_status(current: int, budget: int) -> str:
        """Budget status based on spending."""
        if current <= 0:
            return "No spending planned"
        ratio = current / budget if budget > 0 else 0
        if ratio < 0.5:
            return "Well within budget"
        elif ratio <= 0.75:
            return "Moderately within budget"
        elif ratio <= 1.0:
            return "At budget limit"
        return "Over budget"
    
    @staticmethod
    def _calculate_efficiency(spending: int, budget: int) -> float:
        """Budget efficiency score (0-100)."""
        if budget <= 0:
            return 0
        ratio = spending / budget
        if ratio <= 0.5:
            return 95.0
        elif ratio <= 0.75:
            return 85.0
        elif ratio <= 1.0:
            return 75.0
        return max(0, 50 - (ratio - 1) * 50)


def create_ai_recommender(api_key: Optional[str] = None) -> AIRecommender:
    """Factory function to create AIRecommender instance."""
    return AIRecommender(api_key)
