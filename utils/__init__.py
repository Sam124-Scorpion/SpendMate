"""
SpendMate Utilities - Organized modules for AI recommendations and location services
"""

from .ai import create_ai_recommender, get_recommendations_from_api
from .services import (
    get_places_by_location,
    validate_location,
    get_venue_details,
    filter_by_location,
    get_restaurants_and_hangouts,
    get_theatres_with_movies
)

__all__ = [
    # AI modules
    'create_ai_recommender',
    'get_recommendations_from_api',
    # Location/Services modules
    'get_places_by_location',
    'validate_location',
    'get_venue_details',
    'filter_by_location',
    'get_restaurants_and_hangouts',
    'get_theatres_with_movies'
]
