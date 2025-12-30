from helpers.globals import global_config
import helpers.globals

from typing import Optional
'''
DOCUMETAÇÂO PROCESSO DE BUSCA
=============================

A indexação e a busca são realizadas no arquivo search_engine.py, utilizando a biblioteca Whoosh.

1) Processo de Indexação (build_index e ensure_index):

 - A classe RodamSearch verifica se existe um índice na pasta indexes/(dentro de APPDATA/Rodam).
 - Se não existir, ela lê os arquivos TR002.zip (Português) ou TR000.zip (Inglês) da pasta de dados.
 - Extrai o arquivo translation.json de dentro do ZIP.
 - Itera sobre todos os Papers e Paragraphs desse JSON.
 - Cria documentos no índice Whoosh com os campos: id (formato PPP_SSS_VVV), content (texto do parágrafo) e title

2) Busca (search):
 - Recebe a query string, o idioma e o número máximo de resultados.
 - Abre o índice correspondente (index_pt ou index_en).
 - Usa o QueryParser do Whoosh para analisar a query no campo content
 - Executa a busca e retorna uma lista de dicionários contendo id, paper, section, paragraph e o content encontrado.

Este processo é iniciado na app.py quando a rota /search é chamada, que por sua vez instancia 
    a classe RodamSearch e chama o método .search().

'''

class SearchFragment:
    @staticmethod
    def html(page: Optional[int], open_modal: bool, templates):
        from helpers.search_engine import RodamSearch
        import math
        
        last_query = global_config.query
        max_results = global_config.SearchMaxResults
        items_per_page = global_config.SearchItemsToShow
        lang_id = global_config.LanguageIdToSearch
        sort_order = global_config.SearchResultsOrder
        
        # Language ID is used directly now (0=EN, 2=PT)
        # Removed string mapping as search_engine now expects int
        
        print(f"Last query {last_query} a ser buscada em ID {lang_id}")
            
        modal_script = "<script>showSearchModal();</script>" if open_modal else ""
        
        script = f"""
        {modal_script}
        <script>
        
        async function updateSortOrder(val) {{
            let payload = {{
                "query": "{last_query}",
                "SearchResultsOrder": parseInt(val),
                "LanguageIdToSearch": {lang_id},
                "SearchMaxResults": {max_results}
            }};
            
            try {{
                await fetch('/search', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(payload)
                }});
                loadContent('/search?page=1', 'search');
            }} catch (e) {{
                console.error("Error updating sort order:", e);
            }}
        }}
        </script>
        """
        
        # determine scope string (omitted for brevity, keep existing logic)
        scope_parts = []
        if global_config.SearchParts:
            parts_active = []
            if global_config.SearchIntroduction: parts_active.append("Intro")
            if global_config.SearchPartI: parts_active.append("Part I")
            if global_config.SearchPartII: parts_active.append("Part II")
            if global_config.SearchPartIII: parts_active.append("Part III")
            if global_config.SearchPartIV: parts_active.append("Part IV")
            if parts_active:
                scope_parts.append(f"Parts ({', '.join(parts_active)})")
        if global_config.SearchDocuments:
            doc_list = global_config.SearchDocumentsList
            if doc_list:
                scope_parts.append(f"Docs ({doc_list})")
            else:
                scope_parts.append("Selected Docs") 
        scope_str = " + ".join(scope_parts) if scope_parts else "All"
        print(f"scope_str {scope_str}")

        # Build Header Info
        css_styles = """
        <style>
            .match, .term0, .term1, .term2, .term3 {
                color: magenta !important;
                font-weight: bold;
            }
        </style>
        """
        
        msg_left = f"""
        {css_styles}
        <div class="mb-3 p-2 border-bottom">
            <h4>Busca</h4>
            <p class="mb-1"><strong>Query:</strong> {last_query}</p>
            <p class="mb-1"><strong>Escopo:</strong> {scope_str}</p>
            <p class="mb-1"><strong>Máx. Resultados:</strong> {max_results}</p>
            
            <div class="mt-2">
                <label class="me-2 fw-bold">Ordenação:</label><br />
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="sortOrder" id="sortRank" value="1" 
                           {'checked' if sort_order == 1 else ''} onclick="updateSortOrder(1)">
                    <label class="form-check-label" for="sortRank">Prioridade</label>
                </div>
                <div class="form-check form-check-inline">
                    <input class="form-check-input" type="radio" name="sortOrder" id="sortPar" value="0" 
                           {'checked' if sort_order == 0 else ''} onclick="updateSortOrder(0)">
                    <label class="form-check-label" for="sortPar">Parágrafos</label>
                </div>
            </div>
        </div>
        """
        
        if not last_query:
            return {
                "left": f"{msg_left} {script}",
                "right": "<div class='alert alert-info'>Use o menu de busca para pesquisar.</div>"
            }

       
        # Build Allowed Papers List
        allowed_papers = []
        page_results = [] # Scope safety
        total_items = 0

        helpers.globals.logger.debug("Vai calcular que documentos")
        # If SearchParts is active
        if global_config.SearchParts:
            if global_config.SearchIntroduction: allowed_papers.append(0)
            if global_config.SearchPartI: allowed_papers.extend(range(1, 32))   # 1 to 31
            if global_config.SearchPartII: allowed_papers.extend(range(32, 57)) # 32 to 56
            if global_config.SearchPartIII: allowed_papers.extend(range(56, 120)) # 56 to 119
            if global_config.SearchPartIV: allowed_papers.extend(range(119, 197)) # 119 to 196
            helpers.globals.logger.debug("Entrou em SearchParts")


        # If SearchDocuments is active (merges with parts if both true, logic depends on semantics but usually Union)
        # User said "If global_config.SearchDocuments for true...", usually implied alternate or additive.
        # I'll append. If user meant "Only these", usually UI handles mutual exclusion.
        if global_config.SearchDocuments:
            doc_str = global_config.SearchDocumentsList
            if doc_str:
                parts_str = doc_str.split(';')
                for p_str in parts_str:
                    p_str = p_str.strip()
                    if not p_str: continue
                    
                    # Support both : and - as range separators
                    if ':' in p_str or '-' in p_str:
                        try:
                            # Normalize separator
                            p_str_clean = p_str.replace('-', ':')
                            start, end = map(int, p_str_clean.split(':'))
                            # range is exclusive at end, but user notation usually implies inclusive
                            allowed_papers.extend(range(start, end + 1))
                            print(f"allowed_papers added range {start}-{end}")
                        except: 
                            print(f"allowed_papers erro parsing range: {p_str}")
                            pass
                    else:
                        try:
                            allowed_papers.append(int(p_str))
                            print(f"allowed_papers 2 {allowed_papers}")
                        except: 
                            print(f"allowed_papers com erro 2")
                            pass
        
        print(f"allowed_papers {allowed_papers}")
        # Deduplicate and sort
        if allowed_papers:
            allowed_papers = sorted(list(set(allowed_papers)))
            
            # Optimization: If all papers are selected (0 to 196 = 197 items), disable filter
            if len(allowed_papers) >= 197:
                helpers.globals.logger.debug("Todos os documentos selecionados (197). Filtro desativado para otimização.")
                allowed_papers = []
                print("Todos os dpcumentos selecionados")
            else:
                helpers.globals.logger.debug(f"Filtro de Papers Ativo: {allowed_papers}")
                print(f"Documentos selecionados {allowed_papers}")
        else:
            helpers.globals.logger.debug("Filtro de Papers: Todos (Lista vazia)")
            print(f"Filtro de Papers: Todos (Lista vazia)")
        
        # If allowed_papers is empty here, it implies ALL (if SearchParts/SearchDocs were false)
        # OR it implies NONE (if they were true but selected nothing/empty list).
        # User said: "Se for all, deixe a lista vazia".
        # Logic: If flags are false, list is empty from start -> ALL.
        # If flags are true but produce empty list -> Effectively NONE?
        # But commonly, "SearchParts=False" means "Don't filter by parts".
        
        # Perform Search
        # User requested to remove engine-side filtering ("não passe mais allowed_papers")
        # and perform local filtering instead.
        searcher = RodamSearch()
        
        # We search broadly (ignoring max_results limitation for a moment? No, searcher enforces it. 
        # This might return filtered-out results if max_results is hit before filtering. 
        # But this is what was requested: "deixe que eu farei um filtro local".)
        # Maybe increase max_results slightly? No, stick to config.
        helpers.globals.logger.debug(f"Vai buscar com query= {last_query} lang={lang_id} e max_results={max_results}")
        results = searcher.search(last_query, lang=lang_id, max_results=max_results)

        total_items = len(results)
        helpers.globals.logger.debug(f"Total encontrados antes do filtro local: {total_items}")

        # Local Filter
        if allowed_papers:
            # Note: allowed_papers was emptied if it contained ALL (197) in previous block optimization.
            # So this filter runs only if there is a subset restriction.
            results = [r for r in results if r['paper'] in allowed_papers]
            print(f"VAI FAZER RESTRIÇÂO {len(results)}")
        else:
            print("NÃO VAI FAZER RESTRIÇÂO")
        
        total_items = len(results)
        page_results = [] # Initialize to avoid UnboundLocalError
        helpers.globals.logger.debug(f"Total encontrados após filtro local: {total_items}")

        # Apply Sorting
        if sort_order == 0:
            # Sort by Paragraph (Paper, Section, Paragraph) - Numerical
            results.sort(key=lambda x: (x['paper'], x['section'], x['paragraph']))
            helpers.globals.logger.debug("Resultados ordenados por Parágrafo (Numérico)")
        else:
            helpers.globals.logger.debug("Resultados mantidos por Ranking (Padrão Whoosh)")

        total_pages = math.ceil(total_items / items_per_page) if items_per_page > 0 else 1
        
        # Validate Page
        if page < 1: page = 1
        if page > total_pages: page = total_pages
        
        # Checks if we have any result
        if total_items == 0:
            msg_left += "<div class='alert alert-warning'>Nenhum resultado encontrado.</div>"
        else:
            msg_left += f"<p>Encontrados: {total_items} resultados (Página {page} de {total_pages}).</p>"
            
            # Generate Pagination HTML (Reuse for Top and Bottom)
            pagination_html = ""
            if total_pages > 1:
                pagination_html = '<nav aria-label="Search results pages" class="my-2"><ul class="pagination pagination-sm justify-content-center mb-0">'
                
                # Previous
                disabled_prev = "disabled" if page == 1 else ""
                pagination_html += f"""
                <li class="page-item {disabled_prev}">
                    <a class="page-link" href="javascript:loadContent('/search?page={page-1}', 'search')">Anterior</a>
                </li>
                """
                
                # Page Numbers
                window_start = max(1, page - 2)
                window_end = min(total_pages, page + 2)
                
                if window_start > 1:
                     pagination_html += '<li class="page-item"><a class="page-link" href="javascript:loadContent(\'/search?page=1\', \'search\')">1</a></li>'
                     if window_start > 2:
                         pagination_html += '<li class="page-item disabled"><span class="page-link">...</span></li>'

                for p in range(window_start, window_end + 1):
                    active = "active" if p == page else ""
                    pagination_html += f"""
                    <li class="page-item {active}">
                        <a class="page-link" href="javascript:loadContent('/search?page={p}', 'search')">{p}</a>
                    </li>
                    """
                
                if window_end < total_pages:
                    if window_end < total_pages - 1:
                         pagination_html += '<li class="page-item disabled"><span class="page-link">...</span></li>'
                    pagination_html += f'<li class="page-item"><a class="page-link" href="javascript:loadContent(\'/search?page={total_pages}\', \'search\')">{total_pages}</a></li>'

                # Next
                disabled_next = "disabled" if page == total_pages else ""
                pagination_html += f"""
                <li class="page-item {disabled_next}">
                    <a class="page-link" href="javascript:loadContent('/search?page={page+1}', 'search')">Próximo</a>
                </li>
                """
                pagination_html += "</ul></nav>"

            # Add Top Pagination
            msg_left += pagination_html
            
            # Slice results
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_results = results[start_idx:end_idx]
            
            # Build List in Left Column
            msg_left += "<div class='list-group mb-3'>"
            for item in page_results:
                ref = item.get('title', '???')
                secret_code = item.get('id')
                # Include Text Snippet
                # Use snippet_html provided by search_engine which contains highlights (<b> tags)
                # If unavailable, fallback to manual truncation
                snippet = item.get('snippet_html', '')
                
                # Strip HTML tags
                import re
                import html
                # User asked to "eliminar".
                
                if snippet:
                     # Unescape first to convert &lt;em&gt; to <em> so regex catches it
                     snippet = html.unescape(snippet)
                     # Remove tags except <b> (used for highlighting)
                     snippet = re.sub(r'<(?!/?b(?=>|\s))[^>]*>', '', snippet)
                else:
                     full_text = item.get('text', '')
                     # Remove all tags for fallback
                     clean_text = re.sub(r'<[^>]+>', '', full_text)
                     snippet = clean_text
                     #snippet = clean_text[:250] + "..." if len(clean_text) > 250 else clean_text
                
                # Highlight selection logic if we want:
                msg_left += f"""
                <a href="javascript:loadDynamicContent('{secret_code}')" 
                   class="list-group-item list-group-item-action py-2 px-2" aria-current="true">
                   <div class="d-flex w-100 justify-content-between">
                       <small class="fw-bold text-primary mb-1">{ref}</small>
                   </div>
                   <p class="mb-1 small text-muted" style="font-size: 0.9em; line-height: 1.2;">{snippet}</p>
                </a>
                """
            msg_left += "</div>"
            
            # Add Bottom Pagination
            msg_left += pagination_html

        # Right Column Content
        html_right = ""
        
        if len(page_results) > 0:
            # Use the first item of the CURRENT PAGE, not the global list
            first_item_id = page_results[0]['id']
            
            from helpers.paper_format import FormatPaper
            formatter = FormatPaper()
            
            # paper_display returns List[Tuple[str, str]] -> [(html_left, html_right), ...]
            # We will display the Right column (PT/Content with links)
            print("Vai formatar o primeiro item: {first_item_id}")
            paper_content = formatter.paper_display(first_item_id)
            
            if paper_content:
                # Use shared template for consistent rendering
                template = templates.get_template("paper_table.html")
                html_right = template.render(paragraphs=paper_content)
            else:
                 html_right = "<div class='text-muted p-4 text-center'>Erro ao carregar o documento.</div>"
        else:
             html_right = ""
        
        return {
            "left": f"{msg_left} {script}",
            "right": html_right
        }
