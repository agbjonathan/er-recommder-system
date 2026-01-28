"""
Tests for data ingestion functionality.
"""
import pytest
from app.ingestion.csv_loader import validate_hospital_data
from app.ingestion.enrichment import enrich_hospital_data
from app.ingestion.scheduler import DataScheduler


class TestCSVLoader:
    """Test cases for CSV data loading."""
    
    def test_validate_hospital_data_valid(self):
        """Test validation of valid hospital data."""
        data = [
            {
                "name": "Hospital A",
                "latitude": "45.5",
                "longitude": "-73.5",
                "region": "Longueuil"
            },
            {
                "name": "Hospital B",
                "latitude": "45.6",
                "longitude": "-73.4",
                "region": "Longueuil"
            }
        ]
        assert validate_hospital_data(data) is True
    
    def test_validate_hospital_data_missing_field(self):
        """Test validation fails with missing required field."""
        data = [
            {
                "name": "Hospital A",
                "latitude": "45.5",
                # Missing longitude
                "region": "Longueuil"
            }
        ]
        assert validate_hospital_data(data) is False
    
    def test_validate_hospital_data_empty_field(self):
        """Test validation fails with empty required field."""
        data = [
            {
                "name": "",
                "latitude": "45.5",
                "longitude": "-73.5"
            }
        ]
        assert validate_hospital_data(data) is False


class TestEnrichment:
    """Test cases for data enrichment."""
    
    def test_enrich_hospital_data(self):
        """Test hospital data enrichment."""
        hospital = {
            "name": "Test Hospital",
            "latitude": 45.5,
            "longitude": -73.5
        }
        enriched = enrich_hospital_data(hospital)
        
        assert "location_string" in enriched
        assert enriched["location_string"] == "45.5, -73.5"
        assert enriched["data_enriched"] is True
    
    def test_enrich_preserves_original_data(self):
        """Test that enrichment preserves original fields."""
        hospital = {
            "name": "Test Hospital",
            "latitude": 45.5,
            "longitude": -73.5,
            "custom_field": "value"
        }
        enriched = enrich_hospital_data(hospital)
        
        assert enriched["name"] == "Test Hospital"
        assert enriched["custom_field"] == "value"


class TestScheduler:
    """Test cases for data scheduler."""
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        scheduler = DataScheduler()
        assert scheduler.tasks == []
    
    def test_schedule_task(self):
        """Test scheduling a task."""
        scheduler = DataScheduler()
        
        def dummy_task():
            pass
        
        scheduler.schedule_task(
            task_func=dummy_task,
            interval_minutes=60,
            task_name="test_task"
        )
        
        assert len(scheduler.tasks) == 1
        assert scheduler.tasks[0]["name"] == "test_task"
        assert scheduler.tasks[0]["interval"] == 60
