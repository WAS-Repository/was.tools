#!/usr/bin/env python3
"""
Specialized Source Handlers for Hampton Roads Projects
-----------------------------------------------------
Handlers for different types of data sources, including patents and 
government documents, with specialized extraction and processing logic.
"""

import os
import re
import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import httpx

# Import the location utilities
from location_utils import GeocodingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("source_handlers")

class BaseSourceHandler:
    """Base class for all source handlers."""
    
    def __init__(self, phi3_client=None):
        """
        Initialize the base source handler.
        
        Args:
            phi3_client: Phi3Client instance for NLP processing
        """
        self.phi3_client = phi3_client
        self.geocoding_service = GeocodingService()
        
    def can_handle(self, url: str) -> bool:
        """
        Determine if this handler can process the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if this handler can process the URL, False otherwise
        """
        raise NotImplementedError("Subclasses must implement can_handle")
        
    def extract_content(self, url: str, html_content: str) -> Dict[str, Any]:
        """
        Extract content from the HTML.
        
        Args:
            url: Source URL
            html_content: HTML content to process
            
        Returns:
            Dictionary with extracted content and metadata
        """
        raise NotImplementedError("Subclasses must implement extract_content")
        
    def get_source_type(self) -> str:
        """
        Get the type of source this handler processes.
        
        Returns:
            Source type identifier string
        """
        raise NotImplementedError("Subclasses must implement get_source_type")
        
    def get_links_to_follow(self, url: str, html_content: str) -> List[str]:
        """
        Extract links from the HTML that should be followed.
        
        Args:
            url: Source URL
            html_content: HTML content to process
            
        Returns:
            List of URLs to follow
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = urlparse(url)
        domain = f"{base_url.scheme}://{base_url.netloc}"
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Make relative URLs absolute
            if href.startswith('/'):
                href = domain + href
            elif not href.startswith(('http://', 'https://')):
                href = urljoin(url, href)
                
            # Only follow links from the same domain
            if urlparse(href).netloc == base_url.netloc:
                links.append(href)
                
        return links
        
    def extract_location(self, text: str, title: str = "") -> Dict[str, Any]:
        """
        Extract location information from text.
        
        Args:
            text: Text to extract location from
            title: Optional title for additional context
            
        Returns:
            Dictionary with location information
        """
        combined_text = f"{title}\n{text}"
        return self.geocoding_service.extract_location_from_text(
            combined_text, 
            self.phi3_client
        )


class PatentSourceHandler(BaseSourceHandler):
    """Handler for patent sources like USPTO and Google Patents."""
    
    def can_handle(self, url: str) -> bool:
        """Determine if this handler can process patent URLs."""
        patent_domains = [
            'patents.google.com',
            'patft.uspto.gov',
            'appft.uspto.gov',
            'portal.uspto.gov',
        ]
        
        parsed_url = urlparse(url)
        return parsed_url.netloc in patent_domains
        
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        return "patent"
        
    def extract_content(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract content from patent HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {
            "title": "",
            "content": "",
            "patent_number": "",
            "inventors": [],
            "filing_date": "",
            "publication_date": "",
            "assignee": "",
            "location_info": {},
            "source_type": self.get_source_type()
        }
        
        # Handle Google Patents
        if 'patents.google.com' in url:
            # Extract title
            title_elem = soup.select_one('h1.title')
            if title_elem:
                result["title"] = title_elem.get_text(strip=True)
                
            # Extract abstract/content
            abstract_elem = soup.select_one('div.abstract')
            if abstract_elem:
                result["content"] = abstract_elem.get_text(strip=True)
                
            # Extract patent number
            patent_elem = soup.select_one('meta[name="citation_patent_number"]')
            if patent_elem:
                result["patent_number"] = patent_elem.get('content', '')
                
            # Extract inventors
            inventor_elems = soup.select('meta[name="citation_author"]')
            result["inventors"] = [elem.get('content', '') for elem in inventor_elems]
            
            # Extract dates
            filing_date_elem = soup.select_one('meta[name="citation_patent_application_date"]')
            if filing_date_elem:
                result["filing_date"] = filing_date_elem.get('content', '')
                
            pub_date_elem = soup.select_one('meta[name="citation_patent_publication_date"]')
            if pub_date_elem:
                result["publication_date"] = pub_date_elem.get('content', '')
                
            # Extract assignee
            assignee_elem = soup.select_one('dd.assignee-name')
            if assignee_elem:
                result["assignee"] = assignee_elem.get_text(strip=True)
        
        # Handle USPTO Patent Full-Text Database
        elif 'patft.uspto.gov' in url:
            # USPTO uses tables for layout, making extraction more complex
            # Extract title
            title_elem = soup.find('font', {'size': '+1'})
            if title_elem:
                result["title"] = title_elem.get_text(strip=True)
            
            # Extract content - abstract is usually in a specific table cell
            for td in soup.find_all('td'):
                if td.find(string=re.compile('Abstract')):
                    abstract_text = td.get_text().split('Abstract', 1)
                    if len(abstract_text) > 1:
                        result["content"] = abstract_text[1].strip()
                        break
            
            # Extract patent number from URL or table
            patent_match = re.search(r'PN/(\d+)', url)
            if patent_match:
                result["patent_number"] = patent_match.group(1)
                
            # Get full text for location extraction
            full_text = soup.get_text()
            
            # Extract inventors - typically listed after "Inventors:"
            inventors_match = re.search(r'Inventors?:\s*(.+?)(?:;|Assignee|$)', full_text, re.DOTALL)
            if inventors_match:
                inventors_text = inventors_match.group(1).strip()
                result["inventors"] = [inv.strip() for inv in inventors_text.split(';')]
                
            # Extract assignee
            assignee_match = re.search(r'Assignee:\s*(.+?)(?:;|$)', full_text, re.DOTALL)
            if assignee_match:
                result["assignee"] = assignee_match.group(1).strip()
        
        # If we have inventors with addresses, try to extract Hampton Roads locations
        inventor_text = ', '.join(result["inventors"])
        location_from_inventors = self.extract_location(inventor_text)
        
        # If assignee has location info, try that too
        assignee_location = self.extract_location(result["assignee"])
        
        # Also check the main content
        content_location = None
        if result["content"]:
            content_location = self.extract_location(result["content"], result["title"])
        
        # Prioritize locations based on confidence
        locations = [
            location_from_inventors,
            assignee_location,
            content_location
        ]
        
        # Filter out None values and sort by confidence (highest first)
        locations = [loc for loc in locations if loc and loc.get("confidence", 0) > 0]
        locations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        # Use the highest confidence location
        if locations:
            result["location_info"] = locations[0]
            
            # Only proceed if the location is in Hampton Roads
            if self.geocoding_service.is_in_hampton_roads(result["location_info"]):
                # Format the full content for storage
                full_content = f"""
Patent: {result['patent_number']}
Title: {result['title']}
Inventors: {', '.join(result['inventors'])}
Assignee: {result['assignee']}
Filing Date: {result['filing_date']}
Publication Date: {result['publication_date']}
Location: {result['location_info'].get('city', 'Unknown')}, Virginia
Coordinates: {result['location_info'].get('coordinates', [])}

Abstract:
{result['content']}
                """
                result["content"] = full_content.strip()
                return result
                
        # If location isn't relevant to Hampton Roads, return None
        return None


class GovernmentSourceHandler(BaseSourceHandler):
    """Handler for government sources like regulations.gov and local government sites."""
    
    def can_handle(self, url: str) -> bool:
        """Determine if this handler can process government URLs."""
        gov_domains = [
            '.gov',  # Any .gov domain
            'regulations.gov',
            'virginiabeach.gov',
            'norfolk.gov',
            'chesapeakeva.gov',
            'hampton.gov',
            'nnva.gov',  # Newport News
            'portsmouthva.gov',
            'suffolkva.us',
            'williamsburgva.gov',
            'poquoson-va.gov',
            'yorkcounty.gov',
            'gloucesterva.info',
            'smithfieldva.gov',
            'co.isle-of-wight.va.us',
            'jamescitycountyva.gov',
        ]
        
        parsed_url = urlparse(url)
        return any(domain in parsed_url.netloc for domain in gov_domains)
        
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        return "government"
        
    def extract_content(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract content from government source HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {
            "title": "",
            "content": "",
            "document_id": "",
            "agency": "",
            "publication_date": "",
            "location_info": {},
            "document_type": "government",
            "source_type": self.get_source_type()
        }
        
        # Extract title - common patterns across government sites
        title_elements = [
            soup.select_one('h1'),  # Most common
            soup.select_one('title'),
            soup.select_one('meta[property="og:title"]'),
            soup.select_one('.title'),
            soup.select_one('#title')
        ]
        
        for elem in title_elements:
            if elem and elem.get_text(strip=True):
                result["title"] = elem.get_text(strip=True)
                break
                
        # For regulations.gov
        if 'regulations.gov' in url:
            # Extract document ID from URL
            doc_id_match = re.search(r'document=([^&]+)', url)
            if doc_id_match:
                result["document_id"] = doc_id_match.group(1)
                
            # Extract agency information
            agency_elem = soup.select_one('.agency-name')
            if agency_elem:
                result["agency"] = agency_elem.get_text(strip=True)
                
            # Extract content - regulations.gov uses specific content containers
            content_elem = soup.select_one('.document-content')
            if content_elem:
                result["content"] = content_elem.get_text(strip=True)
        
        # For local government sites, we need more generic extraction
        else:
            # Try to find main content area based on common patterns
            content_selectors = [
                'main',
                'article',
                '#content',
                '.content',
                '.main-content',
                'section.main'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Extract text but skip navigation elements
                    for nav in content_elem.select('nav'):
                        nav.decompose()
                    for menu in content_elem.select('.menu, .nav, .navigation'):
                        menu.decompose()
                        
                    result["content"] = content_elem.get_text(strip=True)
                    if len(result["content"]) > 200:  # Only use if substantial content
                        break
            
            # If we haven't found content, try getting all paragraph text
            if not result["content"]:
                paragraphs = soup.select('p')
                result["content"] = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
        
        # If still no content, use the whole page body
        if not result["content"] and soup.body:
            result["content"] = soup.body.get_text(strip=True)
            
        # If we have content, try to extract location
        if result["content"]:
            # For government sources, use both title and content for location extraction
            result["location_info"] = self.extract_location(result["content"], result["title"])
            
            # Only proceed if the location is in Hampton Roads
            if result["location_info"] and self.geocoding_service.is_in_hampton_roads(result["location_info"]):
                # Format for storage
                domain = urlparse(url).netloc
                agency_text = result["agency"] if result["agency"] else domain
                
                full_content = f"""
Source: {agency_text}
Title: {result['title']}
URL: {url}
Document ID: {result['document_id']}
Location: {result['location_info'].get('city', 'Unknown')}, Virginia
Coordinates: {result['location_info'].get('coordinates', [])}

Content Summary:
{result['content'][:2000]}{'...' if len(result['content']) > 2000 else ''}
                """
                result["content"] = full_content.strip()
                return result
                
        # If location isn't relevant to Hampton Roads, return None
        return None


class LocalNewsSourceHandler(BaseSourceHandler):
    """Handler for local news sources in Hampton Roads."""
    
    def can_handle(self, url: str) -> bool:
        """Determine if this handler can process local news URLs."""
        news_domains = [
            'pilotonline.com',  # The Virginian-Pilot
            'dailypress.com',    # Daily Press
            'wavy.com',          # WAVY-TV
            'wtkr.com',          # WTKR
            '13newsnow.com',     # 13News Now
            'wvec.com',          # WVEC
            'wydaily.com',       # Williamsburg Yorktown Daily
            'southsidedaily.com' # Southside Daily
        ]
        
        parsed_url = urlparse(url)
        return any(domain in parsed_url.netloc for domain in news_domains)
        
    def get_source_type(self) -> str:
        """Get the source type identifier."""
        return "news"
        
    def extract_content(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract content from local news HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        result = {
            "title": "",
            "content": "",
            "author": "",
            "publication_date": "",
            "location_info": {},
            "source_type": self.get_source_type()
        }
        
        # Extract title
        title_elem = soup.select_one('h1') or soup.select_one('meta[property="og:title"]')
        if title_elem:
            if hasattr(title_elem, 'get_text'):
                result["title"] = title_elem.get_text(strip=True)
            else:
                result["title"] = title_elem.get('content', '')
                
        # Extract content - article or main content
        content_selectors = [
            'article',
            '.article-content',
            '.story-content',
            '.entry-content',
            'main',
            '#main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Extract paragraphs
                paragraphs = content_elem.select('p')
                if paragraphs:
                    result["content"] = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
                    break
        
        # Extract publication date
        date_selectors = [
            'meta[property="article:published_time"]',
            'time',
            '.date',
            '.published-date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if hasattr(date_elem, 'get_text'):
                    result["publication_date"] = date_elem.get_text(strip=True)
                else:
                    result["publication_date"] = date_elem.get('content', '')
                break
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            '.byline',
            '.author'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if hasattr(author_elem, 'get_text'):
                    result["author"] = author_elem.get_text(strip=True)
                else:
                    result["author"] = author_elem.get('content', '')
                break
        
        # Extract location information
        if result["content"]:
            result["location_info"] = self.extract_location(result["content"], result["title"])
            
            # Only proceed if the location is in Hampton Roads
            if result["location_info"] and self.geocoding_service.is_in_hampton_roads(result["location_info"]):
                # Format for storage
                domain = urlparse(url).netloc
                
                full_content = f"""
Source: {domain}
Title: {result['title']}
Author: {result['author']}
Published: {result['publication_date']}
Location: {result['location_info'].get('city', 'Unknown')}, Virginia
Coordinates: {result['location_info'].get('coordinates', [])}

Content:
{result['content']}
                """
                result["content"] = full_content.strip()
                return result
                
        # If location isn't relevant to Hampton Roads, return None
        return None


class SourceHandlerFactory:
    """Factory for creating appropriate source handlers."""
    
    def __init__(self, phi3_client=None):
        """
        Initialize the source handler factory.
        
        Args:
            phi3_client: Phi3Client instance for NLP processing
        """
        self.phi3_client = phi3_client
        self.handlers = [
            PatentSourceHandler(phi3_client),
            GovernmentSourceHandler(phi3_client),
            LocalNewsSourceHandler(phi3_client)
        ]
        
    def get_handler_for_url(self, url: str) -> Optional[BaseSourceHandler]:
        """
        Get the appropriate handler for a URL.
        
        Args:
            url: URL to get handler for
            
        Returns:
            Appropriate source handler or None
        """
        for handler in self.handlers:
            if handler.can_handle(url):
                return handler
                
        return None
