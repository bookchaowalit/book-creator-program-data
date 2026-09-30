# Upgrade plan — book-creator-program-data

Current state: **7/10** (pass 1: 5 -> 6.5; pass 2: 6.5 -> 7). Offline contract, adapters and CLI are tested and linted in CI; live capture, source permission and consumers remain unverified by design.

## Backlog

- P0: Push this branch and confirm the new GitHub Actions `CI` workflow is green on both Python versions.
- P1: Replace the copy of `cli.py`/`capture.py` scaffolding shared by the sibling `book-*-data` repos with the shared runtime package once it is independently installable (README gate 3).
- P2: Extract creator-specific terms (audience thresholds, revenue share) only where an official page states them; keep unknown otherwise.
- P2: Add a live-capture smoke job only behind an explicit manual trigger and reviewed source permission (never on push).

## Done in this pass (pass 1)

- Added `.github/workflows/ci.yml`: `ruff check`, `pytest` and an offline CLI smoke (`contract`, `validate demo.json`, `demo --open-only`) on Python 3.10 and 3.13.
- Added `[project.optional-dependencies] dev` (pytest, pinned ruff), `[tool.ruff]` and `[tool.pytest.ini_options]` to `pyproject.toml`; fixed import-order lint.
- Added `tests/test_registry.py`: `sources.json` ↔ packaged `source*.json` consistency (product, domain, category in contract, https URLs, interval), source-ID selector rejects traversal/unknown IDs, every marker-driven adapter normalizes a synthetic page into a valid live record and rejects a challenge page, JSON adapters reject non-object payloads, CLI `validate` exit codes do not echo input.
- GitHub Contents adapter rejects non-object JSON with `ValueError` instead of `AttributeError`.
- Registry test drives every `REQUIRED_MARKERS` HTML adapter with a synthetic page and a challenge-page drift case.

## Done in this pass (pass 2)

- Drift markers now have one source of truth: `capture.normalize` reads `required_markers`
  from each `source-<id>.json` (the duplicate `REQUIRED_MARKERS` code table is gone). A
  config without markers still fails closed (`unknown creator-program source`); empty or
  non-string markers raise `ValueError`.
- New registry test proves the config decides (an extra marker the page lacks fails) and
  that every HTML source ships markers.
