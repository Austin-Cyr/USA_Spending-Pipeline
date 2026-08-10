 # the API client itselfimport requests
import requests
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"


def _get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session


def fetch_awards_page(payload: dict, session: requests.Session | None = None) -> dict:
    """Fetch a single page of award results from USASpending."""
    session = session or _get_session()
    response = session.post(BASE_URL, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()