from src.ingestion.config import build_payload


def test_build_payload_structure():
    payload = build_payload("2024-10-01", "2024-10-31", page=2, limit=50)

    assert payload["page"] == 2
    assert payload["limit"] == 50
    assert payload["filters"]["time_period"] == [
        {"start_date": "2024-10-01", "end_date": "2024-10-31"}
    ]
    assert "Award ID" in payload["fields"]