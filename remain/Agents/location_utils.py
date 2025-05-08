#!/usr/bin/env python3
"""
Location Utilities for Hampton Roads Projects
--------------------------------------------
Utilities for extracting, validating, and geocoding location information
for development projects in the Hampton Roads area.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("location_utils")

# Define Hampton Roads localities with coordinates
HAMPTON_ROADS_LOCALITIES = {
    "Norfolk": {"lat": 36.8508, "lng": -76.2859},
    "Virginia Beach": {"lat": 36.8529, "lng": -75.9780},
    "Chesapeake": {"lat": 36.7682, "lng": -76.2875},
    "Hampton": {"lat": 37.0299, "lng": -76.3452},
    "Newport News": {"lat": 37.0871, "lng": -76.4730},
    "Portsmouth": {"lat": 36.8354, "lng": -76.2983},
    "Suffolk": {"lat": 36.7282, "lng": -76.5836},
    "Williamsburg": {"lat": 37.2707, "lng": -76.7075},
    "Poquoson": {"lat": 37.1224, "lng": -76.3458},
    "Yorktown": {"lat": 37.2390, "lng": -76.5090},
    "Gloucester": {"lat": 37.4075, "lng": -76.5191},
    "Smithfield": {"lat": 36.9824, "lng": -76.6313},
    "Isle of Wight": {"lat": 36.9087, "lng": -76.7054},
    "James City County": {"lat": 37.3304, "lng": -76.7662},
    "York County": {"lat": 37.2374, "lng": -76.5146},
}

# Define zip codes for Hampton Roads area
HAMPTON_ROADS_ZIP_CODES = [
    # Norfolk
    "23501", "23502", "23503", "23504", "23505", "23506", "23507", "23508", "23509", "23510",
    "23511", "23513", "23517", "23518", "23519", "23523", "23551",
    # Virginia Beach
    "23450", "23451", "23452", "23453", "23454", "23455", "23456", "23457", "23459", "23460", 
    "23461", "23462", "23463", "23464", "23465", "23466", "23467", "23471",
    # Chesapeake
    "23320", "23321", "23322", "23323", "23324", "23325", "23326", "23327", "23328",
    # Hampton
    "23630", "23651", "23661", "23663", "23664", "23665", "23666", "23667", "23668", "23669",
    # Newport News
    "23601", "23602", "23603", "23604", "23605", "23606", "23607", "23608", "23609", "23612",
    # Portsmouth
    "23701", "23702", "23703", "23704", "23705", "23707", "23708", "23709",
    # Suffolk
    "23432", "23433", "23434", "23435", "23436", "23437", "23438", "23439",
    # Williamsburg
    "23185", "23186", "23187", "23188",
]

class GeocodingService:
    """A service for geocoding addresses and validating locations."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the geocoding service.
        
        Args:
            api_key: Optional API key for external geocoding service.
                    If None, will use local database lookup.
        """
        self.api_key = api_key or os.environ.get("GEOCODING_API_KEY")
        
    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Geocode an address string to latitude and longitude.
        
        Args:
            address: The address to geocode
            
        Returns:
            Dict with 'lat' and 'lng' if successful, None otherwise
        """
        if not address:
            return None
            
        try:
            # First check if it contains a known locality name
            for locality, coords in HAMPTON_ROADS_LOCALITIES.items():
                if locality.lower() in address.lower():
                    return coords
                    
            # If we have an API key, use external service
            if self.api_key:
                # Using OpenStreetMap Nominatim API as example
                # In production, use a commercial API with proper rate limiting
                params = {
                    "q": f"{address}, Hampton Roads, Virginia",
                    "format": "json",
                    "limit": 1,
                }
                headers = {
                    "User-Agent": "HamptonRoadsDevProject/1.0"
                }
                
                response = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        return {
                            "lat": float(results[0]["lat"]),
                            "lng": float(results[0]["lon"])
                        }
            
            return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
    
    def extract_location_from_text(self, text: str, phi3_client=None) -> Dict[str, Any]:
        """
        Extract location information from text content.
        
        Args:
            text: The text to extract location from
            phi3_client: Optional Phi3Client for NLP-based extraction
            
        Returns:
            Dict with location information including city and coordinates
        """
        result = {
            "city": None,
            "coordinates": None,
            "address": None,
            "zip_code": None,
            "confidence": 0.0
        }
        
        # Use regex to find zip codes in the Hampton Roads area
        import re
        zip_pattern = r"\b(" + "|".join(HAMPTON_ROADS_ZIP_CODES) + r")\b"
        zip_matches = re.findall(zip_pattern, text)
        
        if zip_matches:
            result["zip_code"] = zip_matches[0]
            result["confidence"] = 0.7
        
        # Check for city names
        for locality in HAMPTON_ROADS_LOCALITIES.keys():
            if locality.lower() in text.lower():
                result["city"] = locality
                result["coordinates"] = list(HAMPTON_ROADS_LOCALITIES[locality].values())
                result["confidence"] = 0.8
                break
        
        # If we have Phi3 available, use it for more sophisticated extraction
        if phi3_client and not result["city"]:
            try:
                location_prompt = f"""
                Extract the location information from the following text related to a project or development in Hampton Roads, Virginia.
                If there's no specific location mentioned, respond with 'None'.
                If there is a location, provide it in this format:
                {{
                  "address": "full address if available",
                  "city": "name of the city or locality",
                  "zip_code": "zip code if available"
                }}

                Text: {text[:1500]}  # Limit text length to avoid token limits
                """
                
                phi3_response = phi3_client.generate(location_prompt)
                
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'(\{.*\})', phi3_response, re.DOTALL)
                
                if json_match:
                    location_data = json.loads(json_match.group(1))
                    
                    if location_data.get("city") and location_data["city"] != "None":
                        result["city"] = location_data["city"]
                        result["address"] = location_data.get("address")
                        result["zip_code"] = location_data.get("zip_code")
                        
                        # If we have a city, get its coordinates
                        if result["city"] in HAMPTON_ROADS_LOCALITIES:
                            result["coordinates"] = list(HAMPTON_ROADS_LOCALITIES[result["city"]].values())
                            result["confidence"] = 0.9
                        # Otherwise, geocode the address
                        elif location_data.get("address"):
                            coords = self.geocode_address(location_data["address"])
                            if coords:
                                result["coordinates"] = [coords["lat"], coords["lng"]]
                                result["confidence"] = 0.85
            except Exception as e:
                logger.error(f"Error extracting location with Phi3: {e}")
        
        return result
    
    def is_in_hampton_roads(self, location: Dict[str, Any]) -> bool:
        """
        Determines if a location is within the Hampton Roads area.
        
        Args:
            location: Location dictionary with coordinates or city information
            
        Returns:
            True if in Hampton Roads, False otherwise
        """
        # If we have a city that matches our list
        if location.get("city") and location["city"] in HAMPTON_ROADS_LOCALITIES:
            return True
            
        # If we have a zip code that matches our list
        if location.get("zip_code") and location["zip_code"] in HAMPTON_ROADS_ZIP_CODES:
            return True
            
        # If we have coordinates, check if they're in the bounding box of Hampton Roads
        if location.get("coordinates") and len(location["coordinates"]) == 2:
            lat, lng = location["coordinates"]
            
            # Define a bounding box for Hampton Roads area
            # These are approximate bounds for the Greater Hampton Roads region
            HR_NORTH = 37.5  # Northern boundary latitude
            HR_SOUTH = 36.5  # Southern boundary latitude
            HR_EAST = -75.8  # Eastern boundary longitude
            HR_WEST = -76.8  # Western boundary longitude
            
            if (HR_SOUTH <= lat <= HR_NORTH and HR_WEST <= lng <= HR_EAST):
                return True
                
        return False
