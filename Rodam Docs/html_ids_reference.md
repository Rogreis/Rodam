# Referência de IDs HTML — Rodam

Documento de referência de todos os `id` HTML presentes na página única da aplicação Rodam (`templates/main.html` e modais incluídos). Use esta referência ao escrever JavaScript, CSS ou testes.

---

## 1. Layout Principal (`main.html`)

### Estrutura de Página

| ID | Elemento | Descrição |
|----|----------|-----------|
| `mainContainer` | `div.container-fluid` | Container raiz de toda a página |
| `mainRow` | `div.main-row` | Linha flexível que contém as duas colunas e o divisor |
| `leftColumn` | `div` | Coluna esquerda — exibe o índice (ToC), resultados semânticos ou de artigos. Conteúdo injetado dinamicamente via AJAX |
| `divisor` | `div` | Barra de redimensionamento arrastável entre as colunas |
| `rightColumn` | `div` | Coluna direita — exibe o conteúdo do parágrafo/documento selecionado. Conteúdo injetado dinamicamente via AJAX |

### Navbar

| ID                   | Elemento                       | Descrição                                                                                                                              |
| -------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `mainNavbar`         | `nav.navbar`                   | Barra de navegação principal (Bootstrap 5)                                                                                             |
| `navbarContainer`    | `div.container-fluid`          | Container interno da navbar                                                                                                            |
| `navbarToggler`      | `button.navbar-toggler`        | Botão de colapso da navbar em telas pequenas                                                                                           |
| `navbarNav`          | `div.collapse.navbar-collapse` | Container colapsável com os itens de navegação                                                                                         |
| `navbarMenu`         | `ul.navbar-nav`                | Lista de itens de navegação                                                                                                            |
| `nav-item-urantia`   | `li.nav-item`                  | Item estático que abre o site oficial da Urantia (urantia.org)                                                                         |
| `nav-item-{item.id}` | `li.nav-item`                  | Itens de navegação dinâmicos gerados pelo Jinja2 (ex: `nav-item-indexToc`, `nav-item-search`). `d-none` quando `item.visible == False` |
| `navbarTitleWrapper` | `div.mx-auto`                  | Container centralizado que envolve o título do documento                                                                               |
| `navbarTitle`        | `span.navbar-brand.titulo`     | Texto do título do documento atualmente visualizado. Atualizado via JS após navegação                                                  |

### Ações da Navbar (lado direito)

| ID | Elemento | Descrição |
|----|----------|-----------|
| `navbarActionsBar` | `div.navbar-nav.ms-auto` | Agrupador das ações do lado direito da navbar |
| `trackComboWrapper` | `div.trackCombo` | Wrapper externo do campo de navegação por parágrafo |
| `trackComboInputWrapper` | `div.trackCombo-input-wrapper` | Wrapper do `<input>` do combo de navegação |
| `mytrackCombo` | `input[type=text]` | Campo de texto para navegar diretamente a um parágrafo (ex: `1:2.3`). Dispara `navigateWithCode()` ao pressionar Enter |
| `comboParagraphTrack` | `div.trackCombo-options` | Dropdown de parágrafos visitados recentemente. Populado por `updateComboParagraphTrack()` |
| `btnOpenBrowser` | `button` | Abre a URL atual no navegador padrão do sistema (`openSystemBrowser()`) |
| `btnHighlight` | `button` | Liga/desliga o destaque de termos de busca no conteúdo (`toggleHighlight()`). Alterna entre `btn-outline-warning` e `btn-warning` |
| `btnPrint` | `button` | Aciona `window.print()` para imprimir o conteúdo atual |

### Menu de Contexto Customizado

| ID | Elemento | Descrição |
|----|----------|-----------|
| `customContextMenu` | `div.custom-context-menu` | Menu de contexto customizado exibido ao selecionar texto e clicar com botão direito. Inicialmente `display: none` |

---

## 2. Modal de Configurações (`settings_modal.html`)

| ID | Elemento | Descrição |
|----|----------|-----------|
| `settingsModal` | `div.modal` | Modal de configurações da aplicação (Bootstrap 5). Aberto por `openSettingsModal()`. Ao fechar, dispara `saveSettings()` |
| `darkModeSwitch` | `input[type=checkbox]` | Ativa/desativa o modo escuro (`toggleDarkMode()`) |
| `langTocSwitch` | `input[type=checkbox]` | Alterna o idioma do índice (Português/Inglês) e salva configurações |
| `bgColorsSwitch` | `input[type=checkbox]` | Exibe/oculta as cores de status dos parágrafos em edição (`toggleBgColors()`) |
| `semanticsSwitch` | `input[type=checkbox]` | Exibe/oculta o item de menu de busca semântica (`toggleSemantics()`) |
| `semanticDownloadAlert` | `div.alert` | Alerta exibido durante o download dos arquivos de semântica. Criado dinamicamente por `checkSemanticFiles()` |
| `hlMagenta` | `input[type=radio]` | Opção de cor de destaque: Magenta |
| `hlGold` | `input[type=radio]` | Opção de cor de destaque: Dourado |
| `hlCyan` | `input[type=radio]` | Opção de cor de destaque: Ciano |
| `hlDarkOrange` | `input[type=radio]` | Opção de cor de destaque: Laranja escuro |

---

## 3. Modal de Busca por Texto (`search_modal.html`)

| ID | Elemento | Descrição |
|----|----------|-----------|
| `searchResultsModal` | `div.modal` | Modal principal de busca por texto (Whoosh). `data-bs-backdrop="static"` — não fecha ao clicar fora |
| `searchForm` | `form` | Formulário com todos os controles de busca |
| `modalSearchInput` | `input[type=text]` | Campo de texto da query de busca |
| `langPT` | `input[type=radio]` | Seleção de idioma: Português (value=`2`) |
| `langEN` | `input[type=radio]` | Seleção de idioma: Inglês (value=`0`) |
| `scopeParts` | `input[type=radio]` | Escopo de busca: Por Partes |
| `partsOptions` | `div` | Container das checkboxes de partes (visível quando `scopeParts` está selecionado) |
| `partIntro` | `input[type=checkbox]` | Parte: Introdução |
| `part1` | `input[type=checkbox]` | Parte: Parte I |
| `part2` | `input[type=checkbox]` | Parte: Parte II |
| `part3` | `input[type=checkbox]` | Parte: Parte III |
| `part4` | `input[type=checkbox]` | Parte: Parte IV |
| `scopeDocs` | `input[type=radio]` | Escopo de busca: Por Documentos |
| `docsInput` | `input[type=text]` | Lista de documentos para busca (ex: `1; 5-10; 100`). Habilitado somente quando `scopeDocs` está ativo |
| `maxResults` | `input[type=range]` | Slider do número máximo de resultados (20–300) |
| `maxResultsVal` | `span` | Exibe o valor atual do slider `maxResults` |
| `pageSize` | `select` | Itens por página nos resultados (20 ou 50) |

> **Resultados da busca**: O container de resultados é injetado dinamicamente pela função Python `search_modal.py` — verifique `helpers/search_modal.py` para o `id` do container de resultados.

---

## 4. Modal de Busca Semântica (`semantic_search_modal.html`)

| ID | Elemento | Descrição |
|----|----------|-----------|
| `semanticSearchResultModal` | `div.modal` | Modal de busca semântica por IA. `data-bs-backdrop="static"` — não fecha ao clicar fora. Aberto por `openSemanticModal()` |
| `semanticForm` | `form` | Formulário com todos os controles de busca semântica |
| `modalSemanticInput` | `input[type=text]` | Campo de texto da query semântica (somente Inglês) |
| `semLangPT` | `input[type=radio]` | Idioma Português (desabilitado — semântica só funciona em Inglês) |
| `semLangEN` | `input[type=radio]` | Idioma Inglês (padrão, desabilitado — fixo) |
| `semScopeParts` | `input[type=radio]` | Escopo de busca semântica: Por Partes |
| `semPartsOptions` | `div` | Container das checkboxes de partes semânticas |
| `semPartIntro` | `input[type=checkbox]` | Parte semântica: Introdução |
| `semPart1` | `input[type=checkbox]` | Parte semântica: Parte I |
| `semPart2` | `input[type=checkbox]` | Parte semântica: Parte II |
| `semPart3` | `input[type=checkbox]` | Parte semântica: Parte III |
| `semPart4` | `input[type=checkbox]` | Parte semântica: Parte IV |
| `semScopeDocs` | `input[type=radio]` | Escopo de busca semântica: Por Documentos |
| `semDocsInput` | `input[type=text]` | Lista de documentos para busca semântica. Habilitado somente quando `semScopeDocs` está ativo |
| `semMaxResults` | `input[type=range]` | Slider do número máximo de resultados semânticos (20–300) |
| `semMaxResultsVal` | `span` | Exibe o valor atual do slider `semMaxResults` |
| `semPageSize` | `select` | Itens por página nos resultados semânticos (20 ou 50) |
| `semanticSearchResultsList` | `div` | Container onde os resultados semânticos são renderizados (ou spinner de carregamento) |

---

## 5. Conteúdo Dinâmico (IDs gerados pelo Backend Python)

Os elementos abaixo são injetados em `leftColumn` ou `rightColumn` pelo backend Python e podem ser referenciados no JS:

| ID | Gerado por | Descrição |
|----|-----------|-----------|
| `nav-item-{item.id}` | `app.py` / `main.html` (Jinja loop) | Itens de navegação dinâmicos (ex: `nav-item-indexSemantic`) |
| `semanticDownloadAlert` | `main.html` JS / `checkSemanticFiles()` | Alerta de download do arquivo semântico, criado dinamicamente |

---

## 6. Funções JavaScript que Referenciam IDs

| Função JS | IDs Utilizados |
|-----------|----------------|
| `onMainWindowLoad()` | `leftColumn`, `rightColumn`, `navbarTitle` |
| `loadContent(route, pageId)` | `leftColumn`, `rightColumn`, `navbarTitle` |
| `navigateWithCode(code)` | `rightColumn`, `leftColumn`, `navbarTitle`, `mytrackCombo`, `comboParagraphTrack` |
| `loadDynamicContent(secret)` | `rightColumn`, `mytrackCombo` |
| `updateComboParagraphTrack()` | `comboParagraphTrack` |
| `toggleHighlight()` | `btnHighlight` |
| `highlightTerms(terms)` / `cleanHighlights()` | `rightColumn` |
| `saveSettings()` | `darkModeSwitch`, `bgColorsSwitch`, `semanticsSwitch`, `langTocSwitch`, `leftColumn` |
| `toggleSemantics(show)` | `nav-item-indexSemantic`, `semanticsSwitch` |
| `checkSemanticFiles()` | `semanticsSwitch`, `semanticDownloadAlert` |
| `performSemanticSearch()` | `semanticForm`, `modalSemanticInput`, `semDocsInput`, `semMaxResults`, `semanticSearchResultsList`, `semanticSearchResultModal`, `leftColumn` |
| `changeSemanticSort()` | `leftColumn` |
| `toggleSemanticScope()` | `semanticForm`, `semPartsOptions`, `semDocsInput` |
| `openSettingsModal()` | `settingsModal` |
| `DOMContentLoaded` init | `mytrackCombo`, `comboParagraphTrack`, `darkModeSwitch`, `langTocSwitch`, `bgColorsSwitch`, `semanticsSwitch`, `settingsModal`, `divisor`, `leftColumn`, `rightColumn` |
| Context menu handler | `customContextMenu` |

---

*Gerado em: 07/05/2026 — baseado em `templates/main.html`, `templates/settings_modal.html`, `templates/search_modal.html`, `templates/semantic_search_modal.html`*
