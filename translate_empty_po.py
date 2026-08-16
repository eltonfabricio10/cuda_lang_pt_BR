#!/usr/bin/env python3
"""Fill empty gettext translations with reviewed-machine-translation drafts."""

from __future__ import annotations

import ast
import json
import re
import sys
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


API = "https://translate.googleapis.com/translate_a/single"
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[a-zA-Z]|\{[^{}]*\}|\\n|\n")


def po_value(lines: list[str], start: int, field: str) -> tuple[str, int]:
    value = ast.literal_eval(lines[start][len(field) :].strip())
    end = start + 1
    while end < len(lines) and lines[end].startswith('"'):
        value += ast.literal_eval(lines[end])
        end += 1
    return value, end


def protect(text: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def repl(match: re.Match[str]) -> str:
        token = f"XPH{len(saved)}X"
        saved.append(match.group(0))
        return token

    return PLACEHOLDER.sub(repl, text), saved


def translate(text: str) -> str | None:
    if not re.search(r"[A-Za-zÀ-ÿ]", text) or len(text) > 4500:
        return None
    leading = re.match(r"\s*", text).group(0)
    trailing = re.search(r"\s*$", text).group(0)
    core = text[len(leading) : len(text) - len(trailing) if trailing else len(text)]
    protected, placeholders = protect(core)
    query = urlencode({"client": "gtx", "sl": "en", "tl": "pt", "dt": "t", "q": protected})
    try:
        with urlopen(f"{API}?{query}", timeout=20) as response:
            data = json.load(response)
        time.sleep(0.05)
        result = "".join(part[0] for part in data[0] if part and part[0])
    except Exception:
        return None
    for index, original in enumerate(placeholders):
        result = result.replace(f"XPH{index}X", original)
    if placeholders and any(original not in result for original in placeholders):
        return None
    return leading + result.strip() + trailing


def process(path: Path) -> tuple[Path, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    changes: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("msgid "):
            i += 1
            continue
        msgid, id_end = po_value(lines, i, "msgid ")
        if not msgid or id_end >= len(lines) or not lines[id_end].startswith("msgstr "):
            i = id_end
            continue
        msgstr, str_end = po_value(lines, id_end, "msgstr ")
        repair = msgstr and (
            msgid.startswith("\n") != msgstr.startswith("\n")
            or msgid.endswith("\n") != msgstr.endswith("\n")
            or msgid[:1].isspace() != msgstr[:1].isspace()
            or msgid[-1:].isspace() != msgstr[-1:].isspace()
        )
        if msgstr and not repair:
            i = str_end
            continue
        result = translate(msgid)
        if result:
            encoded = json.dumps(result, ensure_ascii=False)
            changes.append((id_end, str_end, f"msgstr {encoded}"))
        i = str_end
    for start, end, replacement in reversed(changes):
        lines[start:end] = [replacement]
    if changes:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path, len(changes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only")
    args = parser.parse_args()
    paths = sorted(Path("CudaText_addons/langpy/extras").glob(args.only or "*.po"))
    total = 0
    with ThreadPoolExecutor(max_workers=3 if args.only else 8) as pool:
        futures = [pool.submit(process, path) for path in paths]
        for future in as_completed(futures):
            path, count = future.result()
            if count:
                print(f"{path.name}: {count}")
                total += count
    print(f"traduções automáticas rascunhadas: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
