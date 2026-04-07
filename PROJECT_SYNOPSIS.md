# SpendMate - Project Synopsis

## 📋 Project Overview

**SpendMate** (formerly "SpendWise") is an **AI-powered smart spending companion** that helps users make intelligent spending decisions based on their mood, budget, and current location. It provides personalized recommendations and discovers real-time entertainment and dining options nearby.

**Core Tagline**: *"Get smart spending suggestions based on your mood, budget and location"*

---

## 🎯 Problem Statement

Users often struggle with:
- **Decision paralysis** when spending money (what to do with limited budget?)
- **Missing local deals** - unaware of nearby restaurants, movies, hangouts
- **Budget mismanagement** - overspending without tracking efficiency
- **Lack of personalization** - generic recommendations don't match mood/preferences

**SpendMate solves this** by combining:
1. AI-powered spending advice (Gemini API)
2. Real location-based discovery (OpenStreetMap)
3. Mood-aware recommendations
4. Budget tracking and efficiency scoring

---

## ✨ Key Features

### 1. **Personalized Spending Recommendations**
- Input: Mood, Budget, Location
- Output: AI-generated spending plan with breakdown
- Uses Google Gemini AI for intelligent analysis
- Generates money-saving tips and efficiency scores

### 2. **Real-Time Theatre Discovery**
- Finds nearby cinemas/theatres (10km radius)
- Shows currently playing movies
- Displays movie ratings, release dates, descriptions
- Interactive map visualization
- Cache system for instant re-searches

### 3. **Restaurant Discovery**
- Real-time restaurant location detection
- Shows estimated costs (₹150-₹300 range)
- Maps integration with distance calculation
- Categorized by type (fast_food, cafe, restaurant)

### 4. **Hangout Place Discovery**
- Parks, bars, pubs, attractions, entertainment zones
- No estimated cost (leisure focus)
- Perfect for budget-conscious hangouts
- Distance-based sorting

### 5. **Smart Caching System**
- Session-based caching eliminates redundant API calls
- Instant results on repeated searches
- Location-keyed cache keys

### 6. **Conditional Content Filtering**
- Users select: "Any", "Food", "Movie", or "Hangout"
- App displays ONLY relevant sections
- Reduces UI clutter

### 7. **Error Handling & Resilience**
- API chain strategy: Primary → Fallback → Hardcoded
- Retry logic with exponential backoff
- User-friendly error messages
- Graceful degradation

---

## 🏗️ Architecture & Project Structure

### Directory Organization

```
SpendMate/
├── app.py                          # Main Streamlit entry point (103 LOC)
├── ui/                             # UI Components (Modular)
│   ├── __init__.py                 # Package exports
│   ├── input_form.py               # User preference input
│   ├── recommendations_display.py  # AI recommendations section
│   ├── theatre_section.py          # Theatre discovery UI
│   ├── restaurant_section.py       # Restaurant discovery UI
│   ├── hangout_section.py          # Hangout discovery UI
│   └── map_helpers.py              # Shared map utilities
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── ai/                         # AI & Recommendations
│   │   ├── __init__.py
│   │   ├── ai_recommender.py       # Gemini API integration
│   │   └── api_recommendation.py   # Pure API recommendation flow
│   └── services/                   # Location & Discovery Services
│       ├── __init__.py
│       ├── location_api.py         # Nominatim geocoding
│       ├── places_finder.py        # Restaurant/hangout discovery
│       └── theatre_finder.py       # Theatre discovery
├── .env                            # API keys (GEMINI_API_KEY, TMDB_API_KEY)
├── requirements.txt                # Python dependencies
└── PROJECT_SYNOPSIS.md             # This file
```

### Module Responsibilities

| Module | Responsibility | Key Functions |
|--------|---|---|
| **app.py** | Main orchestrator, UI routing | Page config, user input handling, result display |
| **ui/input_form.py** | User preference collection | `render_input_form()` |
| **ui/recommendations_display.py** | AI recommendations UI | `render_recommendations()` |
| **ui/theatre_section.py** | Theatre discovery UI | `render_theatre_section()`, `_display_theatre_map()`, `_display_movies()` |
| **ui/restaurant_section.py** | Restaurant discovery UI | `render_restaurant_section()`, `_display_restaurant_map()` |
| **ui/hangout_section.py** | Hangout discovery UI | `render_hangout_section()`, `_display_hangout_map()` |
| **ui/map_helpers.py** | Reusable map utilities | `create_location_map()`, `display_data_source_status()` |
| **utils/ai/ai_recommender.py** | Gemini API client | `create_ai_recommender()`, `get_budget_balanced_recommendations()` |
| **utils/ai/api_recommendation.py** | Pure API recommendations | `get_recommendations_from_api()` |
| **utils/services/theatre_finder.py** | Theatre discovery logic | `get_theatres_with_movies()` with API chain |
| **utils/services/places_finder.py** | Restaurant/hangout discovery | `get_restaurants_and_hangouts()` |
| **utils/services/location_api.py** | Location utilities | Nominatim geocoding, place validation |

---

## 🔄 How It Works - User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                   │
│    - Select Mood: Happy 😊 / Sad 😔 / Bored 😐 / etc.         │
│    - Enter Budget: ₹100 - ₹10,000                              │
│    - Enter Location: "Kolkata" / "Mumbai" / etc.                │
│    - Select Preference: "Any" / "Food" / "Movie" / "Hangout"   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. GEMINI API CALL                                              │
│    - Extract mood (without emoji)                               │
│    - Prepare recommendation prompt                              │
│    - Call Gemini API (gemini-pro model)                         │
│    - Get: AI advice, budget breakdown, efficiency score, tips   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. DISPLAY RECOMMENDATIONS                                      │
│    - Show personalized plan                                     │
│    - Display budget analysis (3-column metrics)                 │
│    - Show money-saving tips & efficiency score                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. LOCATION-BASED DISCOVERY (if preference matches)             │
│                                                                  │
│ FOR THEATRES (if "Any" or "Movie"):                             │
│   ├─ API Chain: Overpass (OSM) → Nominatim → Fallback          │
│   ├─ Get theatres within 10km radius                            │
│   ├─ Fetch movies from TMDB API                                 │
│   ├─ Display map with locations                                 │
│   └─ Show top 10 theatres + 9 movies grid                       │
│                                                                  │
│ FOR RESTAURANTS (if "Any" or "Food"):                           │
│   ├─ API Chain: Overpass → Fallback                             │
│   ├─ Query restaurant/cafe/fast_food amenities                  │
│   ├─ Calculate distances from user location                     │
│   ├─ Add estimated costs                                        │
│   └─ Display map + top 10 restaurants                           │
│                                                                  │
│ FOR HANGOUTS (if "Any" or "Hangout"):                           │
│   ├─ API Chain: Overpass → Fallback                             │
│   ├─ Query parks, bars, attractions, entertainment             │
│   ├─ No cost estimation (leisure focus)                         │
│   └─ Display map + top 10 hangout places                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. CACHING & SESSION STATE                                      │
│    - Store results in st.session_state with location-based key  │
│    - Instant results on re-search for same location             │
│    - No redundant API calls                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Web UI framework (native st.map(), st.metric(), etc.)
- **Pandas** - Data manipulation & DataFrames
- **NumPy** - Numerical operations

### Backend & APIs
- **Python 3.x** - Core programming language
- **Google Gemini AI** - Powered by `gemini-pro` model
- **OpenStreetMap (OSM)** - Real location data
  - **Nominatim** - Geocoding (location name → coordinates)
  - **Overpass API** - Amenity queries (theatres, restaurants, etc.)
- **TMDb API** - Movie data (optional, for enhanced movie info)
- **Geopy** - Distance calculations, coordinate operations

### Utilities & Libraries
- **Requests** - HTTP calls with retry logic
- **python-dotenv** - Environment variable management
- **SQLite3** - Query/cache storage (optional)
- **Scikit-learn** - ML utilities (imported, reserved for future use)
- **Joblib** - Caching & serialization (reserved for future use)

### External Services
- **Google Gemini API** (Vertex AI, free tier)
- **OpenStreetMap** (Nominatim API, free public service)
- **Overpass API** (free OSM data queries)
- **TMDb API** (free movie data, requires key)

---

## 📡 Data Sources & API Chain Strategy

### API Chain Pattern (Resilience Strategy)

For each discovery type, the app implements a fallback chain:

**Theatre Discovery Chain:**
1. **Primary**: Overpass API (cinema + theatre amenities within 10km)
2. **Fallback 1**: Nominatim API (search terms: "cinema", "movie theater", "theatre", "multiplex")
3. **Fallback 2**: Hardcoded theatre data per city (Kolkata, Mumbai, Delhi, Bangalore)

**Restaurant Discovery Chain:**
1. **Primary**: Overpass API (restaurant + cafe + fast_food amenities)
2. **Fallback**: Hardcoded restaurant data per city with estimated costs

**Hangout Discovery Chain:**
1. **Primary**: Overpass API (attractions, parks, bars, pubs, entertainment)
2. **Fallback**: Hardcoded hangout data per city

### API Connection Details

| API | Endpoint | Rate | Purpose |
|-----|----------|------|---------|
| **Nominatim** | `nominatim.openstreetmap.org/search` | Public (1 req/sec) | Geocoding (location name → lat/lon) |
| **Overpass** | `overpass-api.de/api/interpreter` | Public (unlimited) | Amenity queries within radius |
| **Gemini** | `generativelanguage.googleapis.com/v1/models/gemini-pro` | Free tier (60 req/min) | AI recommendations |
| **TMDb** | `api.themoviedb.org/3/` | Free tier (40 req/10sec) | Movie data |

### Retry Logic

- **Nominatim**: 2 retries, 1-2 second delays
- **Overpass**: 2 retries, 1-2 second delays
- **Gemini**: Exponential backoff (1s, 2s, 4s)
- All with ConnectionError/Timeout/generic exception handling

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Internet connection (for API calls)
- Google Gemini API key (free from Google Cloud)
- TMDb API key (optional, free from themoviedb.org)

### Step 1: Clone/Download Project
```bash
cd "c:\Users\soumi\OneDrive\Desktop\Late PRojects holder\SpendMate"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
Create `.env` file in project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here  # Optional
```

**How to get API keys:**
- **Gemini**: https://aistudio.google.com/apikey
- **TMDb**: https://www.themoviedb.org/settings/api

### Step 5: Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📖 Usage Guide

### Step 1: Select Your Preferences
1. **Mood**: Choose from 5 mood options (Happy 😊, Sad 😔, Bored 😐, Romantic ❤️, Stressed 😤)
2. **Budget**: Enter amount (₹100 - ₹10,000)
3. **Location**: Type city name (e.g., "Kolkata", "Mumbai")
4. **Preference**: Select what you're looking for:
   - **Any**: All sections (theatres, restaurants, hangouts)
   - **Food**: Only restaurants
   - **Movie**: Only theatres & movies
   - **Hangout**: Only hangout places

### Step 2: Get Recommendations
Click **"Get Smarter Suggestions"** button

### Step 3: View Results
The app will display:
1. **AI-Powered Recommendations**
   - Your personalized spending plan
   - Budget breakdown
   - Money-saving tips
   - Efficiency score

2. **Location-Based Discoveries** (based on your preference)
   - Interactive map showing your location + venues
   - List of nearby places with distances
   - Movie ratings, restaurant costs, etc.

### Example Use Case
```
Mood: Happy 😊
Budget: ₹500
Location: Kolkata
Preference: Any

OUTPUT:
- AI suggests: ₹150 for food + ₹200 for movie + ₹150 for hangout
- Shows 10 nearby restaurants with costs
- Shows 10 nearby movie theatres with 9 current movies
- Shows 10 nearby parks/hangouts with distances
```

---

## 🎨 Key Design Decisions

### 1. **Pure API-Only Approach**
- Removed all CSV fallback data for recommendations
- Only Gemini API generates spending advice
- No manual recommendation system
- Benefit: Always current, context-aware AI responses

### 2. **Modular Architecture**
- Split 410-line monolithic file into 7 modular components
- Each UI section in its own file
- Reusable map_helpers for shared functionality
- Benefit: Easy to maintain, extend, test

### 3. **Session-Based Caching**
- Cache results within user session (not persistent)
- Keyed by location (case-insensitive)
- Eliminates duplicate API calls for same location
- Benefit: Instant re-searches without spinner delay

### 4. **API Chain Resilience**
- Primary → Fallback → Hardcoded strategy
- Ensures app never fully fails
- Graceful degradation when APIs unavailable
- Benefit: Better user experience, no 100% API dependency

### 5. **Conditional Rendering**
- Only show relevant sections based on user preference
- Reduces UI clutter and confusion
- Faster load times for specific searches
- Benefit: Personalized, streamlined experience

### 6. **Interactive Maps**
- Streamlit native st.map() for location visualization
- Shows user location vs venues
- Distance calculations via geopy
- Benefit: Visual context, better decision-making

### 7. **Comprehensive Error Handling**
- Try-catch blocks around all API calls
- User-friendly error messages
- Debug logging with prefixes ([APP], [RECOMMENDER], etc.)
- Benefit: Transparent debugging, good UX

---

## 📊 Data Model

### User Input
```python
{
    'budget': int (₹100-₹10,000),
    'mood': str ('Happy 😊' | 'Sad 😔' | 'Bored 😐' | 'Romantic ❤️' | 'Stressed 😤'),
    'location': str ('Kolkata' | 'Mumbai' | 'Delhi' | ...),
    'preferences': str ('Any' | 'Food' | 'Movie' | 'Hangout')
}
```

### AI Recommendation Structure
```python
{
    'status': 'success' | 'failed',
    'ai_advice': str,                      # Personalized plan
    'budget_used_percentage': float,       # 0-100
    'savings_potential': int,              # ₹ amount
    'efficiency_score': float,             # 0-100
    'tips': str,                           # Money-saving tips
    'source': str,                         # 'gemini' | 'fallback'
}
```

### Theatre Structure
```python
{
    'theatres': [
        {
            'name': str,
            'distance': float,             # km from user
            'lat': float,
            'lon': float,
        }
    ],
    'movies': [
        {
            'name': str,
            'rating': float,               # 0-10
            'release_date': str,
            'overview': str,
        }
    ],
    'user_lat': float,
    'user_lon': float,
    'theatre_source': str,                 # 'osm' | 'nominatim' | 'fallback'
    'movie_source': str,                   # 'api' | 'fallback'
}
```

### Restaurant/Hangout Structure
```python
{
    'restaurants': [
        {
            'name': str,
            'distance': float,
            'lat': float,
            'lon': float,
            'estimated_cost': int,        # Only for restaurants
            'type': str,                  # 'restaurant' | 'cafe' | 'fast_food'
        }
    ],
    'hangouts': [
        {
            'name': str,
            'distance': float,
            'lat': float,
            'lon': float,
            'type': str,                  # 'park' | 'bar' | 'attraction' | ...
        }
    ],
    'user_lat': float,
    'user_lon': float,
    'restaurant_source': str,              # 'osm' | 'fallback'
    'hangout_source': str,                 # 'osm' | 'fallback'
}
```

---

## 🔍 Debugging & Logging

### Console Output (Print Statements)
- **[APP]** prefix: Main application flow
- **[RECOMMENDER]** prefix: Gemini API interaction
- **[theatre_finder]** prefix: Theatre discovery
- **[places_finder]** prefix: Restaurant/hangout discovery
- **[location_api]** prefix: Location utilities

### Example Debug Flow
```
[APP] User clicked 'Get Smarter Suggestions'
[APP] Input - Mood: Happy, Budget: 500, Location: Kolkata, Preference: Any
[RECOMMENDER] 🤖 Fetching recommendations from Gemini API...
[APP] Theatre section - Fetching theatres for location: Kolkata
[theatre_finder] Trying Overpass API...
[theatre_finder] Overpass successful! Found 8 theatres
[APP] ✅ Got API recommendations successfully
```

---

## ⚡ Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| User input | <100ms | Instant |
| Gemini API call | 2-8 seconds | Depends on model performance |
| Nominatim geocoding | 1-3 seconds | Depends on server load |
| Overpass query | 2-5 seconds | Depends on server load |
| Cached search | <500ms | Instant (session state) |
| Map rendering | <1 second | Streamlit native |

---

## 🔮 Future Enhancement Ideas

### Short Term
1. **User Preferences Persistence**: Save user's favorite venues
2. **Rating System**: Let users rate recommendations
3. **Review Integration**: Pull Google Reviews for venues
4. **Offline Mode**: Cache popular locations by city

### Medium Term
1. **Social Features**: Share recommendations with friends
2. **Trip Planning**: Multi-day itinerary generation
3. **Budget Alerts**: Notifications when exceeding budget
4. **ML Model**: Learn user preferences over time

### Long Term
1. **Mobile App**: Native iOS/Android version
2. **Real-time Notifications**: Deals & offers nearby
3. **Payment Integration**: Book tickets directly
4. **Voice Commands**: "Hey SpendMate, what should I do?"

---

## 📝 Code Statistics

| Metric | Value |
|--------|-------|
| Main app.py | 103 LOC |
| UI modules | ~480 LOC total |
| Utility modules | ~250 LOC total |
| Total Python code | ~833 LOC |
| Number of files | 15 Python files |
| Number of modules | 3 main packages (app, ui, utils) |
| External APIs | 5 (Gemini, Nominatim, Overpass, TMDb, OSM) |

---

## 🐛 Known Limitations

1. **Search Radius Fixed**: Theatre/restaurant search currently hardcoded to 10km
2. **No Authentication**: No user accounts or login system
3. **Single Recommendation**: Generates one recommendation per query (no variations)
4. **India-Centric**: Fallback data primarily for Indian cities
5. **No Booking Integration**: Shows venues but can't book directly
6. **Mobile Responsive**: Limited mobile optimization

---

## 📄 License & Credits

**Project**: SpendMate - AI Smart Spending Companion
**Status**: Development (v1.0 Complete)
**Developer**: Soumi
**APIs Used**: 
- Google Gemini AI (Free tier)
- OpenStreetMap (Free)
- TMDb (Free tier)

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue**: "Gemini API key not found"
- **Solution**: Add `GEMINI_API_KEY=your_key` to `.env` file

**Issue**: No theatres found
- **Solution**: Ensure location name is correct (e.g., "Kolkata" not "Calcutta")

**Issue**: Map not displaying
- **Solution**: Ensure latitude/longitude values are present in response

**Issue**: Slow API responses
- **Solution**: Check internet connection, API services status

---

## 🎓 Learning Outcomes

This project demonstrates:
- **API Integration**: Multiple external APIs (Gemini, Nominatim, Overpass)
- **Error Handling**: Comprehensive try-catch with graceful degradation
- **Modular Architecture**: Clean separation of concerns
- **Caching Strategies**: Session-state based performance optimization
- **Geo-location**: Distance calculations, geocoding
- **Web Frameworks**: Streamlit for rapid UI development
- **Environment Management**: .env for configuration
- **Documentation**: Comprehensive in-code comments

---

**Last Updated**: April 7, 2026  
**Version**: 1.0 (Refactored & Modularized)  
**Status**: ✅ Fully Functional
