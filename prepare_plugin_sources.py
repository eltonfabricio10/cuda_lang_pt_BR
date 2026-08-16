#!/usr/bin/env python3
"""Baixa e extrai fontes de plugins selecionados do registry do CudaText."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REGISTRY_URL = (
    "https://raw.githubusercontent.com/Alexey-T/CudaText-registry/"
    "master/json/plugins.json"
)


def fetch_json(url: str) -> list[dict[str, object]]:
    request = urllib.request.Request(url, headers={"User-Agent": "cuda-lang-pt-br/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if not isinstance(data, list):
        raise ValueError(f"registry inválido: esperado lista em {url}")
    return [item for item in data if isinstance(item, dict)]


def safe_extract(archive: zipfile.ZipFile, destination: Path) -> None:
    root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"ZIP inseguro, caminho fora do destino: {member.filename}")
    archive.extractall(destination)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", action="append", required=True, help="módulo a preparar; pode repetir")
    parser.add_argument("--output-dir", type=Path, default=Path("CudaText_sources"))
    parser.add_argument("--registry-url", default=REGISTRY_URL)
    parser.add_argument("--keep-archives", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested = set(args.module)
    records = {str(item.get("module")): item for item in fetch_json(args.registry_url)}
    missing = sorted(requested - records.keys())
    if missing:
        print("módulos não encontrados no registry:", ", ".join(missing), file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cudatext-plugin-") as temp_name:
        temp_dir = Path(temp_name)
        for module in sorted(requested):
            url = str(records[module].get("url", ""))
            if not url.lower().endswith(".zip"):
                print(f"URL sem ZIP para {module}: {url}", file=sys.stderr)
                return 2

            archive_path = temp_dir / f"{module}.zip"
            print(f"baixando {module}")
            request = urllib.request.Request(url, headers={"User-Agent": "cuda-lang-pt-br/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response, archive_path.open("wb") as output:
                shutil.copyfileobj(response, output)

            destination = args.output_dir / module
            destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive_path) as archive:
                bad_file = archive.testzip()
                if bad_file is not None:
                    raise ValueError(f"ZIP corrompido para {module}: {bad_file}")
                safe_extract(archive, destination)

            if args.keep_archives:
                archives = args.output_dir / "_archives"
                archives.mkdir(parents=True, exist_ok=True)
                shutil.copy2(archive_path, archives / archive_path.name)

    print(f"fontes preparadas em {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
