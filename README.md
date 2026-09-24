# 🌱 quilt-director

> Director of fleets — Python spirals of knowledge.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Spirals](https://img.shields.io/badge/spirals-8_yielding-brightgreen.svg)](spirals/)
[![Journals](https://img.shields.io/badge/journals-7_persisted-purple.svg)](journal/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What is this?

A long-running director that builds knowledge in spirals. Each spiral:
1. Reads the previous spiral's journal
2. Runs one focused operation
3. Writes its result to `journal/`
4. Commits + pushes

The director uses the [quilt-trace](https://github.com/SuperInstance/quilt-trace) library to render organism views.

## The spirals so far

| # | Title | What happened |
|---|---|---|
| 0 | PLAN | Plan in journal |
| 1 | gaps | Identify 5 gaps in the fleet |
| 2 | env-gaps | Identify 5 setup/env gaps |
| 3 | beyond-horizon | Design 5 new repos to fill gaps |
| 4 | build-quilt-trace | Design + build quilt-trace v0.1.0 |
| 5 | shipped | Journal what landed |
| 6 | render-jev | Render JEV's 483 sessions as organism |
| 7 | fleet-landing | Compose 7 substrates into one landing page |
| 8 | deploy | Package for Cloudflare Pages |

## Token economy

- Each spiral is one focused operation
- API calls only when needed (Gemini for ideation, Groq/DeepSeek for code)
- Most spirals are 0 API calls (built from accumulated wisdom)
- The director remembers what worked

## Run a spiral

```bash
cd /workspace/repos/quilt-director
python3 spirals/01_gaps.py    # identify gaps
python3 spirals/07_fleet_landing.py    # compose landing
```

## Receipt ledger

Every spiral is also a receipt. `tools/book_spirals.py` books one hash-chained
row per spiral (canonical JSON + FNV-1a-64, same family recipe as
[quilt-executor](https://github.com/SuperInstance/quilt-executor)):

```bash
python3 tools/book_spirals.py            # book new/changed spirals → ledger/director.ledger.jsonl
python3 tools/book_spirals.py --verify   # re-derive the chain; exit 1 on tamper (cron-safe)
python3 tests/test_ledger.py             # pins
```

- Spiral journaled → `EFFECT` row `{spiral, file_sha256, journal_sha256}`
- Journal missing → `REFUSED` row with first-class `refusal_type`
  (absence is hash-committed, never silent)
- Re-running is idempotent; mutating a spiral re-books its row
- `DIRECTOR_ROOT` env var points the tool at a different checkout


## Build the landing page

```bash
# Render the fleet organism view
PYTHONPATH=../quilt-trace/src python3 spirals/07_fleet_landing.py

# Serve locally
cd site && python3 -m http.server 8765
# open http://localhost:8765
```

## Related

- [quilt-trace](https://github.com/SuperInstance/quilt-trace) — the visualizer
- [quilt-organism](https://github.com/SuperInstance/quilt-organism) — the walker
- [quilt-optimization](https://github.com/SuperInstance/quilt-optimization) — cuOpt substrate
- [quilt-seed](https://github.com/SuperInstance/quilt-seed) — vessel + legalese
- [jev-quilt](https://github.com/SuperInstance/jev-quilt) — JEV oracle
- [ai-writings](https://github.com/SuperInstance/ai-writings) — the canon

## License

Apache-2.0
