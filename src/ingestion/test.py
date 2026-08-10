from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, page_number, pulled_at FROM raw.award_responses"))
    for row in result:
        print(row)