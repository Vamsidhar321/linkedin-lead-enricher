"""Data export functionality"""
import json, logging
from pathlib import Path
from typing import List, Optional
import pandas as pd
from .data_models import Person, FilterOptions
from .config import config

logger = logging.getLogger(__name__)

class DataExporter:
    """Handles exporting enriched data"""
    
    @staticmethod
    def to_dataframe(people: List[Person]) -> pd.DataFrame:
        data = []
        for person in people:
            row = {
                "Full Name": person.full_name,
                "Job Title": person.job_title or "",
                "Company Name": person.company_name or "",
                "LinkedIn Profile Link": person.linkedin_profile_url,
                "Industry": person.industry or "",
            }
            data.append(row)
        return pd.DataFrame(data)
    
    @staticmethod
    def export_csv(people: List[Person], output_path: Path) -> Path:
        df = DataExporter.to_dataframe(people)
        df.to_csv(output_path, index=False)
        logger.info(f"Exported to CSV: {output_path}")
        return output_path
    
    @staticmethod
    def export(people: List[Person], output_format: str = "csv", output_path: Optional[Path] = None) -> Path:
        if not output_path:
            output_path = config.DOWNLOAD_FOLDER / f"enriched_data.{output_format}"
        if output_format == "csv":
            return DataExporter.export_csv(people, output_path)
        return output_path
