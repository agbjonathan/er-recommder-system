import pytest
from unittest.mock import patch, MagicMock


# ── run_forecasting ───────────────────────────────────────────────────────────

def test_forecasting_calls_train_for_all_horizons():
    fake_predictions = [{"hospital_id": 1, "predicted_pressure": 0.75, "risk_level": "HIGH"}]

    with patch("app.ml.run_forecasting.SessionLocal") as mock_session, \
         patch("app.ml.run_forecasting.train_and_forecast", return_value=fake_predictions) as mock_train, \
         patch("app.ml.run_forecasting.save_forecasts") as mock_save:

        from app.ml.run_forecasting import run_forecasting
        run_forecasting()

        # Should be called once per horizon (1, 2, 4)
        assert mock_train.call_count == 3
        assert mock_save.call_count == 3


def test_forecasting_skips_save_when_no_predictions():
    with patch("app.ml.run_forecasting.SessionLocal"), \
         patch("app.ml.run_forecasting.train_and_forecast", return_value=[]), \
         patch("app.ml.run_forecasting.save_forecasts") as mock_save:

        from app.ml.run_forecasting import run_forecasting
        run_forecasting()

        mock_save.assert_not_called()


def test_forecasting_closes_db_session():
    mock_db = MagicMock()

    with patch("app.ml.run_forecasting.SessionLocal", return_value=mock_db), \
         patch("app.ml.run_forecasting.train_and_forecast", return_value=[]):

        from app.ml.run_forecasting import run_forecasting
        run_forecasting()

        mock_db.close.assert_called_once()


# ── evaluate_forecasts ────────────────────────────────────────────────────────

def test_evaluate_returns_early_when_no_snapshots():
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.first.return_value = None

    with patch("app.ml.evaluate_forecasts.SessionLocal", return_value=mock_db):
        from app.ml.evaluate_forecasts import evaluate_forecasts
        evaluate_forecasts()

        # Should not query forecasts if no snapshots
        mock_db.commit.assert_not_called()


def test_evaluate_commits_when_forecasts_evaluated():
    mock_db = MagicMock()

    # latest snapshot exists
    mock_db.query.return_value.order_by.return_value.first.return_value = (
        MagicMock(),  # snapshot_time tuple
    )
    # no forecasts pending
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with patch("app.ml.evaluate_forecasts.SessionLocal", return_value=mock_db):
        from app.ml.evaluate_forecasts import evaluate_forecasts
        evaluate_forecasts()

        mock_db.commit.assert_called_once()


def test_evaluate_closes_db_on_exception():
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("DB error")

    with patch("app.ml.evaluate_forecasts.SessionLocal", return_value=mock_db):
        from app.ml.evaluate_forecasts import evaluate_forecasts
        evaluate_forecasts()  # should not raise

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()