"""
Job Fetcher
Automated job fetching from 12 public sources (global + India)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.fetchers.utils import fetch_json, fetch_rss, fetch_html, parse_html, extract_text_from_html, extract_all_text_from_html
from app.utils.normalization import normalize_job_data
from app.utils.deduplication import generate_job_hash

logger = logging.getLogger(__name__)


# ============================================
# GLOBAL JOB SOURCES
# ============================================

async def fetch_remotive() -> List[Dict[str, Any]]:
    """
    Fetch jobs from Remotive API (global remote jobs)
    URL: https://remotive.com/api/remote-jobs
    """
    logger.info("Fetching jobs from Remotive...")
    
    url = "https://remotive.com/api/remote-jobs"
    data = await fetch_json(url)
    
    if not data or 'jobs' not in data:
        logger.warning("No jobs found from Remotive")
        return []
    
    jobs = []
    for job in data['jobs'][:50]:  # Limit to 50 jobs
        try:
            normalized = normalize_job_data(
                {
                    'title': job.get('title'),
                    'company': job.get('company_name'),
                    'location': 'Remote',
                    'description': job.get('description', '')[:500],
                    'url': job.get('url'),
                    'tags': job.get('tags', []),
                    'posted_at': job.get('publication_date'),
                    'salary': job.get('salary')
                },
                source='remotive',
                default_country='global'
            )
            
            # Generate hash
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing Remotive job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from Remotive")
    return jobs


async def fetch_arbeitnow() -> List[Dict[str, Any]]:
    """
    Fetch jobs from Arbeitnow API (global jobs)
    URL: https://www.arbeitnow.com/api/job-board-api
    """
    logger.info("Fetching jobs from Arbeitnow...")
    
    url = "https://www.arbeitnow.com/api/job-board-api"
    data = await fetch_json(url)
    
    if not data or 'data' not in data:
        logger.warning("No jobs found from Arbeitnow")
        return []
    
    jobs = []
    for job in data['data'][:50]:
        try:
            normalized = normalize_job_data(
                {
                    'title': job.get('title'),
                    'company': job.get('company_name'),
                    'location': job.get('location', 'Not specified'),
                    'description': job.get('description', '')[:500],
                    'url': job.get('url'),
                    'tags': job.get('tags', []),
                    'posted_at': job.get('created_at')
                },
                source='arbeitnow',
                default_country='global'
            )
            
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing Arbeitnow job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from Arbeitnow")
    return jobs


async def fetch_us_gov_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from US Government Jobs RSS
    URL: https://www.usajobs.gov/rss/jobs
    """
    logger.info("Fetching jobs from US Government...")
    
    url = "https://www.usajobs.gov/rss/jobs"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from US Government RSS")
        return []
    
    jobs = []
    for entry in entries[:30]:
        try:
            normalized = normalize_job_data(
                {
                    'title': entry.get('title'),
                    'company': 'US Government',
                    'location': entry.get('summary', 'USA'),
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='us_gov',
                default_country='us'
            )
            
            normalized['category'] = 'government'
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing US Gov job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from US Government")
    return jobs


async def fetch_uk_gov_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from UK Government Jobs RSS
    Note: UK Civil Service jobs feed
    """
    logger.info("Fetching jobs from UK Government...")
    
    # UK government jobs often require specific search parameters
    # Using a general IT jobs feed as example
    url = "https://www.civilservicejobs.service.gov.uk/csr/index.cgi?SID=dXNlcnNlYXJjaGNvbnRleHQ9NzU3NjY5MiZvd25lcj01MDcwMDAwJm93bmVydHlwZT1mYWlyJnBhZ2VjbGFzcz1Kb2JzJnBhZ2VhY3Rpb249c2VhcmNoY29udGV4dGNvbnZlcnQmc2VhcmNoc29ydD1zY29yZSZzZWFyY2hvcmRlcj1kZXNjJmNzb3VyY2U9Y3NxX2RlZmF1bHQ%3D"
    
    # For now, return empty as UK RSS might need specific handling
    # In production, implement proper UK jobs RSS parsing
    logger.warning("UK Government jobs fetcher not fully implemented")
    return []


async def fetch_indeed_rss() -> List[Dict[str, Any]]:
    """
    Fetch jobs from Indeed RSS feeds
    URL: https://www.indeed.com/rss?q=software+engineer
    """
    logger.info("Fetching jobs from Indeed RSS...")
    
    # Multiple queries for diverse results
    queries = [
        "software+engineer",
        "python+developer",
        "data+scientist",
        "remote+jobs"
    ]
    
    all_jobs = []
    
    for query in queries:
        url = f"https://www.indeed.com/rss?q={query}&l="
        entries = await fetch_rss(url)
        
        if not entries:
            continue
        
        for entry in entries[:10]:  # Limit per query
            try:
                # Extract location from title (Indeed format: "Title - Location")
                title_parts = entry.get('title', '').split(' - ')
                title = title_parts[0] if title_parts else entry.get('title')
                location = title_parts[1] if len(title_parts) > 1 else 'Not specified'
                
                normalized = normalize_job_data(
                    {
                        'title': title,
                        'company': entry.get('author', 'Unknown'),
                        'location': location,
                        'description': entry.get('summary', '')[:500],
                        'url': entry.get('link'),
                        'posted_at': entry.get('published')
                    },
                    source='indeed',
                    default_country='global'
                )
                
                normalized['hash'] = generate_job_hash(
                    normalized['title'],
                    normalized['company'],
                    normalized['url']
                )
                
                all_jobs.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing Indeed job: {e}")
    
    logger.info(f"Fetched {len(all_jobs)} jobs from Indeed")
    return all_jobs


# ============================================
# INDIA JOB SOURCES
# ============================================

async def fetch_sarkari_exam() -> List[Dict[str, Any]]:
    """
    Fetch jobs from Sarkari Exam RSS (India government jobs)
    URL: https://www.sarkariexam.com/feed
    """
    logger.info("Fetching jobs from Sarkari Exam...")
    
    url = "https://www.sarkariexam.com/feed"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from Sarkari Exam")
        return []
    
    jobs = []
    for entry in entries[:30]:
        try:
            normalized = normalize_job_data(
                {
                    'title': entry.get('title'),
                    'company': 'Government of India',
                    'location': 'India',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='sarkari_exam',
                default_country='india'
            )
            
            normalized['category'] = 'government'
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing Sarkari Exam job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from Sarkari Exam")
    return jobs


async def fetch_ht_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from Hindustan Times Employment RSS
    URL: https://www.hindustantimes.com/feeds/rss/education/employment-news/rssfeed.xml
    """
    logger.info("Fetching jobs from Hindustan Times...")
    
    url = "https://www.hindustantimes.com/feeds/rss/education/employment-news/rssfeed.xml"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from Hindustan Times")
        return []
    
    jobs = []
    for entry in entries[:20]:
        try:
            normalized = normalize_job_data(
                {
                    'title': entry.get('title'),
                    'company': 'Various',
                    'location': 'India',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='hindustan_times',
                default_country='india'
            )
            
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing HT job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from Hindustan Times")
    return jobs


async def fetch_the_hindu_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from The Hindu Business RSS
    URL: https://www.thehindu.com/business/Agri-Business/feeder/default.rss
    """
    logger.info("Fetching jobs from The Hindu...")
    
    url = "https://www.thehindu.com/business/Agri-Business/feeder/default.rss"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from The Hindu")
        return []
    
    jobs = []
    for entry in entries[:15]:
        try:
            # Filter for job-related content
            title = entry.get('title', '')
            if not any(word in title.lower() for word in ['job', 'recruitment', 'hiring', 'vacancy']):
                continue
            
            normalized = normalize_job_data(
                {
                    'title': title,
                    'company': 'Various',
                    'location': 'India',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='the_hindu',
                default_country='india'
            )
            
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing The Hindu job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from The Hindu")
    return jobs


async def fetch_sarkariresultcm() -> List[Dict[str, Any]]:
    """
    Fetch jobs from SarkariResultCM RSS
    URL: https://www.sarkariresultcm.in/feed
    """
    logger.info("Fetching jobs from SarkariResultCM...")
    
    url = "https://www.sarkariresultcm.in/feed"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from SarkariResultCM")
        return []
    
    jobs = []
    for entry in entries[:25]:
        try:
            normalized = normalize_job_data(
                {
                    'title': entry.get('title'),
                    'company': 'Government of India',
                    'location': 'India',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='sarkariresultcm',
                default_country='india'
            )
            
            normalized['category'] = 'government'
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing SarkariResultCM job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from SarkariResultCM")
    return jobs


async def fetch_indgovtjobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from IndGovtJobs RSS
    URL: https://feeds.feedburner.com/IndGovtJobs
    """
    logger.info("Fetching jobs from IndGovtJobs...")
    
    url = "https://feeds.feedburner.com/IndGovtJobs"
    entries = await fetch_rss(url)
    
    if not entries:
        logger.warning("No jobs found from IndGovtJobs")
        return []
    
    jobs = []
    for entry in entries[:25]:
        try:
            normalized = normalize_job_data(
                {
                    'title': entry.get('title'),
                    'company': 'Government of India',
                    'location': 'India',
                    'description': entry.get('summary', '')[:500],
                    'url': entry.get('link'),
                    'posted_at': entry.get('published')
                },
                source='indgovtjobs',
                default_country='india'
            )
            
            normalized['category'] = 'government'
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing IndGovtJobs job: {e}")
    
    logger.info(f"Fetched {len(jobs)} jobs from IndGovtJobs")
    return jobs


async def scrape_freejobalert() -> List[Dict[str, Any]]:
    """
    Scrape jobs from FreeJobAlert (static HTML scraping)
    URL: https://www.freejobalert.com/government-jobs/
    LEGAL: Static text scraping only, no automation, no private data
    """
    logger.info("Scraping jobs from FreeJobAlert...")
    
    url = "https://www.freejobalert.com/government-jobs/"
    html = await fetch_html(url)
    
    if not html:
        logger.warning("Failed to fetch FreeJobAlert HTML")
        return []
    
    soup = parse_html(html)
    if not soup:
        return []
    
    jobs = []
    
    try:
        # Find job listings (adjust selectors based on actual HTML structure)
        job_cards = soup.select('.job-card, .job-listing, article')[:20]
        
        for card in job_cards:
            try:
                # Extract job details
                title_elem = card.select_one('h2, h3, .job-title, a')
                link_elem = card.select_one('a')
                desc_elem = card.select_one('p, .description, .summary')
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url_link = link_elem.get('href', '')
                
                # Make absolute URL
                if url_link and not url_link.startswith('http'):
                    url_link = f"https://www.freejobalert.com{url_link}"
                
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                normalized = normalize_job_data(
                    {
                        'title': title,
                        'company': 'Government of India',
                        'location': 'India',
                        'description': description[:500],
                        'url': url_link
                    },
                    source='freejobalert',
                    default_country='india'
                )
                
                normalized['category'] = 'government'
                normalized['hash'] = generate_job_hash(
                    normalized['title'],
                    normalized['company'],
                    normalized['url']
                )
                
                jobs.append(normalized)
            except Exception as e:
                logger.error(f"Error parsing FreeJobAlert job card: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping FreeJobAlert: {e}")
    
    logger.info(f"Scraped {len(jobs)} jobs from FreeJobAlert")
    return jobs


async def fetch_aicte_internships() -> List[Dict[str, Any]]:
    """
    Fetch internships from AICTE API
    URL: https://internship.aicte-india.org/api/internships
    """
    logger.info("Fetching internships from AICTE...")
    
    url = "https://internship.aicte-india.org/api/internships"
    data = await fetch_json(url)
    
    if not data:
        logger.warning("No internships found from AICTE")
        return []
    
    jobs = []
    
    # Handle different response formats
    internships = data if isinstance(data, list) else data.get('data', [])
    
    for internship in internships[:30]:
        try:
            normalized = normalize_job_data(
                {
                    'title': internship.get('title') or internship.get('position'),
                    'company': internship.get('company') or internship.get('organization'),
                    'location': internship.get('location', 'India'),
                    'description': internship.get('description', '')[:500],
                    'url': internship.get('url') or internship.get('apply_link', ''),
                    'posted_at': internship.get('posted_date')
                },
                source='aicte',
                default_country='india'
            )
            
            normalized['category'] = 'internship'
            normalized['hash'] = generate_job_hash(
                normalized['title'],
                normalized['company'],
                normalized['url']
            )
            
            jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error normalizing AICTE internship: {e}")
    
    logger.info(f"Fetched {len(jobs)} internships from AICTE")
    return jobs


# ============================================
# MAIN FETCHER FUNCTION
# ============================================

async def fetch_all_jobs() -> List[Dict[str, Any]]:
    """
    Fetch jobs from all sources concurrently
    
    Returns:
        List of all normalized jobs
    """
    logger.info("Starting job fetch from all sources...")
    
    # Fetch from all sources concurrently
    results = await asyncio.gather(
        fetch_remotive(),
        fetch_arbeitnow(),
        fetch_us_gov_jobs(),
        fetch_indeed_rss(),
        fetch_sarkari_exam(),
        fetch_ht_jobs(),
        fetch_the_hindu_jobs(),
        fetch_sarkariresultcm(),
        fetch_indgovtjobs(),
        scrape_freejobalert(),
        fetch_aicte_internships(),
        return_exceptions=True
    )
    
    # Combine all jobs
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Fetcher error: {result}")
    
    logger.info(f"Total jobs fetched: {len(all_jobs)}")
    return all_jobs
