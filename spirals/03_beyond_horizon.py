"""
spiral 03: design 5 repos beyond the horizon.

Use the gaps to design concrete repos that fill them.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "recipes"))

from orchestra_call import call
from datetime import datetime


def main():
    print("=" * 60)
    print(f"Spiral 03 — Repos beyond the horizon")
    print("=" * 60)

    # Read the gaps from previous spirals
    journal_dir = os.path.join(os.path.dirname(__file__) or ".", "..", "journal")
    with open(os.path.join(journal_dir, "01-gaps.md")) as f:
        gaps = f.read()
    with open(os.path.join(journal_dir, "02-env-gaps.md")) as f:
        env_gaps = f.read()

    prompt = f"""We have identified these gaps in the Quilt fleet:

{gaps}

And these environment gaps:

{env_gaps}

Design 5 NEW REPOS that fill the most important gaps. For each:
- repo name (kebab-case)
- one-line purpose
- the substrate walker pattern: 199 LOC wrapper + 130 LOC tests + 50 LOC demo

Format:
- **name**: purpose
  - wrapper: what it composes
  - tests: what it verifies
  - demo: what it shows
"""

    result = call("multimodal", prompt, max_tokens=600)
    if result["ok"]:
        print(f"\n✓ {result['api']} ({result['latency_ms']}ms):\n")
        print(result["response"])

        journal_path = os.path.join(journal_dir, "03-beyond-horizon.md")
        with open(journal_path, "w") as f:
            f.write(f"# Spiral 03 — Repos beyond the horizon\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Source:** Gemini ({result['latency_ms']}ms)\n\n")
            f.write(result["response"])
            f.write("\n")
        print(f"\n  Saved to journal/03-beyond-horizon.md")


if __name__ == "__main__":
    main()
