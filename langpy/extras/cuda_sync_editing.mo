��          t      �         (     K   :     �  *   �  A   �  "     +   .     Z  F   z  �  �  +  �  0   �  ^   
      i  D   �  3   �  )     >   -  3   l  ?   �  �  �                           
                    	             Do you want to cancel Sync Editing mode? Sync Editing: Cancel? Click somewhere else to cancel, or on ID to continue. Sync Editing: Cancelled Sync Editing: Cannot find IDs in selection Sync Editing: Click on ID to edit it, or somewhere else to cancel Sync Editing: Make selection first Sync Editing: Need several IDs in selection Sync Editing: Need single caret Sync Editing: Not a word! Click another, or click somewhere else again To configure Sync Editing, open lexer-specific config in CudaText (Options / Settings-more / Settings lexer specific) and write there options: case sensitive, regular expression for identifiers:

  "case_sens": true, // case sensitive search
  "id_regex": "\w+", // regex to find id's
  "id_styles": "(?i)id[\w\s]*", // use tokens with these styles
  "id_styles_no": "(?i).*keyword.*", // ignore tokens with these styles
  "syncedit_naive_mode": false, // use 'naive' algorithm (search without lexer analysis, e.g. for plain text)

Also you can write to CudaText's user.json these options:

  "syncedit_mark_words": true, // allows fancy colorizing of words in selection
  "syncedit_ask_to_exit": true, // show confirmation before auto-cancelling
 Project-Id-Version: CudaText
PO-Revision-Date: 2021-07-25 17:53-0300
Language-Team: eltonff <eltonfabricio10@gmail.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Generated-By: pygettext.py 1.5
Language: pt_BR
Last-Translator: 
X-Generator: Poedit 2.3
 Deseja cancelar o modo de Edição Sincronizada? Edição Sincronizada: Cancelar? Clique em outro lugar para cancelar, ou em ID para continuar. Edição Sincronizada: Cancelada Edição Sincronizada: Não foi possível encontrar IDs na seleção Edição Sincronizada: Clique no ID para editar, ou Edição Sincronizada: Selecione primeiro Edição Sincronizada: É necessário vários IDs na seleção Edição Sincronizada: É necessário cursor único Edição Sincronizada: Não é uma palavra! Clique em outro, ou Para configurar a Edição Sincronizada, abrir a configuração específica do lexer no CudaText (Opções / Configurações - Específicas do lexer) e escrever as opções: distinção entre maiúsculas e minúsculas, expressão regular para identificadores:

   "case_sens": true, // pesquisar com distinção entre maiúsculas e minúsculas
   "id_regex": "\w+", // expressão regular para encontrar id's
   "id_styles": "(?i)id [\w\s]*", // usar tokens com esses estilos
   "id_styles_no": "(?i).*keyword.*", // ignorar tokens com esses estilos
   "syncedit_naive_mode": false, // usar o algoritmo 'ingênuo' (pesquisar sem análise lexer, p. ex. para texto simples)

Além disso, você pode escrever no user.json do CudaText estas opções:

   "syncedit_mark_words": true, // permitir colorização de palavras na seleção
   "syncedit_ask_to_exit": true, // exibir confirmação antes do cancelamento automático
 