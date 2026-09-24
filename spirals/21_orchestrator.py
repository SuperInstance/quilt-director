"""Spiral 21 — brew quilt-orchestrator (DAG composer walker)."""
import os, sys, shutil, subprocess
sys.path.insert(0, "/workspace/repos/quilt-brewer/src")
sys.path.insert(0, "/workspace/repos/quilt-schema-registry/src")
from quilt_brewer import brew

target = "/workspace/repos/quilt-orchestrator"
if os.path.exists(target):
    shutil.rmtree(target)

result = brew("quilt-orchestrator", target)
print(f"  ok={result['ok']}  files={len(result['files_written'])}  tests={result['tests_pass']}/{result['tests_total']}  schema={result['schema_compliant']}")

# Run the demo
demo = subprocess.run(
    [sys.executable, os.path.join(target, "examples", "demo.py")],
    capture_output=True, text=True, timeout=15, env={
        **os.environ, "PYTHONPATH": os.path.join(target, "src"),
    },
)
print(demo.stdout.split("\n")[-3] if demo.returncode == 0 else f"  Demo FAILED: {demo.stderr}")

# Run tests
r = subprocess.run(
    [sys.executable, "-m", "unittest", "tests.test_dag"],
    capture_output=True, text=True, cwd=target, env={
        **os.environ, "PYTHONPATH": os.path.join(target, "src"),
    },
)
print(f"  Tests: {r.stdout.split(chr(10))[-3]}")
print("✅ Spiral 21 done — quilt-orchestrator brewed")
