# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LinkedIn Lead Enricher** is a Flask web application that discovers and enriches LinkedIn leads using company URLs and keyword searches. It aggregates engagement data from LinkedIn posts and enriches user profiles with company information, job titles, and seniority levels.

## Setup & Running

1. **Initial Setup**: Run `./setup.sh` to create a Python virtual environment and install dependencies
2. **Environment Configuration**:
   - Copy `.env.template` to `.env`
   - Add `RAPIDAPI_KEY` and `RAPIDAPI_HOST` (required for LinkedIn API access)
   - Optional: `SLACK_WEBHOOK_URL` for Slack notifications
3. **Start Development Server**: `python app.py` (runs on http://localhost:5000 with Flask debug mode enabled)

## Architecture

### Core Application Flow
The app implements a two-stage enrichment workflow orchestrated by `WorkflowOrchestrator`:
1. **Company-based scraping**: Fetches posts from specified company LinkedIn pages
2. **Keyword-based scraping**: Searches posts matching keywords
3. **Engagement extraction**: Identifies users who engaged with posts (likes, comments, shares)
4. **Profile enrichment**: Augments user data with company info and title from LinkedIn profiles
5. **Deduplication**: Removes duplicate person records
6. **Export**: Outputs enriched data as CSV/Excel with optional filtering

### Key Components

**Backend Modules** (`backend/`):
- **config.py**: Configuration management (API keys, Flask settings, file paths, logging). Supports development/production/testing environments.
- **data_models.py**: Pydantic models defining data structures (Person, LinkedInPost, Company, EnrichmentRequest/Response, FilterOptions)
- **linkedin_api.py**: `LinkedInAPIClient` wrapper around RapidAPI endpoints with built-in rate limiting (0.5s delay)
- **workflow_orchestrator.py**: `WorkflowOrchestrator` orchestrates the full enrichment pipeline with progress tracking
- **deduplication.py**: Deduplicator for merging duplicate person records
- **data_exporter.py**: DataExporter for CSV/Excel export with filtering
- **slack_notifier.py**: Optional Slack notifications (currently unused in code)

**Frontend** (`static/app.js`, `templates/index.html`):
- Single-page application communicating with Flask endpoints
- Real-time status polling via `/api/status`
- Data filtering and export interface

**Flask Endpoints** (`app.py`):
- `POST /api/start-enrichment`: Initiates enrichment workflow (runs in background thread)
- `GET /api/status`: Returns current workflow status and statistics
- `POST /api/export`: Exports enriched data with optional filters
- `GET /api/download/<filename>`: Downloads exported file
- `GET /api/stats`: Returns workflow statistics
- `POST /api/reset`: Resets workflow state

### Data Models
- **Person**: Enriched user profile with LinkedIn URL, name, job title, company, engagement history
- **LinkedInPost**: Post metadata including author, engagement counts, dates, and source
- **Company**: Company profile with LinkedIn URL, industry, size, website, description
- **EngagementType**: Enum of like/comment/share
- **SourceType**: Enum of company_post/employee_post/keyword_search

## Key Configuration

Defined in `backend/config.py`:
- `MAX_WORKERS`: Thread pool size (default: 5)
- `REQUEST_TIMEOUT`: API request timeout in seconds (default: 30)
- `RATE_LIMIT_DELAY`: Delay between API requests (default: 1s)
- File paths: `UPLOAD_FOLDER`, `DOWNLOAD_FOLDER`, `TEMP_FOLDER`
- Logging level via `LOG_LEVEL` env var

## Important Development Notes

- **Threading**: The enrichment workflow runs in a background daemon thread to avoid blocking API responses
- **Global State**: `app.py` maintains global `current_workflow` and `workflow_results` for status tracking. This is sufficient for single-user development but would need refactoring for concurrent users in production.
- **API Rate Limiting**: Built into `LinkedInAPIClient` with 0.5s minimum delay between requests
- **Error Handling**: Workflow errors are caught and returned in the response; check server logs for detailed error traces
- **Deduplication**: Merges duplicate people records by matching LinkedIn profile URLs
- **Filtering**: `FilterOptions` allows filtering by job_titles, seniority_levels, company_sizes, engagement_types, source_types, industries before export
