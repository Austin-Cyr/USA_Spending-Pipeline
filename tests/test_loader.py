from sqlalchemy import text
from src.ingestion.db import get_engine
from src.ingestion.loader import land_raw_page


def _clear_raw(engine):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM raw.award_responses WHERE page_number = 9999"))
        conn.commit()


def test_land_raw_page_inserts_row():
    engine = get_engine("local")
    _clear_raw(engine)

    fake_payload = {"results": [{"Award ID": "TEST999"}], "page_metadata": {"hasNext": False}}
    fake_filters = {"time_period": [{"start_date": "2026-01-01", "end_date": "2026-01-31"}]}

    land_raw_page(engine, fake_payload, page_number=9999, request_filters=fake_filters)

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT payload, page_number FROM raw.award_responses WHERE page_number = 9999")
        ).fetchone()

    assert result is not None
    assert result[1] == 9999
    assert result[0]["results"][0]["Award ID"] == "TEST999"

    _clear_raw(engine)