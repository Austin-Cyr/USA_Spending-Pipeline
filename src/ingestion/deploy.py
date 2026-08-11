from src.ingestion.flow import usaspending_ingestion_flow

if __name__ == "__main__":
    usaspending_ingestion_flow.serve(
        name="usaspending-daily-pull",
        cron="0 22 * * *",  # 10 PM daily — end of day, per your earlier plan
    )