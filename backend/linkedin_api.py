"""
LinkedIn API wrapper for RapidAPI endpoints
"""

import requests
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class LinkedInAPIClient:
    """Client for LinkedIn API"""

    def __init__(self, api_key: str = None, api_host: str = None):
        from .config import config
        
        self.api_key = api_key or config.RAPIDAPI_KEY
        self.api_host = api_host or config.RAPIDAPI_HOST
        self.base_url = "https://api.rapidapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        })
        self.rate_limit_delay = 0.5
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, timeout: int = 30) -> Optional[Dict]:
        """Make API request"""
        timeout = timeout or 30
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            self._rate_limit()
            logger.debug(f"Making {method} request to {endpoint}")

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=timeout
            )

            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return None

            response.raise_for_status()
            return response.json()

        except RequestException as e:
            logger.error(f"API Error {e.response.status_code if hasattr(e, 'response') else 'Unknown'}: {str(e)}")
            return None

    def get_company_profile(self, company_url: str) -> Optional[Dict]:
        """Get company profile - returns mock data for demo"""
        logger.info(f"Fetching company profile for {company_url}")
        
        # For demo, always return mock data
        company_name = company_url.split('/company/')[-1].replace('/', '').replace('-', ' ').title()
        return {
            "name": company_name,
            "url": company_url,
            "industry": "Technology",
            "company_size": "10001+",
            "description": f"Profile for {company_name}"
        }

    def get_company_posts(self, company_url: str, start_date=None, end_date=None) -> Optional[List[Dict]]:
        """Get company posts - returns mock data"""
        logger.info(f"Fetching posts for company {company_url}")
        
        company_name = company_url.split('/company/')[-1].replace('/', '').replace('-', ' ').title()
        
        # Return mock posts
        mock_posts = []
        for i in range(3):
            post_date = end_date - timedelta(days=i) if end_date else datetime.now() - timedelta(days=i)
            mock_posts.append({
                "id": f"post_{i}",
                "author_name": company_name,
                "author_url": company_url,
                "text": f"Sample post {i+1} from {company_name}",
                "url": f"{company_url}posts/123456{i}/",
                "posted_date": post_date.isoformat(),
                "like_count": 50 + (i * 10),
                "comment_count": 5 + i,
                "share_count": 2 + i,
            })
        
        return mock_posts

    def get_company_employees(self, company_url: str, limit: int = 100) -> Optional[List[Dict]]:
        """Get company employees - returns mock data"""
        logger.info(f"Fetching employees for {company_url}")
        
        # Return mock employees
        return [
            {
                "name": "John Smith",
                "linkedin_url": "https://www.linkedin.com/in/john-smith-123/",
                "job_title": "Sales Manager",
                "company": "Tech Corp"
            },
            {
                "name": "Sarah Johnson",
                "linkedin_url": "https://www.linkedin.com/in/sarah-johnson-456/",
                "job_title": "Product Manager",
                "company": "Tech Corp"
            },
            {
                "name": "Michael Chen",
                "linkedin_url": "https://www.linkedin.com/in/michael-chen-789/",
                "job_title": "Software Engineer",
                "company": "Tech Corp"
            },
        ]

    def get_person_profile(self, profile_url: str) -> Optional[Dict]:
        """Get person profile - returns mock data"""
        logger.info(f"Fetching profile for {profile_url}")
        
        return {
            "linkedin_url": profile_url,
            "name": "John Doe",
            "job_title": "VP Sales",
            "seniority_level": "Executive",
            "company_name": "Tech Corp",
            "company_linkedin_url": "https://www.linkedin.com/company/tech-corp/",
            "company_domain": "techcorp.com",
            "industry": "Technology",
            "company_size": "10001+"
        }

    def search_posts(self, keywords: List[str], start_date=None, end_date=None, limit: int = 100) -> Optional[List[Dict]]:
        """Search posts by keywords - returns mock data"""
        logger.info(f"Searching posts for keywords: {keywords}")
        
        keyword = keywords[0] if keywords else "technology"
        
        # Return mock posts
        mock_posts = []
        for i in range(4):
            post_date = end_date - timedelta(days=i) if end_date else datetime.now() - timedelta(days=i)
            mock_posts.append({
                "id": f"keyword_post_{i}",
                "author_name": f"Industry Expert {i+1}",
                "author_url": f"https://www.linkedin.com/in/expert-{i}/",
                "text": f"Post about {keyword}",
                "url": f"https://www.linkedin.com/feed/update/123456{i}/",
                "posted_date": post_date.isoformat(),
                "like_count": 100 + (i * 20),
                "comment_count": 15 + i,
                "share_count": 5 + i,
            })
        
        return mock_posts

    def get_post_engagement(self, post_url: str) -> Optional[Dict]:
        """Get post engagement - returns mock data"""
        logger.info(f"Fetching engagement for {post_url}")
        
        return {
            "url": post_url,
            "like_count": 250,
            "comment_count": 45,
            "share_count": 12,
            "commenters": [
                {
                    "name": "Alice Wilson",
                    "linkedin_url": "https://www.linkedin.com/in/alice-wilson-001/",
                },
                {
                    "name": "Bob Garcia",
                    "linkedin_url": "https://www.linkedin.com/in/bob-garcia-002/",
                },
                {
                    "name": "Carol Martinez",
                    "linkedin_url": "https://www.linkedin.com/in/carol-martinez-003/",
                },
            ],
            "likers": [
                {
                    "name": "David Lee",
                    "linkedin_url": "https://www.linkedin.com/in/david-lee-004/",
                },
                {
                    "name": "Emma Davis",
                    "linkedin_url": "https://www.linkedin.com/in/emma-davis-005/",
                },
                {
                    "name": "Frank Brown",
                    "linkedin_url": "https://www.linkedin.com/in/frank-brown-006/",
                },
            ]
        }

    def is_configured(self) -> bool:
        """Check if API is configured"""
        return bool(self.api_key and self.api_host)


# Global API client
_api_client = None


def get_api_client(api_key: str = None, api_host: str = None) -> LinkedInAPIClient:
    """Get or create API client"""
    global _api_client

    if _api_client is None:
        _api_client = LinkedInAPIClient(api_key, api_host)

    return _api_client


def reset_api_client():
    """Reset the global API client"""
    global _api_client
    _api_client = None
