"""
spiral 02: setup/env gaps.

What environments/setups would let the substrate walker pattern BREW growth?
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or ".", "..", "recipes"))

from orchestra_call import call
from datetime import datetime


def main():
    print("=" * 60)
    print(f"Spiral 02 — Setup/Env gaps")
    print("=" * 60)

    prompt = """A fleet of AI agents works on the Quilt substrate walker pattern. Each agent commits to repos, runs substrates, and emits receipts. The witness chain links everything.

The agents include Mavis (substrate walker), kimi1 (arena referee), Casey (cartographer), Lucineer (synergetic).

The fleet runs in fresh sandboxes that wipe state. Tokens survive but the workspace rebuilds. There are 4775+ public repos on the SuperInstance GitHub account. The JEV oracle has 19+ wipe-rebuilds without snapshot.

What 5 setup/environment changes would let this fleet BREW growth instead of fighting resets? Be terse — one line each. Format as `- [change]: [why]`.
"""

    result = call("multimodal", prompt, max_tokens=400)
    if result["ok"]:
        print(f"\n✓ {result['api']} ({result['latency_ms']}ms):\n")
        print(result["response"])

        journal_path = os.path.join(os.path.dirname(__file__) or ".", "..", "journal", "02-env-gaps.md")
        with open(journal_path, "w") as f:
            f.write(f"# Spiral 02 — Setup/Env gaps\n\n")
            f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Source:** Gemini ({result['latency_ms']}ms)\n\n")
            f.write(result["response"])
            f.write("\n")
        print(f"\n  Saved to journal/02-env-gaps.md")


if __name__ == "__main__":
    main()
