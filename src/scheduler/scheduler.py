import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger


scheduler = AsyncIOScheduler()


async def delayed_repeat_task(
        task: Callable,
        repeat_after_minutes: Optional[int | float] = None,
        forever: bool = True
):
    logging.info("Executing %s started", task.__name__)
    await task()
    logging.info("Executing %s finished", task.__name__)
    if repeat_after_minutes:
        while True:
            next_run_time = datetime.now() + timedelta(minutes=repeat_after_minutes)
            scheduler.add_job(func=delayed_repeat_task,
                              args=[task, repeat_after_minutes, forever],
                              trigger=DateTrigger(run_date=next_run_time))
            if not forever:
                break


async def daily_task(task: Callable, *args, time_period: str):
    if isinstance(time_period, str):
        try:
            hour, minute = map(int, time_period.split(":"))
            scheduler.add_job(task, args=args, trigger=CronTrigger(hour=hour, minute=minute))
        except Exception as e:
            logging.warning(e)
