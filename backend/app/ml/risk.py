
def pressure_to_risk(pressure: float) -> str:
    """
    Convert a predicted pressure score into a human-readable risk level.

    Args:
        pressure: Predicted pressure score on a normalized scale (typically 0.0–1.0).
            If ``None``, the risk level is reported as ``"UNKNOWN"``.

    Returns:
        str: One of the following risk levels:

            * ``"LOW"`` for pressure values strictly less than ``0.4``.
            * ``"MEDIUM"`` for pressure values greater than or equal to ``0.4``
              and strictly less than ``0.7``.
            * ``"HIGH"`` for pressure values greater than or equal to ``0.7``.
            * ``"UNKNOWN"`` if ``pressure`` is ``None``.
    """

    if pressure is None:
        return "UNKNOWN"

    if pressure < 0.4:
        return "LOW"
    elif pressure < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"
