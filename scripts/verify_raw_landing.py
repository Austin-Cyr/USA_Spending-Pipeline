from src.ingestion.db import get_engine
from sqlalchemy import text

engine = get_engine("local")

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, page_number, pulled_at FROM raw.award_responses"))
    for row in result:
        print(row)