#!/usr/bin/env python3
"""Reconcile plugin source strings with the editable pt-BR PO catalogs."""

from __future__ import annotations

import argparse
import configparser
import subprocess
import tempfile
import tokenize
from pathlib import Path


KEYWORDS = [
    "_",
    "msg_status",
    "dlg_input",
    "dlg_menu",
    "dlg_custom",
    "pgettext:1c,2",
]


def module_name(install_file: Path) -> str | None:
    for line in install_file.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if line.startswith("subdir="):
            return line.partition("=")[2].strip()
    return None


def decoded_source(path: Path) -> str:
    raw = path.read_bytes()
    try:
        encoding, _ = tokenize.detect_encoding(iter(raw.splitlines(keepends=True)).__next__)
    except (SyntaxError, UnicodeDecodeError):
        encoding = "latin-1"
    return raw.decode(encoding, errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--addons", type=Path, default=Path("CudaText_addons"))
    args = parser.parse_args()
    plugins = args.addons / "plugin"
    po_dir = args.addons / "langpy" / "extras"
    po_dir.mkdir(parents=True, exist_ok=True)
    created = merged = skipped = 0

    with tempfile.TemporaryDirectory(prefix="cudatext-po-") as temp_name:
        temp_root = Path(temp_name)
        for install_file in sorted(plugins.glob("*/install.inf")):
            module = module_name(install_file)
            if not module or module.startswith("cuda_ftp_libs_") or module == "pywin32":
                skipped += 1
                continue
            source_dir = install_file.parent
            normalized = temp_root / module
            normalized.mkdir(parents=True, exist_ok=True)
            source_files = []
            for source in sorted(source_dir.rglob("*.py")):
                target = normalized / source.relative_to(source_dir)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(decoded_source(source), encoding="utf-8")
                source_files.append(target)
            if not source_files:
                skipped += 1
                continue

            pot = temp_root / f"{module}.pot"
            command = [
                "xgettext",
                "--from-code=UTF-8",
                "--language=Python",
                *[f"--keyword={keyword}" for keyword in KEYWORDS],
                f"--output={pot}",
                *(str(source) for source in source_files),
            ]
            result = subprocess.run(command, text=True, capture_output=True)
            if result.returncode != 0 or not pot.exists():
                skipped += 1
                continue
            if pot.read_text(encoding="utf-8", errors="replace").count("\nmsgid ") == 0:
                skipped += 1
                continue

            po = po_dir / f"{module}.po"
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

    print(f"catálogos criados: {created}")
    print(f"catálogos atualizados: {merged}")
    print(f"plugins ignorados: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
