"""
Restaurants & Hangout Places Finder - Find nearby restaurants and entertainment venues
Uses Overpass API (OpenStreetMap) for real place data with geographic filtering
"""
import requests
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import time

load_dotenv()

# Fallback restaurant and hangout data for Indian cities
FALLBACK_RESTAURANTS = {
    "kolkata": [
        {"name": "Arsalan Restaurant", "distance": 1.2, "lat": 22.5640, "lon": 88.3567, "cost": 300},
        {"name": "Bhojohori Manna", "distance": 2.1, "lat": 22.5750, "lon": 88.3650, "cost": 250},
        {"name": "Peter Cat", "distance": 2.8, "lat": 22.5821, "lon": 88.3800, "cost": 400},
        {"name": "Flury's", "distance": 3.2, "lat": 22.5726, "lon": 88.3639, "cost": 350},
    ],
    "mumbai": [
        {"name": "Mahesh Lunch Home", "distance": 1.5, "lat": 19.0758, "lon": 72.8726, "cost": 350},
        {"name": "Gajalee", "distance": 2.0, "lat": 19.0176, "lon": 72.8479, "cost": 300},
        {"name": "Trishna", "distance": 2.5, "lat": 19.0835, "lon": 72.8671, "cost": 400},
    ],
}

FALLBACK_HANGOUTS = {
    "kolkata": [
        {"name": "Victoria Memorial", "distance": 2.5, "lat": 22.5448, "lon": 88.3426, "type": "tourist_attraction"},
        {"name": "Birla Planetarium", "distance": 3.1, "lat": 22.5448, "lon": 88.3439, "type": "museum"},
        {"name": "Science Centre", "distance": 2.8, "lat": 22.5397, "lon": 88.3628, "type": "museum"},
    ],
    "mumbai": [
        {"name": "Gateway of India", "distance": 1.5, "lat": 18.9580, "lon": 72.8355, "type": "tourist_attraction"},
        {"name": "Marine Drive", "distance": 2.0, "lat": 19.0428, "lon": 72.8252, "type": "landmark"},
    ],
}


def get_location_coordinates(location_str):
    """Geocode location string to coordinates using Nominatim"""
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"[places_finder] 🔍 Geocoding location: {location_str} (Attempt {attempt + 1}/{max_retries})")
            geolocator = Nominatim(user_agent="spendmate_places_finder", timeout=5)
            location = geolocator.geocode(location_str, timeout=5)
            
            if location is None:
                print(f"[places_finder] ⚠️ Location '{location_str}' not found")
                return None
            
            lat, lon = location.latitude, location.longitude
            print(f"[places_finder] ✅ Found coordinates: {lat:.4f}, {lon:.4f}")
            return (lat, lon)
        
        except Exception as e:
            print(f"[places_finder] ⚠️ Geocoding error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_nearby_restaurants_from_osm(lat, lon, radius=10000):
    """
    Fetch nearby restaurants using Overpass API
    Returns: list of restaurant dicts with name, distance, lat, lon, estimated cost
    """
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"[places_finder] 🍽️ Querying Overpass for restaurants near {lat:.4f}, {lon:.4f} (Attempt {attempt + 1}/{max_retries})")
            
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query for restaurant amenities
            query = f"""
            [out:json][timeout:15];
            (
                node["amenity"="restaurant"](around:{radius},{lat},{lon});
                way["amenity"="restaurant"](around:{radius},{lat},{lon});
                node["amenity"="cafe"](around:{radius},{lat},{lon});
                way["amenity"="cafe"](around:{radius},{lat},{lon});
                node["amenity"="fast_food"](around:{radius},{lat},{lon});
                way["amenity"="fast_food"](around:{radius},{lat},{lon});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data=query, timeout=15)
            
            if response.status_code != 200:
                print(f"[places_finder] ⚠️ Overpass error: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
            
            data = response.json()
            restaurants = []
            
            for element in data.get("elements", []):
                try:
                    t_lat = element.get("lat") or (element.get("center", {}).get("lat") if "center" in element else None)
                    t_lon = element.get("lon") or (element.get("center", {}).get("lon") if "center" in element else None)
                    
                    if t_lat is None or t_lon is None:
                        continue
                    
                    tags = element.get("tags", {})
                    name = tags.get("name", tags.get("operator", "Unknown Restaurant"))
                    amenity_type = tags.get("amenity", "restaurant")
                    
                    distance = geodesic((lat, lon), (t_lat, t_lon)).km
                    
                    # Estimate cost based on type
                    cost_map = {"fast_food": 150, "cafe": 200, "restaurant": 300}
                    estimated_cost = cost_map.get(amenity_type, 250)
                    
                    restaurant = {
                        "name": name,
                        "distance": round(distance, 2),
                        "lat": t_lat,
                        "lon": t_lon,
                        "type": amenity_type,
                        "estimated_cost": estimated_cost,
                        "tags": tags
                    }
                    
                    restaurants.append(restaurant)
                    print(f"[places_finder] ✅ Found: {name} ({distance:.2f} km, ₹{estimated_cost})")
                
                except Exception as e:
                    continue
            
            if restaurants:
                restaurants = sorted(restaurants, key=lambda x: x["distance"])
                print(f"[places_finder] ✅ Total restaurants found: {len(restaurants)}")
                return restaurants
            else:
                print(f"[places_finder] ⚠️ No restaurants found")
                return None
        
        except Exception as e:
            print(f"[places_finder] ⚠️ Error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_nearby_hangouts_from_osm(lat, lon, radius=10000):
    """
    Fetch nearby hangout places (parks, entertainment, attractions) using Overpass API
    Returns: list of place dicts with name, distance, lat, lon, type
    """
    max_retries = 2
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            print(f"[places_finder] 🎉 Querying Overpass for hangout places (Attempt {attempt + 1}/{max_retries})")
            
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            # Query for entertainment and attractions
            query = f"""
            [out:json][timeout:15];
            (
                node["tourism"="attraction"](around:{radius},{lat},{lon});
                way["tourism"="attraction"](around:{radius},{lat},{lon});
                node["leisure"="park"](around:{radius},{lat},{lon});
                way["leisure"="park"](around:{radius},{lat},{lon});
                node["amenity"="bar"](around:{radius},{lat},{lon});
                way["amenity"="bar"](around:{radius},{lat},{lon});
                node["amenity"="pub"](around:{radius},{lat},{lon});
                way["amenity"="pub"](around:{radius},{lat},{lon});
                node["leisure"="entertainment"](around:{radius},{lat},{lon});
                way["leisure"="entertainment"](around:{radius},{lat},{lon});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data=query, timeout=15)
            
            if response.status_code != 200:
                print(f"[places_finder] ⚠️ Overpass error: {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
            
            data = response.json()
            hangouts = []
            
            for element in data.get("elements", []):
                try:
                    t_lat = element.get("lat") or (element.get("center", {}).get("lat") if "center" in element else None)
                    t_lon = element.get("lon") or (element.get("center", {}).get("lon") if "center" in element else None)
                    
                    if t_lat is None or t_lon is None:
                        continue
                    
                    tags = element.get("tags", {})
                    name = tags.get("name", "Unknown Place")
                    place_type = tags.get("tourism") or tags.get("leisure") or tags.get("amenity", "attraction")
                    
                    distance = geodesic((lat, lon), (t_lat, t_lon)).km
                    
                    hangout = {
                        "name": name,
                        "distance": round(distance, 2),
                        "lat": t_lat,
                        "lon": t_lon,
                        "type": place_type,
                        "tags": tags
                    }
                    
                    hangouts.append(hangout)
                    print(f"[places_finder] ✅ Found: {name} ({place_type}, {distance:.2f} km)")
                
                except Exception as e:
                    continue
            
            if hangouts:
                hangouts = sorted(hangouts, key=lambda x: x["distance"])
                print(f"[places_finder] ✅ Total hangout places found: {len(hangouts)}")
                return hangouts
            else:
                print(f"[places_finder] ⚠️ No hangout places found")
                return None
        
        except Exception as e:
            print(f"[places_finder] ⚠️ Error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
    
    return None


def get_restaurants_and_hangouts(location_str):
    """
    Get nearby restaurants and hangout places
    Returns: dict with restaurants, hangouts, coordinates, and data source info
    """
    print(f"\n[places_finder] 📍 Getting restaurants and hangout places for: {location_str}")
    
    # Step 1: Geocode location
    coords = get_location_coordinates(location_str)
    
    if coords is None:
        print(f"[places_finder] ⚠️ Could not geocode location")
        return {
            "restaurants": [],
            "hangouts": [],
            "user_lat": None,
            "user_lon": None,
            "restaurant_source": "fallback",
            "hangout_source": "fallback",
            "error": "Could not find location coordinates"
        }
    
    user_lat, user_lon = coords
    
    # Step 2: Get restaurants
    print(f"[places_finder] 🍽️ Fetching restaurants...")
    restaurants = get_nearby_restaurants_from_osm(user_lat, user_lon, radius=10000)
    
    if restaurants is None or len(restaurants) == 0:
        print(f"[places_finder] 📌 Using fallback restaurants")
        restaurants = get_fallback_restaurants_for_location(location_str)
        restaurant_source = "fallback"
    else:
        restaurant_source = "osm"
    
    # Step 3: Get hangout places
    print(f"[places_finder] 🎉 Fetching hangout places...")
    hangouts = get_nearby_hangouts_from_osm(user_lat, user_lon, radius=10000)
    
    if hangouts is None or len(hangouts) == 0:
        print(f"[places_finder] 📌 Using fallback hangout places")
        hangouts = get_fallback_hangouts_for_location(location_str)
        hangout_source = "fallback"
    else:
        hangout_source = "osm"
    
    result = {
        "restaurants": restaurants,
        "hangouts": hangouts,
        "user_lat": user_lat,
        "user_lon": user_lon,
        "restaurant_source": restaurant_source,
        "hangout_source": hangout_source,
        "location_name": location_str
    }
    
    print(f"[places_finder] ✅ Found {len(restaurants)} restaurants ({restaurant_source}) and {len(hangouts)} hangout places ({hangout_source})")
    return result


def get_fallback_restaurants_for_location(location_str):
    """Get fallback restaurant data for location"""
    location_lower = location_str.lower()
    for city in FALLBACK_RESTAURANTS.keys():
        if city in location_lower:
            return FALLBACK_RESTAURANTS[city]
    return FALLBACK_RESTAURANTS.get("kolkata", [])


def get_fallback_hangouts_for_location(location_str):
    """Get fallback hangout data for location"""
    location_lower = location_str.lower()
    for city in FALLBACK_HANGOUTS.keys():
        if city in location_lower:
            return FALLBACK_HANGOUTS[city]
    return FALLBACK_HANGOUTS.get("kolkata", [])
