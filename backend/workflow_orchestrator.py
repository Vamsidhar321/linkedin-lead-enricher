"""
Workflow orchestrator that coordinates company-based and keyword-based scraping
"""

import logging
from typing import List, Optional, Callable
from datetime import datetime
from .data_models import (
    Person, LinkedInPost, SourceType, EngagementType,
    EnrichmentRequest, EnrichmentResponse
)
from .linkedin_api import LinkedInAPIClient
from .deduplication import Deduplicator
from .data_exporter import DataExporter

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates the complete enrichment workflow"""

    def __init__(
        self,
        api_client: LinkedInAPIClient,
        slack_notifier: Optional = None,
        progress_callback: Optional[Callable] = None
    ):
        """
        Initialize workflow orchestrator

        Args:
            api_client: LinkedIn API client
            slack_notifier: Optional Slack notifier (deprecated, unused)
            progress_callback: Optional callback for progress updates
        """
        self.api_client = api_client
        self.progress_callback = progress_callback

        # Data collections
        self.posts: List[LinkedInPost] = []
        self.people: List[Person] = []
        self.stats = {
            "companies_processed": 0,
            "keywords_searched": 0,
            "posts_found": 0,
            "engagements_found": 0,
            "people_enriched": 0,
        }

    def _progress_update(self, stage: str, current: int, total: int):
        """Update progress"""
        if self.progress_callback:
            self.progress_callback(stage, current, total)

    def run_enrichment(self, request: EnrichmentRequest) -> EnrichmentResponse:
        """
        Run the complete enrichment workflow

        Args:
            request: Enrichment request with URLs and keywords

        Returns:
            Enrichment response with results
        """
        logger.info("Starting enrichment workflow")

        try:
            # Notify start
            company_count = len(request.company_urls) if request.company_urls else 0
            keyword_count = len(request.keywords) if request.keywords else 0
            logger.info(f"Processing {company_count} companies and {keyword_count} keywords")

            # Step 1: Company-based scraping
            if request.company_urls:
                self._run_company_scraping(request.company_urls, request.start_date, request.end_date)

            # Step 2: Keyword-based scraping
            if request.keywords:
                self._run_keyword_scraping(request.keywords, request.start_date, request.end_date)

            # Step 3: Extract engagements and enrich profiles
            self._extract_engagements_and_enrich()

            # Step 4: Deduplication
            self.people = Deduplicator.deduplicate_people(self.people)
            self.stats["people_enriched"] = len(self.people)

            # Step 5: Notify completion
            response = EnrichmentResponse(
                status="completed",
                total_posts_found=self.stats["posts_found"],
                total_engagements=self.stats["engagements_found"],
                unique_people_enriched=self.stats["people_enriched"],
            )

            logger.info(f"Enrichment completed: {response}")
            return response

        except Exception as e:
            logger.error(f"Enrichment workflow failed: {e}")

            return EnrichmentResponse(
                status="failed",
                error_message=str(e)
            )

    def _run_company_scraping(
        self,
        company_urls: List[str],
        start_date: datetime,
        end_date: datetime
    ):
        """Run company-based scraping"""
        logger.info(f"Starting company-based scraping for {len(company_urls)} companies")

        for idx, company_url in enumerate(company_urls):
            try:
                self._progress_update("Company Scraping", idx + 1, len(company_urls))

                # Get company profile
                company_profile = self.api_client.get_company_profile(company_url)
                if not company_profile:
                    logger.warning(f"Could not fetch company profile for {company_url}")
                    continue

                # Get company posts
                company_posts = self.api_client.get_company_posts(
                    company_url, start_date, end_date
                )

                if company_posts:
                    for post in company_posts:
                        self.posts.append(LinkedInPost(
                            post_id=post.get("id", ""),
                            author_name=company_profile.get("name", ""),
                            author_linkedin_url=company_url,
                            post_text=post.get("text", ""),
                            post_url=post.get("url", ""),
                            posted_date=datetime.fromisoformat(post.get("posted_date", datetime.now().isoformat())),
                            like_count=post.get("like_count", 0),
                            comment_count=post.get("comment_count", 0),
                            share_count=post.get("share_count", 0),
                            source=SourceType.COMPANY_POST,
                            source_detail=company_url,
                        ))

                    logger.info(f"Found {len(company_posts)} posts from {company_url}")
                    self.stats["posts_found"] += len(company_posts)

                # Get company employees
                employees = self.api_client.get_company_employees(company_url)

                if employees:
                    logger.info(f"Found {len(employees)} employees at {company_url}")

                    # Get posts from employees
                    for emp in employees:
                        emp_posts = self.api_client.get_company_posts(
                            emp.get("linkedin_url", ""), start_date, end_date
                        )

                        if emp_posts:
                            for post in emp_posts:
                                self.posts.append(LinkedInPost(
                                    post_id=post.get("id", ""),
                                    author_name=emp.get("name", ""),
                                    author_linkedin_url=emp.get("linkedin_url", ""),
                                    post_text=post.get("text", ""),
                                    post_url=post.get("url", ""),
                                    posted_date=datetime.fromisoformat(post.get("posted_date", datetime.now().isoformat())),
                                    like_count=post.get("like_count", 0),
                                    comment_count=post.get("comment_count", 0),
                                    share_count=post.get("share_count", 0),
                                    source=SourceType.EMPLOYEE_POST,
                                    source_detail=company_url,
                                ))

                            self.stats["posts_found"] += len(emp_posts)

                self.stats["companies_processed"] += 1

            except Exception as e:
                logger.error(f"Error processing company {company_url}: {e}")
                continue

    def _run_keyword_scraping(
        self,
        keywords: List[str],
        start_date: datetime,
        end_date: datetime
    ):
        """Run keyword-based scraping"""
        logger.info(f"Starting keyword-based scraping for {len(keywords)} keywords")

        for idx, keyword in enumerate(keywords):
            try:
                self._progress_update("Keyword Scraping", idx + 1, len(keywords))

                # Search for posts with keyword
                posts = self.api_client.search_posts(
                    [keyword], start_date, end_date, limit=100
                )

                if posts:
                    for post in posts:
                        self.posts.append(LinkedInPost(
                            post_id=post.get("id", ""),
                            author_name=post.get("author_name", ""),
                            author_linkedin_url=post.get("author_url", ""),
                            post_text=post.get("text", ""),
                            post_url=post.get("url", ""),
                            posted_date=datetime.fromisoformat(post.get("posted_date", datetime.now().isoformat())),
                            like_count=post.get("like_count", 0),
                            comment_count=post.get("comment_count", 0),
                            share_count=post.get("share_count", 0),
                            source=SourceType.KEYWORD_SEARCH,
                            source_detail=keyword,
                        ))

                    logger.info(f"Found {len(posts)} posts for keyword '{keyword}'")
                    self.stats["posts_found"] += len(posts)

                self.stats["keywords_searched"] += 1

            except Exception as e:
                logger.error(f"Error searching keyword '{keyword}': {e}")
                continue

    def _extract_engagements_and_enrich(self):
        """Extract engagements from all posts and enrich profiles"""
        logger.info(f"Extracting engagements from {len(self.posts)} posts")

        for idx, post in enumerate(self.posts):
            self._progress_update("Engagement Extraction", idx + 1, len(self.posts))

            try:
                # Get engagement/comments for this post
                engagement_data = self.api_client.get_post_engagement(post.post_url or post.post_id)

                if engagement_data:
                    # Extract people who engaged (comments, likes, etc.)
                    commenters = engagement_data.get("commenters", [])
                    likers = engagement_data.get("likers", [])

                    # Process commenters
                    for person_data in commenters:
                        person = self._create_person_from_data(
                            person_data,
                            EngagementType.COMMENT,
                            post.source,
                            post.source_detail,
                        )
                        self.people.append(person)
                        self.stats["engagements_found"] += 1

                    # Process likers
                    for person_data in likers:
                        person = self._create_person_from_data(
                            person_data,
                            EngagementType.LIKE,
                            post.source,
                            post.source_detail,
                        )
                        self.people.append(person)
                        self.stats["engagements_found"] += 1

            except Exception as e:
                logger.error(f"Error extracting engagement from post {post.post_id}: {e}")
                continue

    def _create_person_from_data(
        self,
        person_data: dict,
        engagement_type: EngagementType,
        source_type: SourceType,
        source_detail: Optional[str],
    ) -> Person:
        """Create Person object from raw engagement data"""
        # Fetch full profile if needed
        profile_url = person_data.get("linkedin_url", "")

        full_profile = None
        if profile_url:
            full_profile = self.api_client.get_person_profile(profile_url)

        return Person(
            linkedin_profile_url=profile_url,
            full_name=person_data.get("name", "Unknown"),
            job_title=full_profile.get("job_title") if full_profile else None,
            seniority_level=full_profile.get("seniority_level") if full_profile else None,
            company_name=full_profile.get("company_name") if full_profile else None,
            company_linkedin_url=full_profile.get("company_linkedin_url") if full_profile else None,
            company_domain=full_profile.get("company_domain") if full_profile else None,
            industry=full_profile.get("industry") if full_profile else None,
            company_size=full_profile.get("company_size") if full_profile else None,
            engagement_type=engagement_type,
            engagement_types=[engagement_type],
            source_type=[source_type],
            source_detail=[source_detail] if source_detail else [],
        )

    def get_stats(self) -> dict:
        """Get workflow statistics"""
        return self.stats

    def export_results(
        self,
        output_format: str = "csv",
        output_path: Optional[str] = None,
        filters=None
    ):
        """Export enriched data"""
        logger.info(f"Exporting {len(self.people)} people in {output_format} format")

        from pathlib import Path
        if output_path:
            output_path = Path(output_path)

        return DataExporter.export(
            self.people,
            output_format=output_format,
            output_path=output_path,
            filters=filters
        )
