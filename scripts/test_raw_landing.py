from src.ingestion.client import fetch_awards_page
from src.ingestion.config import build_payload
from src.ingestion.db import get_engine
from src.ingestion.loader import land_raw_page

payload = build_payload("2024-10-01", "2024-10-31", page=1, limit=5)
data = fetch_awards_page(payload)

engine = get_engine("local")
land_raw_page(engine, data, page_number=1, request_filters=payload["filters"])

print(f"Landed {len(data['results'])} results into raw.award_responses")

from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, page_number, pulled_at FROM raw.award_responses"))
    for row in result:
        print(row)