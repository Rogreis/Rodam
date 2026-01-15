from helpers.translations import Paper

class SemanticFormatter:

    @staticmethod
    def _generate_github_url(self, display_text: str) -> str:
        return f'<small><a href="javascript:void(0)" onclick="openGithubLink(\'{self.paper_str}\', \'{self.section_str}\', \'{self.par_str}\')" class="{self.css_class}" title="Edita o conteúdo deste parágrafo no github">{display_text}</a></small>'


    @staticmethod
    def format_results_to_html(results: list, elapsed: float) -> str:
        """
        Formata a lista de resultados da busca semântica em HTML para a coluna esquerda.
        """
        if not results:
            return '<div class="p-3 text-muted text-center">Nenhum resultado encontrado.</div>'

        html_parts = []
        html_parts.append('<div class="list-group list-group-flush p-2">')
        
        # Header / Statas
        html_parts.append(f'<div class="text-muted small mb-2 text-end">Encontrados {len(results)} resultados em {elapsed:.2f}s</div>')

        for item in results:
            rank = item.get('rank', 0)
            score_pct = item.get('score', 0) * 100
            assunto = item.get('assunto', '')
            links_str = item.get('links', '')
            
            # Processar links (ex: "100:1.1 100:2.1")
            links_html = ""
            if links_str:
                code_list = links_str.split()
                for code in code_list:
                    c = code.strip()
                    if c:
                        # Valida se o c é um parágrafo válido
                        if not Paper.extract_code_triplet(c):
                            continue
                        
                        # onclick chama navigateWithCode (definido no main.html)
                        links_html += f'''
                        <a href="#" 
                           onclick="event.preventDefault(); navigateWithCode('{c}', true); return false;">{c}</a>
                        '''
            
            # Use Theme-Aware Bootstrap Classes (Requires Bootstrap 5.3+ data-bs-theme)
            card_class = "list-group-item mb-3 rounded shadow-sm border"

            card_html = f'''
            <div class="{card_class}">
                <div class="d-flex w-100 justify-content-between align-items-center mb-1">
                    <span class="badge bg-secondary">#{rank}</span>
                    <small class="text-success">{score_pct:.1f}%</small>
                </div>
                <p class="mb-2 fw-bold" style="font-size: 0.95rem;">{assunto}</p>
                <div class="">
                    {links_html}
                </div>
            </div>
            '''
            html_parts.append(card_html)

        html_parts.append('</div>')
        return "".join(html_parts)
