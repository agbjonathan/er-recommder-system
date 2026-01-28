from apscheduler.schedulers.background import BackgroundScheduler
from app.ingestion.main import run_ingestion
from datetime import datetime

scheduler = BackgroundScheduler()
scheduler.add_job(run_ingestion, "interval", hours=0.05, next_run_time=datetime.now())

def start_scheduler():
    scheduler.start()
