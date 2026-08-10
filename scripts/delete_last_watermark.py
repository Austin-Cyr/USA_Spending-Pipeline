# python -m scripts.delete_last_watermark
# scripts/delete_last_watermark.py
from sqlalchemy import text
from src.ingestion.db import get_engine

engine = get_engine("local")
with engine.connect() as conn:
    conn.execute(text("""
        DELETE FROM raw.pull_watermark
        WHERE id = (
            SELECT id FROM raw.pull_watermark
            ORDER BY run_completed_at DESC
            LIMIT 1
        )
    """))
    conn.commit()
    print("Most recent watermark row deleted.")