"""Deduplication logic"""
import logging
from typing import List, Dict
from .data_models import Person

logger = logging.getLogger(__name__)

class Deduplicator:
    """Handles deduplication of person records"""
    
    @staticmethod
    def deduplicate_people(people: List[Person]) -> List[Person]:
        dedup_dict: Dict[str, Person] = {}
        for person in people:
            profile_url = person.linkedin_profile_url
            if profile_url not in dedup_dict:
                dedup_dict[profile_url] = person
            else:
                existing = dedup_dict[profile_url]
                merged = Deduplicator._merge_person_records(existing, person)
                dedup_dict[profile_url] = merged
        return list(dedup_dict.values())
    
    @staticmethod
    def _merge_person_records(existing: Person, new: Person) -> Person:
        merged = existing.model_copy()
        if new.job_title and not merged.job_title:
            merged.job_title = new.job_title
        merged.engagement_count += new.engagement_count
        return merged
