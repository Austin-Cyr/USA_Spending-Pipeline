# filter payload / constants
DEFAULT_FIELDS = [
    "Award ID", "Recipient Name", "Start Date", "End Date",
    "Award Amount", "Awarding Agency", "Awarding Sub Agency",
    "Contract Award Type", "NAICS Code", "NAICS Description",
]

def build_payload(start_date: str, end_date: str, page: int = 1, limit: int = 100) -> dict:
    return {
        "filters": {
            "award_type_codes": ["A", "B", "C", "D"],
            "time_period": [{"start_date": start_date, "end_date": end_date}],
        },
        "fields": DEFAULT_FIELDS,
        "page": page,
        "limit": limit,
        "sort": "Award Amount",
        "order": "desc",
    }