from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs import ingestion, forecasting, evaluate
from app.core.logging import logger

def start() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        ingestion.run,
        trigger="cron",
        minute="0",
        id="ingestion",
        name="Data Ingestion Job",
        replace_existing=True,
    )
    scheduler.add_job(
        forecasting.run,
        trigger="cron",
        minute="5",
        id="forecasting",
        name="Forecasting Job",
        replace_existing=True,
    )
    scheduler.add_job(
        evaluate.run,
        trigger="cron",
        minute="10",
        id="evaluation",
        name="Evaluation Job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — running jobs locally")
    return scheduler
