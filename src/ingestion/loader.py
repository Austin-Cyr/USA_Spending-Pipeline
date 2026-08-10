import json
from sqlalchemy import text
from sqlalchemy.engine import Engine

def land_raw_page(engine: Engine, payload: dict, page_number: int, request_filters: dict) -> None:
    """Write a single API response page into raw.award_responses."""
    insert_sql = text("""
        INSERT INTO raw.award_responses (payload, page_number, request_filters)
        VALUES (:payload, :page_number, :request_filters)
    """)
    with engine.connect() as conn:
        conn.execute(
            insert_sql,
            {
                "payload": json.dumps(payload),
                "page_number": page_number,
                "request_filters": json.dumps(request_filters),
            },
        )
        conn.commit()