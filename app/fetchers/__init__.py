"""
Fetchers Package
Automated data fetching from public APIs, RSS feeds, and legal web scraping
"""

from .job_fetcher import fetch_all_jobs
from .course_fetcher import fetch_all_courses

__all__ = ['fetch_all_jobs', 'fetch_all_courses']
