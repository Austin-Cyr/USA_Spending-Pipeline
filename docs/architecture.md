# Architecture

## Overview

This pipeline pulls U.S. federal contract award data from the USASpending.gov 
API, places it in a raw JSONB table, then transforms it through a staged dbt 
model layer, and finally produces a queryable star schema. The pipeline is orchestrated end to 
end by Prefect and validated by an automated test suite that is run on every commit.

Orchestrated by **Prefect** (retries, scheduling, run visibility).
Validated by **pytest** + **GitHub Actions CI** on every push.

## Stage 1: Ingestion

**Location:** `src/ingestion/client.py`, `config.py`, `flow.py`

- `client.py` wraps the USASpending `spending_by_award` API endpoint with 
  a `requests.Session` configured for automaticaly retry or backoff on 
   failures codes (429, 500, 502, 503, 504).
- `config.py` builds the filter/payload structure for each request — 
  award type codes, date range, requested fields, pagination.
- `flow.py` wraps the whole pull in a Prefect flow, with individual 
  fetch/land steps as retry-safe Prefect tasks.
- **Incremental pulls:** a `raw.pull_watermark` table tracks the last 
  successfully pulled date. Each run only requests data since that 
  watermark, rather than re-pulling the full history every time. See 
  `docs/decisions.md` for the reasoning behind date-level (not 
  timestamp-level) granularity.
- **Error handling:** failed API calls retry automatically at the task 
  level (Prefect) and the HTTP level (`requests` retry adapter). A 
  failed run does not advance the watermark, so the next run will 
  retry the same date range.

## Stage 2: Raw landing

**Location:** `src/ingestion/loader.py`, `db.py`

- Each API response page is written to `raw.award_responses` as a full 
  JSONB blob, alongside metadata: `page_number`, `request_filters`, 
  `pulled_at`.
- This is an append-only "bronze layer" — nothing is overwritten or 
  deleted here. If a downstream transformation bug is found later, the 
  original API responses can be reprocessed without re-hitting the API.

## Stage 3: Staging (dbt)

**Location:** `usaspending_dbt/models/staging/`

- `stg_awards.sql` unnests the JSONB `results` array from `raw.award_responses` 
  and casts each field to its proper type (dates, numeric amounts).
- `stg_agencies.sql`, `stg_recipients.sql`, `stg_naics.sql` deduplicate 
  the repeated agency/recipient/NAICS text found across award records 
  and generate surrogate keys (via `dbt_utils.generate_surrogate_key`) 
  for use in the mart layer.
- Materialized as **views** — lightweight, always reflect current raw data.

## Stage 4: Marts (dbt)

**Location:** `usaspending_dbt/models/marts/`

- A standard star schema: `fact_awards` at the center, joined to 
  `dim_agency`, `dim_recipient`, and `dim_naics`.
- Materialized as **tables** — the final, queryable layer.
- Tested for referential integrity (`relationships` tests between 
  `fact_awards` and each dimension) and uniqueness/not-null constraints 
  on all key columns.

## Orchestration

**Location:** `src/ingestion/flow.py`, `deploy.py`

- The full ingestion flow runs under Prefect, with retry-safe tasks and 
  run visibility via the Prefect UI.
- A scheduled deployment (`deploy.py`) triggers the flow daily via cron, 
  timed for end-of-day to ensure a full day's award data is captured 
  before the watermark advances (see `docs/decisions.md`).
- dbt transformations are run separately, after ingestion completes 
  (`dbt run` against the updated raw data).

## Testing & CI

**Location:** `tests/`, `.github/workflows/ci.yml`

- pytest suite covers the API client (mocked HTTP responses), payload 
  config logic, watermark read/write behavior, and raw-landing inserts 
  — the latter two run against a real Postgres instance rather than a 
  mock, to validate actual SQL behavior.
- GitHub Actions runs the full suite on every push and pull request, 
  against a fresh, ephemeral Postgres service container — proving the 
  pipeline is reproducible from a clean state, not just working against 
  a pre-populated local database.
- dbt tests (`not_null`, `unique`, `relationships`) validate the mart 
  layer's data quality and referential integrity separately.

## Known data limitations

- NAICS Code/Description are frequently `null` in USASpending's source 
  data for certain award types and agencies — this is reflected 
  accurately in `dim_naics` rather than backfilled or filtered out.
- Classified/national-security contracts are not present in USASpending 
  at all, per the source system's own scope.