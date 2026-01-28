"""
CSV data loader for importing hospital and wait time data.
"""
import csv
from typing import List, Dict, Any
from pathlib import Path
from app.core.logging import logger


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing row data
    """
    data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(dict(row))
        
        logger.info(f"Successfully loaded {len(data)} rows from {file_path}")
        return data
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV file {file_path}: {str(e)}")
        raise


def validate_hospital_data(data: List[Dict[str, Any]]) -> bool:
    """
    Validate hospital data structure.
    
    Args:
        data: List of hospital data dictionaries
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    required_fields = ['name', 'latitude', 'longitude']
    
    for idx, row in enumerate(data):
        for field in required_fields:
            if field not in row or not row[field]:
                logger.error(f"Row {idx} missing required field: {field}")
                return False
    
    logger.info(f"Validated {len(data)} hospital records")
    return True
