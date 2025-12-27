from helpers.globals import global_config, translations_manager

class TocFragment:
    def html(self):
        # Determine language (Config or Default 0)
        lang_id = getattr(global_config, 'LanguageForToc', 0)
        
        # Load Translation
        tr = translations_manager.get(lang_id)
        if not tr:
            # Attempt load if not cached (though global.py loads them)
            tr = translations_manager.load(lang_id)
        
        if not tr:
            return {
                "left": f"<div class='alert alert-warning'>Translation ID {lang_id} not loaded.</div>", 
                "right": ""
            }
            
        documents = []
        if tr.papers:
            for paper in tr.papers:
                p_idx = paper.get("PaperIndex", -1)
                for p in paper.get("Paragraphs", []):
                    try:
                        if int(p.get("ParagraphNo", -1)) == 0:
                            # Create a copy or modify if safe. Here we create a dict with needed fields to avoid mutating cached translation structure too much
                            doc_item = p.copy()
                            doc_item['PaperIndex'] = p_idx
                            documents.append(doc_item)
                    except (ValueError, TypeError):
                        continue
            
        # Group by PaperIndex to reconstruct hierarchy
        from itertools import groupby
        
        # Sort documents by PaperIndex then SectionIndex to ensure order
        documents.sort(key=lambda x: (int(x.get('PaperIndex', -1)), int(x.get('SectionIndex', 0))))
        
        # Buffers for each part
        content_intro = ""
        content_part_i = ""
        content_part_ii = ""
        content_part_iii = ""
        content_part_iv = ""
        
        # Group by PaperIndex
        for p_idx, group_iter in groupby(documents, key=lambda x: int(x.get('PaperIndex', -1))):
            headers = list(group_iter)
            if not headers:
                continue
                
            # Identify Paper Title (SectionIndex 0) and Sections
            paper_title_node = next((h for h in headers if int(h.get("SectionIndex", 0)) == 0), None)
            
            # If no explicit 0 section, use first
            if not paper_title_node:
                paper_title_node = headers[0]
                
            sections = [h for h in headers if h != paper_title_node]
            
            # Build Paper HTML
            paper_title = paper_title_node.get("Text", f"Documento {p_idx}")
            doc_label = f"{p_idx}. {paper_title}" if p_idx > 0 else paper_title # Intro might not need number? User asked for number.
            
            # Sub-tree HTML (Sections)
            sections_html = ""
            if sections:
                sections_html = '<div class="list-group list-group-flush ms-3 border-start border-secondary">'
                for sec in sections:
                    s_idx = sec.get("SectionIndex", 0)
                    s_title = sec.get("Text", "Seção")
                    s_label = f"{s_idx}. {s_title}"
                    sections_html += f'''
                    <a href="#" class="list-group-item list-group-item-action bg-transparent border-0 py-1 text-reset small"
                       style="user-select: text;">{s_label}</a>
                    '''
                sections_html += '</div>'

            # Accordion Item for this Paper
            # We use a unique ID based on p_idx
            paper_id = f"paper{p_idx}"
            
            paper_html = f'''
            <div class="accordion-item bg-transparent border-0">
                <h2 class="accordion-header" id="head{paper_id}">
                    <button class="accordion-button collapsed shadow-none bg-transparent text-reset py-2" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#collapse{paper_id}" aria-expanded="false" 
                            aria-controls="collapse{paper_id}"
                            style="user-select: text;">
                        {doc_label}
                    </button>
                </h2>
                <div id="collapse{paper_id}" class="accordion-collapse collapse" aria-labelledby="head{paper_id}">
                    <div class="accordion-body p-0">
                        {sections_html}
                    </div>
                </div>
            </div>
            '''
            
            # Categorize
            if p_idx == 0:
                content_intro += paper_html
            elif 1 <= p_idx <= 31:
                content_part_i += paper_html
            elif 32 <= p_idx <= 56:
                content_part_ii += paper_html
            elif 57 <= p_idx <= 119:
                content_part_iii += paper_html
            else:
                content_part_iv += paper_html

        # Helper to create the Main Part Nodes
        def create_node(node_id, title, content):
            return f'''
            <div class="accordion-item bg-transparent border-0">
                <h2 class="accordion-header" id="heading{node_id}">
                    <button class="accordion-button collapsed shadow-none bg-transparent text-reset fw-bold" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#collapse{node_id}" aria-expanded="false" 
                            aria-controls="collapse{node_id}"
                            style="user-select: text;">
                        {title}
                    </button>
                </h2>
                <div id="collapse{node_id}" class="accordion-collapse collapse" aria-labelledby="heading{node_id}" 
                     data-bs-parent="#tocAccordion">
                    <div class="accordion-body p-0 ps-2">
                        {content}
                    </div>
                </div>
            </div>
            '''

        html_intro = create_node("Intro", "Introdução", content_intro)
        html_part_i = create_node("PartI", "Parte I", content_part_i)
        html_part_ii = create_node("PartII", "Parte II", content_part_ii)
        html_part_iii = create_node("PartIII", "Parte III", content_part_iii)
        html_part_iv = create_node("PartIV", "Parte IV", content_part_iv)
        
        html = f'<div class="accordion accordion-flush user-select-text" id="tocAccordion">{html_intro}{html_part_i}{html_part_ii}{html_part_iii}{html_part_iv}</div>'
        
        # Right column empty or instructions
        right_html = """
        <div class="p-4 text-center text-muted">
            <h4>Bem-vindo ao Rodam</h4>
            <p>Selecione um documento à esquerda para começar a leitura.</p>
        </div>
        """
        
        return {
            "left": html,
            "right": right_html
        }
