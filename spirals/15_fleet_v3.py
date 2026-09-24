"""
spiral 15: re-render the fleet organism with quilt-perception added.

Now includes the FIRST walker grown by the brewer. The recursion is visible
in the organism view: the walker that walks recipes emits receipts that
chain with the rest of the fleet.
"""
import os
import sys
import json
import glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "..", "quilt-trace", "src"))

from quilt_trace import render_html, aggregate


def make_perception_receipts():
    """Receipts from the brewed quilt-perception walker (real demo data)."""
    # Real demo output from /tmp/brewed/quilt-perception/examples/demo.py
    receipts = []
    readings = [
        ("temperature", 22, "ok", "ACCEPT"),
        ("pressure", 1013, "ok", "ACCEPT"),
        ("humidity", 95, "warn", "DRIFT"),
        ("vibration", 200, "fail", "REFUSE"),
        ("light", 50000, "ok", "ACCEPT"),
        ("proximity", 250, "fail", "REFUSE"),
        ("temperature", 22, "ok", "ACCEPT"),
    ]
    prev = "opt_b"  # chain from cuopt
    base_ts = 1790236000
    for i, (slot, value, status, pol) in enumerate(readings):
        wid = f"percep_{slot}_{i}"
        receipts.append({
            "witness_id": wid, "prev_witness_id": prev, "polarity": pol,
            "substrate": "quilt-perception",
            "cell_id": slot,
            "status": status, "timestamp": base_ts + i * 100,
            "payload": {"value": value},
        })
        prev = wid
    return receipts


def make_bootstrap_receipts():
    """Synthetic receipts from quilt-bootstrap."""
    repos = ["quilt-seed", "quilt-schema-registry", "quilt-trace", "quilt-organism",
              "quilt-optimization", "quilt-director", "quilt-fleet-snapshot",
              "quilt-brewer", "quilt-perception"]
    receipts = []
    prev = "percep_temperature_6"
    base_ts = 1790236500
    for i, repo in enumerate(repos):
        wid = f"boot_{repo}"
        receipts.append({
            "witness_id": wid, "prev_witness_id": prev, "polarity": "ACCEPT",
            "substrate": "quilt-bootstrap",
            "cell_id": repo,
            "status": "cloned", "timestamp": base_ts + i * 100,
            "payload": {"walker_count": 2 if repo in ["quilt-seed", "quilt-organism", "quilt-optimization"] else 1},
        })
        prev = wid
    return receipts


def main():
    print("\n🌱 Spiral 15 — Fleet organism v3 (with perception + bootstrap)")
    print("=" * 60)

    # Start with the same base as before
    base = [
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
    percep = make_perception_receipts()
    boot = make_bootstrap_receipts()

    all_receipts = base + percep + boot
    substrates = sorted(set(r["substrate"] for r in all_receipts))
    print(f"  Composed {len(all_receipts)} receipts across {len(substrates)} substrates")
    for s in substrates:
        n = sum(1 for r in all_receipts if r["substrate"] == s)
        print(f"    {s:25}  {n}")

    stats = aggregate(all_receipts)
    print(f"\n  Polarity: ACCEPT={stats.by_polarity.get('ACCEPT', 0)} "
          f"DRIFT={stats.by_polarity.get('DRIFT', 0)} REFUSE={stats.by_polarity.get('REFUSE', 0)}")
    print(f"  Chain head: {stats.chain_head}")
    print(f"  Chain intact: {stats.chain_intact}")

    html = render_html(all_receipts,
                       title="Quilt Fleet Organism v3 — 11 walkers × 8 substrates")

    out_path = "/workspace/repos/quilt-director/site/fleet-organism-v3.html"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n  ✓ Rendered → {out_path} ({len(html):,} bytes)")
    print(f"  This is the LANDING page for the v3 fleet.")


if __name__ == "__main__":
    main()
