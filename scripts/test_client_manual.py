from src.ingestion.client import fetch_awards_page
from src.ingestion.config import build_payload
import json


payload = build_payload("2024-10-01", "2024-10-31", page=1, limit=5)
data = fetch_awards_page(payload)

print(f"Got {len(data['results'])} results")
for award in data["results"]:
    print(award)
print(json.dumps(data["results"][0], indent=2))