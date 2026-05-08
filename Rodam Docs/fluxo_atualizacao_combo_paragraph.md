# Fluxo de Atualização do ComboParagraphTrack via TreeView

Este documento descreve o caminho de execução que ocorre quando um usuário clica em um nó da árvore de conteúdos (ToC), resultando na atualização do componente `comboParagraphTrack`.

## 1. Origem do Evento (Frontend - TreeView)
*   **Arquivo**: `templates/bs5_treeview.html`
*   **Local**: `$('#treeview').treeview({ onNodeSelected: ... })`
*   **Ação**: 
    1. O componente TreeView detecta o clique.
    2. O evento `onNodeSelected` é disparado.
    3. O ID interno do nó (ex: `120_003_000`) é convertido para uma referência de parágrafo legível (ex: `120:3-0`).
    4. A função global `window.navigateWithCode(cleanRef)` é chamada.

## 2. Controlador Principal (Frontend)
*   **Arquivo**: `templates/main.html`
*   **Local**: `async function navigateWithCode(code)`
*   **Ação**: 
    1. Recebe o código do passo anterior.
    2. Realiza uma requisição assíncrona (`fetch`) para a rota `/api/navigate` no backend.

## 3. Backend (Validação e Processamento)
*   **Arquivo**: `app.py`
*   **Local**: Rota `@app.get("/api/navigate")` | Função `navigate_to_paragraph`
*   **Ação**: 
    1. Valida a referência recebida.
    2. Padroniza a formatação (ex: garante separadores corretos como `120:3.0`).
    3. Retorna o código validado no campo JSON `final_code`.

## 4. Atualização da Interface (Frontend)
*   **Arquivo**: `templates/main.html`
*   **Local**: Dentro do bloco `try/then` da função `navigateWithCode`
*   **Ação**:
    1. Recebe o `result.final_code` do backend.
    2. Atualiza visualmente o input: `document.getElementById('mytrackCombo').value = validCode;`.
    3. Atualiza a lista em memória `recentParagraphs` (adiciona o novo código ao topo e remove duplicatas).
    4. Chama a função **`updateComboParagraphTrack()`**.

## 5. Renderização do Combo
*   **Arquivo**: `templates/main.html`
*   **Local**: `function updateComboParagraphTrack()`
*   **Ação**: 
    1. Limpa o HTML atual do container `comboParagraphTrack`.
    2. Itera sobre a lista `recentParagraphs`.
    3. Cria e insere os novos elementos `<div>` correspondentes ao histórico atualizado.
