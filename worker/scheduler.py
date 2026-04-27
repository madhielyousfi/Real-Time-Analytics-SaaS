import logging
import time
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import get_settings
from .jobs.recompute_metrics import recompute_all_metrics
from .jobs.cleanup_events import cleanup_events, cleanup_sessions

settings = get_settings()
logger = logging.getLogger(__name__)


def run_scheduler():
    scheduler = BlockingScheduler()
    
    scheduler.add_job(
        recompute_all_metrics,
        trigger=IntervalTrigger(hours=1),
        id="recompute_metrics",
        name="Recompute hourly metrics",
        replace_existing=True
    )
    
    scheduler.add_job(
        lambda: cleanup_events(days_old=90),
        trigger=IntervalTrigger(days=1),
        id="cleanup_events",
        name="Cleanup old events",
        replace_existing=True
    )
    
    scheduler.add_job(
        lambda: cleanup_sessions(days_old=90),
        trigger=IntervalTrigger(days=1),
        id="cleanup_sessions",
        name="Cleanup old sessions",
        replace_existing=True
    )
    
    logger.info("Starting scheduler...")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()


if __name__ == "__main__":
    run_scheduler()