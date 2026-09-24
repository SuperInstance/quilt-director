"""
spiral 12: re-render the fleet organism with the new walkers.

Now includes 7 walker sources (was 6):
- New: quilt-brewer (recipes → walkers)
- New: quilt-schema-registry (validation receipts)

The organism view composes ALL walkers into a single landing page.
"""
import os
import sys
import json
import glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "..", "quilt-trace", "src"))

from quilt_trace import render_html, aggregate


def make_brewer_receipts():
    """Synthetic receipts from quilt-brewer (4 recipes brewed)."""
    recipes = ["quilt-perception", "quilt-fable", "quilt-orchestrator", "quilt-linker"]
    receipts = []
    prev = "opt_b"  # chain from cuopt
    base_ts = 1790235000
    for i, recipe in enumerate(recipes):
        receipts.append({
            "witness_id": f"brew_{recipe}",
            "prev_witness_id": prev,
            "polarity": "ACCEPT",
            "substrate": "quilt-brewer",
            "cell_id": recipe,
            "status": "brewed",
            "timestamp": base_ts + i * 100,
            "payload": {"files": 6, "tests": 9 if i % 2 == 0 else 8},
        })
        prev = f"brew_{recipe}"
    return receipts


def make_schema_receipts():
    """Synthetic receipts from quilt-schema-registry (compliance checks)."""
    substrates = [
        ("VibeReceipt", "ACCEPT"),
        ("CUReceipt", "ACCEPT"),
        ("OptimizationReceipt", "ACCEPT"),
        ("OrganismReceipt", "ACCEPT"),
        ("VectorizeReceiver", "ACCEPT"),
        ("CanonScoreReceiver", "ACCEPT"),
        ("TraceReceipt", "ACCEPT"),
        ("JEVReceipt", "ACCEPT"),
    ]
    receipts = []
    prev = "brew_quilt-linker"  # chain from brewer
    base_ts = 1790235400
    for i, (name, pol) in enumerate(substrates):
        receipts.append({
            "witness_id": f"schema_{name}",
            "prev_witness_id": prev,
            "polarity": pol,
            "substrate": "quilt-schema-registry",
            "cell_id": name,
            "status": "validated",
            "timestamp": base_ts + i * 100,
            "payload": {"fields": 8, "compliant": True},
        })
        prev = f"schema_{name}"
    return receipts


def main():
    print("\n🌱 Spiral 12 — Fleet organism v2 (with brewer + schema)")
    print("=" * 60)

    # Reuse the v1 receipts (start from the same composition)
    opt = [
        {"witness_id": "opt_a", "prev_witness_id": "", "polarity": "ACCEPT",
         "substrate": "cuopt-routing", "cell_id": "warehouse-delivery",
         "status": "Optimal", "timestamp": 1790230000,
         "payload": {"problem": "VRP", "total_cost": 56}},
        {"witness_id": "opt_b", "prev_witness_id": "opt_a", "polarity": "ACCEPT",
         "substrate": "cuopt-lp", "cell_id": "production-mix",
         "status": "Optimal", "timestamp": 1790230500,
         "payload": {"problem": "LP", "objective_value": 1350}},
    ]

    # Add the new ones
    brewer = make_brewer_receipts()
    schema = make_schema_receipts()

    # Add JEV sessions too
    sessions_dir = "/workspace/jev-quilt/jev_sessions"
    jev = []
    prev = schema[-1]["witness_id"]
    base_ts = 1790235500
    if os.path.exists(sessions_dir):
        files = sorted(glob.glob(os.path.join(sessions_dir, "*.json")))[:10]
        n = 0
        for path in files:
            try:
                with open(path) as f:
                    session = json.load(f)
            except Exception:
                continue
            if not isinstance(session, dict):
                continue
            decisions = session.get("decisions", [])
            if not decisions:
                continue
            d = decisions[0]
            if isinstance(d, list) and len(d) > 2:
                score = float(d[2])
            elif isinstance(d, dict):
                score = float(d.get("confidence", 0.5))
            else:
                continue
            pol = "ACCEPT" if score >= 0.7 else ("DRIFT" if score >= 0.3 else "REFUSE")
            wid = f"jev_{n}"
            jev.append({
                "witness_id": wid, "prev_witness_id": prev, "polarity": pol,
                "substrate": "jev-oracle", "cell_id": f"sess_{n}",
                "status": "scored", "timestamp": base_ts + n * 100,
                "payload": {"score": round(score, 4)},
            })
            prev = wid
            n += 1

    all_receipts = opt + brewer + schema + jev
    print(f"  Composed {len(all_receipts)} receipts across {len(set(r['substrate'] for r in all_receipts))} substrates")

    stats = aggregate(all_receipts)
    print(f"  Polarity: ACCEPT={stats.by_polarity.get('ACCEPT', 0)} "
          f"DRIFT={stats.by_polarity.get('DRIFT', 0)} REFUSE={stats.by_polarity.get('REFUSE', 0)}")
    print(f"  Chain head: {stats.chain_head}")
    print(f"  Chain intact: {stats.chain_intact}")

    html = render_html(all_receipts,
                       title="The Quilt Organism — fleet v2 (10 walkers × 7 substrates)")
    out_path = "/workspace/repos/quilt-director/site/fleet-organism-v2.html"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n  ✓ Rendered → {out_path} ({len(html):,} bytes)")
    print(f"  This is the LANDING page for the v2 fleet.")


if __name__ == "__main__":
    main()
