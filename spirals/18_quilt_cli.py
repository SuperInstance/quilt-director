"""
spiral 18: design the unified 'quilt' CLI.

The fleet has 10 repos. Currently you use each one separately:
- python3 -m quilt_bootstrap --mode full
- python3 -m quilt_brewer brew <recipe> <dest>
- python3 -m quilt_trace <receipts.jsonl>
- python3 -m quilt_fleet_snapshot build
- python3 -m quilt_schema_registry ...

What if there was ONE command that did it all?

    quilt bootstrap    # bring up the fleet
    quilt brew         # grow a new walker
    quilt trace        # render receipts as HTML
    quilt snapshot     # bake state into tarball
    quilt schema       # validate receipts
    quilt org          # render the fleet organism view
    quilt status       # show fleet state
    quilt serve        # serve the landing pages
    quilt new recipe   # scaffold a new recipe

This is the SUBSTRATE WALKER at the command layer.
"""
import os
import sys


def main():
    print("\n🌱 Spiral 18 — Design the unified 'quilt' CLI")
    print("=" * 60)

    # The unified command surface
    commands = {
        "bootstrap": {
            "module": "quilt_bootstrap",
            "purpose": "Bring up the Quilt fleet in a fresh sandbox",
            "subcommands": ["minimal", "full", "demo", "status"],
        },
        "brew": {
            "module": "quilt_brewer",
            "purpose": "Grow new substrate walkers from recipes",
            "subcommands": ["<recipe>", "--list", "--from-file"],
        },
        "trace": {
            "module": "quilt_tracer",
            "purpose": "Render any substrate walker's witness chain as HTML",
            "subcommands": ["<source.jsonl>", "--out FILE", "--title"],
        },
        "snapshot": {
            "module": "quilt_fleet_snapshot",
            "purpose": "Bake the fleet state into a portable tarball",
            "subcommands": ["build", "verify", "restore"],
        },
        "schema": {
            "module": "quilt_schema_registry",
            "purpose": "Validate receipts and chain against canonical envelope",
            "subcommands": ["validate <receipt>", "register", "list", "compliance"],
        },
        "organism": {
            "purpose": "Render the fleet organism view (composed across walkers)",
            "subcommands": ["v1", "v2", "v3", "jev"],
        },
        "status": {
            "purpose": "Show fleet state — what's installed, what's missing",
            "subcommands": [],
        },
        "serve": {
            "purpose": "Serve the landing pages on a local port",
            "subcommands": ["--port"],
        },
        "version": {
            "purpose": "Show the quilt CLI version + fleet inventory",
            "subcommands": [],
        },
    }

    print(f"\n[The unified quilt CLI — {len(commands)} commands]\n")
    for cmd, info in commands.items():
        subs = ", ".join(info["subcommands"][:3]) if info["subcommands"] else "—"
        print(f"  quilt {cmd:11}  {info['purpose']}")
        print(f"  {'':13}  Subcommands: {subs}")

    # Where this lives
    print(f"\n[Where this would live]")
    print(f"  /workspace/repos/quilt-cli/quilt_cli/__main__.py")
    print(f"  Or: a thin wrapper around the fleet's existing modules")

    # The implementation would be ~199 LOC, calling each module
    print(f"\n[Implementation pattern]")
    print(f"  Each subcommand is a thin wrapper:")
    print(f"    'quilt bootstrap --mode full' → python3 -m quilt_bootstrap")
    print(f"    'quilt brew <recipe>'        → python3 -m quilt_brewer")
    print(f"    'quilt trace receipts.jsonl' → python3 -m quilt_trace")
    print(f"  Glue: a single argparse dispatcher that fans out to the fleet")

    # Why this matters
    print(f"\n[Why this matters]")
    print(f"  The substrate walker pattern is now CONSUMABLE.")
    print(f"  A new developer types 'quilt status' and sees the fleet.")
    print(f"  Type 'quilt bootstrap --mode full' and the pattern is online.")
    print(f"  Type 'quilt brew <recipe>' and a new walker is born.")

    print("\n" + "=" * 60)
    print("✅ Unified CLI designed — ready for spiral 19 to ship")
    print("=" * 60)


if __name__ == "__main__":
    main()
