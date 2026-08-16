#!/usr/bin/env python3
"""Merge gettext strings found in the Python sources shipped with langmenu."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


KEYWORDS = ["_", "msg_status", "dlg_input", "dlg_menu", "dlg_custom"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addons", type=Path, default=Path("CudaText_addons"))
    args = parser.parse_args()
    source_root = args.addons / "langmenu"
    po_root = args.addons / "langpy" / "extras"
    created = merged = 0

    with tempfile.TemporaryDirectory(prefix="cudatext-langmenu-po-") as temp:
        temp_root = Path(temp)
        for source_dir in sorted(p for p in source_root.iterdir() if p.is_dir()):
            files = sorted(source_dir.rglob("*.py"))
            if not files:
                continue
            pot = temp_root / f"{source_dir.name}.pot"
            result = subprocess.run(
                [
                    "xgettext",
                    "--from-code=UTF-8",
                    "--language=Python",
                    *[f"--keyword={keyword}" for keyword in KEYWORDS],
                    f"--output={pot}",
                    *(str(path) for path in files),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode or not pot.exists():
                continue
            if pot.read_text(encoding="utf-8", errors="replace").count("\nmsgid ") == 0:
                continue
            po = po_root / f"{source_dir.name}.po"
            if po.exists():
                subprocess.run(
                    ["msgmerge", "--update", "--no-fuzzy-matching", str(po), str(pot)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                merged += 1
            else:
                subprocess.run(
                    ["msginit", "--no-translator", "--locale=pt_BR", "-i", str(pot), "-o", str(po)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                )
                created += 1
    print(f"POs criados: {created}; POs atualizados: {merged}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
