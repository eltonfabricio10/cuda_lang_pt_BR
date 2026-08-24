#!/usr/bin/env bash
set -u
set -o pipefail

PLUGIN_DIR="plugin"
LANGMENU_DIR="langmenu"
LANG_FILE="pt_BR.ini"
DRY_RUN=0
BACKUP=1

case "${1:-}" in
  "") ;;
  --dry-run|-n) DRY_RUN=1 ;;
  --no-backup) BACKUP=0 ;;
  *) echo "Uso: $0 [--dry-run|--no-backup]"; exit 1 ;;
esac

[ -d "$PLUGIN_DIR" ] || { echo "ERRO: pasta '$PLUGIN_DIR' não encontrada."; exit 1; }

mkdir -p "$LANGMENU_DIR"

plugins=0; dirs=0; files=0; updated=0; added=0; removed=0

module_name() {
  local n="${1#plugin.}"
  n="$(printf '%s' "$n" | tr '[:upper:]' '[:lower:]')"
  n="${n//./_}"
  printf 'cuda_%s' "$n"
}

key_exists() {
  grep -F -q -x -- "$1=" "$2" || grep -F -q -- "^$1=" "$2"
}

while IFS= read -r -d '' inf; do
  plugins=$((plugins+1))
  plugin="$(basename "$(dirname "$inf")")"
  module="$(module_name "$plugin")"
  dir="$LANGMENU_DIR/$module"
  ini="$dir/$LANG_FILE"

  echo
  echo "=== $plugin -> $module ==="

  if [ ! -d "$dir" ]; then
    echo "[CRIAR PASTA] $dir"
    dirs=$((dirs+1))
    [ "$DRY_RUN" -eq 1 ] || mkdir -p "$dir"
  fi

  if [ ! -f "$ini" ]; then
    echo "[CRIAR ARQUIVO] $ini"
    files=$((files+1))
    if [ "$DRY_RUN" -eq 1 ]; then
      work="$(mktemp)"; printf '[menu]\n' > "$work"
    else
      printf '[menu]\n' > "$ini"
      work="$(mktemp)"; cp "$ini" "$work"
    fi
  else
    work="$(mktemp)"
    cp "$ini" "$work"
  fi

  # Remove entradas quebradas geradas pela versão anterior: \=texto
  bad="$(grep -c '^[[:space:]]*\\=' "$work" 2>/dev/null || true)"
  if [ "$bad" -gt 0 ]; then
    echo "[CORRIGIR] removendo $bad entrada(s) quebrada(s) \\=..."
    tmp="$(mktemp)"
    awk '!/^[[:space:]]*\\=/' "$work" > "$tmp"
    mv "$tmp" "$work"
    removed=$((removed+bad))
  fi

  # Garante [menu]
  if ! grep -q '^[[:space:]]*\[menu\][[:space:]]*$' "$work"; then
    tmp="$(mktemp)"
    { printf '[menu]\n'; cat "$work"; } > "$tmp"
    mv "$tmp" "$work"
  fi

  add_key() {
    local key="$1"
    [ -z "$key" ] && return
    [ "$key" = "-" ] && return

    if ! grep -F -q -- "$key=" "$work"; then
      printf '%s=%s\n' "$key" "$key" >> "$work"
      echo "  + $key"
      added=$((added+1))
      changed=1
    fi
  }

  changed=0

  # title=
  title="$(awk '/^title=/{sub(/^title=/,""); print; exit}' "$inf")"
  [ -n "$title" ] && add_key "$title"

  # caption=A\B\C -> cria A, B e C
  while IFS= read -r line; do
    caption="${line#caption=}"
    [ -z "$caption" ] && continue

    IFS='\' read -r -a parts <<< "$caption"
    for key in "${parts[@]}"; do
      add_key "$key"
    done
  done < <(grep '^caption=' "$inf" || true)

  # Detecta mudanças por remoção também
  [ "$bad" -gt 0 ] && changed=1

  if [ "$changed" -eq 1 ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "[SIMULAÇÃO] arquivo seria atualizado"
    else
      if [ -f "$ini" ] && [ "$BACKUP" -eq 1 ]; then
        cp -f "$ini" "$ini.bak"
      fi
      mv "$work" "$ini"
      work=""
      updated=$((updated+1))
      echo "[OK] atualizado"
    fi
  else
    echo "[OK] já sincronizado"
  fi

  [ -n "${work:-}" ] && [ -f "$work" ] && rm -f "$work"
done < <(find "$PLUGIN_DIR" -type f -name 'install.inf' -print0 | sort -z)

echo
echo "========== RESUMO =========="
echo "Plugins processados : $plugins"
echo "Pastas criadas      : $dirs"
echo "Arquivos criados    : $files"
echo "Arquivos atualizados: $updated"
echo "Chaves adicionadas  : $added"
echo "Entradas \\= removidas: $removed"
[ "$DRY_RUN" -eq 1 ] && echo "Modo simulação: nada foi alterado."
echo "Concluído."
