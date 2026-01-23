"""
Time utility functions for date/time operations.
"""
from datetime import datetime, timedelta
from typing import Optional
import pytz


def get_current_utc_time() -> datetime:
    """
    Get current UTC time.
    
    Returns:
        datetime: Current UTC datetime
    """
    return datetime.utcnow()


def get_current_time_in_timezone(timezone: str = "America/Montreal") -> datetime:
    """
    Get current time in specified timezone.
    
    Args:
        timezone: Timezone identifier (e.g., 'America/Montreal')
        
    Returns:
        datetime: Current datetime in specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_timestamp(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime from string.
    
    Args:
        date_string: Date string to parse
        format_str: Format string
        
    Returns:
        Optional[datetime]: Parsed datetime or None if parsing fails
    """
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """
    Add minutes to a datetime.
    
    Args:
        dt: Base datetime
        minutes: Number of minutes to add
        
    Returns:
        datetime: New datetime with minutes added
    """
    return dt + timedelta(minutes=minutes)


def get_time_difference_minutes(dt1: datetime, dt2: datetime) -> float:
    """
    Calculate difference between two datetimes in minutes.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        float: Difference in minutes (positive if dt1 > dt2)
    """
    diff = dt1 - dt2
    return diff.total_seconds() / 60


def is_business_hours(dt: datetime) -> bool:
    """
    Check if datetime falls within business hours (8 AM - 5 PM).
    
    Args:
        dt: Datetime to check
        
    Returns:
        bool: True if within business hours
    """
    return 8 <= dt.hour < 17


def is_weekend(dt: datetime) -> bool:
    """
    Check if datetime falls on a weekend.
    
    Args:
        dt: Datetime to check
        
    Returns:
        bool: True if Saturday or Sunday
    """
    return dt.weekday() >= 5
