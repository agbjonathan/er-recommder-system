"""
Mathematical utility functions.
"""
import math
from typing import List, Optional


def calculate_mean(values: List[float]) -> float:
    """
    Calculate the arithmetic mean of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Mean value
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_median(values: List[float]) -> float:
    """
    Calculate the median of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Median value
    """
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    if n % 2 == 0:
        return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    else:
        return sorted_values[n // 2]


def calculate_std_dev(values: List[float]) -> float:
    """
    Calculate the standard deviation of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        float: Standard deviation
    """
    if len(values) < 2:
        return 0.0
    
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate the specified percentile of a list of values.
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        float: Percentile value
    """
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * (percentile / 100)
    
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(math.floor(index))]
        upper = sorted_values[int(math.ceil(index))]
        return lower + (upper - lower) * (index - math.floor(index))


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))


def normalize(value: float, min_value: float, max_value: float) -> float:
    """
    Normalize a value to range [0, 1].
    
    Args:
        value: Value to normalize
        min_value: Minimum value in range
        max_value: Maximum value in range
        
    Returns:
        float: Normalized value between 0 and 1
    """
    if max_value == min_value:
        return 0.0
    return (value - min_value) / (max_value - min_value)


def round_to_nearest(value: float, nearest: float = 1.0) -> float:
    """
    Round a value to the nearest specified increment.
    
    Args:
        value: Value to round
        nearest: Increment to round to
        
    Returns:
        float: Rounded value
    """
    return round(value / nearest) * nearest


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value to return if division by zero
        
    Returns:
        float: Result of division or default value
    """
    if denominator == 0:
        return default
    return numerator / denominator
