import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()

def get_engine(env: str = "local") -> Engine:
    """env: 'local' for Docker Postgres, 'prod' for Neon."""
    url = os.getenv("DATABASE_URL_LOCAL") if env == "local" else os.getenv("DATABASE_URL")
    return create_engine(url)

def create_watermark_table(engine: Engine) -> None:
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