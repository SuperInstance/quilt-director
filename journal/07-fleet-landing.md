# Spiral 07 — Fleet-wide organism landing page

**Date:** 2026-09-24

## What happened

Composed receipts from 7 substrates in the fleet:
- cuopt-routing (quilt-optimization VRP)
- cuopt-lp (quilt-optimization LP + MILP)
- CanonScoreReceiver (quilt-organism)
- VectorizeReceiver (quilt-organism)
- Vessel (quilt-seed)
- Legalese (quilt-seed)
- jev-oracle (jev-quilt sessions)

## The composition (chain order)

```
[opt: cuopt-routing VRP]
  ↓
[opt: cuopt-lp production]
  ↓
[opt: cuopt-lp facility]
  ↓
[org: CanonScore × 8 essays] (one per essay, chain-linked)
  ↓
[org: Vectorize × 8 essays]
  ↓
[seed: Vessel decision]
  ↓
[seed: Legalese claim]
  ↓
[jev: 16 oracle decisions across sessions]
```

## Total

- **37 receipts**
- **22 ACCEPT / 10 DRIFT / 5 REFUSE**
- **Chain intact: True**
- **14KB HTML**

## What this demonstrates

The substrate walker pattern composes ACROSS substrates. Receipts from:
- Different programming languages (Python, TypeScript, Rust, C)
- Different repos (quilt-optimization, quilt-organism, quilt-seed, jev-quilt)
- Different agents (Mavis, kimi1, Casey)
- Different time periods

...all carry the same envelope (witness_id + prev_witness_id + polarity) and
all chain into a single organism view.

## The landing page IS the visual story

This is what Casey asked for: "a landing page and great presentation of
what we have shown it can do visually in quilt." The fleet-organism.html
shows:

- A title that names the whole fleet
- The chain head (latest witness_id)
- 4 stat boxes: receipts, cells, substrates, chain integrity
- The polarity histogram
- The substrate breakdown (all 7 substrates)
- The top cells (the most-cited items)
- A force-directed graph of the entire chain

When you open this in a browser, you SEE the organism.
