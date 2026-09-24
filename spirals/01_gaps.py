"""
spiral 01: identify gaps in the fleet.

Uses Gemini to reason about what the SuperInstance fleet has vs. what it needs.
Token-aware: short prompts, single call.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__) or ".") + "/recipes")

from orchestra_call import call
import json
from datetime import datetime


def main():
    print("=" * 60)
    print(f"Spiral 01 — Gaps in the fleet")
    print(f"  Date: {datetime.now().isoformat()}")
    print("=" * 60)

    # Context: what we have (from scouts)
    have = [
        "quilt-cell (basic cell, 14-tuple)",
        "quilt-seed (vessel, legalese, stations, fables, substrate walkers)",
        "quilt-optimization (cuOpt wrapper)",
        "quilt-organism (corpus walker, scouts, memoirs)",
        "quilt-cli (orchestra, scout, chord, holodeck commands)",
        "quilt-spreadsheet-inference (Holodeck, multi-LLM zoo)",
        "quilt-transformer-arena (adversarial GAN lane)",
        "jev-quilt (JEV oracle as substrate, 483 receipts)",
        "ai-writings (2786+ pieces corpus)",
        "quilt-pincher (TypeScript implementation)",
        "quilt-cell-harness, quilt-claw, quilt-c, quilt-rust, quilt-py (polyformalism)",
        "quilt-fluidics, quilt-fold (recent canon)",
        "quilt-jev-toolkit, micrograd-quilt, nexus-vessel, pong-quilt, profile-lane",
    ]

    prompt = f"""The Quilt fleet has these repos:
{chr(10).join('- ' + h for h in have)}

It's a substrate walker pattern (199 LOC wrapper + tests + demo). Each cell is a 14-tuple, the witness log is append-only, Mavis composes substrates.

What are 5 things the fleet DOES NOT HAVE but should, to compose the substrate walker pattern at the next layer? Be terse — one line each.

Format as: `- [name]: [one line why]`
"""

    result = call("multimodal", prompt, max_tokens=400)
    if result["ok"]:
        print(f"\n✓ {result['api']} ({result['latency_ms']}ms):\n")
        print(result["response"])

        # Save to journal
        journal_path = os.path.join(os.path.dirname(__file__) or ".", "..", "journal", "01-gaps.md")
        with open(journal_path, "w") as f:
            f.write(f"# Spiral 01 — Gaps in the fleet\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Source:** Gemini ({result['latency_ms']}ms)\n\n")
            f.write(f"## What we have\n\n")
            for h in have:
                f.write(f"- {h}\n")
            f.write(f"\n## What we don't have but should\n\n")
            f.write(result["response"])
            f.write("\n")
        print(f"\n  Saved to journal/01-gaps.md")
    else:
        print(f"  ✗ {result['error']}")


if __name__ == "__main__":
    main()
