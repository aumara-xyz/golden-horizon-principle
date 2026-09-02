#!/usr/bin/env python3
"""Build the deterministic Round-4 artifact hash manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LAB = HERE.parent
OUT = HERE / "MANIFEST.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    paths = [
        LAB / "PREDICTIONS-codex-r4.md",
        LAB / "RESULTS-codex-r4.md",
        LAB / "LAB-SUMMARY.md",
    ]
    paths.extend(
        path
        for path in sorted(HERE.rglob("*"))
        if path.is_file()
        and path != OUT
        and "__pycache__" not in path.parts
    )
    rows = {}
    for path in paths:
        key = str(path.relative_to(LAB))
        rows[key] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    result = {
        "schema": "codex-r4-manifest-v1",
        "status": "MEASURED",
        "prediction_commits": {
            "R4.1": "c6f9358",
            "R4.2": "bbf37eb",
            "R4.3": "bff4c82",
            "R4.4": "d97797a",
        },
        "files": rows,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
