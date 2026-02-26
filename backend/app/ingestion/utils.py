def to_int(value):
    """Convert value to int or return None if invalid."""
    try:
        if value is None:
            return None
        value = str(value).strip().lower()
        if "pas d'information" in value:
            return None
        return int(float(value))
    except Exception:
        return None


def to_float(value):
    """Convert value to float or return None if invalid."""
    try:
        if value is None:
            return None
        value = str(value).strip().lower()
        if "pas d'information" in value:
            return None
        return float(value)
    except Exception:
        return None
