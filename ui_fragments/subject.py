class SubjectFragment:
    @staticmethod
    def render_view(results_html, script=""):
        """
        Gera o HTML completo da coluna esquerda para a visão de Assuntos.
        Inclui Header (Icone, Botão) e Info de Configuração.
        """
        from helpers.globals import global_config
        
        # Calculate Scope String
        scope_str = "Todos"
        if global_config.SemanticSearchParts:
            parts_active = []
            if global_config.SemanticSearchIntroduction: parts_active.append("Intro")
            if global_config.SemanticSearchPartI: parts_active.append("Part I")
            if global_config.SemanticSearchPartII: parts_active.append("Part II")
            if global_config.SemanticSearchPartIII: parts_active.append("Part III")
            if global_config.SemanticSearchPartIV: parts_active.append("Part IV")
            if parts_active:
                scope_str = f"Partes ({', '.join(parts_active)})"
            else:
                scope_str = "Nenhuma Parte Selecionada"
                
        elif global_config.SemanticSearchDocuments:
            doc_list = global_config.SemanticSearchDocumentsList
            scope_str = f"Docs: {doc_list}" if doc_list else "Docs: (Vazio)"

        sort_relevance_checked = "checked" if getattr(global_config, 'SemanticSearchSortOrder', True) else ""
        sort_paragraphs_checked = "checked" if not getattr(global_config, 'SemanticSearchSortOrder', True) else ""

        info_html = f"""
            <div class="w-100 mb-3 p-2 border-bottom text-start">
                <p class="mb-1"><strong>Query:</strong> {global_config.SemanticQuery}</p>
                <p class="mb-1"><strong>Escopo:</strong> {scope_str}</p>
                <p class="mb-1"><strong>Máx. Resultados:</strong> {global_config.SemanticSearchMaxResults}</p>
                <div class="mt-2">
                    <label class="me-2 fw-bold">Ordenação:</label><br />
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sortOrderSem" id="sortRankSem" value="1" {sort_relevance_checked} onchange="changeSemanticSort(true)">
                        <label class="form-check-label" for="sortRankSem">Relevância</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sortOrderSem" id="sortParSem" value="0" {sort_paragraphs_checked} onchange="changeSemanticSort(false)">
                        <label class="form-check-label" for="sortParSem">Parágrafos</label>
                    </div>
                </div>
            </div>
        """
        
        return f"""
            <div class="d-flex flex-column align-items-center justify-content-start h-100 text-muted p-3" style="overflow-y: auto;">
                <div class="d-flex w-100 justify-content-between align-items-center mb-0">
                    <h5 class="mb-0"><i class="bi bi-diagram-3"></i> Assuntos</h5>
                    <button class="btn btn-sm btn-outline-primary" onclick="openSemanticModal()">
                        <i class="bi bi-search"></i> Nova Busca
                    </button>
                </div>
                
                {info_html}
                
                {results_html}
                
                {script}
            </div>
            """

    def html(self):
        import os
        import json
        from helpers.globals import SEMANTIC_RESULTS_FILE
        from helpers.semantic_formatter import SemanticFormatter

        results_html = '<div id="semanticResultsPlaceholder" class="mt-4 w-100"></div>'
        
        # Check if we have saved results
        if os.path.exists(SEMANTIC_RESULTS_FILE):
            try:
                with open(SEMANTIC_RESULTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results = data.get('results', [])
                    elapsed = data.get('elapsed', 0)
                    
                    if results:
                        formatted = SemanticFormatter.format_results_to_html(results, elapsed)
                        results_html = f'<div id="semanticResultsPlaceholder" class="mt-4 w-100">{formatted}</div>'
            except Exception as e:
                print(f"Error loading saved semantic results: {e}")

        script = ""
        # Auto-open logic if no results
        if '<div class="list-group' not in results_html:
             script = """
                <script>
                    if (typeof openSemanticModal === 'function') {
                        setTimeout(openSemanticModal, 100);
                    }
                </script>
             """

        left_content = result = self.render_view(results_html, script)

        return {
            "left": left_content,
            "right": None 
        }
