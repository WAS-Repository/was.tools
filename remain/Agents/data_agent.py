#!/usr/bin/env python3
"""
Enhanced Hampton Roads Development Crawler
----------------------------------------
This script uses Phi3 to crawl websites for information about development projects
in the Hampton Roads area and stores the data in OrbitDB.
"""

import os
import sys
import json
import time
import logging
import hashlib
import datetime
import requests
import schedule
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
import httpx
from playwright.async_api import async_playwright
import asyncio
import re
import random
from typing import List, Dict, Any, Optional, Union, Tuple

# Import our specialized modules
from location_utils import GeocodingService
from source_handlers import SourceHandlerFactory, BaseSourceHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("hampton_roads_crawler")

# Load environment variables
load_dotenv()

# Constants for crawler configuration
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:3000")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
CRAWL_INTERVAL_HOURS = int(os.getenv("CRAWL_INTERVAL_HOURS", 24))
MAX_PAGES_PER_SITE = int(os.getenv("MAX_PAGES_PER_SITE", 50))
CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", 2.0))
USER_AGENT = os.getenv("USER_AGENT", "HamptonRoadsDevelopmentTracker/1.0")

# Mapping of city names to likely locations
CITY_LOCATIONS = {
    "norfolk": [36.8508, -76.2859],
    "virginia beach": [36.8529, -75.9780],
    "chesapeake": [36.7682, -76.2874],
    "portsmouth": [36.8354, -76.2983],
    "suffolk": [36.7282, -76.5836],
    "hampton": [37.0298, -76.3452],
    "newport news": [37.0871, -76.4730],
    "williamsburg": [37.2707, -76.7075],
    "james city": [37.3143, -76.7567],
    "gloucester": [37.4099, -76.5271],
    "york": [37.2415, -76.5408],
    "poquoson": [37.1224, -76.3458],
    "isle of wight": [36.9000, -76.7023],
    "surry": [37.1374, -76.8861],
    "southampton": [36.7232, -77.1030],
    "smithfield": [36.9824, -76.6314]
}

# Target websites to crawl (municipalities, news sites, development authorities)
TARGET_WEBSITES = [
    # City government websites
    {"url": "https://www.norfolk.gov/1376/Development", "category": "developments"},
    {"url": "https://www.vbgov.com/government/departments/planning/Pages/default.aspx", "category": "permits"},
    {"url": "https://www.chesapeakeva.gov/government/departments/planning", "category": "permits"},
    {"url": "https://www.suffolkva.us/259/Planning-Community-Development", "category": "developments"},
    {"url": "https://hampton.gov/3598/Development-Services", "category": "developments"},
    {"url": "https://www.portsmouthva.gov/160/Planning", "category": "developments"},
    {"url": "https://www.nnva.gov/2318/Development-Projects", "category": "developments"},
    
    # News sites
    {"url": "https://www.pilotonline.com/business/", "category": "developments"},
    {"url": "https://www.13newsnow.com/business", "category": "developments"},
    {"url": "https://www.wavy.com/news/local-news/", "category": "developments"},
    
    # Development authorities
    {"url": "https://hamptonroadseco.org/development-projects/", "category": "developments"},
    {"url": "https://www.hreda.com/news/", "category": "developments"},
    {"url": "https://www.yesvirginiabeach.com/resources/news", "category": "developments"},
    {"url": "https://www.suffolkeconomicdevelopment.com/resources/news/", "category": "developments"}
]

class Document:
    """Represents a document to be stored in OrbitDB."""
    
    def __init__(
        self, 
        title: str, 
        content: str, 
        url: str, 
        source: str,
        category: str,
        coordinates: Optional[List[float]] = None,
        city: Optional[str] = None,
        extracted_info: Optional[Dict[str, Any]] = None,
        source_type: str = "general"
    ):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.category = category
        self.coordinates = coordinates
        self.city = city
        self.extracted_info = extracted_info or {}
        self.source_type = source_type  # New field to track the type of source (patent, government, news, etc)
        self.created = datetime.datetime.now().isoformat()
        
        # Generate a unique ID based on URL and content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()
        self.id = f"doc_{int(time.time())}_{content_hash[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for storage."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "category": self.category,
            "coordinates": self.coordinates,
            "city": self.city,
            "extracted_info": self.extracted_info,
            "source_type": self.source_type,
            "created": self.created,
            # Add geospatial flag to make spatial queries easier
            "has_location": self.coordinates is not None and len(self.coordinates) == 2
        }

class Phi3Client:
    """Client for interacting with Microsoft's Phi3 model via Ollama."""
    
    def __init__(self, endpoint: str = OLLAMA_ENDPOINT):
        self.endpoint = endpoint
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text from Phi3 model."""
        try:
            payload = {
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Error generating text with Phi3: {e}")
            return ""
    
    def extract_project_info(self, text: str, url: str) -> Dict[str, Any]:
        """Extract structured information about development projects."""
        prompt = f"""
        Read the following text about a potential development project in Hampton Roads, Virginia, and extract structured information.
        
        TEXT:
        {text[:4000]}
        
        URL: {url}
        
        Extract the following information in JSON format:
        - project_name: The name of the development project
        - description: A brief description of the project
        - location: Where the project is located (city, address, etc.)
        - key_players: Organizations and people involved (developers, contractors, etc.)
        - project_cost: The cost of the project if mentioned
        - timeline: Information about when the project will start/complete
        - project_type: Type of development (commercial, residential, mixed-use, infrastructure, etc.)
        - contact_info: Any contact information for the project
        
        Output JSON format only, nothing else.
        If a field cannot be determined, use null.
        """
        
        try:
            response = self.generate(prompt)
            
            # Try to parse JSON from the response
            # Sometimes the model might add extra text before/after the JSON
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                return data
            
            # If no JSON pattern found, try to parse the whole response
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error extracting project info: {e}")
            return {
                "project_name": None,
                "description": None,
                "location": None,
                "key_players": None,
                "project_cost": None,
                "timeline": None,
                "project_type": None,
                "contact_info": None
            }
    
    def detect_city(self, text: str) -> Optional[str]:
        """Detect which Hampton Roads city is mentioned in the text."""
        prompt = f"""
        Read the following text and determine which city or locality in Hampton Roads, Virginia is primarily mentioned.
        
        TEXT:
        {text[:2000]}
        
        The possible cities/localities are:
        - Norfolk
        - Virginia Beach
        - Chesapeake
        - Portsmouth
        - Suffolk
        - Hampton
        - Newport News
        - Williamsburg
        - James City
        - Gloucester
        - York
        - Poquoson
        - Isle of Wight
        - Surry
        - Southampton
        - Smithfield
        
        Respond with only the name of the primary city/locality discussed. If no specific city is clearly mentioned, respond with "unknown".
        """
        
        try:
            response = self.generate(prompt, max_tokens=50).strip().lower()
            
            # Check if response is one of the valid cities
            for city in CITY_LOCATIONS.keys():
                if city in response:
                    return city
            
            return None
        except Exception as e:
            logger.error(f"Error detecting city: {e}")
            return None
    
    def is_relevant(self, text: str, title: str) -> bool:
        """Determine if the content is relevant to development projects in Hampton Roads."""
        prompt = f"""
        Determine if the following text is about a development project, building construction, infrastructure, or real estate development in the Hampton Roads region of Virginia.
        
        TITLE: {title}
        
        TEXT:
        {text[:3000]}
        
        The Hampton Roads region includes:
        Norfolk, Virginia Beach, Chesapeake, Portsmouth, Suffolk, Hampton, Newport News, Williamsburg, James City, Gloucester, York, Poquoson, Isle of Wight, Surry, Southampton, and Smithfield.
        
        Respond with only "yes" if it's about a development project in Hampton Roads, or "no" if it's not.
        """
        
        try:
            response = self.generate(prompt, max_tokens=10).strip().lower()
            return "yes" in response
        except Exception as e:
            logger.error(f"Error checking relevance: {e}")
            return False

class OrbitDBClient:
    """Client for interacting with OrbitDB via HTTP API."""
    
    def __init__(self, api_endpoint: str = API_ENDPOINT):
        self.api_endpoint = api_endpoint.rstrip('/')
    
    def upload_document(self, document: Document) -> Dict[str, Any]:
        """Upload a document to OrbitDB via API endpoint."""
        try:
            # First, upload content to IPFS
            ipfs_upload_url = f"{self.api_endpoint}/api/ipfs/upload"
            
            ipfs_payload = {
                "content": document.content,
                "fileName": f"{document.id}.txt",
                "contentType": "text/plain"
            }
            
            ipfs_response = requests.post(ipfs_upload_url, json=ipfs_payload)
            ipfs_response.raise_for_status()
            ipfs_data = ipfs_response.json()
            
            if ipfs_data.get("status") != "ok":
                raise Exception(f"IPFS upload failed: {ipfs_data.get('message')}")
            
            # Get the CID from response
            cid = ipfs_data.get("cid")
            
            # Now store document metadata in OrbitDB
            db_upload_url = f"{self.api_endpoint}/api/db/technology"
            
            # Prepare document data with reference to IPFS content
            doc_data = document.to_dict()
            doc_data["cid"] = cid
            
            db_payload = {"data": doc_data}
            
            db_response = requests.post(db_upload_url, json=db_payload)
            db_response.raise_for_status()
            db_data = db_response.json()
            
            if db_data.get("status") != "ok":
                raise Exception(f"OrbitDB upload failed: {db_data.get('message')}")
            
            logger.info(f"Successfully uploaded document '{document.title}' to OrbitDB with ID: {db_data.get('id')}")
            return db_data
        except Exception as e:
            logger.error(f"Error uploading to OrbitDB: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_document_exists(self, url: str) -> bool:
        """Check if a document with the given URL already exists in the database."""
        try:
            api_url = f"{self.api_endpoint}/api/db/technology"
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.warning(f"Error checking document existence: {data.get('message')}")
                return False
            
            documents = data.get("data", [])
            for doc in documents:
                if doc.get("url") == url:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            return False

class WebCrawler:
    """Web crawler for Hampton Roads development information."""
    
    def __init__(self):
        self.phi3 = Phi3Client()
        self.orbitdb = OrbitDBClient()
        self.geocoding_service = GeocodingService()
        self.source_handler_factory = SourceHandlerFactory(self.phi3)
        self.visited_urls = set()
    
    async def crawl_website(self, site_info: Dict[str, str]):
        """Crawl a website for development information."""
        url = site_info.get("url")
        category = site_info.get("category")
        if not url or not category:
            logger.error(f"Missing URL or category in site info: {site_info}")
            return
        
        try:
            logger.info(f"Crawling {url} for {category}...")
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Queue of URLs to crawl (BFS approach)
            queue = [url]
            # Keep track of visited URLs to avoid duplicates
            visited = set()
            
            while queue and len(visited) < MAX_PAGES_PER_SITE:
                current_url = queue.pop(0)
                
                if current_url in visited or current_url in self.visited_urls:
                    continue
                    
                visited.add(current_url)
                self.visited_urls.add(current_url)
                
                try:
                    # Skip binary/media files and certain extensions
                    if should_skip_url(current_url):
                        continue
                    
                    # Check if we already have this document
                    if self.orbitdb.check_document_exists(current_url):
                        logger.info(f"Document already exists for {current_url}, skipping...")
                        continue
                    
                    # Fetch page content with timeout
                    logger.info(f"Fetching {current_url}...")
                    response = requests.get(current_url, timeout=30, headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
                    })
                    response.raise_for_status()
                    
                    content_type = response.headers.get('Content-Type', '')
                    if not content_type.startswith('text/html'):
                        continue
                    
                    html = response.text
                    
                    # Get the appropriate source handler for this URL
                    source_handler = self.source_handler_factory.get_handler_for_url(current_url)
                    source_type = "general"
                    
                    if source_handler:
                        # Use specialized handler for this source type
                        logger.info(f"Using specialized handler for {current_url}: {source_handler.__class__.__name__}")
                        source_type = source_handler.get_source_type()
                        
                        # Extract content using specialized handler
                        extraction_result = source_handler.extract_content(current_url, html)
                        
                        if extraction_result is None:
                            # Source handler determined content is not relevant to Hampton Roads
                            logger.info(f"Content from {current_url} not relevant to Hampton Roads, skipping...")
                            continue
                            
                        # Create document from extraction result
                        document = Document(
                            title=extraction_result["title"],
                            content=extraction_result["content"],
                            url=current_url,
                            source=base_url,
                            category=category,
                            source_type=source_type
                        )
                        
                        # Add location information
                        if "location_info" in extraction_result and extraction_result["location_info"]:
                            location_info = extraction_result["location_info"]
                            document.city = location_info.get("city")
                            document.coordinates = location_info.get("coordinates")
                            
                            # Add additional location data to extracted_info
                            document.extracted_info["location"] = location_info
                            
                        # Add any other extracted information
                        for key, value in extraction_result.items():
                            if key not in ["title", "content", "location_info"]:
                                document.extracted_info[key] = value
                                
                        # Get links to follow from specialized handler
                        soup = BeautifulSoup(html, 'html.parser')
                        next_links = source_handler.get_links_to_follow(current_url, html)
                        
                    else:
                        # Default generic handler if no specialized handler
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title and content
                        title = soup.title.string if soup.title else ""
                        # Get text content from main body of page
                        content = ""
                        body = soup.find('body')
                        if body:
                            # Remove script and style elements
                            for script in body(["script", "style"]):
                                script.extract()
                            content = body.get_text(separator='\n', strip=True)
                        
                        # Limit content length
                        content = content[:MAX_CONTENT_LENGTH]
                        
                        # Skip if content is too short
                        if len(content) < MIN_CONTENT_LENGTH:
                            continue
                        
                        # Check if content is relevant to development projects in Hampton Roads
                        if not self.phi3.is_relevant(content, title):
                            logger.info(f"Content not relevant for {current_url}, skipping...")
                            continue
                        
                        # Find city first using Phi3
                        city = self.phi3.detect_city(content)
                        
                        # Then use our improved location extraction
                        location_info = self.geocoding_service.extract_location_from_text(content, self.phi3)
                        if location_info and location_info.get("city"):
                            city = location_info.get("city")
                            coordinates = location_info.get("coordinates")
                        else:
                            coordinates = None
                        
                        # Check if location is in Hampton Roads
                        if location_info and not self.geocoding_service.is_in_hampton_roads(location_info):
                            logger.info(f"Location not in Hampton Roads for {current_url}, skipping...")
                            continue
                        
                        # Extract structured information
                        extracted_info = self.phi3.extract_project_info(content, current_url)
                        if location_info:
                            extracted_info["location"] = location_info
                        
                        # Create document
                        document = Document(
                            title=title,
                            content=content,
                            url=current_url,
                            source=base_url,
                            category=category,
                            city=city,
                            coordinates=coordinates,
                            extracted_info=extracted_info,
                            source_type=source_type
                        )
                        
                        # Process next level of links
                        next_links = extract_links(soup, current_url, base_url)
                    
                    # Skip if we couldn't determine coordinates
                    if not document.coordinates:
                        logger.info(f"No coordinates available for {current_url}, attempting to geocode...")
                        # One last attempt to find coordinates if we have a city
                        if document.city:
                            city_coords = self.geocoding_service.geocode_address(document.city)
                            if city_coords:
                                document.coordinates = [city_coords["lat"], city_coords["lng"]]
                                logger.info(f"Found coordinates for {document.city}: {document.coordinates}")
                        
                        # If we still don't have coordinates and we need them for map display
                        if not document.coordinates:
                            logger.warning(f"Could not determine coordinates for {current_url}, may not appear on map")
                    
                    # Upload to OrbitDB
                    result = self.orbitdb.upload_document(document)
                    
                    # Add new links to queue
                    if len(visited) < MAX_PAGES_PER_SITE:
                        for link in next_links:
                            if link not in visited and link not in self.visited_urls:
                                queue.append(link)
                    
                    # Random delay between requests
                    time.sleep(random.uniform(1, 3))
                    
                    delay = CRAWL_DELAY + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                
                except Exception as e:
                    logger.error(f"Error crawling {url}: {e}")
                    await asyncio.sleep(CRAWL_DELAY)
            
            await browser.close()
        
        logger.info(f"Completed crawl of {start_url}, visited {pages_crawled} pages")

async def crawl_all_sites():
    """Crawl all target websites."""
    logger.info("Starting crawl of all target websites")
    
    crawler = WebCrawler()
    
    for site_info in TARGET_WEBSITES:
        await crawler.crawl_website(site_info)
    
    logger.info("Completed crawl of all target websites")

def run_crawler():
    """Run the crawler."""
    logger.info("Running Hampton Roads development crawler")
    asyncio.run(crawl_all_sites())

def schedule_crawler():
    """Schedule the crawler to run at regular intervals."""
    logger.info(f"Scheduling crawler to run every {CRAWL_INTERVAL_HOURS} hours")
    
    # Run once immediately
    run_crawler()
    
    # Schedule future runs
    schedule.every(CRAWL_INTERVAL_HOURS).hours.do(run_crawler)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    schedule_crawler() 