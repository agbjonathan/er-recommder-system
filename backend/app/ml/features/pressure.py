def compute_pressure_score(snapshot):
    """
    Compute hospital pressure level from one ER snapshot.
    This is NOT stored in DB — it's a derived ML feature.
    """

    # Safety guards
    total = max(snapshot.patients_total, 1)
    stretchers = max(snapshot.functional_stretchers, 1)

    stretcher_ratio = snapshot.occupied_stretchers / stretchers
    waiting_ratio = snapshot.patients_waiting_mc / total
    long_stay_ratio = snapshot.patients_over_24h / total

    # Weighted formula (can evolve later)
    pressure = (
        0.5 * stretcher_ratio +
        0.3 * waiting_ratio +
        0.2 * long_stay_ratio
    )

    return round(pressure, 3)
