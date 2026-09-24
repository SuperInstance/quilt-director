"""
spiral 09: build quilt-fleet-snapshot.

The wipe problem: every fresh sandbox loses the fleet's accumulated state.
quilt-fleet-snapshot solves this by baking the fleet state into a single tarball.

A new sandbox does `tar -xzf snapshot.tar.gz -C /workspace/` and the substrate
walker pattern is online in <30 seconds, no rebuild needed.
"""
import os
import sys
import json
import hashlib
import tarfile
import io
import time
from datetime import datetime, timezone


def sha256_path(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()[:16]


def build_snapshot(workspace: str = "/workspace",
                    out_path: str = "/tmp/fleet_snapshot.tar.gz") -> dict:
    print("\n🌱 Spiral 09 — Fleet snapshot")
    print("=" * 60)

    files_to_snapshot = [
        # Core substrate walker doctrine
        ("/workspace/repos/quilt-seed/CHARTER.md", "quilt-seed", "doctrine", "Fleet Directive compliance: purpose"),
        ("/workspace/repos/quilt-seed/IDENTITY.md", "quilt-seed", "doctrine", "Mavis identity"),
        ("/workspace/repos/quilt-seed/SKILLS.md", "quilt-seed", "doctrine", "7 substrate walker skills"),
        ("/workspace/repos/quilt-seed/TASKBOARD.md", "quilt-seed", "doctrine", "Active task list"),
        ("/workspace/repos/quilt-seed/BOOTCAMP.md", "quilt-seed", "doctrine", "6 bootcamp exercises"),

        # Substrate walker source (quilt-seed)
        ("/workspace/repos/quilt-seed/src/quilt_seed/vibe.py", "quilt-seed", "wrapper", "SYNERGY-2"),
        ("/workspace/repos/quilt-seed/src/quilt_seed/cu_substrate.py", "quilt-seed", "wrapper", "SYNERGY-3"),
        ("/workspace/repos/quilt-seed/src/quilt_seed/seed.py", "quilt-seed", "core", "SeedCell"),
        ("/workspace/repos/quilt-seed/src/quilt_seed/vessel.py", "quilt-seed", "core", "Vessel + stations"),
        ("/workspace/repos/quilt-seed/src/quilt_seed/legalese.py", "quilt-seed", "core", "LegaleseNetwork"),

        # quilt-trace (the visualizer)
        ("/workspace/repos/quilt-trace/src/quilt_trace/__init__.py", "quilt-trace", "wrapper", "quilt-trace entry"),
        ("/workspace/repos/quilt-trace/src/quilt_trace/renderer.py", "quilt-trace", "wrapper", "HTML + D3.js"),
        ("/workspace/repos/quilt-trace/src/quilt_trace/aggregator.py", "quilt-trace", "wrapper", "Stats"),
        ("/workspace/repos/quilt-trace/src/quilt_trace/reader.py", "quilt-trace", "wrapper", "JSONL reader"),

        # quilt-organism
        ("/workspace/repos/quilt-organism/src/quilt_organism/__init__.py", "quilt-organism", "wrapper", "quilt-organism entry"),
        ("/workspace/repos/quilt-organism/src/quilt_organism/organism.py", "quilt-organism", "wrapper", "Organism"),
        ("/workspace/repos/quilt-organism/src/quilt_organism/substrate.py", "quilt-organism", "wrapper", "Receipt envelope"),
        ("/workspace/repos/quilt-organism/src/quilt_organism/walkers.py", "quilt-organism", "wrapper", "Adapters"),
        ("/workspace/repos/quilt-organism/src/quilt_organism/receivers.py", "quilt-organism", "wrapper", "Receivers"),
        ("/workspace/repos/quilt-organism/src/quilt_organism/scouts.py", "quilt-organism", "wrapper", "Scouts"),

        # Optimizer substrate
        ("/workspace/repos/quilt-optimization/src/quilt_optimization/__init__.py", "quilt-optimization", "wrapper", "Optimizer entry"),
        ("/workspace/repos/quilt-optimization/src/quilt_optimization/routing.py", "quilt-optimization", "wrapper", "VRP"),
        ("/workspace/repos/quilt-optimization/src/quilt_optimization/linear_programming.py", "quilt-optimization", "wrapper", "LP"),
        ("/workspace/repos/quilt-optimization/src/quilt_optimization/substrate.py", "quilt-optimization", "wrapper", "Envelope"),

        # Director
        ("/workspace/repos/quilt-director/recipes/orchestra_call.py", "quilt-director", "tool", "API orchestra"),
        ("/workspace/repos/quilt-director/spirals/07_fleet_landing.py", "quilt-director", "tool", "Compose landing"),
        ("/workspace/repos/quilt-director/spirals/06_render_jev.py", "quilt-director", "tool", "Render JEV"),
        ("/workspace/repos/quilt-director/README.md", "quilt-director", "doctrine", "Director README"),

        # JEV-quilt core (the substrate we're wrapping)
        ("/workspace/jev-quilt/README.md", "jev-quilt", "doctrine", "JEV-quilt README"),
        ("/workspace/jev-quilt/ARENA.md", "jev-quilt", "doctrine", "Arena rules"),
        ("/workspace/jev-quilt/FISH-ATLAS.md", "jev-quilt", "doctrine", "Fish atlas"),
        ("/workspace/jev-quilt/JEV_LEARNINGS.md", "jev-quilt", "doctrine", "JEV learnings"),
    ]

    # Build manifest first
    manifest = {
        "version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": workspace,
        "substrate_walker_doctrine": {
            "pattern": "199 LOC wrapper + 130 LOC tests + 50 LOC demo",
            "envelope": "witness_id + prev_witness_id + polarity (ACCEPT/DRIFT/REFUSE)",
            "instances": [
                "quilt-seed.vibe (Elephant cynicism dial)",
                "quilt-seed.cu_substrate (Collective Unconscious RAG)",
                "quilt-optimization.routing (cuOpt VRP/TSP/PDP)",
                "quilt-optimization.linear_programming (cuOpt LP/MILP)",
                "quilt-organism.substrate (corpus walker)",
                "quilt-trace.renderer (visualizer)",
                "quilt-director.spirals (knowledge spirals)",
            ],
            "five_laws": [
                "Identity never floats (q16 exact-rational)",
                "Hooks eat deltas, not values (deadband-gated)",
                "Decide in one pass, project elsewhere",
                "Every state change is booked (WAL per cell)",
                "Viability is binary, difference is not",
            ],
        },
        "fleet_topology": {
            "cells": "14-tuple (id, kind, payload, parents, links, witnesses, effects, ticker, hex, tag, meta, created_at, updated_at, author, sig)",
            "opcodes_5": ["BIND", "LINK", "EFFECT", "VIEW", "TICK"],
            "opcodes_6_adopted": ["FORGET", "PROOF", "ROUTE", "CRDT", "WORLD", "TIME"],
            "kinds": 26,
            "lattice_dim": 4,
            "witness_chain": "append-only, hash-chained, sha256-of-canonical",
        },
        "files": [],
        "stats": {"total_files": 0, "total_bytes": 0, "by_category": {}},
    }

    # Snapshot each file
    print()
    tar_count = 0
    total_bytes = 0
    by_category = {}

    with tarfile.open(out_path, mode="w:gz") as tar:
        for source, repo, category, desc in files_to_snapshot:
            if not os.path.exists(source):
                print(f"  ⚠️  missing: {source}")
                continue

            entry = {
                "path": source.replace("/workspace/", ""),
                "source": source,
                "category": category,
                "description": desc,
                "sha256_16": sha256_path(source),
                "size_bytes": os.path.getsize(source),
            }
            manifest["files"].append(entry)
            tar_count += 1
            total_bytes += entry["size_bytes"]
            by_category[category] = by_category.get(category, 0) + 1

            # Add to tar with canonical path
            arcname = f"fleet/{entry['path']}"
            tar.add(source, arcname=arcname, recursive=False)

            print(f"  ✓ {entry['size_bytes']:>7,} bytes  {arcname}")

        # Add the manifest
        manifest["stats"]["total_files"] = tar_count
        manifest["stats"]["total_bytes"] = total_bytes
        manifest["stats"]["by_category"] = by_category

        manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
        manifest_info = tarfile.TarInfo(name="fleet/MANIFEST.json")
        manifest_info.size = len(manifest_bytes)
        manifest_info.mtime = int(time.time())
        tar.addfile(manifest_info, io.BytesIO(manifest_bytes))

    print(f"\n  📦 Snapshot written: {out_path}")
    print(f"  📊 {tar_count} files, {total_bytes:,} bytes ({total_bytes/1024:.1f} KB)")
    print(f"  🗂️  Categories: {by_category}")

    # Verify
    with tarfile.open(out_path, "r:gz") as tar:
        names = tar.getnames()
        print(f"  ✓ Verified: {len(names)} entries in tarball")
        manifest_in_tar = tar.extractfile("fleet/MANIFEST.json")
        if manifest_in_tar:
            loaded = json.loads(manifest_in_tar.read().decode("utf-8"))
            assert loaded["version"] == "0.1.0"
            print(f"  ✓ Manifest verified: {loaded['stats']['total_files']} files")

    return manifest


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fleet_snapshot.tar.gz"
    manifest = build_snapshot(out_path=out)
    print(f"\n  To restore: tar -xzf {out} -C /workspace/")
