# app/jobs/scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from core.config import settings
from jobs.tasks import nightly_backfill_prices, intraday_refresh_prices

# REPLACE the global construction with a lazy singleton:
_scheduler: AsyncIOScheduler | None = None

def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    # construct after settings are loaded
    _scheduler = AsyncIOScheduler(timezone=settings.jobs_timezone)

    # parse "HH:MM"
    try:
        hh, mm = (int(x) for x in settings.backfill_at.split(":"))
    except Exception as e:
        raise ValueError(f"Invalid BACKFILL_AT='{settings.backfill_at}'") from e

    _scheduler.add_job(
        nightly_backfill_prices,
        CronTrigger(hour=hh, minute=mm, timezone=settings.jobs_timezone),
        id="nightly_backfill_prices",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )

    if settings.intraday_enable:
        _scheduler.add_job(
            intraday_refresh_prices,
            IntervalTrigger(seconds=max(5, settings.intraday_interval_sec), timezone=settings.jobs_timezone),
            id="intraday_refresh_prices",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=120,
        )

    _scheduler.start()

def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
