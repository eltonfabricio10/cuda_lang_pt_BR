#!/usr/bin/env bash
#
# gerar_dicionario_mestre.sh
#
# Gera um dicionário mestre com todas as traduções pendentes dos
# arquivos:
#
#   langmenu/cuda_*/pt_BR.ini
#
# Uma tradução é considerada pendente quando, dentro da seção [menu]:
#
#   Original=Original
#
# O resultado remove duplicatas globais e gera:
#
#   [translations]
#   Config=Config
#   Open console=Open console
#   ...
#
# O script NÃO altera nenhum pt_BR.ini.
#
# Uso:
#   ./gerar_dicionario_mestre.sh
#
# Opções:
#   --output ARQUIVO     Define o arquivo de saída.
#                         Padrão: traducoes_mestre_pt_BR.ini
#   --overwrite          Permite substituir um arquivo existente.
#   --help               Mostra esta ajuda.
#

set -u
set -o pipefail

LANGMENU_DIR="langmenu"
LOCALE_FILE="pt_BR.ini"
OUTPUT="traducoes_mestre_pt_BR.ini"
OVERWRITE=0

usage() {
    cat <<'EOF'
Uso:
  ./gerar_dicionario_mestre.sh [opções]

Opções:
  --output, -o ARQUIVO   Arquivo INI de saída.
  --overwrite, -f        Substitui arquivo existente.
  --help, -h             Mostra esta ajuda.

Exemplos:
  ./gerar_dicionario_mestre.sh

  ./gerar_dicionario_mestre.sh \
      --output dicionario_pt_BR.ini

  ./gerar_dicionario_mestre.sh --overwrite
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --output|-o)
            shift
            [ $# -gt 0 ] || {
                echo "ERRO: --output precisa de um nome de arquivo."
                exit 1
            }
            OUTPUT="$1"
            ;;
        --overwrite|-f)
            OVERWRITE=1
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

if [ ! -d "$LANGMENU_DIR" ]; then
    echo "ERRO: pasta '$LANGMENU_DIR' não encontrada."
    echo "Execute o script na pasta que contém 'langmenu/'."
    exit 1
fi

if [ -e "$OUTPUT" ] && [ "$OVERWRITE" -eq 0 ]; then
    echo "ERRO: o arquivo '$OUTPUT' já existe."
    echo "Use --overwrite para substituí-lo."
    exit 1
fi

tmp="$(mktemp)"
sorted="$(mktemp)"

cleanup() {
    rm -f "$tmp" "$sorted"
}
trap cleanup EXIT

files_analyzed=0
pending_found=0

# Percorre todos os pt_BR.ini em diretórios cuda_*.
while IFS= read -r -d '' ini; do
    files_analyzed=$((files_analyzed + 1))

    # Lê somente a seção [menu].
    #
    # Para cada linha:
    #   chave=valor
    #
    # inclui apenas quando:
    #   chave == valor
    #
    # A linha inteira é preservada, evitando perder caracteres como:
    #   &
    #   ...
    #   < >
    #   apostrofes
    #   espaços
    awk '
        BEGIN {
            in_menu = 0
        }

        /^[[:space:]]*\[/ {
            in_menu = ($0 ~ /^[[:space:]]*\[menu\][[:space:]]*$/)
            next
        }

        !in_menu {
            next
        }

        /^[[:space:]]*;/ {
            next
        }

        /^[[:space:]]*$/ {
            next
        }

        {
            pos = index($0, "=")

            if (pos == 0)
                next

            key = substr($0, 1, pos - 1)
            value = substr($0, pos + 1)

            # Corrige CR caso o arquivo tenha linhas CRLF.
            sub(/\r$/, "", key)
            sub(/\r$/, "", value)

            if (key != "" && key == value)
                print key "=" value
        }
    ' "$ini" >> "$tmp"

done < <(
    find "$LANGMENU_DIR" \
        -type f \
        -name "$LOCALE_FILE" \
        -path '*/cuda_*/*' \
        -print0 | sort -z
)

if [ -s "$tmp" ]; then
    # LC_ALL=C evita alterações indevidas de locale durante a ordenação.
    LC_ALL=C sort -u "$tmp" > "$sorted"
else
    : > "$sorted"
fi

pending_found="$(wc -l < "$sorted" | tr -d ' ')"

{
    printf '; Dicionário mestre de traduções do CudaText\n'
    printf '; Gerado automaticamente por gerar_dicionario_mestre.sh\n'
    printf '; Fonte: langmenu/cuda_*/pt_BR.ini\n'
    printf '; Arquivos analisados: %s\n' "$files_analyzed"
    printf '; Entradas únicas pendentes: %s\n' "$pending_found"
    printf '; Edite somente o valor após o primeiro sinal =\n'
    printf '; Exemplo: Open=Abrir\n'
    printf '\n[translations]\n'

    cat "$sorted"
} > "$OUTPUT"

echo
echo "Dicionário mestre criado:"
echo "  $OUTPUT"
echo
echo "Arquivos analisados       : $files_analyzed"
echo "Traduções pendentes únicas: $pending_found"
echo
echo "O arquivo original pt_BR.ini não foi alterado."
echo
echo "Exemplo de edição:"
echo "  Config=Configuração"
echo "  Open console=Abrir console"
echo "  Toggle=Alternar"
