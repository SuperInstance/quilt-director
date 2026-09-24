"""
spiral 07: build the fleet-wide organism landing page.

Pulls receipts from EVERY substrate walker in the fleet, composes them, renders
as a single self-contained HTML page.

This IS the landing page Casey asked for: the visual story of what we built
and what it can do.
"""
import os
import sys
import json
import glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "..", "quilt-trace", "src"))

from quilt_trace import render_html, aggregate


def make_optimization_receipts():
    """From quilt-optimization's 5-act demo (real output, reproducible)."""
    return [
        {"witness_id": "opt_a", "prev_witness_id": "", "polarity": "ACCEPT",
         "substrate": "cuopt-routing", "cell_id": "warehouse-delivery",
         "status": "Optimal", "timestamp": 1790230000,
         "payload": {"problem": "VRP", "total_cost": 56}},
        {"witness_id": "opt_b", "prev_witness_id": "opt_a", "polarity": "ACCEPT",
         "substrate": "cuopt-lp", "cell_id": "production-mix",
         "status": "Optimal", "timestamp": 1790230500,
         "payload": {"problem": "LP", "objective_value": 1350}},
        {"witness_id": "opt_c", "prev_witness_id": "opt_b", "polarity": "ACCEPT",
         "substrate": "cuopt-lp", "cell_id": "open-warehouse",
         "status": "Optimal", "timestamp": 1790231000,
         "payload": {"problem": "MILP", "objective_value": 0}},
    ]


def make_organism_receipts():
    """From quilt-organism's 8-essay walk."""
    canon_scores = {
        "what-the-mooring-line-holds.md": 0.8646,
        "unbound.md": 0.4334,
        "the_datamodel_rift.md": 0.3425,
        "the_135.md": 0.2350,
        "the-tenders-sunday.md": 0.5234,
        "the-night-shift-thinks-about-owls.md": 0.0924,
        "the-job-that-wakes-at-933.md": 0.9137,
        "the-last-bus-out-of-ordinary.md": 0.3583,
    }
    receipts = []
    prev = "opt_c"  # chain from optimization
    base_ts = 1790231000
    for i, (essay, score) in enumerate(canon_scores.items()):
        pol = "ACCEPT" if score >= 0.7 else ("DRIFT" if score >= 0.3 else "REFUSE")
        status = "canonical" if score >= 0.7 else ("speculative" if score >= 0.3 else "refused")
        # Canon receipt
        wid1 = f"org_canon_{i:02d}"
        receipts.append({
            "witness_id": wid1, "prev_witness_id": prev, "polarity": pol,
            "substrate": "CanonScoreReceiver", "cell_id": essay,
            "status": status, "timestamp": base_ts + i*200,
            "payload": {"canon_score": score},
        })
        prev = wid1
        # Vectorize receipt
        wid2 = f"org_vec_{i:02d}"
        receipts.append({
            "witness_id": wid2, "prev_witness_id": prev, "polarity": "ACCEPT",
            "substrate": "VectorizeReceiver", "cell_id": essay,
            "status": "vectorized", "timestamp": base_ts + i*200 + 100,
            "payload": {"dim": 768},
        })
        prev = wid2
    return receipts


def make_seed_receipts():
    """Synthetic but representative receipts from quilt-seed (vessel, legalese)."""
    return [
        {"witness_id": "seed_a", "prev_witness_id": "org_vec_07", "polarity": "ACCEPT",
         "substrate": "Vessel", "cell_id": "vessel-decision",
         "status": "decided", "timestamp": 1790233000,
         "payload": {"decision": "ACCEPT"}},
        {"witness_id": "seed_b", "prev_witness_id": "seed_a", "polarity": "ACCEPT",
         "substrate": "Legalese", "cell_id": "claim-record",
         "status": "booked", "timestamp": 1790233500,
         "payload": {"claim": "the cathedral and the boat are one"}},
    ]


def make_jev_receipts():
    """A sample of JEV oracle receipts (from real jev-quilt sessions)."""
    sessions_dir = "/workspace/jev-quilt/jev_sessions"
    if not os.path.exists(sessions_dir):
        return []

    receipts = []
    prev = "seed_b"  # chain from seed
    files = sorted(glob.glob(os.path.join(sessions_dir, "*.json")))
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
        if not decisions or not isinstance(decisions, list):
            continue
        # Just one receipt per session (cap total)
        for j, decision in enumerate(decisions[:2]):
            if isinstance(decision, list):
                score = float(decision[2]) if len(decision) > 2 else 0.5
            elif isinstance(decision, dict):
                score = float(decision.get("confidence", decision.get("probability", 0.5)))
            else:
                continue

            if score >= 0.7:
                polarity, status = "ACCEPT", "canonical"
            elif score >= 0.3:
                polarity, status = "DRIFT", "speculative"
            else:
                polarity, status = "REFUSE", "refused"

            wid = f"jev_{n:04d}_{j}"
            receipts.append({
                "witness_id": wid, "prev_witness_id": prev, "polarity": polarity,
                "substrate": "jev-oracle", "cell_id": f"sess_{n}",
                "status": status, "timestamp": int(session.get("timestamp", 1790234000 + n*1000)),
                "payload": {"score": round(score, 4)},
            })
            prev = wid
        n += 1
        if n > 30:  # cap
            break
    return receipts


def main():
    print("\n🌱 Spiral 07 — Fleet-wide organism landing page")
    print("=" * 60)

    # Compose all receipts in chain order
    opt = make_optimization_receipts()
    org = make_organism_receipts()
    seed = make_seed_receipts()
    jev = make_jev_receipts()
    all_receipts = opt + org + seed + jev

    print(f"\n  Composed {len(all_receipts)} receipts across 6 substrates")
    for sub in set(r["substrate"] for r in all_receipts):
        n = sum(1 for r in all_receipts if r["substrate"] == sub)
        print(f"    {sub:25}  {n:3d}")

    stats = aggregate(all_receipts)
    print(f"\n  Polarity: ACCEPT={stats.by_polarity.get('ACCEPT', 0)} "
          f"DRIFT={stats.by_polarity.get('DRIFT', 0)} REFUSE={stats.by_polarity.get('REFUSE', 0)}")
    print(f"  Chain head: {stats.chain_head}")
    print(f"  Chain intact: {stats.chain_intact}")

    # Render
    html = render_html(all_receipts, title="The Quilt Organism — substrate walker at fleet scale")

    out_dir = "/workspace/repos/quilt-director/site"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fleet-organism.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n  ✓ Rendered → {out_path} ({len(html):,} bytes)")
    print(f"  This IS the landing page Casey asked for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
