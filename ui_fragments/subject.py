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
                <div class="d-flex w-100 justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="bi bi-diagram-3"></i> Assuntos</h5>
                    <button class="btn btn-sm btn-outline-primary" onclick="openSemanticModal()">
                        <i class="bi bi-search"></i> Nova Busca
                    </button>
                </div>
                
                {results_html}
                
                {script}
            </div>
            """,
            "right": None 
        }
