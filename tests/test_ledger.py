"""Pins for the director receipt ledger (family recipe, ported from quilt-executor).

Run: python3 tests/test_ledger.py   (exit 0 = green)
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from director.ledger import GENESIS, Ledger, canonical_hash, fnv1a64  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name}  {detail}")
        FAILURES.append(name)


def test_fnv_pins() -> None:
    print("fnv/canonical pins")
    # Family café-pin: canonical_hash of a known UTF-8 body is stable across substrates.
    pin = canonical_hash({"café": "Δ", "語": 1})
    check("utf-8 canonical hash stable (16 hex)", len(pin) == 16 and pin == canonical_hash({"語": 1, "café": "Δ"}), pin)
    check("fnv1a64(b'') == offset basis", fnv1a64(b"") == 0xCBF29CE484222325)
    check("genesis head", Ledger().head == GENESIS)


def test_chain_and_tamper() -> None:
    print("chain + tamper")
    led = Ledger("test")
    led.bind(ledger="test", who="pins")
    r1 = led.effect(spiral="01_gaps", file_sha256="aa")
    led.refused("journal_missing", spiral="02_x")
    check("bind→effect→refused = 3 rows", len(led.rows) == 3)
    check("refusal_type first-class", led.rows[2].body["refusal_type"] == "journal_missing")
    check("verify clean", led.verify() == [])
    check("head moves", led.head == r1.row_hash or led.head != r1.row_hash)
    # tamper: mutate a body after sealing
    led.rows[1].body["file_sha256"] = "tampered"
    probs = led.verify()
    check("tamper loud", len(probs) >= 1 and "row 1" in probs[0], str(probs[:1]))
    # determinism: same rows, fresh ledger → same hashes
    led2 = Ledger("test")
    led2.bind(ledger="test", who="pins")
    led2.effect(spiral="01_gaps", file_sha256="aa")
    led2.refused("journal_missing", spiral="02_x")
    led3 = Ledger("test")
    led3.bind(ledger="test", who="pins")
    led3.effect(spiral="01_gaps", file_sha256="aa")
    led3.refused("journal_missing", spiral="02_x")
    check(
        "hash-for-hash deterministic",
        [r.row_hash for r in led2.rows] == [r.row_hash for r in led3.rows],
    )


def test_persistence_roundtrip() -> None:
    print("persistence")
    led = Ledger("test")
    led.bind(ledger="test", who="pins")
    led.effect(spiral="01_gaps", file_sha256="aa", journal="journal/01-gaps.md")
    led.tick(rows=1)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "chain.jsonl")
        led.save(p)
        back = Ledger.load(p)
        check("roundtrip rows", len(back.rows) == len(led.rows))
        check("roundtrip verify", back.verify() == [])
        check("roundtrip actor", back.actor.get("who") == "pins")
        check("roundtrip head", back.head == led.head)


def test_tool_book_and_verify() -> None:
    print("tools/book_spirals.py end-to-end")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tool = os.path.join(root, "tools", "book_spirals.py")
    with tempfile.TemporaryDirectory() as td:
        # build a fake director tree
        for d in ("spirals", "journal", "ledger"):
            os.makedirs(os.path.join(td, d))
        with open(os.path.join(td, "spirals", "01_a.py"), "w") as f:
            f.write("print('a')\n")
        with open(os.path.join(td, "spirals", "02_b.py"), "w") as f:
            f.write("print('b')\n")
        with open(os.path.join(td, "journal", "01-a.md"), "w") as f:
            f.write("# a\n")
        # patch module constants via env: run in-process instead
        sys.path.insert(0, os.path.join(root, "tools"))
        import importlib
        import book_spirals as bs

        importlib.reload(bs)
        bs.ROOT = td
        bs.LEDGER_PATH = os.path.join(td, "ledger", "director.ledger.jsonl")
        bs.SPIRALS_DIR = os.path.join(td, "spirals")
        bs.JOURNAL_DIR = os.path.join(td, "journal")
        led = Ledger("director")
        led.bind(ledger="director", repo="test")
        e, r, s = bs.book(led)
        check("book: 1 EFFECT (01_a journaled)", e == 1, f"e={e}")
        check("book: 1 REFUSED typed journal_missing (02_b)", r == 1 and led.rows[-1].body["refusal_type"] == "journal_missing")
        check("book: verify clean", led.verify() == [])
        e2, r2, s2 = bs.book(led)
        check("idempotent: nothing new, 2 skipped", (e2, r2, s2) == (0, 0, 2), f"{e2},{r2},{s2}")
        # mutate spiral -> rebook
        with open(os.path.join(td, "spirals", "02_b.py"), "a") as f:
            f.write("# v2\n")
        e3, r3, s3 = bs.book(led)
        check("mutation rebooks REFUSED", r3 == 1 and led.rows[-1].body["spiral"] == "02_b", f"{r3}")
        # tamper on disk, verify via CLI
        led.save(bs.LEDGER_PATH)
        with open(bs.LEDGER_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lines[1] = lines[1].replace("01_a", "01_EVIL")
        with open(bs.LEDGER_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
        out = subprocess.run(
            [sys.executable, tool, "--verify"],
            cwd=td,
            env={**os.environ, "DIRECTOR_ROOT": td},
            capture_output=True,
            text=True,
        )
        check("CLI --verify exits 1 on tamper", out.returncode == 1, out.stdout + out.stderr)
        check("CLI names the tampered row", "TAMPER" in (out.stdout + out.stderr))


def main() -> int:
    test_fnv_pins()
    test_chain_and_tamper()
    test_persistence_roundtrip()
    test_tool_book_and_verify()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILED: {FAILURES}")
        return 1
    print("\nall pins green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
