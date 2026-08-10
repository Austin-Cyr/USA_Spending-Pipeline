from datetime import date
from sqlalchemy import text
from sqlalchemy.engine import Engine

SOURCE = "usaspending_awards"

def get_last_watermark(engine: Engine) -> date | None:
    """Return the end_date of the most recent successful pull, or None if no prior runs."""
    query = text("""
        SELECT last_successful_end_date
        FROM raw.pull_watermark
        WHERE source = :source
        ORDER BY run_completed_at DESC
        LIMIT 1
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"source": SOURCE}).fetchone()
        return result[0] if result else None


def record_watermark(engine: Engine, end_date: date) -> None:
    """Record a successful pull's end date."""
    insert_sql = text("""
        INSERT INTO raw.pull_watermark (source, last_successful_end_date)
        VALUES (:source, :end_date)
    """)
    with engine.connect() as conn:
        conn.execute(insert_sql, {"source": SOURCE, "end_date": end_date})
        conn.commit()