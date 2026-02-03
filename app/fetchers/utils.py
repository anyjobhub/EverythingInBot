"""
Fetcher Utilities
Common functions for HTTP requests, RSS parsing, and error handling
"""

import aiohttp
import asyncio
import feedparser
import logging
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def fetch_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 10,
    retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Fetch JSON data from URL with retry logic
    
    Args:
        url: URL to fetch
        headers: Optional HTTP headers
        params: Optional query parameters
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        
    Returns:
        JSON response or None on failure
    """
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url} (attempt {attempt + 1}/{retries})")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        
        # Exponential backoff
        if attempt < retries - 1:
            await asyncio.sleep(2 ** attempt)
    
    return None


async def fetch_rss(url: str, timeout: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch and parse RSS feed
    
    Args:
        url: RSS feed URL
        timeout: Request timeout in seconds
        
    Returns:
        List of feed entries or None on failure
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse RSS in thread pool (feedparser is blocking)
                    loop = asyncio.get_event_loop()
                    feed = await loop.run_in_executor(None, feedparser.parse, content)
                    
                    if feed.entries:
                        return [entry for entry in feed.entries]
                    else:
                        logger.warning(f"No entries in RSS feed: {url}")
                else:
                    logger.warning(f"HTTP {response.status} for RSS feed: {url}")
                    
    except Exception as e:
        logger.error(f"Error fetching RSS {url}: {e}")
    
    return None


async def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch HTML content from URL
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        HTML content or None on failure
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={'User-Agent': 'Mozilla/5.0 (compatible; EverythingInBot/1.0)'}
            ) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    
    except Exception as e:
        logger.error(f"Error fetching HTML {url}: {e}")
    
    return None


def parse_html(html: str, parser: str = 'lxml') -> Optional[BeautifulSoup]:
    """
    Parse HTML with BeautifulSoup
    
    Args:
        html: HTML content
        parser: Parser to use
        
    Returns:
        BeautifulSoup object or None
    """
    try:
        return BeautifulSoup(html, parser)
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
        return None


async def fetch_with_rate_limit(
    urls: List[str],
    fetch_func,
    rate_limit: int = 5,
    **kwargs
) -> List[Any]:
    """
    Fetch multiple URLs with rate limiting
    
    Args:
        urls: List of URLs to fetch
        fetch_func: Async function to use for fetching
        rate_limit: Max concurrent requests
        **kwargs: Additional arguments for fetch_func
        
    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(rate_limit)
    
    async def fetch_with_semaphore(url):
        async with semaphore:
            return await fetch_func(url, **kwargs)
    
    tasks = [fetch_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)


def extract_text_from_html(soup: BeautifulSoup, selector: str) -> str:
    """
    Extract text from HTML element
    
    Args:
        soup: BeautifulSoup object
        selector: CSS selector
        
    Returns:
        Extracted text or empty string
    """
    try:
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return ""


def extract_all_text_from_html(soup: BeautifulSoup, selector: str) -> List[str]:
    """
    Extract text from all matching HTML elements
    
    Args:
        soup: BeautifulSoup object
        selector: CSS selector
        
    Returns:
        List of extracted text
    """
    try:
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements if el]
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return []
