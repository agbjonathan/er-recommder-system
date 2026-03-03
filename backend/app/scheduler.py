from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs import ingestion, forecasting, evaluate
from app.core.logging import logger

def start() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        ingestion.run,
        trigger="cron",
        minute="*",
        id="ingestion",
        replace_existing=True,
    )
    scheduler.add_job(
        forecasting.run,
        trigger="cron",
        minute="5",
        id="forecasting",
        replace_existing=True,
    )
    scheduler.add_job(
        evaluate.run,
        trigger="cron",
        minute="10",
        id="evaluation",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — running jobs locally")
    return scheduler
