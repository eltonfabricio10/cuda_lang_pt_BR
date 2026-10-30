#!/usr/bin/env bash
# comparar_plugins_langmenu_v2.sh
# Compara plugins CudaText com traduções em langmenu.
# Métodos:
#   1. Nome exato extraído de homepage=
#   2. Nome normalizado
#   3. Conteúdo: title= e captions do install.inf x chaves [menu] do pt_BR.ini
#
# Segurança:
#   padrão: dry-run
#   --apply: altera apenas correspondências inequívocas
#   nunca apaga pastas
#   --backup: copia a pasta antes de renomear

set -u
set -o pipefail

PLUGINS="plugin"
LANGMENU="langmenu"
REPORT="relatorio_comparacao_plugins_langmenu.txt"
APPLY=0
BACKUP=0
MIN_MATCHES=2
MIN_RATIO_PERCENT=60

usage() {
cat <<'EOF'
Uso:
  ./comparar_plugins_langmenu_v2.sh [opções]

Opções:
  -p, --plugins PASTA       Pasta raiz plugin (padrão: plugin)
  -l, --langmenu PASTA      Pasta raiz langmenu (padrão: langmenu)
  -r, --report ARQUIVO      Arquivo do relatório
      --dry-run             Simulação (padrão)
      --apply               Renomeia correspondências seguras
      --backup              Cria cópia .bak antes de renomear
      --min-matches N       Mínimo de chaves iguais para match por conteúdo (padrão: 2)
      --min-ratio N         Percentual mínimo de coincidência (padrão: 60)
  -h, --help                Ajuda

A homepage é usada para obter o nome oficial:
  homepage=https://github.com/autor/NOME
  -> NOME

A correspondência é tentada nesta ordem:
  1. Pasta langmenu/NOME
  2. Nome normalizado (case, -, _, . e espaços)
  3. Conteúdo:
       install.inf: title= e caption= (após a última \)
       pt_BR.ini: chaves da seção [menu]

No modo --apply, somente correspondências únicas e seguras são renomeadas.
EOF
}

normalize() {
    printf '%s' "$1" |
        tr '[:upper:]' '[:lower:]' |
        sed 's/[-_.[:space:]]//g'
}

trim() {
    local x="$1"
    x="${x#"${x%%[![:space:]]*}"}"
    x="${x%"${x##*[![:space:]]}"}"
    printf '%s' "$x"
}

extract_homepage_name() {
    local inf="$1" hp name
    hp="$(awk '
      BEGIN { IGNORECASE=1 }
      /^[[:space:]]*homepage[[:space:]]*=/ {
        x=$0; sub(/^[^=]*=/, "", x)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", x)
        print x; exit
      }' "$inf")"
    [ -n "$hp" ] || return 1
    hp="${hp%%#*}"
    hp="${hp%%\?*}"
    hp="${hp%/}"
    name="${hp##*/}"
    name="${name%.git}"
    [ -n "$name" ] || return 1
    printf '%s' "$name"
}

# Retorna title e captions após a última barra invertida.
# Formato de saída: uma chave por linha.
extract_plugin_keys() {
    local inf="$1"
    awk '
      BEGIN { IGNORECASE=1 }
      /^[[:space:]]*(title|caption)[[:space:]]*=/ {
        line=$0
        sub(/^[^=]*=/, "", line)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)

        # Para caption=Menu\Submenu\Item, usar Item.
        n=split(line, a, /\\/)
        key=a[n]
        if (key != "") print key
      }' "$inf" | sed '/^[[:space:]]*$/d' | sort -u
}

# Extrai as chaves da seção [menu].
extract_langmenu_keys() {
    local ini="$1"
    awk '
      BEGIN { inmenu=0; IGNORECASE=1 }
      /^[[:space:]]*\[/ {
        section=$0
        gsub(/^[[:space:]]*\[|\][[:space:]]*$/, "", section)
        inmenu=(tolower(section)=="menu")
        next
      }
      inmenu && /^[[:space:]]*[;#]/ { next }
      inmenu && /^[^=]+=/ {
        key=$0
        sub(/=.*/, "", key)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", key)
        if (key != "") print key
      }' "$ini" | sort -u
}

count_lines() {
    if [ -s "$1" ]; then wc -l < "$1" | tr -d ' '; else echo 0; fi
}

# Conta interseção exata e também normalizada.
compare_key_sets() {
    local a="$1" b="$2" tmp="$3"
    local exact norm

    comm -12 "$a" "$b" > "$tmp.exact"

    awk '{print}' "$a" | while IFS= read -r x; do
        normalize "$x"
        printf '\n'
    done | sort -u > "$tmp.a.norm"

    awk '{print}' "$b" | while IFS= read -r x; do
        normalize "$x"
        printf '\n'
    done | sort -u > "$tmp.b.norm"

    comm -12 "$tmp.a.norm" "$tmp.b.norm" > "$tmp.norm"

    exact="$(count_lines "$tmp.exact")"
    norm="$(count_lines "$tmp.norm")"
    printf '%s %s' "$exact" "$norm"
}

while [ $# -gt 0 ]; do
    case "$1" in
        -p|--plugins) shift; PLUGINS="${1:?Falta o caminho da pasta plugin}";;
        -l|--langmenu) shift; LANGMENU="${1:?Falta o caminho da pasta langmenu}";;
        -r|--report) shift; REPORT="${1:?Falta o nome do relatório}";;
        --dry-run) APPLY=0;;
        --apply) APPLY=1;;
        --backup) BACKUP=1;;
        --min-matches) shift; MIN_MATCHES="${1:?Falta número}";;
        --min-ratio) shift; MIN_RATIO_PERCENT="${1:?Falta percentual}";;
        -h|--help) usage; exit 0;;
        *) echo "ERRO: opção desconhecida: $1"; usage; exit 1;;
    esac
    shift
done

[ -d "$PLUGINS" ] || { echo "ERRO: pasta não encontrada: $PLUGINS"; exit 1; }
[ -d "$LANGMENU" ] || { echo "ERRO: pasta não encontrada: $LANGMENU"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

declare -A LANG_DIR
declare -A LANG_NORM
declare -A LANG_INI

while IFS= read -r -d '' dir; do
    base="$(basename "$dir")"
    LANG_DIR["$base"]="$dir"
    norm="$(normalize "$base")"
    if [ -n "${LANG_NORM[$norm]:-}" ]; then
        LANG_NORM["$norm"]+=$'\n'"$dir"
    else
        LANG_NORM["$norm"]="$dir"
    fi
    [ -f "$dir/pt_BR.ini" ] && LANG_INI["$dir"]="$dir/pt_BR.ini"
done < <(find "$LANGMENU" -mindepth 1 -maxdepth 1 -type d -print0)

REPORT_EXACT="$TMP/exact"
REPORT_NORMAL="$TMP/normal"
REPORT_CONTENT="$TMP/content"
REPORT_AMBIG="$TMP/ambiguous"
REPORT_MISSING="$TMP/missing"
REPORT_NOHOME="$TMP/nohomepage"
REPORT_CHANGED="$TMP/changed"

: > "$REPORT_EXACT"; : > "$REPORT_NORMAL"; : > "$REPORT_CONTENT"
: > "$REPORT_AMBIG"; : > "$REPORT_MISSING"; : > "$REPORT_NOHOME"; : > "$REPORT_CHANGED"

analyzed=0; exact_count=0; normal_count=0; content_count=0
missing_count=0; nohome_count=0; ambiguous_count=0; changed_count=0

while IFS= read -r -d '' inf; do
    analyzed=$((analyzed+1))
    plugin_dir="$(dirname "$inf")"
    plugin_folder="$(basename "$plugin_dir")"

    if ! official="$(extract_homepage_name "$inf")"; then
        echo "$plugin_folder | sem homepage= | $inf" >> "$REPORT_NOHOME"
        nohome_count=$((nohome_count+1))
        continue
    fi

    # 1. EXATA
    if [ -n "${LANG_DIR[$official]:-}" ]; then
        echo "$plugin_folder -> $official | método: NOME EXATO" >> "$REPORT_EXACT"
        exact_count=$((exact_count+1))
        continue
    fi

    # 2. NORMALIZADA
    norm="$(normalize "$official")"
    candidates="${LANG_NORM[$norm]:-}"
    if [ -n "$candidates" ]; then
        ccount="$(printf '%s\n' "$candidates" | sed '/^$/d' | wc -l | tr -d ' ')"
        if [ "$ccount" -eq 1 ]; then
            candidate="$(printf '%s\n' "$candidates" | head -n1)"
            old="$(basename "$candidate")"
            echo "$plugin_folder | $old -> $official | método: NOME NORMALIZADO" >> "$REPORT_NORMAL"
            normal_count=$((normal_count+1))

            if [ "$APPLY" -eq 1 ]; then
                target="$LANGMENU/$official"
                if [ ! -e "$target" ]; then
                    if [ "$BACKUP" -eq 1 ]; then
                        backup="${candidate}.bak"
                        i=1
                        while [ -e "$backup" ]; do backup="${candidate}.bak.$i"; i=$((i+1)); done
                        cp -a -- "$candidate" "$backup"
                    fi
                    mv -- "$candidate" "$target"
                    echo "$old -> $official | método: NOME NORMALIZADO" >> "$REPORT_CHANGED"
                    changed_count=$((changed_count+1))
                fi
            fi
            continue
        fi
    fi

    # 3. CONTEÚDO
    plugin_keys="$TMP/plugin.$analyzed.keys"
    extract_plugin_keys "$inf" > "$plugin_keys"
    total_keys="$(count_lines "$plugin_keys")"

    if [ "$total_keys" -eq 0 ]; then
        echo "$plugin_folder | homepage: $official | sem title/caption utilizável" >> "$REPORT_MISSING"
        missing_count=$((missing_count+1))
        continue
    fi

    best_dir=""
    best_score=-1
    best_exact=0
    best_norm=0
    best_ratio=0
    tied=0
    best_matches_file=""

    for dir in "${!LANG_INI[@]}"; do
        ini="${LANG_INI[$dir]}"
        lang_keys="$TMP/lang.$analyzed.$RANDOM.keys"
        extract_langmenu_keys "$ini" > "$lang_keys"

        [ -s "$lang_keys" ] || continue

        cmpbase="$TMP/cmp.$analyzed.$RANDOM"
        read -r e n < <(compare_key_sets "$plugin_keys" "$lang_keys" "$cmpbase")

        # Pontuação privilegia correspondência exata.
        score=$(( e * 1000 + n ))
        ratio=$(( n * 100 / total_keys ))

        if [ "$score" -gt "$best_score" ]; then
            best_score="$score"
            best_dir="$dir"
            best_exact="$e"
            best_norm="$n"
            best_ratio="$ratio"
            best_matches_file="$cmpbase.exact"
            tied=0
        elif [ "$score" -eq "$best_score" ] && [ "$score" -gt 0 ]; then
            tied=1
        fi
    done

    # Critério seguro:
    # pelo menos MIN_MATCHES chaves normalizadas
    # e pelo menos MIN_RATIO_PERCENT das chaves do plugin.
    if [ "$best_score" -ge 0 ] &&
       [ "$best_norm" -ge "$MIN_MATCHES" ] &&
       [ "$best_ratio" -ge "$MIN_RATIO_PERCENT" ] &&
       [ "$tied" -eq 0 ]; then

        old="$(basename "$best_dir")"
        {
            echo "$plugin_folder"
            echo "  homepage/nome oficial : $official"
            echo "  pasta encontrada       : $old"
            echo "  método                 : CONTEÚDO"
            echo "  chaves do plugin       : $total_keys"
            echo "  coincidências exatas   : $best_exact"
            echo "  coincidências normaliz.: $best_norm"
            echo "  cobertura              : ${best_ratio}%"
            echo "  chaves coincidentes:"
            [ -s "$best_matches_file" ] && sed 's/^/    - /' "$best_matches_file"
            echo
        } >> "$REPORT_CONTENT"

        content_count=$((content_count+1))

        if [ "$APPLY" -eq 1 ]; then
            target="$LANGMENU/$official"
            if [ ! -e "$target" ]; then
                if [ "$BACKUP" -eq 1 ]; then
                    backup="${best_dir}.bak"
                    i=1
                    while [ -e "$backup" ]; do backup="${best_dir}.bak.$i"; i=$((i+1)); done
                    cp -a -- "$best_dir" "$backup"
                fi
                mv -- "$best_dir" "$target"
                echo "$old -> $official | método: CONTEÚDO | cobertura: ${best_ratio}%" >> "$REPORT_CHANGED"
                changed_count=$((changed_count+1))
            fi
        fi
    elif [ "$best_score" -gt 0 ]; then
        old="$(basename "$best_dir")"
        {
            echo "$plugin_folder | homepage: $official"
            echo "  melhor candidato: $old"
            echo "  coincidências: $best_norm/$total_keys (${best_ratio}%)"
            [ "$tied" -eq 1 ] && echo "  motivo: EMPATE entre candidatos"
            [ "$best_norm" -lt "$MIN_MATCHES" ] && echo "  motivo: poucas chaves coincidentes"
            [ "$best_ratio" -lt "$MIN_RATIO_PERCENT" ] && echo "  motivo: cobertura abaixo do mínimo"
        } >> "$REPORT_AMBIG"
        ambiguous_count=$((ambiguous_count+1))
    else
        echo "$plugin_folder | homepage: $official | nenhuma pasta correspondente encontrada" >> "$REPORT_MISSING"
        missing_count=$((missing_count+1))
    fi
done < <(find "$PLUGINS" -type f -name install.inf -print0 | sort -z)

{
echo "RELATÓRIO DE COMPARAÇÃO PLUGIN × LANGMENU"
echo "=========================================="
echo
echo "Plugins : $PLUGINS"
echo "Langmenu: $LANGMENU"
echo "Modo    : $([ "$APPLY" -eq 1 ] && echo "REAL (--apply)" || echo "DRY-RUN")"
echo "Backup  : $([ "$BACKUP" -eq 1 ] && echo "SIM" || echo "NÃO")"
echo
echo "CRITÉRIOS DE CONTEÚDO"
echo "------------------------------------------"
echo "Mínimo de chaves coincidentes: $MIN_MATCHES"
echo "Cobertura mínima             : ${MIN_RATIO_PERCENT}%"
echo
echo "RESUMO"
echo "------------------------------------------"
echo "install.inf analisados           : $analyzed"
echo "Nome exato                       : $exact_count"
echo "Nome normalizado                 : $normal_count"
echo "Correspondência por conteúdo     : $content_count"
echo "Ambíguos/baixa confiança         : $ambiguous_count"
echo "Sem correspondência              : $missing_count"
echo "Sem homepage                     : $nohome_count"
echo "Alterações realizadas            : $changed_count"
echo
echo "1. CORRESPONDÊNCIAS EXATAS"
echo "=========================================="
cat "$REPORT_EXACT"
echo
echo "2. CORRESPONDÊNCIAS NORMALIZADAS"
echo "=========================================="
cat "$REPORT_NORMAL"
echo
echo "3. CORRESPONDÊNCIAS PELO CONTEÚDO"
echo "=========================================="
cat "$REPORT_CONTENT"
echo
echo "4. AMBÍGUAS / BAIXA CONFIANÇA"
echo "=========================================="
cat "$REPORT_AMBIG"
echo
echo "5. SEM CORRESPONDÊNCIA"
echo "=========================================="
cat "$REPORT_MISSING"
echo
echo "6. SEM HOMEPAGE"
echo "=========================================="
cat "$REPORT_NOHOME"
echo
echo "7. ALTERAÇÕES REALIZADAS"
echo "=========================================="
cat "$REPORT_CHANGED"
} > "$REPORT"

if [ "$APPLY" -eq 1 ]; then
    echo "Modo REAL concluído."
else
    echo "Dry-run concluído. Nenhuma pasta foi alterada."
fi
echo "Relatório: $REPORT"
