"""
Deduplication Utilities
Hash-based duplicate detection for jobs and courses
"""

import hashlib
from typing import Dict, Any


def generate_job_hash(title: str, company: str, url: str) -> str:
    """
    Generate unique hash for job listing
    
    Args:
        title: Job title
        company: Company name
        url: Job URL
        
    Returns:
        MD5 hash string
    """
    # Normalize and combine fields
    data = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def generate_course_hash(title: str, platform: str) -> str:
    """
    Generate unique hash for course
    
    Args:
        title: Course title
        platform: Platform name
        
    Returns:
        MD5 hash string
    """
    # Normalize and combine fields
    data = f"{title.lower().strip()}|{platform.lower().strip()}"
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def is_duplicate(collection, hash_value: str) -> bool:
    """
    Check if hash already exists in collection
    
    Args:
        collection: MongoDB collection
        hash_value: Hash to check
        
    Returns:
        True if duplicate exists
    """
    return collection.find_one({"hash": hash_value}) is not None


async def is_duplicate_async(collection, hash_value: str) -> bool:
    """
    Async version of is_duplicate
    
    Args:
        collection: MongoDB collection
        hash_value: Hash to check
        
    Returns:
        True if duplicate exists
    """
    result = await collection.find_one({"hash": hash_value})
    return result is not None


def deduplicate_list(items: list, hash_key: str = "hash") -> list:
    """
    Remove duplicates from list based on hash key
    
    Args:
        items: List of dictionaries
        hash_key: Key containing hash value
        
    Returns:
        Deduplicated list
    """
    seen = set()
    unique_items = []
    
    for item in items:
        hash_value = item.get(hash_key)
        if hash_value and hash_value not in seen:
            seen.add(hash_value)
            unique_items.append(item)
    
    return unique_items
