#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADDON_ROOT="${CUDATEXT_ADDONS_DIR:-$ROOT_DIR/CudaText_addons}"

if command -v zip >/dev/null 2>&1; then
    ARCHIVER=zip
elif command -v 7z >/dev/null 2>&1; then
    ARCHIVER=7z
else
    echo "erro: zip ou 7z não encontrado" >&2
    exit 1
fi

package_data() {
    local source_dir="$1"
    local package="$2"
    local subdir="$3"
    local temp_dir
    temp_dir="$(mktemp -d)"
    trap 'rm -rf "$temp_dir"' RETURN

    cp "$source_dir/install.inf" "$temp_dir/install.inf"

    if [ "$subdir" = "lang" ]; then
        cp "$source_dir/pt_BR.ini" "$temp_dir/pt_BR.ini"
    else
        find "$source_dir" -mindepth 1 -maxdepth 1 -type d -exec cp -a {} "$temp_dir/" \;
    fi

    rm -f "$package"
    if [ "$ARCHIVER" = zip ]; then
        (cd "$temp_dir" && zip -qr "$package" ./*)
    else
        (cd "$temp_dir" && 7z a -tzip -bd -y "$package" ./* >/dev/null)
    fi
    echo "pacote gerado: $package"
}

package_data \
    "$ADDON_ROOT/lang" \
    "$ADDON_ROOT/lang/main-translations.pt_BR.zip" \
    "lang"

package_data \
    "$ADDON_ROOT/langmenu" \
    "$ADDON_ROOT/langmenu/menu-translations.pt_BR.zip" \
    "langmenu"

bash "$ROOT_DIR/build_plugin_translations.sh"
