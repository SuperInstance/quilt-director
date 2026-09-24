"""
Spiral 25 — Fleet organism v4.

Compose receipts across all 13 walker instances (12 quilt bootstrap walker
instances + quilt-canon-witness ledger) and render the fleet organism
in chain order.

Walker set:
  1. quilt-seed.vibe
  2. quilt-seed.cu_substrate
  3. quilt-trace.renderer
  4. quilt-organism.substrate
  5. quilt-organism.scouts
  6. quilt-optimization.routing
  7. quilt-optimization.linear_programming
  8. quilt-schema-registry.registry
  9. quilt-fleet-snapshot.snapshot
 10. quilt-brewer.brewer
 11. quilt-perception.sensor_stream
 12. quilt-canon-witness.ledger
 13. quilt-fable.narrative
 14. quilt-orchestrator.dag
 15. quilt-linker.graph

15 walker instances × 4 receipts each = 60 receipts across the chain.
Render via quilt-trace → site/fleet-organism-v4.html
"""
import os
import sys
import json
import hashlib
import time

RECEIPTS_PATH = "/workspace/repos/quilt-director/site/fleet-v4-receipts.jsonl"
HTML_OUT = "/workspace/repos/quilt-director/site/fleet-organism-v4.html"

WALKERS = [
    ("quilt-seed", "vibe"),
    ("quilt-seed", "cu_substrate"),
    ("quilt-trace", "renderer"),
    ("quilt-organism", "substrate"),
    ("quilt-organism", "scouts"),
    ("quilt-optimization", "routing"),
    ("quilt-optimization", "linear_programming"),
    ("quilt-schema-registry", "registry"),
    ("quilt-fleet-snapshot", "snapshot"),
    ("quilt-brewer", "brewer"),
    ("quilt-perception", "sensor_stream"),
    ("quilt-canon-witness", "ledger"),
    ("quilt-fable", "narrative"),
    ("quilt-orchestrator", "dag"),
    ("quilt-linker", "graph"),
]


def step_payload(walker_name: str, instance_name: str, tick: int) -> dict:
    """Per-walker payload — 4 receipts each, status rotates."""
    statuses = ["ok", "ok", "warn", "ok"]
    status = statuses[tick % 4]
    return {
        "walker": walker_name,
        "instance": instance_name,
        "tick": tick,
        "status": status,
        "value": tick * 17 + 3,
    }


def status_to_polarity(status: str) -> str:
    return {"ok": "ACCEPT", "warn": "DRIFT", "fail": "REFUSE"}.get(status, "DRIFT")


def make_receipt(prev_wid: str, payload: dict, cell_id: str) -> dict:
    h = hashlib.sha256()
    h.update(cell_id.encode())
    h.update(json.dumps(payload, sort_keys=True, default=str).encode())
    h.update(prev_wid.encode())
    wid = h.hexdigest()[:16]
    receipt = {
        "witness_id": wid,
        "prev_witness_id": prev_wid,
        "cell_id": cell_id,
        "substrate": payload["walker"],
        "polarity": status_to_polarity(payload["status"]),
        "status": payload["status"],
        "timestamp": time.time() + payload["tick"] * 0.001,
        "payload": payload,
    }
    return receipt


def main():
    print("\n🌱 Spiral 25 — Fleet organism v4")
    print(f"   {len(WALKERS)} walker instances × 4 receipts = {len(WALKERS)*4} total")
    print("=" * 60)

    os.makedirs(os.path.dirname(RECEIPTS_PATH), exist_ok=True)

    receipts = []
    prev = "0x0000000000000000"  # GENESIS

    for walker_name, instance_name in WALKERS:
        for tick in range(4):
            cell_id = f"{walker_name}.{instance_name}.t{tick}"
            payload = step_payload(walker_name, instance_name, tick)
            receipt = make_receipt(prev, payload, cell_id)
            receipts.append(receipt)
            prev = receipt["witness_id"]

    with open(RECEIPTS_PATH, "w") as f:
        for r in receipts:
            f.write(json.dumps(r) + "\n")

    # Stats
    counts = {"ACCEPT": 0, "DRIFT": 0, "REFUSE": 0}
    for r in receipts:
        counts[r["polarity"]] += 1
    print(f"\n  Receipts: {len(receipts)}")
    print(f"  Polarity:  ACCEPT={counts['ACCEPT']}  DRIFT={counts['DRIFT']}  REFUSE={counts['REFUSE']}")

    # Render via quilt-trace
    print("\n  Rendering via quilt-trace...")
    sys.path.insert(0, "/workspace/repos/quilt-trace/src")
    try:
        from quilt_trace import read_receipts, render_html
        parsed = list(read_receipts(RECEIPTS_PATH))
        html = render_html(parsed, title="The Quilt Fleet — Organism v4")
        with open(HTML_OUT, "w") as f:
            f.write(html)
        print(f"  ✓ Rendered {len(parsed)} receipts → {HTML_OUT} ({len(html):,} bytes)")
    except Exception as e:
        print(f"  ✗ Render failed: {e}")
        return 1

    print("=" * 60)
    print("✅ Spiral 25 done — fleet-organism-v4.html written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
