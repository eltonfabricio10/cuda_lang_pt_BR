#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PO_DIR="$ROOT_DIR/langpy/extras"
MO_DIR="$ROOT_DIR/langpy/pt_BR/LC_MESSAGES"
PACKAGE="$ROOT_DIR/langpy/plugins-translations.pt_BR.zip"
TMP_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

command -v msgfmt >/dev/null 2>&1 || {
    echo "erro: msgfmt não encontrado" >&2
    exit 1
}
if command -v zip >/dev/null 2>&1; then
    ARCHIVER=zip
elif command -v 7z >/dev/null 2>&1; then
    ARCHIVER=7z
else
    echo "erro: zip ou 7z não encontrado" >&2
    exit 1
fi

mkdir -p "$MO_DIR"
rm -f "$MO_DIR"/*.mo

compiled=0
skipped=0

for po_file in "$PO_DIR"/*.po; do
    [ -e "$po_file" ] || continue
    name="$(basename "$po_file" .po)"

    # Arquivos de backup e catálogos sem nenhuma tradução não são distribuíveis.
    case "$name" in
        *-bkp)
            skipped=$((skipped + 1))
            continue
            ;;
    esac

    stats="$(msgfmt --statistics -o /dev/null "$po_file" 2>&1 || true)"
    if printf '%s\n' "$stats" | grep -Eq '(^| )0 translated message(s)?([,.]|$)'; then
        skipped=$((skipped + 1))
        continue
    fi

    msgfmt -o "$MO_DIR/$name.mo" "$po_file"
    cp "$MO_DIR/$name.mo" "$TMP_DIR/$name.mo"
    compiled=$((compiled + 1))
done

mkdir -p "$TMP_DIR/pt_BR/LC_MESSAGES"
cp "$MO_DIR"/*.mo "$TMP_DIR/pt_BR/LC_MESSAGES/"
cp "$ROOT_DIR/langpy/install.inf" "$TMP_DIR/install.inf"

rm -f "$PACKAGE"
if [ "$ARCHIVER" = zip ]; then
    (cd "$TMP_DIR" && zip -qr "$PACKAGE" install.inf pt_BR)
else
    (cd "$TMP_DIR" && 7z a -tzip -bd -y "$PACKAGE" install.inf pt_BR >/dev/null)
fi

echo "catálogos compilados: $compiled"
echo "catálogos ignorados: $skipped"
echo "pacote gerado: $PACKAGE"
