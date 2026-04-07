"""
UI Components for SpendMate Application
Organized modules for different sections of the UI
"""

from .input_form import render_input_form
from .recommendations_display import render_recommendations
from .theatre_section import render_theatre_section
from .restaurant_section import render_restaurant_section
from .hangout_section import render_hangout_section
from .map_helpers import create_location_map

__all__ = [
    'render_input_form',
    'render_recommendations',
    'render_theatre_section',
    'render_restaurant_section',
    'render_hangout_section',
    'create_location_map'
]
