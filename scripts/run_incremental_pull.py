from datetime import date, timedelta

from src.ingestion.client import fetch_awards_page
from src.ingestion.config import build_payload
from src.ingestion.db import get_engine, create_watermark_table
from src.ingestion.loader import land_raw_page
from src.ingestion.watermark import get_last_watermark, record_watermark
from src.ingestion.logging_config import setup_logging

logger = setup_logging()

engine = get_engine("local")
create_watermark_table(engine)

last_watermark = get_last_watermark(engine)
start_date = (last_watermark + timedelta(days=1)) if last_watermark else date(2024, 10, 1)
end_date = date.today()

if start_date > end_date:
    logger.info("No new date range to pull. Already up to date.")
else:
    logger.info(f"Pulling awards from {start_date} to {end_date}")

    page = 1
    total_results = 0
    while True:
        payload = build_payload(str(start_date), str(end_date), page=page, limit=100)
        try:
            data = fetch_awards_page(payload)
        except Exception:
            logger.exception(f"Failed to fetch page {page}")
            raise

        land_raw_page(engine, data, page_number=page, request_filters=payload["filters"])
        total_results += len(data["results"])
        logger.info(f"Landed page {page} ({len(data['results'])} results)")

        if not data["page_metadata"]["hasNext"]:
            break
        page += 1

    record_watermark(engine, end_date)
    logger.info(f"Run complete. {total_results} total results landed. Watermark updated to {end_date}")