import requests
import time

def get_places_by_location(location, place_type, limit=5):
    """
    Search for places in a given location using OpenStreetMap Nominatim API.
    
    Args:
        location (str): City or area name (e.g., "Kolkata", "Mumbai")
        place_type (str): Type of place to search for (e.g., "restaurant", "cafe", "movie_theater")
        limit (int): Maximum number of results to return
    
    Returns:
        list: List of places with name, address, and estimated cost
    """
    
    # Map place types to search queries
    search_queries = {
        "restaurant": "restaurant",
        "fast_food": "fast food restaurant",
        "cafe": "cafe coffee",
        "movie": "cinema movie theater",
        "place": "tourist attraction entertainment",
        "hangout": "bar pub club"
    }
    
    search_query = search_queries.get(place_type, place_type)
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            "q": f"{search_query} in {location}",
            "format": "json",
            "limit": limit
        }
        
        headers = {
            "User-Agent": "SpendMate-App"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return []
        
        results = []
        
        for idx, place in enumerate(data):
            # Extract place name and address
            display_name = place.get("display_name", "").split(",")
            name = display_name[0].strip() if display_name else "Unknown"
            
            # Estimate cost based on place type
            estimated_cost = estimate_place_cost(place_type)
            
            results.append({
                "name": name,
                "address": place.get("display_name", "Unknown Address"),
                "cost": estimated_cost,
                "latitude": place.get("lat"),
                "longitude": place.get("lon"),
                "place_type": place_type
            })
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching places: {str(e)}")
        return []


def estimate_place_cost(place_type):
    """
    Estimate average cost for a place type.
    
    Args:
        place_type (str): Type of place
    
    Returns:
        int: Estimated cost in rupees
    """
    
    cost_mapping = {
        "restaurant": 300,
        "fast_food": 200,
        "cafe": 180,
        "movie": 250,
        "place": 200,
        "hangout": 350
    }
    
    return cost_mapping.get(place_type, 200)


def filter_by_location(recommendations, location):
    """
    Enhance recommendations with location-based information.
    
    Args:
        recommendations (dict): Recommendations dict with food, place, movie
        location (str): User's location
    
    Returns:
        dict: Enhanced recommendations with location details
    """
    
    enhanced_recommendations = recommendations.copy()
    
    # Add location info to place recommendation
    if 'place' in enhanced_recommendations:
        enhanced_recommendations['place']['location'] = location
    
    return enhanced_recommendations


def get_venue_details(location, venue_type):
    """
    Get detailed information about venues in a location.
    
    Args:
        location (str): City name
        venue_type (str): Type of venue
    
    Returns:
        dict: Venue details with location coordinates
    """
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "SpendMate-App"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            location_info = data[0]
            return {
                "city": location,
                "latitude": location_info.get("lat"),
                "longitude": location_info.get("lon"),
                "address": location_info.get("display_name", ""),
                "venue_type": venue_type
            }
        
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching venue details: {str(e)}")
        return None


def validate_location(location):
    """
    Validate if a location exists using Nominatim.
    
    Args:
        location (str): Location name
    
    Returns:
        bool: True if location is valid, False otherwise
    """
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "SpendMate-App"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return len(data) > 0
    
    except requests.exceptions.RequestException as e:
        print(f"Error validating location: {str(e)}")
        return False
