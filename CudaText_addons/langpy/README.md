# Traduções de plugins

## Organização

- `extras/*.po`: fonte editável das traduções gettext.
- `pt_BR/LC_MESSAGES/*.mo`: catálogos compilados usados pelo CudaText.
- `plugins-translations.pt_BR.zip`: pacote distribuível pelo gerenciador de complementos.

Arquivos `.po` com nomes terminados em `-bkp` são cópias de segurança e não devem
ser distribuídos. Catálogos sem nenhuma mensagem traduzida também permanecem
fora do pacote até que recebam uma tradução.

## Gerar os catálogos e o pacote

Na raiz do repositório:

```bash
bash build_plugin_translations.sh
```

O processo exige `msgfmt` e `zip`. Ele recompila os `.mo` a partir dos `.po`,
remove artefatos antigos e recria `plugins-translations.pt_BR.zip`.

Antes de publicar, revisar as estatísticas de tradução e testar o ZIP em uma
instalação atual do CudaText.

## Catálogo oficial de plugins

O catálogo de plugins ativos é mantido pelo projeto CudaText em:

<https://github.com/Alexey-T/CudaText-registry/blob/master/json/plugins.json>

O campo `module` é o identificador usado para comparar o registry com os
diretórios `langmenu` e `langpy`. Plugins antigos, internos ou auxiliares podem
existir neste repositório sem aparecer no registry; eles não devem ser
removidos automaticamente.

Os demais arquivos do diretório `json` possuem escopos diferentes:

- `plugins.json`: plugins ativos e fonte principal deste projeto;
- `linters.json`: linters, considerados somente quando tiverem interface textual;
- `data.json`: pacotes de dados, temas, ícones e traduções da aplicação;
- `snippets.json`: snippets, sem catálogo gettext de interface;
- `_removed.json`: itens removidos, sem prioridade para novas traduções.

O registry atualmente lista uma tradução `pt_PT`, mas não um pacote `pt_BR`.
Este repositório, portanto, mantém uma tradução brasileira independente.

Para auditar a cobertura atual:

```bash
bash audit_plugin_registry.sh
```

## Preparar fontes de plugins

Para baixar somente os plugins que serão revisados, use o preparador seletivo:

```bash
python3 prepare_plugin_sources.py \
  --module cuda_bootstrap_complete \
  --module cuda_git_conflict
```

As fontes são extraídas em `CudaText_sources/`. O script valida o ZIP e bloqueia
caminhos que tentem escapar do diretório de destino. Use `--keep-archives`
somente quando for necessário preservar os ZIPs originais.
