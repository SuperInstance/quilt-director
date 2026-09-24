"""Spiral 20 — brew quilt-fable from the brewer's recipe.

quilt-fable is a multi-voice narrative walker that takes a topic
and emits a 3-voice chord (narrator/lyricist/structuralist) in
3 output forms (prose/poem/doctrine).
"""
import os
import sys
import shutil
import subprocess

sys.path.insert(0, "/workspace/repos/quilt-brewer/src")
sys.path.insert(0, "/workspace/repos/quilt-schema-registry/src")

from quilt_brewer import brew


def main():
    print("\n🌱 Spiral 20 — Brew quilt-fable")
    print("=" * 60)

    target = "/workspace/repos/quilt-fable"

    if os.path.exists(target):
        print(f"  Removing old {target}")
        shutil.rmtree(target)

    result = brew("quilt-fable", target)
    print(f"  ok={result['ok']}")
    if result.get("error"):
        print(f"  ERROR: {result['error']}")
        return 1

    print(f"  Files written: {len(result['files_written'])}")
    for f in result["files_written"]:
        print(f"    • {f}")
    print(f"  Tests: {result['tests_pass']}/{result['tests_total']} pass")
    print(f"  Schema compliant: {result['schema_compliant']}")

    # Install in editable mode
    print("\n  Installing quilt-fable editable...")
    p = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", target,
         "--quiet", "--no-deps", "--break-system-packages"],
        capture_output=True, text=True, timeout=60,
    )

    # Run the demo
    print("\n  Running demo...")
    demo = subprocess.run(
        [sys.executable, os.path.join(target, "examples", "demo.py")],
        capture_output=True, text=True, timeout=15, env={
            **os.environ, "PYTHONPATH": os.path.join(target, "src"),
        },
    )
    print(demo.stdout)
    if demo.returncode != 0:
        print(f"  Demo FAILED: {demo.stderr}")

    print("=" * 60)
    print("✅ Spiral 20 done — quilt-fable brewed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
