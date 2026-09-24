"""
spiral 06: render jev-quilt's 483 sessions as the organism.

The jev-quilt repo has 483 session JSON files. Each is a JEV oracle evaluation.
We render them as a single organism view.

The point: the substrate walker pattern at scale — what does it look like when
the witness chain has 100s of receipts? Does the organism still SEE itself?
"""
import os
import sys
import json
import glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "..", "quilt-trace", "src"))

from quilt_trace import render_html, aggregate


def parse_decision(decision):
    """Parse one JEV decision into a normalized score."""
    if isinstance(decision, list):
        # [kind, value, confidence, ...]
        try:
            return float(decision[2]) if len(decision) > 2 else 0.5
        except (ValueError, TypeError):
            return 0.5
    elif isinstance(decision, dict):
        return float(decision.get("confidence", decision.get("probability", decision.get("score", 0.5))))
    return 0.5


def main():
    print("\n🌱 Spiral 06 — render jev-quilt's sessions")
    print("=" * 60)

    sessions_dir = "/workspace/jev-quilt/jev_sessions"
    if not os.path.exists(sessions_dir):
        candidates = glob.glob("/workspace/**/jev_sessions", recursive=True)
        if candidates:
            sessions_dir = candidates[0]
        else:
            print("  ✗ no jev_sessions found")
            return 1

    print(f"  Sessions dir: {sessions_dir}")
    session_files = sorted(glob.glob(os.path.join(sessions_dir, "*.json")))
    print(f"  Found {len(session_files)} session files")

    # Convert each session into a receipt-like shape
    receipts = []
    prev = ""
    skipped_empty = 0
    for i, path in enumerate(session_files):
        try:
            with open(path) as f:
                session = json.load(f)
        except Exception:
            continue

        if not isinstance(session, dict):
            skipped_empty += 1
            continue

        decisions = session.get("decisions", [])
        if not decisions or not isinstance(decisions, list):
            skipped_empty += 1
            continue

        questions = session.get("questions", [])
        session_name = os.path.basename(path).replace(".json", "")[:30]

        # Take up to 5 decisions per session (keeps total tractable)
        for j, decision in enumerate(decisions[:5]):
            score = parse_decision(decision)
            qid = questions[j][0] if j < len(questions) and isinstance(questions[j], list) else f"q{j}"

            if score >= 0.7:
                polarity, status = "ACCEPT", "canonical"
            elif score >= 0.3:
                polarity, status = "DRIFT", "speculative"
            else:
                polarity, status = "REFUSE", "refused"

            wid = f"jev_{i:04d}_{j:02d}"
            receipts.append({
                "witness_id": wid,
                "prev_witness_id": prev,
                "polarity": polarity,
                "substrate": "jev-oracle",
                "cell_id": f"{session_name}/{qid}"[:40],
                "status": status,
                "timestamp": int(session.get("timestamp", i * 1000)),
                "payload": {"score": round(score, 4)},
            })
            prev = wid

    print(f"\n  Skipped {skipped_empty} empty sessions")
    print(f"  Composed {len(receipts)} receipts")
    stats = aggregate(receipts)
    print(f"  Polarity: ACCEPT={stats.by_polarity.get('ACCEPT', 0)} "
          f"DRIFT={stats.by_polarity.get('DRIFT', 0)} REFUSE={stats.by_polarity.get('REFUSE', 0)}")
    print(f"  Chain head: {stats.chain_head[:16]}")
    print(f"  Chain intact: {stats.chain_intact}")

    # Render
    html = render_html(receipts, title="JEV Oracle — 483 Sessions of the Eye")

    out_dir = "/workspace/repos/quilt-director/site"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "jev-organism.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n  ✓ Rendered → {out_path} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
