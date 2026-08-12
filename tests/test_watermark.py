from datetime import date
from src.ingestion.db import get_engine, create_watermark_table
from src.ingestion.watermark import get_last_watermark, record_watermark
from sqlalchemy import text


def _clear_watermark(engine):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM raw.pull_watermark"))
        conn.commit()


def test_watermark_returns_none_when_empty():
    engine = get_engine("local")
    create_watermark_table(engine)
    _clear_watermark(engine)

    result = get_last_watermark(engine)
    assert result is None


def test_watermark_records_and_retrieves():
    engine = get_engine("local")
    create_watermark_table(engine)
    _clear_watermark(engine)

    record_watermark(engine, date(2026, 1, 15))
    result = get_last_watermark(engine)

    assert result == date(2026, 1, 15)