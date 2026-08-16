#!/usr/bin/env python3
"""Generate PO sources from already downloaded registered plugin sources."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


KEYWORDS = ["_", "msg_status", "dlg_input", "dlg_menu", "dlg_custom"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("langpy/extras"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for source in sorted(args.sources.iterdir()):
        if not source.is_dir() or source.name.startswith("cuda_ftp_libs_"):
            continue
        output = args.output_dir / f"{source.name}.po"
        if output.exists():
            continue
        files = sorted(source.rglob("*.py"))
        if not files:
            continue
        command = [
            "xgettext",
            "--from-code=UTF-8",
            "--language=Python",
            *[f"--keyword={keyword}" for keyword in KEYWORDS],
            f"--output={output}",
            *(str(path) for path in files),
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            if output.exists():
                output.unlink()
            print(f"ignorado (xgettext): {source.name}")
            continue
        if not output.exists():
            continue
        text = output.read_text(encoding="utf-8")
        text = text.replace("charset=CHARSET", "charset=UTF-8")
        text = text.replace(str(args.sources) + "/", "./")
        output.write_text(text, encoding="utf-8")
        if text.count("\nmsgid ") == 0:
            output.unlink()
            continue
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
