from apscheduler.schedulers.background import BackgroundScheduler
from app.ingestion.main import run_ingestion
from datetime import datetime, timezone

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(
        run_ingestion,
        "interval",
        hours=1,
        next_run_time=datetime.now(timezone.utc),
        id="run_ingestion_job",
        replace_existing=True,
    )
    scheduler.start()
