# book-creator-program-data

Find recurring creator support with audience, deliverable and rights conditions.

Status: **local source pilot**, version 0.1.0. Five manually invoked official
public sources run through the shared bounded capture and lake replay lane.
There is no scheduler, hosted API, consumer integration or sponsorship action.
Capture never falls back from live data to fixtures.

## Users and boundary

For people and small teams discovering creator and contributor programs.
Creator-qualified participation; individual project grants and general affiliates remain their own domains.

Subcategories: creator-fund, ambassador, sponsorship-program, open-source-sponsorship, contributor-program.

Domain-specific terms: `creator_medium`, `audience_requirement`, `deliverables`, `content_rights`.
Each record represents one program/offer intake window. A repeat intake receives
a distinct source record ID. Cross-domain packages use `related_records` rather
than copying the same award into several products.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
book-creator-program-data contract
book-creator-program-data demo --open-only
book-creator-program-data demo --query "creator-fund"
book-creator-program-data validate src/book_creator_program_data/demo.json
python -m unittest discover -s tests -v
python -m pip install -e ".[dev]"  # pytest + pinned ruff
ruff check . && python -m pytest -q
```

CI (`.github/workflows/ci.yml`) runs `ruff check`, the offline test suite and a
CLI smoke test on Python 3.10 and 3.13. `tests/test_registry.py` keeps
`sources.json`, the packaged `source*.json` configs and the contract in sync.

With dependencies already available, use `PYTHONPATH=src python3 -m book_creator_program_data`.
`demo` uses the fixed synthetic clock 2026-09-07T00:00:00Z unless `--as-of` is
provided. `--open-only` excludes closed, unknown-deadline, expired, stale (72h
default), and future-checked records. This is an availability filter; it does
not assert personal eligibility, selection probability, or a guaranteed payout.

Contract: `src/book_creator_program_data/schema.json` (`creator_program.v1`).
Unknown amounts, currencies, eligibility and deadlines remain unknown. Cash,
credit, discount, in-kind benefits and access are different value kinds. Never
sum them as cash income. Queries and validation are read-only and do not persist
provided files. The `live` label requires captured lineage, but validation alone
does not verify that referenced lake objects exist or prove source truth.

## Data ownership and source policy

Owner: bookchaowalit. Public program metadata only; no applications, personal
screening answers, financial credentials, cookies, or private transcripts.
See `sources.json` and the source policy JSON files under
`src/book_creator_program_data/`: YouTube, Google Developer Experts, GitHub
Sponsors and Mozilla contributor pages are enabled for public metadata only.
Exact source permission and retention are reviewed before network ingestion. No
account, sponsorship or payment action is performed.

Implemented flow: approved source pull → immutable landing bytes
and checksum → Bronze Parquet and manifest through the shared lake runtime →
versioned read-only contract → consumer pull. Each product owns its source
adapters and lake prefix. Producers never write into another app's database,
CRM, tasks, application tracker, or notification system.

## Remaining implementation gates

1. Expand creator-medium, deliverable and rights extraction without inferring
   audience size or sponsorship income.
2. Package the local shared capture runtime for independent deployment.
3. Add retention/access controls and runtime monitoring.
4. Connect a read-only consumer. Eligibility, ranking, deadlines and
   application workflow belong to consumers with separate private storage.

## Official source pilots

Sources: [YouTube Partner Program](https://support.google.com/youtube/answer/94522),
[Google Developer Experts](https://developers.google.com/community/experts),
[GitHub Sponsors](https://github.com/sponsors), [About GitHub Sponsors](https://docs.github.com/en/sponsors/getting-started-with-github-sponsors/about-github-sponsors),
and [Mozilla contributors](https://www.mozilla.org/en-US/contribute/). The adapter
preserves public program metadata and leaves thresholds, nomination, region,
approval, payout, volunteer and rights terms subject to the current official
policies.

```bash
export SOLO_DATA_LAKE_ROOT=/path/to/solo-data-lake
PYTHONPATH=src "$SOLO_DATA_LAKE_ROOT/.venv/bin/python" -m book_creator_program_data.capture acquire --lake "$PWD/data/lake" --state-dir "$PWD/data/control"
PYTHONPATH=src "$SOLO_DATA_LAKE_ROOT/.venv/bin/python" -m book_creator_program_data.capture records --lake "$PWD/data/lake" --state-dir "$PWD/data/control"
```

No runtime port is reserved. The former `opportunity.v1` is archival; `job.v1` remains a separate job-data contract.
Breaking contract changes require a new version and a consumer migration.
There is no production deployment to roll back; discard demo output or restore
the previous contract version locally. Source permission, live availability,
lake replay and real eligibility are **unverified**, not passing gates.
