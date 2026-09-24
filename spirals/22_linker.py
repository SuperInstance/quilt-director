"""Spiral 22 — brew quilt-linker (graph linker walker)."""
import os, sys, shutil, subprocess
sys.path.insert(0, "/workspace/repos/quilt-brewer/src")
sys.path.insert(0, "/workspace/repos/quilt-schema-registry/src")
from quilt_brewer import brew

target = "/workspace/repos/quilt-linker"
if os.path.exists(target):
    shutil.rmtree(target)

result = brew("quilt-linker", target)
print(f"  ok={result['ok']}  files={len(result['files_written'])}  tests={result['tests_pass']}/{result['tests_total']}  schema={result['schema_compliant']}")

demo = subprocess.run(
    [sys.executable, os.path.join(target, "examples", "demo.py")],
    capture_output=True, text=True, timeout=15, env={
        **os.environ, "PYTHONPATH": os.path.join(target, "src"),
    },
)
print(demo.stdout.split("\n")[-3] if demo.returncode == 0 else f"  Demo FAILED: {demo.stderr}")
