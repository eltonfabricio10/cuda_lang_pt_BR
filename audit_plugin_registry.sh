#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_URL="https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/plugins.json"

command -v curl >/dev/null 2>&1 || {
    echo "erro: curl não encontrado" >&2
    exit 1
}
command -v jq >/dev/null 2>&1 || {
    echo "erro: jq não encontrado" >&2
    exit 1
}

registry_modules="$(curl -fsSL "$REGISTRY_URL" | jq -r '.[].module' | sort -u)"
menu_modules="$(find "$ROOT_DIR/langmenu" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort -u)"
po_modules="$(find "$ROOT_DIR/langpy/extras" -maxdepth 1 -type f -name '*.po' -printf '%f\n' \
    | sed 's/\.po$//' | sed 's/-bkp$//' | sort -u)"
mo_modules="$(find "$ROOT_DIR/langpy/pt_BR/LC_MESSAGES" -maxdepth 1 -type f -name '*.mo' -printf '%f\n' \
    | sed 's/\.mo$//' | sort -u)"

printf '%s\n' "Plugins registrados: $(printf '%s\n' "$registry_modules" | sed '/^$/d' | wc -l)"
printf '%s\n' "Menus pt-BR locais: $(printf '%s\n' "$menu_modules" | sed '/^$/d' | wc -l)"
printf '%s\n' "Fontes PO locais: $(printf '%s\n' "$po_modules" | sed '/^$/d' | wc -l)"
printf '%s\n' "Catálogos MO locais: $(printf '%s\n' "$mo_modules" | sed '/^$/d' | wc -l)"

printf '%s\n' "--- registrados sem menu pt-BR ---"
comm -23 <(printf '%s\n' "$registry_modules") <(printf '%s\n' "$menu_modules")

printf '%s\n' "--- registrados sem fonte PO ---"
comm -23 <(printf '%s\n' "$registry_modules") <(printf '%s\n' "$po_modules")

printf '%s\n' "--- fontes PO sem catálogo MO ---"
comm -23 <(printf '%s\n' "$po_modules") <(printf '%s\n' "$mo_modules")
