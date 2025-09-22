# ruff: noqa: SIM117
import datetime
from typing import Any

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo.database import Database

from gw2tp.db_schema import COLLECTIONS
from gw2tp.db_schema import cleanup_old_records
from gw2tp.helper import host_url
from gw2tp.helper import is_running_on_railway

from .db import db


api_base = host_url()


async def _fetch_single_request(
    db: Database,
    collection_name: str,
    data_keys: list[str],
) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_base}{collection_name}") as response:
            data: dict[str, Any] = await response.json()
            if data.get("detail", "") == "Not Found":
                print(f"API command '{collection_name}' not found.")
                return
            doc = {
                key: value
                for key, value in data.items()
                if any(key.startswith(data_key) for data_key in data_keys)
            }
            doc["timestamp"] = datetime.datetime.now(
                tz=datetime.timezone(datetime.timedelta(hours=2), "UTC")
            ).isoformat()
            db[collection_name].insert_one(doc)


async def fetch_api_data() -> None:
    print("Fetching data...")
    fetch_keys = ["crafting_cost", "sell"]
    for collection_name in COLLECTIONS:
        await _fetch_single_request(
            db,
            collection_name,
            fetch_keys,
        )
    print("Fetching done...")


def start_scheduler() -> None:
    scheduler = AsyncIOScheduler()

    async def fetch_job() -> None:
        await fetch_api_data()

    def cleanup_job() -> None:
        cleanup_old_records(db, days=14)
        print("Database cleanup completed...")

    if is_running_on_railway():
        scheduler.add_job(
            fetch_job,
            "interval",
            minutes=15,
            max_instances=1,
        )
        scheduler.add_job(
            cleanup_job,
            "cron",
            hour=0,  # daily at midnight UTC
            minute=0,
            max_instances=1,
        )
    else:
        scheduler.add_job(
            fetch_job,
            "interval",
            seconds=10,
            max_instances=1,
        )
        scheduler.add_job(
            cleanup_job,
            "interval",
            hours=1,
            max_instances=1,
        )
    scheduler.start()
