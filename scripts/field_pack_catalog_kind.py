"""Published-card venue filter: zoo | both | aquarium | neither.

Source of truth: static/field-pack/data/card-kinds.tsv
A zoo kit may list kind=zoo or kind=both only.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CARD_KINDS_TSV = REPO / "static" / "field-pack" / "data" / "card-kinds.tsv"

ZOO_OK_KINDS = frozenset({"zoo", "both"})
AQUARIUM_ONLY_KIND = "aquarium"
NEITHER_KIND = "neither"


def load_card_kinds(path: Path | None = None) -> dict[str, dict[str, str]]:
    """slug → {title, hub, kind}."""
    src = path or CARD_KINDS_TSV
    rows: dict[str, dict[str, str]] = {}
    for i, line in enumerate(src.read_text(encoding="utf-8").splitlines()):
        if not line.strip() or (i == 0 and line.startswith("slug")):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            raise ValueError(f"bad card-kinds row: {line!r}")
        slug, title, hub, kind = (p.strip() for p in parts[:4])
        rows[slug] = {"title": title, "hub": hub, "kind": kind}
    return rows


def card_venue_kind(slug: str, kinds: dict[str, dict[str, str]] | None = None) -> str:
    table = kinds if kinds is not None else load_card_kinds()
    row = table.get(slug or "")
    return str((row or {}).get("kind") or "")


def card_ok_on_zoo_kit(slug: str, kinds: dict[str, dict[str, str]] | None = None) -> bool:
    return card_venue_kind(slug, kinds) in ZOO_OK_KINDS
