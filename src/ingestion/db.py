import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()

def get_engine(env: str = "local") -> Engine:
    """env: 'local' for Docker Postgres, 'prod' for Neon."""
    url = os.getenv("DATABASE_URL_LOCAL") if env == "local" else os.getenv("DATABASE_URL")
    return create_engine(url)