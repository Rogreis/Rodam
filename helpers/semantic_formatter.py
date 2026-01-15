
class SemanticFormatter:
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
                        # onclick chama navigateWithCode (definido no main.html)
                        links_html += f'''
                        <a href="javascript:void(0)" 
                           class="badge bg-primary text-decoration-none me-1" 
                           onclick="navigateWithCode('{c}')">{c}</a>
                        '''
            
            card_html = f'''
            <div class="list-group-item bg-dark text-white border-secondary mb-3 rounded shadow-sm">
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
