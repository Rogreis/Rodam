class SubjectFragment:
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

        # Note: If we have results, we might NOT want to auto-open the modal immediately, 
        # or maybe we do? Request says "has data to display and no need to re-do search".
        # So if we have results, we disable the auto-open script.
        
        from helpers.globals import global_config

        # Calculate Scope String
        scope_parts = []
        if global_config.SemanticSearchParts:
            parts_active = []
            if global_config.SemanticSearchIntroduction: parts_active.append("Intro")
            if global_config.SemanticSearchPartI: parts_active.append("Part I")
            if global_config.SemanticSearchPartII: parts_active.append("Part II")
            if global_config.SemanticSearchPartIII: parts_active.append("Part III")
            if global_config.SemanticSearchPartIV: parts_active.append("Part IV")
            if parts_active:
                scope_parts.append(f"Parts ({', '.join(parts_active)})")
        
        scope_str = " + ".join(scope_parts) if scope_parts else "Todos"

        info_html = f"""
            <div class="w-100 mb-3 p-2 border-bottom text-start">
                <p class="mb-1"><strong>Query:</strong> {global_config.SemanticQuery}</p>
                <p class="mb-1"><strong>Escopo:</strong> {scope_str}</p>
                <p class="mb-1"><strong>Máx. Resultados:</strong> {global_config.SemanticSearchMaxResults}</p>
                <div class="mt-2">
                    <label class="me-2 fw-bold">Ordenação:</label><br />
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sortOrderSem" id="sortRankSem" value="1" checked disabled>
                        <label class="form-check-label" for="sortRankSem">Prioridade</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sortOrderSem" id="sortParSem" value="0" disabled>
                        <label class="form-check-label" for="sortParSem">Parágrafos</label>
                    </div>
                </div>
            </div>
        """

        script = """
            <script>
                // Auto-open modal when this view is loaded ONLY if no results are shown?
                // Or always allow user to click button.
                // If we have results, we probably don't want to popup the modal over them.
                // Let's check if the placeholder is empty or not via JS? 
                // Easier logic: If python loaded results, don't include the script.
            </script>
        """
        
        if '<div class="list-group' in results_html:
             # Results loaded
             script = ""
        else:
             # No results, keep auto-open behavior
             script = """
                <script>
                    if (typeof openSemanticModal === 'function') {
                        setTimeout(openSemanticModal, 100);
                    }
                </script>
             """

        return {
            "left": f"""
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
            """,
            "right": None 
        }
