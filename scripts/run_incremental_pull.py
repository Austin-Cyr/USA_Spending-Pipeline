from datetime import date, timedelta

from src.ingestion.client import fetch_awards_page
from src.ingestion.config import build_payload
from src.ingestion.db import get_engine, create_watermark_table
from src.ingestion.loader import land_raw_page
from src.ingestion.watermark import get_last_watermark, record_watermark

engine = get_engine("local")
create_watermark_table(engine)

last_watermark = get_last_watermark(engine)
start_date = (last_watermark + timedelta(days=1)) if last_watermark else date(2024, 10, 1)
end_date = date.today()

if start_date > end_date:
    print("No new date range to pull. Already up to date.")
else:
    print(f"Pulling awards from {start_date} to {end_date}")

    page = 1
    while True:
        payload = build_payload(str(start_date), str(end_date), page=page, limit=100)
        data = fetch_awards_page(payload)

        land_raw_page(engine, data, page_number=page, request_filters=payload["filters"])
        print(f"Landed page {page} ({len(data['results'])} results)")

        if not data["page_metadata"]["hasNext"]:
            break
        page += 1

    record_watermark(engine, end_date)
    print(f"Watermark updated to {end_date}")