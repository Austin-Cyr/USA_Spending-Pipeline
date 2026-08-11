# python -m src.ingestion.flow
from datetime import date, timedelta

from prefect import flow, task, get_run_logger
from prefect.cache_policies import NO_CACHE
from src.ingestion.client import fetch_awards_page
from src.ingestion.config import build_payload
from src.ingestion.db import get_engine, create_watermark_table
from src.ingestion.loader import land_raw_page
from src.ingestion.watermark import get_last_watermark, record_watermark

@task(retries=2, retry_delay_seconds=10, cache_policy=NO_CACHE)
def fetch_page_task(start_date: str, end_date: str, page: int) -> dict:
    payload = build_payload(start_date, end_date, page=page, limit=100)
    return {"data": fetch_awards_page(payload), "payload": payload}

@task(cache_policy=NO_CACHE)
def land_page_task(engine, data: dict, page: int, filters: dict) -> None:
    land_raw_page(engine, data, page_number=page, request_filters=filters)

@flow(name="usaspending-incremental-pull")
def usaspending_ingestion_flow():
    logger = get_run_logger()

    engine = get_engine("local")
    create_watermark_table(engine)

    last_watermark = get_last_watermark(engine)
    start_date = (last_watermark + timedelta(days=1)) if last_watermark else date(2024, 10, 1)
    end_date = date.today()

    if start_date > end_date:
        logger.info("No new date range to pull. Already up to date.")
        return

    logger.info(f"Pulling awards from {start_date} to {end_date}")

    page = 1
    total_results = 0
    while True:
        result = fetch_page_task(str(start_date), str(end_date), page)
        data = result["data"]

        land_page_task(engine, data, page, result["payload"]["filters"])
        total_results += len(data["results"])
        logger.info(f"Landed page {page} ({len(data['results'])} results)")

        if not data["page_metadata"]["hasNext"]:
            break
        page += 1

    record_watermark(engine, end_date)
    logger.info(f"Run complete. {total_results} total results landed. Watermark updated to {end_date}")


if __name__ == "__main__":
    usaspending_ingestion_flow()