import pytest

pg_only = pytest.mark.skip(reason="date_trunc requires PostgreSQL")

def test_congestion_map_returns_geojson(client, sample_forecast):
    res = client.get("/api/dashboard/congestion/map?horizon=1")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert isinstance(data["features"], list)
    assert len(data["features"]) >= 1


def test_congestion_map_feature_has_required_fields(client, sample_forecast):
    res = client.get("/api/dashboard/congestion/map?horizon=1")
    feature = res.json()["features"][0]
    props = feature["properties"]
    assert "hospital_id" in props
    assert "name" in props
    assert "risk_level" in props
    assert "predicted_pressure" in props
    geom = feature["geometry"]
    assert geom["type"] == "Point"
    assert len(geom["coordinates"]) == 2


def test_congestion_map_coordinates_are_valid(client, sample_forecast):
    res = client.get("/api/dashboard/congestion/map?horizon=1")
    coords = res.json()["features"][0]["geometry"]["coordinates"]
    lon, lat = coords  # GeoJSON order: [lon, lat]
    assert -180 <= lon <= 180, f"Invalid longitude: {lon}"
    assert -90 <= lat <= 90, f"Invalid latitude: {lat}"


from unittest.mock import patch

MOCK_STATS = {
    "global_series": [{"label": "08:00", "predicted": 0.65, "observed": 0.63}],
    "risk_comparison": [{"risk": "HIGH", "predicted": 10, "observed": 8}],
    "hospital_stats": [{"hospital_id": 1, "name": "Test", "mean_predicted": 0.75, "mean_observed": 0.72, "risk_level": "HIGH"}],
    "generated_at": "2026-02-26T12:00:00+00:00",
}


def test_stats_invalid_horizon_rejected(client):
    res = client.get("/api/dashboard/stats?horizon_hours=0")
    assert res.status_code == 422

@pg_only
def test_stats_returns_expected_keys(client):
    with patch("app.api.dashboard.get_dashboard_stats", return_value=MOCK_STATS):
        res = client.get("/api/dashboard/stats?horizon_hours=1")
        assert res.status_code == 200
        data = res.json()
        assert all(k in data for k in ("global_series", "risk_comparison", "hospital_stats", "generated_at"))



@pytest.mark.skip(reason="date_trunc requires PostgreSQL, not SQLite")
def test_stats_with_unknown_hospital_returns_empty_series(client):
    res = client.get("/api/dashboard/stats?horizon_hours=1&hospital_id=999999")
    assert res.status_code == 200
    assert res.json()["global_series"] == []