import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL_LOCAL"))

ddl = """
CREATE TABLE IF NOT EXISTS raw.award_responses (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    page_number INT NOT NULL,
    request_filters JSONB NOT NULL,
    pulled_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

with engine.connect() as conn:
    conn.execute(text(ddl))
    conn.commit()
    print("raw.award_responses created.")