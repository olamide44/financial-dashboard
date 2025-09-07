# app/jobs/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.jobs.tasks import nightly_backfill_prices, intraday_refresh_prices

# Create a scheduler scoped to the configured timezone
scheduler = AsyncIOScheduler(timezone=settings.jobs_timezone)

def start_scheduler() -> None:
    """
    Configure and start the APScheduler instance based on environment settings.
    """
    # Parse the HH:MM string from settings.backfill_at
    try:
        backfill_hour, backfill_minute = map(int, settings.backfill_at.split(":"))
    except ValueError:
        raise ValueError(f"Invalid BACKFILL_AT value: {settings.backfill_at}")

    # Schedule the nightly backfill job
    scheduler.add_job(
        nightly_backfill_prices,
        CronTrigger(hour=backfill_hour, minute=backfill_minute),
        id="nightly_backfill_prices",
        name="Nightly Backfill Prices",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,  # 1 hour grace
    )

    # Schedule the intraday refresh job if enabled
    if settings.intraday_enable:
        scheduler.add_job(
            intraday_refresh_prices,
            IntervalTrigger(seconds=settings.intraday_interval_sec),
            id="intraday_refresh_prices",
            name="Intraday Refresh Prices",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,  # 1 minute grace
        )

    scheduler.start()

def shutdown_scheduler() -> None:
    """
    Shut down the scheduler gracefully.
    """
    scheduler.shutdown(wait=False)
