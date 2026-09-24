"""Book one ledger row per spiral into ledger/director.ledger.jsonl.

Usage:
  python3 tools/book_spirals.py            # incremental: book new/CHANGED spirals
  python3 tools/book_spirals.py --verify   # re-derive chain; exit 1 on tamper
                                           # (cron/tick crosscheck — no rows added)

Semantics per spiral (spirals/NN_name.py + journal/NN-name.md):
  journal present  -> EFFECT row  {spiral, file_sha256, journal_sha256, bytes}
  journal missing  -> REFUSED row {refusal_type: journal_missing, spiral, file_sha256}
A spiral whose file_sha256 matches the last EFFECT/REFUSED row for that spiral
is unchanged: skipped (idempotent re-runs add nothing).

REFUSED rows are typed and hash-committed — absence is visible, never silent.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from director.ledger import Ledger  # noqa: E402

ROOT = os.environ.get(
    "DIRECTOR_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
LEDGER_PATH = os.path.join(ROOT, "ledger", "director.ledger.jsonl")
SPIRALS_DIR = os.path.join(ROOT, "spirals")
JOURNAL_DIR = os.path.join(ROOT, "journal")


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def spiral_number(path: str) -> int:
    m = re.match(r"(\d+)_", os.path.basename(path))
    return int(m.group(1)) if m else 0


def list_spirals() -> list[str]:
    if not os.path.isdir(SPIRALS_DIR):
        return []
    return sorted(
        (
            os.path.join(SPIRALS_DIR, f)
            for f in os.listdir(SPIRALS_DIR)
            if f.endswith(".py") and not f.startswith("_")
        ),
        key=spiral_number,
    )


def journal_for(spiral_path: str) -> str:
    """journal/NN-*.md for this spiral. The number is the spiral's identity —
    slugs drift (05_shipped → 05-shipped-quilt-trace.md, 06_render_jev →
    06-rendered-jev.md), so never derive the journal name from the slug."""
    num = spiral_number(spiral_path)
    if os.path.isdir(JOURNAL_DIR):
        matches = sorted(
            f for f in os.listdir(JOURNAL_DIR) if f.startswith(f"{num:02d}-") and f.endswith(".md")
        )
        if matches:
            return os.path.join(JOURNAL_DIR, matches[0])
    return os.path.join(JOURNAL_DIR, f"{num:02d}.md")


def last_row_for(led: Ledger, spiral: str) -> dict | None:
    for r in reversed(led.rows):
        if r.body.get("spiral") == spiral and r.kind in ("EFFECT", "REFUSED"):
            return r.body
    return None


def book(led: Ledger) -> tuple[int, int, int]:
    """Book rows for spirals not yet represented at their current hash.

    Returns (effected, refused, skipped).
    """
    effected = refused = skipped = 0
    for sp in list_spirals():
        name = os.path.splitext(os.path.basename(sp))[0]
        fhash = sha256_file(sp)
        prev = last_row_for(led, name)
        if prev and prev.get("file_sha256") == fhash:
            skipped += 1
            continue
        jp = journal_for(sp)
        if os.path.isfile(jp):
            led.effect(
                spiral=name,
                file_sha256=fhash,
                journal_sha256=sha256_file(jp),
                journal=os.path.relpath(jp, ROOT),
                bytes=os.path.getsize(sp),
            )
            effected += 1
        else:
            led.refused(
                "journal_missing",
                spiral=name,
                file_sha256=fhash,
                journal=os.path.relpath(jp, ROOT),
            )
            refused += 1
    return effected, refused, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true", help="check chain only; add nothing")
    args = ap.parse_args()

    if os.path.isfile(LEDGER_PATH):
        led = Ledger.load(LEDGER_PATH)
    else:
        led = Ledger("director")
        led.bind(
            ledger="director",
            repo="SuperInstance/quilt-director",
            recipe="canonical-json+fnv1a64 (quilt-executor family)",
        )

    if args.verify:
        problems = led.verify()
        effect_n = sum(1 for r in led.rows if r.kind == "EFFECT")
        refused_n = sum(1 for r in led.rows if r.kind == "REFUSED")
        print(f"verify: {len(led.rows)} rows ({effect_n} EFFECT, {refused_n} REFUSED)")
        if problems:
            for p in problems:
                print(f"  TAMPER: {p}")
            return 1
        print("verify: OK")
        return 0

    e, r, s = book(led)
    problems = led.verify()
    if problems:
        for p in problems:
            print(f"  TAMPER: {p}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    led.save(LEDGER_PATH)
    print(f"booked: {e} EFFECT, {r} REFUSED, {s} unchanged | head {led.head}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
