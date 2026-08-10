import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
print(repr(os.getenv("DATABASE_URL_LOCAL")))
engine = create_engine(os.getenv("DATABASE_URL_LOCAL"))


with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connection successful:", result.fetchone())

with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS marts"))
    conn.commit()
    print("Schemas created in local Postgres.")

with engine.connect() as conn:
    result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
    for row in result:
        print(row)