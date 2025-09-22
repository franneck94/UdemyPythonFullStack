import datetime
from typing import Any

from pymongo.database import Database


# Collection names for MongoDB
COLLECTIONS = [
    "scholar_rune",
    "guardian_rune",
    "dragonhunter_rune",
    "relic_of_fireworks",
    "relic_of_thief",
    "relic_of_aristocracy",
]


def cleanup_old_records(
    db: Database,
    days: int = 14,
) -> None:
    cutoff_date = datetime.datetime.now(
        tz=datetime.timezone.utc
    ) - datetime.timedelta(days=days)
    for collection_name in COLLECTIONS:
        collection = db[collection_name]
        collection.delete_many({"timestamp": {"$lt": cutoff_date.isoformat()}})


def get_db_data(
    db: Database,
    collection_name: str,
    start_datetime: datetime.datetime | None = None,
    end_datetime: datetime.datetime | None = None,
) -> list[dict]:
    collection = db[collection_name]
    query = {}
    if start_datetime:
        query["timestamp"] = {"$gte": start_datetime.isoformat()}
    if end_datetime:
        if "timestamp" in query:
            query["timestamp"]["$lte"] = end_datetime.isoformat()
        else:
            query["timestamp"] = {"$lte": end_datetime.isoformat()}
    results: list[dict[str, Any]] = list(collection.find(query))
    for doc in results:
        doc.pop("_id", None)
    return results
