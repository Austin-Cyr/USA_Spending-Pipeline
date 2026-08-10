# run with python -m scripts.check_watermark

from sqlalchemy import text
from src.ingestion.db import get_engine

engine = get_engine("local")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT source, last_successful_end_date, run_completed_at
        FROM raw.pull_watermark
        ORDER BY run_completed_at DESC
    """))
    rows = result.fetchall()

if not rows:
    print("No watermark rows found.")
else:
    print(f"{'source':<25} {'last_successful_end_date':<28} {'run_completed_at'}")
    for row in rows:
        print(f"{row[0]:<25} {str(row[1]):<28} {row[2]}")