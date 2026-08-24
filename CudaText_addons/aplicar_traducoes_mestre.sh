#!/usr/bin/env bash
#
# aplicar_traducoes_mestre.sh
#
# Aplica traduções de um dicionário mestre aos arquivos:
#   langmenu/cuda_*/pt_BR.ini
#
# Regra de segurança:
#   - só altera entradas da seção [menu]
#   - só altera quando o valor atual é exatamente igual à chave
#   - traduções existentes são preservadas
#   - suporta simulação, backup e relatório
#

set -u
set -o pipefail

DICTIONARY="traducoes_mestre_pt_BR_375_completo.ini"
LANGMENU="langmenu"
REPORT="relatorio_aplicacao_traducoes.txt"
DRY_RUN=0
BACKUP=0

usage() {
cat <<'EOF'
Uso:
  ./aplicar_traducoes_mestre.sh [opções]

Opções:
  --dictionary, -d ARQUIVO   Dicionário mestre INI.
  --langmenu, -l PASTA       Pasta langmenu.
  --report, -r ARQUIVO       Arquivo de relatório.
  --dry-run                  Apenas simula, sem alterar arquivos.
  --backup                   Cria arquivo .bak antes de alterar.
  --help, -h                 Mostra esta ajuda.

Exemplos:
  ./aplicar_traducoes_mestre.sh --dry-run

  ./aplicar_traducoes_mestre.sh \
      --dictionary traducoes_mestre_pt_BR_375_completo.ini \
      --backup

  ./aplicar_traducoes_mestre.sh --report resultado.txt
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dictionary|-d)
            shift
            [ $# -gt 0 ] || { echo "ERRO: --dictionary precisa de um arquivo."; exit 1; }
            DICTIONARY="$1"
            ;;
        --langmenu|-l)
            shift
            [ $# -gt 0 ] || { echo "ERRO: --langmenu precisa de uma pasta."; exit 1; }
            LANGMENU="$1"
            ;;
        --report|-r)
            shift
            [ $# -gt 0 ] || { echo "ERRO: --report precisa de um arquivo."; exit 1; }
            REPORT="$1"
            ;;
        --dry-run)
            DRY_RUN=1
            ;;
        --backup)
            BACKUP=1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "ERRO: opção desconhecida: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

[ -f "$DICTIONARY" ] || { echo "ERRO: dicionário não encontrado: $DICTIONARY"; exit 1; }
[ -d "$LANGMENU" ] || { echo "ERRO: pasta não encontrada: $LANGMENU"; exit 1; }

TMP_DICT="$(mktemp)"
TMP_PENDING="$(mktemp)"
TMP_CHANGED="$(mktemp)"
trap 'rm -f "$TMP_DICT" "$TMP_PENDING" "$TMP_CHANGED"' EXIT

# Extrai somente a seção [translations].
awk '
BEGIN { inside=0 }
/^[[:space:]]*\[/ {
    inside = ($0 ~ /^[[:space:]]*\[translations\][[:space:]]*$/)
    next
}
inside {
    line=$0
    sub(/\r$/, "", line)
    if (line ~ /^[[:space:]]*$/ || line ~ /^[[:space:]]*;/) next
    pos=index(line, "=")
    if (pos == 0) next
    key=substr(line, 1, pos-1)
    val=substr(line, pos+1)
    if (key != "") print key "\t" val
}
' "$DICTIONARY" > "$TMP_DICT"

DICT_COUNT="$(wc -l < "$TMP_DICT" | tr -d ' ')"
[ "$DICT_COUNT" -gt 0 ] || { echo "ERRO: nenhuma entrada encontrada em [translations]."; exit 1; }

FILES_ANALYZED=0
FILES_CHANGED=0
TRANSLATIONS_APPLIED=0
EXISTING_TRANSLATIONS=0
PENDING=0

while IFS= read -r -d '' FILE; do
    FILES_ANALYZED=$((FILES_ANALYZED + 1))
    TMP_OUT="$(mktemp)"

    RESULT="$(
    awk -v dict="$TMP_DICT" -v pend="$TMP_PENDING" '
    BEGIN {
        FS="\t"
        while ((getline < dict) > 0) {
            translations[$1]=$2
        }
        close(dict)
        in_menu=0
        changed=0
        applied=0
        existing=0
        pending_count=0
    }

    /^[[:space:]]*\[/ {
        in_menu = ($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/)
        print
        next
    }

    !in_menu {
        print
        next
    }

    /^[[:space:]]*;/ || /^[[:space:]]*$/ {
        print
        next
    }

    {
        raw=$0
        clean=$0
        sub(/\r$/, "", clean)

        pos=index(clean, "=")
        if (pos == 0) {
            print raw
            next
        }

        key=substr(clean, 1, pos-1)
        value=substr(clean, pos+1)

        if (key in translations) {
            target=translations[key]

            # Entrada pendente: chave=chave.
            if (value == key) {
                if (target != key && target != "") {
                    print key "=" target
                    changed=1
                    applied++
                } else {
                    print raw
                    print key >> pend
                    pending_count++
                }
            } else {
                print raw
                existing++
            }
        } else {
            print raw
        }
    }

    END {
        printf "%d %d %d %d\n", changed, applied, existing, pending_count > "/dev/stderr"
    }
    ' "$FILE" > "$TMP_OUT" 2>&1
    )"

    # O awk acima escreve o arquivo e as estatísticas; para evitar depender
    # de stderr misturado, calcula estatísticas por comparação adicional.
    FILE_APPLIED="$(awk -v dict="$TMP_DICT" '
    BEGIN {
        while ((getline < dict) > 0) { split($0,a,"\t"); tr[a[1]]=a[2] }
        close(dict); in_menu=0; n=0
    }
    /^[[:space:]]*\[/ { in_menu=($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/); next }
    in_menu {
        line=$0; sub(/\r$/, "", line); p=index(line,"=")
        if (p>0) {
            k=substr(line,1,p-1); v=substr(line,p+1)
            if ((k in tr) && v==k && tr[k]!=k && tr[k]!="") n++
        }
    }
    END {print n}
    ' "$FILE")"

    FILE_EXISTING="$(awk -v dict="$TMP_DICT" '
    BEGIN { while ((getline < dict)>0){split($0,a,"\t"); tr[a[1]]=a[2]}; close(dict); m=0 }
    /^[[:space:]]*\[/ { in_menu=($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/); next }
    in_menu {
        line=$0; sub(/\r$/, "", line); p=index(line,"=")
        if(p>0){k=substr(line,1,p-1);v=substr(line,p+1);if((k in tr)&&v!=k)m++}
    }
    END{print m}
    ' "$FILE")"

    if [ "$FILE_APPLIED" -gt 0 ]; then
        FILES_CHANGED=$((FILES_CHANGED + 1))
        TRANSLATIONS_APPLIED=$((TRANSLATIONS_APPLIED + FILE_APPLIED))
        printf '%s (%s traduções)\n' "$FILE" "$FILE_APPLIED" >> "$TMP_CHANGED"

        if [ "$DRY_RUN" -eq 0 ]; then
            if [ "$BACKUP" -eq 1 ]; then
                cp -p -- "$FILE" "$FILE.bak"
            fi

            # Regera corretamente o arquivo substituindo somente pendências.
            awk -v dict="$TMP_DICT" '
            BEGIN { while ((getline < dict)>0){split($0,a,"\t");tr[a[1]]=a[2]}; close(dict); in_menu=0 }
            /^[[:space:]]*\[/ { in_menu=($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/); print; next }
            !in_menu { print; next }
            /^[[:space:]]*;/ || /^[[:space:]]*$/ { print; next }
            {
                raw=$0; line=$0; sub(/\r$/, "", line); p=index(line,"=")
                if(p==0){print raw; next}
                k=substr(line,1,p-1); v=substr(line,p+1)
                if((k in tr) && v==k && tr[k]!=k && tr[k]!="") print k "=" tr[k]
                else print raw
            }' "$FILE" > "$FILE.tmp.$$"
            mv -- "$FILE.tmp.$$" "$FILE"
        fi
    fi

    EXISTING_TRANSLATIONS=$((EXISTING_TRANSLATIONS + FILE_EXISTING))
    rm -f "$TMP_OUT"

done < <(
    find "$LANGMENU" -type f -name "pt_BR.ini" -path '*/cuda_*/*' -print0 | sort -z
)

# Verificação final de pendências: após aplicação (ou em simulação, considerando
# as traduções disponíveis no dicionário).
while IFS= read -r -d '' FILE; do
    awk -v dict="$TMP_DICT" '
    BEGIN { while ((getline < dict)>0){split($0,a,"\t");tr[a[1]]=a[2]}; close(dict); in_menu=0 }
    /^[[:space:]]*\[/ { in_menu=($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/); next }
    in_menu {
        line=$0; sub(/\r$/, "", line); p=index(line,"=")
        if(p>0){k=substr(line,1,p-1);v=substr(line,p+1)
            if((k in tr) && v==k && (tr[k]==k || tr[k]=="")) print FILENAME ": " k
        }
    }' "$FILE" >> "$TMP_PENDING"
done < <(find "$LANGMENU" -type f -name "pt_BR.ini" -path '*/cuda_*/*' -print0 | sort -z)

PENDING="$(wc -l < "$TMP_PENDING" | tr -d ' ')"

{
echo "RELATÓRIO DE APLICAÇÃO DE TRADUÇÕES"
echo "==================================="
echo
echo "Dicionário             : $DICTIONARY"
echo "Pasta analisada        : $LANGMENU"
echo "Modo                   : $([ "$DRY_RUN" -eq 1 ] && echo SIMULAÇÃO || echo APLICAÇÃO)"
echo "Backup                 : $([ "$BACKUP" -eq 1 ] && echo SIM || echo NÃO)"
echo
echo "RESUMO"
echo "-----------------------------------"
printf "Entradas no dicionário       : %s\n" "$DICT_COUNT"
printf "Arquivos analisados          : %s\n" "$FILES_ANALYZED"
printf "Arquivos alterados           : %s\n" "$FILES_CHANGED"
printf "Traduções aplicadas          : %s\n" "$TRANSLATIONS_APPLIED"
printf "Traduções existentes         : %s\n" "$EXISTING_TRANSLATIONS"
printf "Chaves ainda pendentes       : %s\n" "$PENDING"
echo
echo "ARQUIVOS ALTERADOS"
echo "-----------------------------------"
if [ -s "$TMP_CHANGED" ]; then cat "$TMP_CHANGED"; else echo "Nenhum."; fi
echo
echo "PENDÊNCIAS SEM TRADUÇÃO"
echo "-----------------------------------"
if [ -s "$TMP_PENDING" ]; then sort -u "$TMP_PENDING"; else echo "Nenhuma."; fi
} > "$REPORT"

echo
if [ "$DRY_RUN" -eq 1 ]; then
    echo "SIMULAÇÃO CONCLUÍDA — nenhum arquivo foi alterado."
else
    echo "APLICAÇÃO CONCLUÍDA."
fi
echo "Relatório: $REPORT"
echo "Arquivos analisados : $FILES_ANALYZED"
echo "Arquivos alterados  : $FILES_CHANGED"
echo "Traduções aplicadas : $TRANSLATIONS_APPLIED"
echo "Pendências          : $PENDING"
