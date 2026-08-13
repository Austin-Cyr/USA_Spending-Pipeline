# USASpending Data Pipeline

An automated ETL pipeline for U.S. federal contract spending data, built 
with Python, Prefect, and dbt — pulling from the USASpending.gov API 
into a tested, orchestrated, dual-environment (dev/prod) star schema.

## Why this exists

I built this to practice — and demonstrate — the full data engineering 
lifecycle end to end: ingestion, orchestration, transformation, testing, 
and CI, against a real, publicly available government dataset, rather 
than a toy CSV.

## What it does

- **Ingests** U.S. federal contract award data from the USASpending.gov 
  API, with retry/backoff logic and incremental (watermark-based) pulls
- **Lands** raw API responses into Postgres as JSONB, preserving a full 
  audit trail
- **Transforms** raw data into a tested star schema via dbt (staging → 
  marts)
- **Orchestrates** the full pipeline with Prefect — scheduled daily, 
  retry-safe, visible via the Prefect UI
- **Tests** every layer: pytest for the ingestion code, dbt tests for 
  data quality and referential integrity, all run automatically via 
  GitHub Actions CI on every push

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full stage-by-stage breakdown.

## Tech stack

Python · Prefect · dbt · PostgreSQL (Neon for production, Docker for local dev/test) · pytest · GitHub Actions

## A few design decisions worth noting

- **Dev/prod split:** local Docker Postgres for development, hosted Neon 
  for production — mirrors real-world environment separation
- **Prefect over Airflow:** chosen for this project's scope; see 
  [`docs/decisions.md`](docs/decisions.md) for the full reasoning
- **Date-level (not timestamp-level) watermarking:** a deliberate 
  tradeoff based on how frequently the source data actually changes

Full list of tradeoffs and the reasoning behind them: [`docs/decisions.md`](docs/decisions.md)

## Running it locally

**Prerequisites:** Docker Desktop running, Python 3.12+, a `.env` file 
(see `.env.example`)

```bash
# 1. Start local Postgres
docker compose up -d

# 2. Set up the environment
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 3. Run the ingestion flow
python -m src.ingestion.flow

# 4. Run dbt transformations
cd usaspending_dbt
dbt run

# 5. Run tests
pytest
dbt test
```

## Status

🚧 Actively developed — see [project plan](docs/project-plan.md) for 
the full milestone breakdown.