"""
Flask web application for LinkedIn enricher
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from threading import Thread

from backend.config import config
from backend.linkedin_api import get_api_client
from backend.data_models import EnrichmentRequest, FilterOptions, EnrichmentResponse
from backend.workflow_orchestrator import WorkflowOrchestrator

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Global state for workflow
current_workflow = None
workflow_results = None


@app.route("/", methods=["GET"])
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/api/start-enrichment", methods=["POST"])
def start_enrichment():
    """Start the enrichment workflow"""
    global current_workflow, workflow_results

    try:
        data = request.get_json()

        # Parse request data
        company_urls = data.get("company_urls", [])
        if isinstance(company_urls, str):
            company_urls = [url.strip() for url in company_urls.split("\n") if url.strip()]

        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [kw.strip() for kw in keywords.split("\n") if kw.strip()]

        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date"))

        # Validate input
        if not company_urls and not keywords:
            return jsonify({"error": "Please provide company URLs or keywords"}), 400

        # Create enrichment request
        enrich_request = EnrichmentRequest(
            company_urls=company_urls if company_urls else None,
            keywords=keywords if keywords else None,
            start_date=start_date,
            end_date=end_date,
            slack_webhook_url=None,
            enable_notifications=False,
        )

        # Create API client and workflow
        api_client = get_api_client()

        if not api_client.is_configured():
            return jsonify({
                "error": "API not configured. Please set RAPIDAPI_KEY and RAPIDAPI_HOST in .env"
            }), 500

        # Create workflow in a background thread
        def run_workflow():
            global current_workflow, workflow_results

            try:
                current_workflow = WorkflowOrchestrator(api_client, slack_notifier=None)
                workflow_results = current_workflow.run_enrichment(enrich_request)
                logger.info(f"Workflow completed: {workflow_results.status}")
            except Exception as e:
                logger.error(f"Workflow error: {e}", exc_info=True)
                workflow_results = EnrichmentResponse(
                    status="failed",
                    error_message=str(e)
                )

        thread = Thread(target=run_workflow, daemon=True)
        thread.start()

        return jsonify({
            "status": "started",
            "message": "Enrichment workflow started",
            "company_urls": len(company_urls) if company_urls else 0,
            "keywords": len(keywords) if keywords else 0,
        })

    except Exception as e:
        logger.error(f"Error starting enrichment: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current workflow status"""
    global current_workflow, workflow_results

    if not current_workflow and not workflow_results:
        return jsonify({"status": "idle"})

    if workflow_results:
        return jsonify({
            "status": workflow_results.status,
            "total_posts": workflow_results.total_posts_found or 0,
            "total_engagements": workflow_results.total_engagements or 0,
            "unique_people": workflow_results.unique_people_enriched or 0,
            "error": workflow_results.error_message,
        })

    if current_workflow:
        stats = current_workflow.get_stats()
        return jsonify({
            "status": "processing",
            "stats": stats,
        })

    return jsonify({"status": "unknown"})


@app.route("/api/export", methods=["POST"])
def export_data():
    """Export enriched data"""
    global workflow_results, current_workflow

    try:
        data = request.get_json()
        export_format = data.get("format", "csv")

        # Apply filters if provided
        filters = None
        if data.get("filters"):
            filter_data = data.get("filters")
            filters = FilterOptions(
                job_titles=filter_data.get("job_titles"),
                seniority_levels=filter_data.get("seniority_levels"),
                company_sizes=filter_data.get("company_sizes"),
                engagement_types=filter_data.get("engagement_types"),
                source_types=filter_data.get("source_types"),
                industries=filter_data.get("industries"),
            )

        if not current_workflow or not current_workflow.people:
            return jsonify({"error": "No data available to export"}), 400

        # Export data
        output_path = current_workflow.export_results(
            output_format=export_format,
            filters=filters
        )

        return jsonify({
            "status": "success",
            "download_url": f"/api/download/{output_path.name}",
            "filename": output_path.name,
        })

    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<filename>", methods=["GET"])
def download_file(filename):
    """Download exported file"""
    try:
        file_path = config.DOWNLOAD_FOLDER / filename

        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get workflow statistics"""
    global current_workflow

    if not current_workflow:
        return jsonify({"error": "No active workflow"}), 400

    stats = current_workflow.get_stats()
    return jsonify(stats)


@app.route("/api/reset", methods=["POST"])
def reset_workflow():
    """Reset the workflow"""
    global current_workflow, workflow_results

    current_workflow = None
    workflow_results = None

    return jsonify({"status": "reset"})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info("Starting LinkedIn Enricher Flask app...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=config.FLASK_DEBUG,
        threaded=True
    )
