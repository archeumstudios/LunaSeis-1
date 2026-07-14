# Contributing to LunaSeis-1

LunaSeis-1 prioritizes scientific traceability over metric chasing.

## Before contributing

- Read `docs/research_protocol_v0.1.md` and `docs/CURRENT_STATUS.md`.
- Never commit raw archive files, credentials, or uncontrolled checkpoints.
- Do not tune against consumed continuous frames v0.1 or v0.2.
- Call non-catalogued windows `catalog-negative background`, not guaranteed noise.
- Preserve failed experiments and exact seeds/configurations.

## Development checks

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q lunaseis scripts tests
git diff --check
```

Scientific changes should include a machine-readable configuration, provenance-aware outputs, tests, and a decision record when they alter evaluation meaning.
