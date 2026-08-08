import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
print(repr(os.getenv("DATABASE_URL")))
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connection successful:", result.fetchone())