
def pressure_to_risk(pressure: float) -> str:
    """
    Convert a predicted pressure score into a human-readable risk level.
    
    """

    if pressure is None:
        return "UNKNOWN"

    if pressure < 0.4:
        return "LOW"
    elif pressure < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"
