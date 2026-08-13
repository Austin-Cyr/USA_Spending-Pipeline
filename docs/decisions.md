# Design Decisions

Below are ADR-style notes describing the data pipeline engineering tradeoffs reviewed and made through this project.

---

## 1. Dev/prod environment split: local Docker Postgres vs. Neon

**Decision:** I decided to use a local, Dockerized Postgres instance for development and testing, and a hosted Neon Postgres instance as the production target.

**Why:** This mirrors how real data teams separate environments to develop and iterate against a disposable local database without negative impact to the production data. Additionally, I chose this method to further my experience with a Docker environment. I engineered the switch via via an environment variable (`DATABASE_URL` vs `DATABASE_URL_LOCAL`) and a small `get_engine(env=...)` helper.

**Tradeoff:** This decision added additional setup steps and troubleshooting to support Docker, WSL2 and port conflicts. 

---

## 2. Watermark granularity: date-level, not timestamp-level

**Decision:** I decided to track the incremental pulls via the use of 'Date' vs 'Timestamp'. 

**Why:** I discovered that USASpending award data doesn't refresh through the day and awards are typically releaed within the same day. This made Date-level tracking simpler and sufficient for this scope.

**Tradeoff:** This decision does require running the pipeline at the end of the day to ensure a full day's data is captured before the watermark advances past it. If the source data ever needed intra-day tracking,  I could easily fix this with a an update from `DATE` for `TIMESTAMPTZ` and use `datetime.utcnow()` instead of `date.today()`.

---

## 3. NAICS Code/Description are frequently null — not a bug

**Decision:** I decided to leave NAICS fields nullable throughout the pipeline (staging, `dim_naics`, `fact_awards`) rather than filtering out or flagging awards missing NAICS data.

**Why:** I investigated directly against the raw API response and confirmed USASpending itself returns `null` for NAICS on many awards. 

**Note:** `dim_naics` will only ever reflect awards where NAICS was actually reported by the source system.

---

## 4. CI runs on Python 3.12, not the local dev version (3.14)

**Decision:** GitHub Actions CI is pinned to Python 3.12, despite my local environment using 3.14.7.

**Why:** Python 3.14 is very new and I have found that some packages may not support all environments just yet. It was suggesetd to use a prior version to avoid CI-only dependency failures that are not related to how best to write the code.

---

## 5. Removed `pywin32` from `requirements.txt`

**Decision:** I manually stripped `pywin32`  from `requirements.txt` after it broke the Linux-based CI build.

**Why:** `pywin32` had been pulled in as a transitive dependency during local Windows development and pinned into `requirements.txt` via `pip freeze`. It has no Linux equivalent, so `pip install` failed immediately on GitHub's `ubuntu-latest` runner. Removing the explicit pin doesn't affect local Windows functionality — pip still installs it automatically there if anything actually needs it.

**Takeaway:** `pip freeze` output should be reviewed for varying dependencies before relying on it in a cross-platform CI environment.

---

## 6. Restricted pytest discovery to `tests/`

**Decision:** I added a `pytest.ini` with `testpaths = tests` to explicitly scope pytest's test discovery.

**Why:** Pytest's default discovery rules picked up any file matching `test_*.py` anywhere in the repo — including manual, one-off verification scripts kept in `scripts/` (for example `scripts/test_raw_landing.py`) for ad-hoc debugging. One of these scripts ran live API calls and database writes on import, which passed locally but failed in CI, since it was never meant to be an automated test in the first place.

**Takeaway:** I discovered that naming conventions matter during manual debugging with short cuts. I can accidentally run a "test" pytest.

---

## 7. Prefect tasks explicitly disable caching on DB/engine arguments

**Decision:** I set `cache_policy=NO_CACHE` on Prefect tasks that received a SQLAlchemy `Engine` object as an argument.

**Why:** Prefect's default caching behavior tries to hash task inputs to build a cache key. A SQLAlchemy `Engine` holds live connections and can't be serialized/hashed, which caused a error on every task run. Since these tasks perform database writes, caching their results weren't needed.

---

## 8. Raw layer stores full JSONB payloads, not pre-parsed columns

**Decision:** I set `raw.award_responses` to store the entire API response page as a JSONB blob, plus minimal metadata (`page_number`, `request_filters`, `pulled_at`) instead of individual parsed columns.

**Why:** This preserves a full audit trail of exactly what the API returned. If a downstream transformation bug is discovered later, the raw data can be reprocessed without needing to re-hit the API. This is the standard "bronze layer" pattern in a medallion (raw → staging → marts) architecture.