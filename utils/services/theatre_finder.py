"""
Theatre Finder Utility - Find nearby cinemas using OpenStreetMap and their playing movies
Uses Geopy for geocoding and Overpass API for real theatre data
Fallback: Nominatim API if Overpass fails
"""
import requests
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import time

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Import location API for fallback
try:
    from .location_api import get_places_by_location
except ImportError:
    get_places_by_location = None

# Fallback theatre data for all major Indian cities
FALLBACK_THEATRES = {
    "kolkata": [
        {"name": "PVR Cinemas", "distance": 2.5, "lat": 22.5640, "lon": 88.3567},
        {"name": "INOX Kolkata", "distance": 3.2, "lat": 22.5726, "lon": 88.3639},
        {"name": "Prachi Cinema Hall", "distance": 4.1, "lat": 22.5780, "lon": 88.3700},
        {"name": "Mahajati Sadan Auditorium", "distance": 5.5, "lat": 22.5833, "lon": 88.3750},
        {"name": "IMAX Kolkata", "distance": 6.2, "lat": 22.5900, "lon": 88.3800},
    ],
    "mumbai": [
        {"name": "PVR Phoenix", "distance": 2.0, "lat": 19.0176, "lon": 72.8479},
        {"name": "IMAX Mumbai", "distance": 2.5, "lat": 19.0758, "lon": 72.8726},
        {"name": "Cinepolis Nexus", "distance": 3.0, "lat": 19.0760, "lon": 72.8675},
        {"name": "INOX Mumbai", "distance": 3.5, "lat": 19.0835, "lon": 72.8671},
    ],
    "delhi": [
        {"name": "PVR Priya Delhi", "distance": 2.0, "lat": 28.5673, "lon": 77.1961},
        {"name": "INOX Delhi", "distance": 2.8, "lat": 28.5590, "lon": 77.2115},
        {"name": "Cinepolis Delhi", "distance": 3.2, "lat": 28.5631, "lon": 77.1845},
        {"name": "M Cinema Delhi", "distance": 4.0, "lat": 28.5450, "lon": 77.1900},
    ],
    "bangalore": [
        {"name": "PVR Forum Bangalore", "distance": 2.2, "lat": 13.0012, "lon": 77.5714},
        {"name": "INOX Bangalore", "distance": 2.8, "lat": 13.0345, "lon": 77.6245},
        {"name": "Cinepolis Bangalore", "distance": 3.5, "lat": 13.0479, "lon": 77.6104},
    ],
}


def get_location_coordinates(location_str):
    """
    Geocode location string to coordinates using Nominatim (OpenStreetMap)
    Returns: (latitude, longitude) tuple or None if not found
    Handles connection errors with retry logic
    """
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"[theatre_finder] 🔍 Geocoding location: {location_str} (Attempt {attempt + 1}/{max_retries})")
            
            geolocator = Nominatim(user_agent="spendmate_theatre_finder", timeout=5)
            location = geolocator.geocode(location_str, timeout=5)
            
            if location is None:
                print(f"[theatre_finder] ⚠️ Location '{location_str}' not found in OpenStreetMap")
                return None
            
            lat, lon = location.latitude, location.longitude
            print(f"[theatre_finder] ✅ Found coordinates: {lat:.4f}, {lon:.4f}")
            return (lat, lon)
        
        except requests.exceptions.ConnectionError as e:
            print(f"[theatre_finder] ⚠️ Connection error during geocoding: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
        
        except requests.exceptions.Timeout:
            print(f"[theatre_finder] ⚠️ Geocoding timeout (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
        
        except Exception as e:
            print(f"[theatre_finder] ❌ Geocoding error: {type(e).__name__} - {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_nearby_theatres_from_osm(lat, lon, radius=15000):
    """
    Fetch nearby theatres using Overpass API (OpenStreetMap)
    radius: search radius in meters (default 10km for wider coverage)
    Returns: list of theatre dicts with name, distance, lat, lon
    Handles connection errors with retry logic
    """
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"[theatre_finder] 📡 Querying OpenStreetMap for theatres near {lat:.4f}, {lon:.4f} within {radius}m (Attempt {attempt + 1}/{max_retries})")
            
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query for cinema amenities with multiple search terms
            query = f"""
            [out:json][timeout:15];
            (
                node["amenity"="cinema"](around:{radius},{lat},{lon});
                way["amenity"="cinema"](around:{radius},{lat},{lon});
                relation["amenity"="cinema"](around:{radius},{lat},{lon});
                node["amenity"="theatre"](around:{radius},{lat},{lon});
                way["amenity"="theatre"](around:{radius},{lat},{lon});
                relation["amenity"="theatre"](around:{radius},{lat},{lon});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data=query, timeout=15)
            
            if response.status_code != 200:
                print(f"[theatre_finder] ⚠️ Overpass API Error: {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    continue
                return None
            
            data = response.json()
            
            if "elements" not in data:
                print(f"[theatre_finder] ⚠️ No elements in Overpass response")
                return None
            
            theatres = []
            
            for element in data.get("elements", []):
                try:
                    # Get coordinates
                    t_lat = None
                    t_lon = None
                    
                    if "lat" in element and "lon" in element:
                        t_lat = element["lat"]
                        t_lon = element["lon"]
                    elif "center" in element:
                        t_lat = element["center"]["lat"]
                        t_lon = element["center"]["lon"]
                    
                    if t_lat is None or t_lon is None:
                        continue
                    
                    # Get name
                    tags = element.get("tags", {})
                    name = tags.get("name", tags.get("operator", "Unknown Cinema"))
                    
                    # Calculate distance
                    distance = geodesic((lat, lon), (t_lat, t_lon)).km
                    
                    theatre = {
                        "name": name,
                        "distance": round(distance, 2),
                        "lat": t_lat,
                        "lon": t_lon,
                        "tags": tags
                    }
                    
                    theatres.append(theatre)
                    print(f"[theatre_finder] ✅ Found: {name} ({distance:.2f} km)")
                
                except Exception as e:
                    print(f"[theatre_finder] ⚠️ Error processing element: {str(e)}")
                    continue
            
            if theatres:
                theatres = sorted(theatres, key=lambda x: x["distance"])
                print(f"[theatre_finder] ✅ Total OSM theatres found: {len(theatres)}")
                return theatres
            else:
                print(f"[theatre_finder] ⚠️ No theatres found in OpenStreetMap")
                return None
        
        except requests.exceptions.ConnectionError as e:
            print(f"[theatre_finder] ⚠️ Connection error with Overpass API: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
        
        except requests.exceptions.Timeout:
            print(f"[theatre_finder] ⚠️ Overpass API timeout (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
        
        except Exception as e:
            print(f"[theatre_finder] ❌ Overpass API error: {type(e).__name__} - {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_theatres_from_nominatim(location_str, lat, lon):
    """
    Fallback theatre search using Nominatim API when Overpass fails
    Searches for cinema/movie_theater using text-based search
    Returns: list of theatre dicts or None
    """
    max_retries = 2
    retry_delay = 1
    search_terms = [
        f"cinema in {location_str}",
        f"movie theater in {location_str}",
        f"theatre in {location_str}",
        f"multiplex in {location_str}"
    ]
    
    for attempt in range(max_retries):
        try:
            print(f"[theatre_finder] 🔄 Fallback: Searching Nominatim for cinemas (Attempt {attempt + 1}/{max_retries})")
            
            all_theatres = []
            
            # Try multiple search terms to get more results
            for search_term in search_terms:
                url = "https://nominatim.openstreetmap.org/search"
                
                params = {
                    "q": search_term,
                    "format": "json",
                    "limit": 15  # Increased from 10 to 15
                }
                
                headers = {
                    "User-Agent": "SpendMate-App"
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                for place in data:
                    try:
                        place_lat = float(place.get("lat", 0))
                        place_lon = float(place.get("lon", 0))
                        name = place.get("display_name", "Unknown Cinema").split(",")[0].strip()
                        
                        # Calculate distance
                        distance = geodesic((lat, lon), (place_lat, place_lon)).km
                        
                        # Only include if within 15km
                        if distance > 15:
                            continue
                        
                        theatre = {
                            "name": name,
                            "distance": round(distance, 2),
                            "lat": place_lat,
                            "lon": place_lon,
                            "tags": {"source": "nominatim"}
                        }
                        
                        # Avoid duplicates
                        if not any(t["name"].lower() == name.lower() for t in all_theatres):
                            all_theatres.append(theatre)
                            print(f"[theatre_finder] ✅ Found via Nominatim: {name} ({distance:.2f} km)")
                    
                    except Exception as e:
                        print(f"[theatre_finder] ⚠️ Error processing place: {str(e)}")
                        continue
            
            if all_theatres:
                all_theatres = sorted(all_theatres, key=lambda x: x["distance"])
                print(f"[theatre_finder] ✅ Nominatim found {len(all_theatres)} cinemas")
                return all_theatres
            
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            
            return None
        
        except requests.exceptions.Timeout:
            print(f"[theatre_finder] ⚠️ Nominatim timeout (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return None
        
        except Exception as e:
            print(f"[theatre_finder] ⚠️ Nominatim error: {type(e).__name__} - {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_city_from_coordinates(lat, lon):
    """
    Reverse geocode coordinates to city name
    """
    try:
        geolocator = Nominatim(user_agent="spendmate_theatre_finder")
        location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
        
        # Extract city from address
        address_parts = location.address.split(',')
        if len(address_parts) >= 2:
            city = address_parts[-2].strip().lower()
            return city
    except:
        pass
    
    return None


def get_fallback_theatres_for_location(lat, lon):
    """Get fallback theatre data for closest city"""
    print(f"[theatre_finder] 📌 Using fallback theatres")
    
    # Try to determine city from coordinates
    city = get_city_from_coordinates(lat, lon)
    
    if city and any(city_name in city for city_name in FALLBACK_THEATRES.keys()):
        for city_name in FALLBACK_THEATRES.keys():
            if city_name in city:
                return FALLBACK_THEATRES[city_name]
    
    # Default to Kolkata
    return FALLBACK_THEATRES.get("kolkata", [])


def get_city_from_location(location_str):
    """Extract city name from location string"""
    location_lower = location_str.lower().strip()
    for city in FALLBACK_THEATRES.keys():
        if city in location_lower:
            return city
    return "kolkata"  # Default to Kolkata


def get_fallback_theatres(location_str):
    """Get fallback theatre data for a location"""
    city = get_city_from_location(location_str)
    print(f"[theatre_finder] 📌 Using fallback theatres for {city}")
    return FALLBACK_THEATRES.get(city, FALLBACK_THEATRES["kolkata"])


def get_now_playing_movies():
    """
    Fetch movies currently playing from TMDb API with retry logic
    Returns list of movie dicts with name, rating, genre, poster
    Handles connection errors and network issues gracefully
    """
    if not TMDB_API_KEY:
        print("[theatre_finder] ⚠️ TMDB_API_KEY not found, using fallback movies")
        return get_fallback_movies()
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"[theatre_finder] 📡 Fetching now-playing movies from TMDb API (Attempt {attempt + 1}/{max_retries})...")
            
            url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&region=IN&page=1"
            
            # Use session with connection pooling for better reliability
            session = requests.Session()
            session.headers.update({
                'Accept': 'application/json',
                'User-Agent': 'SpendMate-App/1.0'
            })
            
            # Make request with shorter timeout
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if "results" not in data:
                    print("[theatre_finder] ⚠️ No results in TMDb response")
                    return get_fallback_movies()
                
                movies = []
                for movie in data.get("results", [])[:12]:  # Get top 12 movies
                    movie_info = {
                        "name": movie.get("title", "Unknown"),
                        "rating": round(movie.get("vote_average", 0), 1),
                        "popularity": movie.get("popularity", 0),
                        "overview": movie.get("overview", ""),
                        "poster": movie.get("poster_path", ""),
                        "release_date": movie.get("release_date", ""),
                    }
                    movies.append(movie_info)
                
                print(f"[theatre_finder] ✅ Fetched {len(movies)} movies from TMDb API")
                session.close()
                return movies
            else:
                print(f"[theatre_finder] ⚠️ TMDb API Error: {response.status_code}")
                session.close()
                if attempt < max_retries - 1:
                    print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    continue
                return get_fallback_movies()
        
        except requests.exceptions.Timeout:
            print(f"[theatre_finder] ⚠️ TMDb API timeout (Attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return get_fallback_movies()
        
        except requests.exceptions.ConnectionError as e:
            print(f"[theatre_finder] ⚠️ Connection error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            print("[theatre_finder] 📌 Using fallback movies after connection errors")
            return get_fallback_movies()
        
        except Exception as e:
            print(f"[theatre_finder] ⚠️ Error fetching movies: {type(e).__name__} - {str(e)}")
            if attempt < max_retries - 1:
                print(f"[theatre_finder] ⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
                continue
            return get_fallback_movies()
    
    # Fallback if all retries fail
    print("[theatre_finder] 📌 All retries failed, using fallback movies")
    return get_fallback_movies()


def get_fallback_movies():
    """Get fallback movie data"""
    print("[theatre_finder] 📌 Using fallback movies")
    return [
        {
            "name": "Bhaiyya Ji",
            "rating": 7.2,
            "popularity": 85.5,
            "overview": "A gripping action thriller",
            "poster": "",
            "release_date": "2026-04-07"
        },
        {
            "name": "Article 370",
            "rating": 7.8,
            "popularity": 92.3,
            "overview": "A political drama",
            "poster": "",
            "release_date": "2026-03-15"
        },
        {
            "name": "Teri Baaton Mein Aisa Uljha Jiya",
            "rating": 7.5,
            "popularity": 78.9,
            "overview": "A romantic comedy",
            "poster": "",
            "release_date": "2026-02-20"
        },
        {
            "name": "Fighter",
            "rating": 7.4,
            "popularity": 95.1,
            "overview": "An action-packed thriller",
            "poster": "",
            "release_date": "2026-01-25"
        },
        {
            "name": "Khel Khel Mein",
            "rating": 7.6,
            "popularity": 82.4,
            "overview": "A sports drama",
            "poster": "",
            "release_date": "2026-02-10"
        },
    ]


def get_theatres_with_movies(location_str):
    """
    Get nearby theatres and their playing movies using real location data
    API Chain: Overpass API -> Nominatim API -> Hardcoded Fallback
    Returns: dict with theatres, movies, coordinates, and data source info
    """
    print(f"\n[theatre_finder] 🎬 Getting theatres and movies for: {location_str}")
    
    # Step 1: Geocode location to coordinates
    coords = get_location_coordinates(location_str)
    
    if coords is None:
        print(f"[theatre_finder] ⚠️ Could not geocode location, using fallback")
        # Return fallback data without real coordinates
        return {
            "theatres": get_fallback_theatres_for_location(22.5640, 88.3567),  # Kolkata fallback coords
            "movies": get_now_playing_movies(),
            "user_lat": None,
            "user_lon": None,
            "movie_source": "fallback",
            "theatre_source": "fallback",
            "total_theatres": 0,
            "total_movies": 0,
            "error": "Could not find location coordinates"
        }
    
    user_lat, user_lon = coords
    
    # Step 2: Query OpenStreetMap for real theatres (API Chain)
    print(f"[theatre_finder] 🔗 Starting API chain for theatres...")
    
    # Try Overpass API first (10km radius for wider coverage)
    theatres = get_nearby_theatres_from_osm(user_lat, user_lon, radius=10000)
    theatre_source = "osm"
    
    # If Overpass fails, try Nominatim fallback API
    if theatres is None or len(theatres) == 0:
        print(f"[theatre_finder] 📌 Overpass returned no results, trying Nominatim API...")
        theatres = get_theatres_from_nominatim(location_str, user_lat, user_lon)
        
        if theatres is not None and len(theatres) > 0:
            theatre_source = "nominatim"
            print(f"[theatre_finder] ✅ Successfully got theatres from Nominatim")
        else:
            # If both APIs fail, use hardcoded fallback
            print(f"[theatre_finder] 📌 Both APIs failed, using hardcoded fallback theatres")
            theatres = get_fallback_theatres_for_location(user_lat, user_lon)
            theatre_source = "fallback"
    
    # Step 3: Fetch movies
    movies = get_now_playing_movies()
    movie_source = "api" if TMDB_API_KEY else "fallback"
    
    result = {
        "theatres": theatres,
        "movies": movies,
        "user_lat": user_lat,
        "user_lon": user_lon,
        "movie_source": movie_source,
        "theatre_source": theatre_source,
        "total_theatres": len(theatres),
        "total_movies": len(movies),
        "location_name": location_str
    }
    
    print(f"[theatre_finder] ✅ Found {len(theatres)} theatres ({theatre_source}) and {len(movies)} movies ({movie_source})")
    return result
