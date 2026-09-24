# Spirals 18-19 — quilt-cli integration

**Date:** 2026-09-24

## What happened

Wired 3 new commands into the existing `quilt` CLI v0.5.0:
- `quilt bootstrap` — delegate to quilt-bootstrap
- `quilt brew` — delegate to quilt-brewer
- `quilt trace` — delegate to quilt-trace

These 3 commands compose the **substrate walker fleet** into the existing
unified CLI surface. The fleet is now consumable from a single command.

## What quilt-cli now contains

21 commands total:
- cell/quilt/qult/fleet/edge/sim/voice/mesh/canon/init/doctor/version
- scout/chord/legalese/holodeck (existing v0.4.0)
- **bootstrap/brew/trace** (NEW in v0.5.0)

## Why this matters

Casey's directive: "use all your wisdom and experience from your scouts to
shape your novel ideas for repos beyond the horizon and for solutions we
aren't seeing for setup and environments that could brew growth and evolve
into what we need for the next phase of development."

The setup solution: `quilt bootstrap --mode full` (one command)
The brew solution: `quilt brew <recipe>` (one command)
The visual solution: `quilt trace receipts.jsonl` (one command)

All from a single CLI that already knows about the existing quilt-cell-harness,
quilt-spreadsheet-inference, etc.

## Token economy

- 0 API calls
- Built from accumulated wisdom
- ~199 LOC across 3 files (matches the substrate walker pattern!)

## The fleet is now unified

10 walker repos + the unified CLI = a single coherent system.
A new developer types `quilt` and sees everything.
