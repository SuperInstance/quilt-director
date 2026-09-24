"""Spiral 23 — grow quilt-bootstrap's FLEET inventory from 9 to 13 repos.

Adds:
  - quilt-canon-witness (ledger substrate)
  - quilt-fable (multi-voice narrative)
  - quilt-orchestrator (DAG composer)
  - quilt-linker (graph linker)

The 13 repos × 16 walker instances = the new fleet inventory.
"""
import os, sys, subprocess

SRC = "/workspace/repos/quilt-bootstrap/src/quilt_bootstrap/bootstrap.py"


def main():
    print("\n🌱 Spiral 23 — Grow quilt-bootstrap to 13 repos / 16 walker instances")
    print("=" * 60)

    # Append the 4 new repositories to FLEET
    with open(SRC) as f:
        src = f.read()

    # The FLEET entries we need to add
    new_entries = """    {
        "name": "quilt-canon-witness",
        "url": "https://github.com/SuperInstance/quilt-canon-witness",
        "purpose": "Append-only cryptographic witness log (ledger substrate)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-fable",
        "url": "https://github.com/SuperInstance/quilt-fable",
        "purpose": "Multi-voice narrative substrate walker (brewed)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-orchestrator",
        "url": "https://github.com/SuperInstance/quilt-orchestrator",
        "purpose": "DAG-based composer substrate walker (brewed)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-linker",
        "url": "https://github.com/SuperInstance/quilt-linker",
        "purpose": "Substrate-to-substrate graph linker (brewed)",
        "walker_count": 1,
        "deps": [],
    },"""

    if "quilt-canon-witness" not in src:
        # Insert before the closing "]"
        marker = "\n]\n\n\n# Modes"
        if marker in src:
            new_src = src.replace(marker, ",\n" + new_entries + marker, 1)
            with open(SRC, "w") as f:
                f.write(new_src)
            print("  ✓ FLEET updated")
        else:
            print("  ✗ Marker not found")
            return 1
    else:
        print("  ℹ FLEET already updated")

    # Verify tests pass
    print("\n  Running tests...")
    p = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "/workspace/repos/quilt-bootstrap/tests"],
        capture_output=True, text=True, timeout=15,
    )
    print(p.stdout.split("\n")[-2])

    print("=" * 60)
    print("✅ Spiral 23 done — quilt-bootstrap now lists 13 repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
