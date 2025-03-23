"""Tools management module for the NetSourceAI chatbot.
This module provides a collection of tools for fetching information from various sources.
"""

from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json
import yaml
import requests
import re
import wikipedia

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class Tools_Class:
    """Class responsible for managing and providing various information retrieval tools.
    
    This class implements different tools for fetching data from various sources
    including Wikipedia, web searches, and system information.
    
    Attributes:
        config (Dict[str, Any]): Application configuration
        ai_tools (List[Dict]): List of available tool definitions
    """
    
    def __init__(self):
        """Initialize tool components and configurations."""
        self.config = load_config()
        self.ai_tools = self._load_tools()
    
    def _load_tools(self) -> List[Dict]:
        """Load tool definitions from JSON configuration.
        
        Returns:
            List[Dict]: List of tool definitions
        """
        with open("tools_definition.json", "r", encoding='utf-8') as file:
            return json.load(file)
    
    # --- Date and Time Method ---
    
    def get_current_date_and_time(self) -> str:
        """Get the current system date and time.
        
        Returns:
            str: Formatted current date and time
        """
        return f"The current date and time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # --- Web Search Methods ---
    
    def fetch_internet_information(self, query: str) -> str:
        """Search and retrieve information from the internet.
        
        Args:
            query (str): Search query string
            
        Returns:
            str: Formatted search results with summaries
        """
        try:
            with DDGS() as ddgs:
                # Perform the search using DuckDuckGo
                results = ddgs.text(
                    query,
                    safesearch=self.config["search"]["safesearch"],
                    max_results=self.config["search"]["max_results"]
                )
                # Process the results
                summary = ""
                for result in results:
                    # Extract title
                    title = result.get('title', 'Title not available')
                    # Extract URL
                    url = result.get('href', '')
                    # Extract and summarize content
                    content = self._get_and_summarize_content(url)
                    # Append to summary
                    summary += f"Title: {title}\nURL: {url}\n - Summary: {content}\n\n"
        except Exception as e:
            # Handle any exceptions that occur during the search
            summary = f"Search error: {e}"
        finally:
            # Return the summary or an error message
            return summary
    
    def _get_and_summarize_content(self, url: str) -> str:
        """Extract and summarize content from a webpage.
        
        Args:
            url (str): URL to process
            
        Returns:
            str: Summarized content
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            text = ' '.join(para.get_text() for para in paragraphs)
            
            sentences = re.split(r'(?<=[.!?]) +', text)
            if sentences:
                summary = ' '.join(sentences[:self.config["search"]["num_sentences"]])
                return summary.strip()
            return "No content found."
        except Exception as e:
            return f"Error processing {url}: {e}"
    
    # --- Wikipedia Methods ---
    
    def fetch_wikipedia_information(self, wikipedia_query: str) -> str:
        """Search and retrieve information from Wikipedia.
        
        Args:
            wikipedia_query (str): Wikipedia search query
            
        Returns:
            str: Formatted Wikipedia search results
        """
        try:
            wikipedia.set_lang(self.config["search"]["wikipedia_lang"])
            pages = wikipedia.search(wikipedia_query)
            return self._process_wikipedia_pages(pages)
        except Exception as error:
            return f"Error during Wikipedia search for {wikipedia_query}: {error}"
    
    def _process_wikipedia_pages(self, pages: List[str]) -> str:
        """Process Wikipedia search results.
        
        Args:
            pages (List[str]): List of Wikipedia page titles
            
        Returns:
            str: Formatted summaries of Wikipedia pages
        """
        summary = ""
        for i, page_name in enumerate(pages[:3]):  # Limit to 3 pages
            try:
                page = wikipedia.page(page_name)
                summary += (f"Page {i+1} - Title: {page.title}\n"
                          f"URL: {page.url}\n"
                          f" - Summary: {page.summary}\n\n")
            except Exception as e:
                summary += f"Error processing page {page_name}: {e}\n\n"
        return summary or "No Wikipedia results found."