"""Canonical receipt ledger for quilt-director — family recipe port.

Ported from SuperInstance/quilt-executor (executor/ledger.py), same recipe as
laya4quilt / tagseq2tagseq4quilt / gpu_bpe4quilt: canonical JSON (sorted keys,
compact, UTF-8) + FNV-1a-64 hash chain. Any family substrate verifies our rows.

One row per director event: spiral runs (EFFECT), typed refusals (REFUSED —
never silent), periodic ticks (TICK). Tamper = loud refusal at verify().
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
FNV_MASK = 0xFFFFFFFFFFFFFFFF
GENESIS = "0" * 16


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & FNV_MASK
    return h


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_hash(obj: Any) -> str:
    return f"{fnv1a64(canonical(obj).encode('utf-8')):016x}"


@dataclass
class ReceiptRow:
    seq: int
    prev_hash: str
    kind: str  # BIND | EFFECT | REFUSED | TICK
    body: dict
    row_hash: str = ""

    def seal(self) -> None:
        self.row_hash = canonical_hash(
            {"seq": self.seq, "prev": self.prev_hash, "kind": self.kind, "body": self.body}
        )


class Ledger:
    """Append-only hash-chained receipt log. Tamper = loud refusal at verify."""

    def __init__(self, name: str = "director"):
        self.name = name
        self.rows: list[ReceiptRow] = []
        self.actor: dict[str, Any] = {}

    @property
    def head(self) -> str:
        return self.rows[-1].row_hash if self.rows else GENESIS

    @property
    def seq(self) -> int:
        return len(self.rows)

    def _append(self, kind: str, body: dict) -> ReceiptRow:
        row = ReceiptRow(seq=self.seq, prev_hash=self.head, kind=kind, body=body)
        row.seal()
        self.rows.append(row)
        return row

    def bind(self, **actor) -> ReceiptRow:
        """Anchor the ledger to an actor/environment description."""
        self.actor = dict(actor)
        return self._append("BIND", {"actor": self.actor})

    def effect(self, **body) -> ReceiptRow:
        """A completed operation (e.g. a spiral ran and journaled)."""
        return self._append("EFFECT", body)

    def refused(self, refusal_type: str, **body) -> ReceiptRow:
        """A typed absence — hash-committed, never silent.

        refusal_type examples: journal_missing, spiral_crashed, api_absent,
        out_of_scope. The type is first-class so crosschecks can group them.
        """
        return self._append("REFUSED", {"refusal_type": refusal_type, **body})

    def tick(self, **body) -> ReceiptRow:
        """Periodic heartbeat row (cron crosscheck anchor)."""
        return self._append("TICK", body)

    # -- persistence -----------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "actor": self.actor,
            "rows": [
                {
                    "seq": r.seq,
                    "prev": r.prev_hash,
                    "kind": r.kind,
                    "body": r.body,
                    "hash": r.row_hash,
                }
                for r in self.rows
            ],
        }

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for r in self.rows:
                f.write(
                    canonical(
                        {
                            "seq": r.seq,
                            "prev": r.prev_hash,
                            "kind": r.kind,
                            "body": r.body,
                            "hash": r.row_hash,
                        }
                    )
                    + "\n"
                )

    @classmethod
    def load(cls, path: str) -> "Ledger":
        led = cls()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                led.rows.append(
                    ReceiptRow(
                        seq=d["seq"],
                        prev_hash=d["prev"],
                        kind=d["kind"],
                        body=d["body"],
                        row_hash=d["hash"],
                    )
                )
        binds = [r for r in led.rows if r.kind == "BIND"]
        led.actor = binds[-1].body.get("actor", {}) if binds else {}
        led.name = led.actor.get("ledger", "director")
        return led

    def verify(self) -> list[str]:
        """Re-derive the chain. Returns a list of problems (empty = clean)."""
        problems: list[str] = []
        prev = GENESIS
        for i, r in enumerate(self.rows):
            want = canonical_hash(
                {"seq": r.seq, "prev": r.prev_hash, "kind": r.kind, "body": r.body}
            )
            if r.seq != i:
                problems.append(f"row {i}: seq {r.seq} != position {i}")
            if r.prev_hash != prev:
                problems.append(
                    f"row {i} ({r.kind}): prev {r.prev_hash} != chain head {prev}"
                )
            if r.row_hash != want:
                problems.append(f"row {i} ({r.kind}): hash {r.row_hash} != re-derived {want}")
            prev = r.row_hash
        return problems
