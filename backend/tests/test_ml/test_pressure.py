import pytest
from app.ml.risk import pressure_to_risk


# ── Boundary values ────────────────────────────────────────────────────────────

def test_exactly_at_low_medium_boundary():
    assert pressure_to_risk(0.4) == "MEDIUM"


def test_exactly_at_medium_high_boundary():
    assert pressure_to_risk(0.7) == "HIGH"


# ── LOW range ─────────────────────────────────────────────────────────────────

def test_low_min():
    assert pressure_to_risk(0.0) == "LOW"


def test_low_mid():
    assert pressure_to_risk(0.2) == "LOW"


def test_low_just_below_boundary():
    assert pressure_to_risk(0.399) == "LOW"


# ── MEDIUM range ──────────────────────────────────────────────────────────────

def test_medium_just_above_low():
    assert pressure_to_risk(0.401) == "MEDIUM"


def test_medium_mid():
    assert pressure_to_risk(0.55) == "MEDIUM"


def test_medium_just_below_high():
    assert pressure_to_risk(0.699) == "MEDIUM"


# ── HIGH range ────────────────────────────────────────────────────────────────

def test_high_just_above_medium():
    assert pressure_to_risk(0.701) == "HIGH"


def test_high_mid():
    assert pressure_to_risk(0.85) == "HIGH"


def test_high_above_1():
    assert pressure_to_risk(1.2) == "HIGH"


def test_high_extreme():
    assert pressure_to_risk(2.0) == "HIGH"


# ── Return type ───────────────────────────────────────────────────────────────

def test_always_returns_string():
    for v in [0.0, 0.4, 0.7, 1.0]:
        result = pressure_to_risk(v)
        assert isinstance(result, str)


def test_always_returns_valid_level():
    valid = {"LOW", "MEDIUM", "HIGH"}
    for v in [0.0, 0.3, 0.4, 0.5, 0.7, 0.9, 1.5]:
        assert pressure_to_risk(v) in valid