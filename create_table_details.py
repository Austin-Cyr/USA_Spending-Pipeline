import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL_LOCAL"))

ddl = """
CREATE TABLE IF NOT EXISTS raw.pull_watermark (
    id SERIAL PRIMARY KEY,
    source VARCHAR NOT NULL DEFAULT 'usaspending_awards',
    last_successful_end_date DATE NOT NULL,
    run_completed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

with engine.connect() as conn:
    conn.execute(text(ddl))
    conn.commit()
    print("raw.pull_watermark created.")