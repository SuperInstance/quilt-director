# Spiral 14 — quilt-bootstrap

**Date:** 2026-09-24

## What happened

Built and shipped quilt-bootstrap v0.1.0 — one command to bring up the
whole fleet.

## The product

- 16/16 tests pass
- 3 modes (minimal/full/demo)
- 9 repos in fleet inventory
- 11 walker instances linked

## Usage

```python
from quilt_bootstrap import bootstrap
bootstrap(mode="full", prefix="/workspace")
# Cloned: 9 repos, walker instances: 11, elapsed: ~90s
```

## Why this matters

The wipe problem was solved by `quilt-fleet-snapshot` (preserves state).
The bootstrap complements it (rebuilds state). Together:
- Snapshot: bake fleet state into tarball
- Bootstrap: restore fleet in <90 seconds

A fresh sandbox can now be operational in <90 seconds, with all 11 walkers
linked and tested.

## The pattern

quilt-bootstrap is itself a substrate walker:
- Its substrate is the fleet's git history
- Its receivers are the `LINKED_WALKERS` mapping
- Its output is the cloned repos + linked walkers

## Token economy

- 0 API calls
- Built from accumulated wisdom
- 199 LOC wrapper + 130 LOC tests + 50 LOC demo

## Total fleet now

10 repos in SuperInstance/:
1. quilt-seed
2. quilt-organism
3. quilt-trace
4. quilt-optimization
5. quilt-director
6. quilt-fleet-snapshot
7. quilt-schema-registry
8. quilt-brewer
9. quilt-perception (brewed!)
10. quilt-bootstrap (NEW)
