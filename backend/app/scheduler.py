from apscheduler.schedulers.background import BackgroundScheduler
from app.ingestion.main import run_ingestion
from app.ml.evaluate_forecasts import evaluate_forecasts
from app.ml.run_forecasting import run_forecasting
from datetime import datetime, timezone, timedelta

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        run_ingestion,
        "interval",
        hours=1,
        next_run_time=datetime.now(timezone.utc),
        id="run_ingestion_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800, 
    )

    scheduler.add_job(
        run_forecasting,
        "interval",
        hours=1,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=5),
        id="run_forecasting_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800, 
    )

    scheduler.add_job(
        evaluate_forecasts,
        "interval",
        hours=1,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=10),
        id="evaluate_forecasts_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=1800,
    )

    scheduler.start()
