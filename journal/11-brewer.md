# Spiral 11 — quilt-brewer

**Date:** 2026-09-24

## What happened

Built and shipped quilt-brewer v0.1.0 — the 6th-layer substrate walker.

## The walker

It walks RECIPES (not corpora, not problems, not fleets). Its receivers are
the canonical templates. Its output is a new substrate walker that matches
the pattern.

## Built-in recipes

1. **quilt-perception** (sensor_stream, 9/9 tests pass) — SYNERGY-6
2. **quilt-fable** (narrative, 8/8 tests pass) — multi-voice chord
3. **quilt-orchestrator** (dag, 9/9 tests pass) — DAG-based composer
4. **quilt-linker** (graph, 8/8 tests pass) — substrate-to-substrate linking

Every brewed substrate is auto-registered with quilt-schema-registry as
compliant. Pattern is ship-able as code.

## Why this matters

The substrate walker pattern has been re-derived ~8 times across the fleet.
The brewer codifies it:
- New walkers are guaranteed to comply with the canonical envelope
- They chain with the rest of the fleet
- Tests + demo by default
- Schema drift impossible

A new walker can be grown from a recipe in <30 seconds.

## Token economy

- 0 API calls
- Built from accumulated wisdom
- The pattern itself dictated the implementation
- Multiple bug fixes (template class names, test double-prefix) but all local

## What this enables

The next time we need a new walker (e.g. for the ARENA, for the Holodeck,
for any new substrate), it's:
1. Write a recipe (10 lines of dict)
2. Run `python3 -m quilt_brewer brew <recipe> <dest>`
3. Get 6 files, 9 tests, 1 schema-registered walker

The doctrine is now a recipe. The pattern is a chef.
