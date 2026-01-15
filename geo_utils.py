"""
Geolocation and Timezone Utilities
Detects user location and timezone information
"""

import requests
from typing import Optional, Dict
import pytz
from datetime import datetime


def get_user_location() -> Dict[str, str]:
    """
    Get user's location based on IP address.
    
    Returns:
        Dict with country, country_code, city, timezone
    """
    try:
        # Use ipapi.co for geolocation (free tier: 1000 requests/day)
        response = requests.get("https://ipapi.co/json/", timeout=3)
        
        # Handle rate limiting or other errors immediately
        if response.status_code == 429:
            print("⚠️ Geo service rate limit reached. Using Unknown.")
            return {
                "country": "Unknown", "country_code": "XX", "city": "Unknown",
                "timezone": "UTC", "latitude": None, "longitude": None
            }
            
        response.raise_for_status()
        data = response.json()
        
        return {
            "country": data.get("country_name", "Unknown"),
            "country_code": data.get("country_code", "XX"),
            "city": data.get("city", "Unknown"),
            "timezone": data.get("timezone", "UTC"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude")
        }
    except Exception as e:
        print(f"Error getting location: {str(e)}")
        return {
            "country": "Unknown",
            "country_code": "XX",
            "city": "Unknown",
            "timezone": "UTC",
            "latitude": None,
            "longitude": None
        }


def get_country_flag(country_code: str) -> str:
    """
    Get emoji flag for a country code.
    
    Args:
        country_code: Two-letter country code (e.g., 'US', 'GB')
        
    Returns:
        Flag emoji string
    """
    if len(country_code) != 2:
        return "🌍"
    
    try:
        # Convert country code to flag emoji
        # Flag emojis are created by combining regional indicator symbols
        offset = 127397  # Offset for regional indicator symbols
        flag = "".join(chr(ord(char) + offset) for char in country_code.upper())
        return flag
    except:
        return "🌍"


def get_local_time(timezone_str: str) -> str:
    """
    Get current local time for a timezone.
    
    Args:
        timezone_str: Timezone string (e.g., 'America/New_York')
        
    Returns:
        Formatted time string
    """
    try:
        tz = pytz.timezone(timezone_str)
        local_time = datetime.now(tz)
        return local_time.strftime("%I:%M %p")
    except:
        return datetime.now().strftime("%I:%M %p")


def get_local_date(timezone_str: str) -> str:
    """
    Get current local date for a timezone.
    
    Args:
        timezone_str: Timezone string
        
    Returns:
        Formatted date string
    """
    try:
        tz = pytz.timezone(timezone_str)
        local_date = datetime.now(tz)
        return local_date.strftime("%B %d, %Y")
    except:
        return datetime.now().strftime("%B %d, %Y")


def format_location_display(location_data: Dict) -> str:
    """
    Format location data for display.
    
    Args:
        location_data: Location dict from get_user_location()
        
    Returns:
        Formatted string like "🇺🇸 New York, United States"
    """
    flag = get_country_flag(location_data.get("country_code", "XX"))
    city = location_data.get("city", "Unknown")
    country = location_data.get("country", "Unknown")
    
    return f"{flag} {city}, {country}"


def format_time_display(location_data: Dict) -> str:
    """
    Format time display with timezone.
    
    Args:
        location_data: Location dict from get_user_location()
        
    Returns:
        Formatted string like "🕐 02:30 PM EST"
    """
    timezone_str = location_data.get("timezone", "UTC")
    local_time = get_local_time(timezone_str)
    
    # Get timezone abbreviation
    try:
        tz = pytz.timezone(timezone_str)
        tz_abbr = datetime.now(tz).strftime("%Z")
    except:
        tz_abbr = "UTC"
    
    return f"🕐 {local_time} {tz_abbr}"
