import responses
from src.ingestion.client import fetch_awards_page, BASE_URL


@responses.activate
def test_fetch_awards_page_success():
    mock_response = {
        "results": [{"Award ID": "TEST123", "Recipient Name": "Test Recipient"}],
        "page_metadata": {"page": 1, "hasNext": False},
    }
    responses.add(
        responses.POST,
        BASE_URL,
        json=mock_response,
        status=200,
    )

    payload = {"filters": {}, "page": 1, "limit": 100}
    result = fetch_awards_page(payload)

    assert result == mock_response
    assert len(result["results"]) == 1
    assert result["results"][0]["Award ID"] == "TEST123"


@responses.activate
def test_fetch_awards_page_raises_on_error():
    responses.add(
        responses.POST,
        BASE_URL,
        json={"error": "Bad Request"},
        status=400,
    )

    payload = {"filters": {}, "page": 1, "limit": 100}

    try:
        fetch_awards_page(payload)
        assert False, "Expected an exception to be raised"
    except Exception:
        pass