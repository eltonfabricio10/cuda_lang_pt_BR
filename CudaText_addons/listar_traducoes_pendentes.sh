#!/usr/bin/env bash
set -u
set -o pipefail

LANGMENU_DIR="langmenu"
LOCALE_FILE="pt_BR.ini"
MODE="list"
OUTPUT=""

usage() {
cat <<'EOF'
Uso: ./listar_traducoes_pendentes.sh [opções]

Opções:
  --count, -c             Mostra apenas a quantidade pendente por plugin
  --output, -o ARQUIVO    Salva também o relatório em um arquivo
  --help, -h              Mostra esta ajuda
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --count|-c) MODE="count" ;;
    --output|-o) shift; [ $# -gt 0 ] || { echo "ERRO: falta arquivo."; exit 1; }; OUTPUT="$1" ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Opção desconhecida: $1"; exit 1 ;;
  esac
  shift
done

[ -d "$LANGMENU_DIR" ] || { echo "ERRO: pasta '$LANGMENU_DIR' não encontrada."; exit 1; }

report="$(mktemp)"
trap 'rm -f "$report"' EXIT

total_files=0; plugins_pending=0; total_pending=0
printf 'RELATÓRIO DE TRADUÇÕES PENDENTES\n================================\n\n' > "$report"

while IFS= read -r -d '' ini; do
  plugin="$(basename "$(dirname "$ini")")"

  pending="$(awk '
    BEGIN { in_menu=0 }
    /^[[:space:]]*\[/ {
      in_menu = ($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/)
      next
    }
    !in_menu || /^[[:space:]]*;/ || /^[[:space:]]*$/ { next }
    {
      p=index($0,"=")
      if (!p) next
      k=substr($0,1,p-1); v=substr($0,p+1)
      sub(/\r$/,"",k); sub(/\r$/,"",v)
      if (k != "" && k == v) print k
    }
  ' "$ini")"

  total_files=$((total_files+1))
  if [ -n "$pending" ]; then
    count="$(printf '%s\n' "$pending" | wc -l)"
    plugins_pending=$((plugins_pending+1))
    total_pending=$((total_pending+count))

    if [ "$MODE" = "count" ]; then
      printf '%s: %s pendente(s)\n' "$plugin" "$count" >> "$report"
    else
      printf '%s\n' "$plugin" >> "$report"
      printf '%s\n' "$pending" | sed 's/^/  - /' >> "$report"
      printf '\n' >> "$report"
    fi
  fi
done < <(find "$LANGMENU_DIR" -type f -name "$LOCALE_FILE" -path '*/cuda_*/*' -print0 | sort -z)

printf '\nRESUMO\n================================\n' >> "$report"
printf 'Arquivos analisados       : %s\n' "$total_files" >> "$report"
printf 'Plugins com pendências    : %s\n' "$plugins_pending" >> "$report"
printf 'Total de chaves pendentes : %s\n' "$total_pending" >> "$report"

cat "$report"
if [ -n "$OUTPUT" ]; then cp "$report" "$OUTPUT"; echo; echo "Relatório salvo em: $OUTPUT"; fi
