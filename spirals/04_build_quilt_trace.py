"""
spiral 04: build quilt-trace — witness chain visualizer + organism landing page.

This is the missing piece that lets the organism SEE itself. Visualize the
witness chain, show what substrates composed, show the memes/canon.

The substrate walker pattern at visualization layer:
  - 199 LOC Python wrapper (fetch + aggregate + render data)
  - 130 LOC tests
  - 50 LOC demo
  + A landing page (HTML/CSS/JS) that shows the organism in motion

Token-aware: build the wrapper in plain Python, no API calls needed for the core.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "recipes"))

from orchestra_call import call
from datetime import datetime
import json


def main():
    print("=" * 60)
    print(f"Spiral 04 — Build quilt-trace")
    print("=" * 60)

    # Design the spec via Gemini (one short call)
    prompt = """Design a tiny Python library called quilt-trace that:
1. Reads receipts from any substrate walker (quilt-seed CellReceipt, quilt-optimization OptimizationReceipt, quilt-organism OrganismReceipt, or any with prev_witness_id + witness_id + polarity)
2. Aggregates by polarity (ACCEPT/DRIFT/REFUSE counts)
3. Builds a JSON graph: nodes = receipts, edges = prev_witness_id chains
4. Outputs a self-contained HTML file with embedded JS for D3.js rendering of the chain

The HTML should show:
- Chain head (latest witness_id)
- Polarity histogram (3 bars)
- Top 10 most-cited items
- Substrate breakdown (which substrates emitted how many receipts)
- The chain itself as a force-directed graph

Output ONLY: name, files, ~200 LOC budget, key design choices. No preamble.
"""

    result = call("multimodal", prompt, max_tokens=400)
    if result["ok"]:
        print(f"\n✓ {result['api']} ({result['latency_ms']}ms):\n")
        print(result["response"])

        # Save the design
        journal_dir = os.path.join(os.path.dirname(__file__) or ".", "..", "journal")
        journal_path = os.path.join(journal_dir, "04-quilt-trace-design.md")
        with open(journal_path, "w") as f:
            f.write(f"# Spiral 04 — quilt-trace design\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Source:** Gemini ({result['latency_ms']}ms)\n\n")
            f.write(result["response"])
            f.write("\n")
        print(f"\n  Saved to {journal_path}")


if __name__ == "__main__":
    main()
