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
        self.model = "gemini-2.5-flash-lite"  # Updated to flash-lite for better performance and cost-efficiency
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
            "Happy": f"**Budget Status**: {status}. **Recommendation**: You have ₹{remaining} remaining. Splurge on your happiest choice—maybe upgrade food or add a dessert. Happiness multiplier: spend on experiences over things.",
            "Sad": f"**Budget Status**: {status}. **Recommendation**: Self-care spend of ₹{total} is wise. Consider a relaxing restaurant (comfort food) + lighter movie. Save ₹{remaining} for spontaneous mood-lifters.",
            "Bored": f"**Budget Status**: {status}. **Recommendation**: Mix high-energy (movie/adventure place) with low-stress food. You have ₹{remaining}—consider adding a unique food experience to break monotony.",
            "Romantic": f"**Budget Status**: {status}. **Recommendation**: Perfect romantic spend of ₹{total}. Go subtle on budget with ₹{remaining} left—use it for ambiance (candles, special seating) rather than quantity.",
            "Stressed": f"**Budget Status**: {status}. **Recommendation**: Relaxation budget is wisely set at ₹{total}. Prioritize calm food + comfort movie. Keep ₹{remaining} as buffer—you deserve zero financial stress today."
        }
        
        return fallback_tips.get(mood, f"**Budget**: {status}. Spent ₹{total}/{budget}. **Remaining**: ₹{remaining}. Allocate remaining for your mood priority to maximize satisfaction.")
    
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
        
        budget_status = self._get_budget_status(total, budget)
        remaining = budget - total
        
        prompt = f"""You are a budget optimization advisor. Analyze this {location} spending plan:

MOOD: {mood} | TOTAL BUDGET: ₹{budget} | SPENT: ₹{total} | REMAINING: ₹{remaining}

SELECTIONS: Food: {food.get('name', 'None')} (₹{food.get('cost', 0)}), Movie: {movie.get('name', 'None')} (₹{movie.get('cost', 0)}), Place: {place.get('name', 'None')} (₹{place.get('cost', 0)})

Respond in 3-4 concise points:
1. **Budget Status**: Is this {budget_status}? Justify briefly.
2. **Allocation**: Is the food-movie-place split wise for {mood} mood?
3. **Optimization**: One specific change to maximize {mood} enjoyment within budget.
4. **Quick Tip**: One actionable money-saving hack for {location}.

Be descriptive but brief (no bullet lists, use bold for emphasis)."""

        result = self._call_gemini_api(prompt, max_tokens=600, temperature=0.7, cache_key=cache_key)
        
        if result['success']:
            return {
                "success": True,
                "ai_advice": result['content'],
                "current_total": total,
                "budget": budget,
                "budget_status": self._get_budget_status(total, budget),
                "savings_potential": max(0, budget - total),
                "budget_used_percentage": (total / budget * 100) if budget > 0 else 0,
                "source": "gemini"
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
            "source": "fallback"
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
        
        prompt = f"""You are a smart budget optimizer for {location}. Find the BEST combo for {mood} mood within ₹{budget}.

MOOD: {mood} | BUDGET: ₹{budget} | LOCATION: {location}

AVAILABLE OPTIONS:
{options_text}

SELECT: 1 food, 1 movie, 1 place that maximize {mood} experience while staying within budget.

RESPONSE FORMAT (concise):
**Selected**: Food: [name] (₹X) | Movie: [name] (₹X) | Place: [name] (₹X)
**Total**: ₹X | **Remaining**: ₹Y
**Why This Combo**: 2-sentence description of why this matches {mood} mood + budget optimization.

Focus: Maximize mood satisfaction + budget balance."""

        result = self._call_gemini_api(prompt, max_tokens=500, temperature=0.7, cache_key=cache_key)
        
        if result['success']:
            return {"success": True, "optimization": result['content'], "source": "gemini"}
        
        # Fallback - simple recommendation
        fallback = "Unable to optimize right now. Choose items that match your mood and stay within your budget. Mix high, medium, and low-cost options for variety."
        return {"success": True, "optimization": fallback, "source": "fallback"}
    
    def _get_fallback_tips(self, mood: str, budget: int, spending: int) -> str:
        """Generate fallback money-saving tips when API is unavailable."""
        remaining = budget - spending
        spend_ratio = (spending / budget * 100) if budget > 0 else 0
        
        mood_hacks = {
            "Happy": f"""**1. Food Hack**: Double your happiness with food combos—budget pizza + premium dessert beats expensive mid-range meal.
**2. Entertainment Hack**: Matinee shows + casual movie snacks = same joy, ₹{min(200, remaining//3)} saved.
**3. Experience Hack**: Unique free zones (gardens, viewpoints) + paid highlights = memorable without overspending ₹{remaining}.""",
            
            "Sad": f"""**1. Food Hack**: Comfort means home-style cooking; splurge on one comfort dish rather than multiple expensive items.
**2. Entertainment Hack**: Heartwarming movies cost same as sad ones—pick mood-lifters. Save ₹{min(150, remaining//4)} on premium tickets.
**3. Experience Hack**: Visit peaceful spots (parks, cafes) instead of expensive tourist zones. Spend ₹{remaining} on relaxation quality.""",
            
            "Bored": f"""**1. Food Hack**: Try cuisines you've never had in budget sections—novel food beats expensive standard dining.
**2. Entertainment Hack**: Multi-format entertainment (indie films + experimental shows) engages more, costs less. Save ₹{min(200, remaining//3)}.
**3. Experience Hack**: Mix famous + hidden gems locally—saves money, adds adventure to ₹{remaining}.""",
            
            "Romantic": f"""**1. Food Hack**: Ambiance > price. Budget restaurant with candles + music beats expensive generic place.
**2. Entertainment Hack**: Parallel movies/shows separately then discuss = romantic connection, save ₹{remaining//2} vs couples-only extras.
**3. Experience Hack**: Walk-do-talk dates cost less, bond more. Reserve ₹{remaining} for one special paid memory.""",
            
            "Stressed": f"""**1. Food Hack**: Light, stress-free food (salads, calm cafes) prevent stress-eating regrets. Budget wisely on nutrition.
**2. Entertainment Hack**: Choose calming content (nature docs, light comedies) not intense thrillers. Save ₹{min(150, remaining//3)}.
**3. Experience Hack**: Spend ₹{remaining} on stress-relief zones (spas, gardens) not crowded tourist spots. Quality rest > quantity."""
        }
        
        return mood_hacks.get(mood, f"""**Budget Efficiency**: You've used {spend_ratio:.0f}% of ₹{budget}.
**1. Mix Categories**: Balance high + low-cost items across food/entertainment/places.
**2. Timing Matters**: Off-peak hours for restaurants/entertainment reduce costs by ₹{min(300, remaining//2)}.
**3. Maximize ₹{remaining}**: Use remaining for experience upgrades, not duplicates.""")
    
    def get_personalized_tips(self, mood: str, budget: int, current_spending: int, location: str) -> Dict:
        """Get personalized money-saving tips with fallback."""
        remaining = budget - current_spending
        spend_ratio = (current_spending / budget * 100) if budget > 0 else 0
        cache_key = f"tips_{mood}_{budget}_{current_spending}"
        
        prompt = f"""Generate 3 specific money-saving hacks for a {mood} person in {location}.

CONTEXT: Budget ₹{budget} | Spent ₹{current_spending} ({spend_ratio:.0f}%) | Remaining ₹{remaining}

TIPS (be specific to {mood} mood + {location}, not generic):
1. [Food hack]: How to optimize food spend for {mood} mood
2. [Entertainment hack]: Smart way to save on movie/entertainment while keeping vibes right
3. [Experience hack]: One way to maximize remaining ₹{remaining} for memorable experience

Each tip: 1-2 sentences, specific, actionable. No generic advice."""

        result = self._call_gemini_api(prompt, max_tokens=500, temperature=0.8, cache_key=cache_key)
        
        if result['success']:
            return {
                "success": True,
                "tips": result['content'],
                "remaining_budget": remaining,
                "efficiency_score": self._calculate_efficiency(current_spending, budget),
                "source": "gemini"
            }
        
        # Fallback tips
        return {
            "success": True,  # Return as success to show fallback
            "tips": self._get_fallback_tips(mood, budget, current_spending),
            "remaining_budget": remaining,
            "efficiency_score": self._calculate_efficiency(current_spending, budget),
            "source": "fallback"
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
