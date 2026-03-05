"""
Pydantic data models for LinkedIn enrichment workflow
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EngagementType(str, Enum):
    """Types of engagement with posts"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"


class SourceType(str, Enum):
    """Source of discovery for engagement"""
    COMPANY_POST = "company_post"
    EMPLOYEE_POST = "employee_post"
    KEYWORD_SEARCH = "keyword_search"


class Company(BaseModel):
    """Company profile information"""
    name: str
    linkedin_url: str
    company_id: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    follower_count: Optional[int] = None

    class Config:
        from_attributes = True


class LinkedInPost(BaseModel):
    """LinkedIn post information"""
    post_id: str
    author_name: str
    author_linkedin_url: str
    post_text: Optional[str] = None
    post_url: Optional[str] = None
    posted_date: datetime
    engagement_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    source: SourceType
    source_detail: Optional[str] = None

    class Config:
        from_attributes = True


class Person(BaseModel):
    """Person profile - enriched with company/title info"""
    linkedin_profile_url: str
    full_name: str
    job_title: Optional[str] = None
    seniority_level: Optional[str] = None
    company_name: Optional[str] = None
    company_linkedin_url: Optional[str] = None
    company_domain: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    engagement_type: EngagementType
    engagement_count: int = 1
    engagement_types: List[EngagementType] = Field(default_factory=list)
    source_type: List[SourceType] = Field(default_factory=list)
    source_detail: List[str] = Field(default_factory=list)
    engagement_date: Optional[datetime] = None
    post_date: Optional[datetime] = None
    enriched_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class EnrichmentRequest(BaseModel):
    """Request model for enrichment workflow"""
    company_urls: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    start_date: datetime
    end_date: datetime
    slack_webhook_url: Optional[str] = None
    enable_notifications: bool = False

    class Config:
        from_attributes = True


class EnrichmentResponse(BaseModel):
    """Response model for enrichment workflow"""
    status: str
    total_posts_found: int = 0
    total_engagements: int = 0
    unique_people_enriched: int = 0
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class FilterOptions(BaseModel):
    """Options for filtering enriched results before export"""
    job_titles: Optional[List[str]] = None
    seniority_levels: Optional[List[str]] = None
    company_sizes: Optional[List[str]] = None
    engagement_types: Optional[List[EngagementType]] = None
    source_types: Optional[List[SourceType]] = None
    industries: Optional[List[str]] = None

    class Config:
        from_attributes = True
