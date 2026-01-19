import sys
import os

# Adiciona o diretório pai (raiz do projeto) ao sys.path para resolver o pacote helpers
# Isso permite rodar o arquivo diretamente ou via debugger sem erros de módulo
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from helpers.translations import Paper

class SemanticFormatter:
    @staticmethod
    def generate_light_snippet(text: str, query: str, window: int = 60) -> str:
        """
        Gera um snippet leve usando regex e string slicing, muito mais rápido que NLP completo.
        """
        import re
        if not text or not query:
            return ""

        # Normalização básica para busca (case insensitive)
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Tenta encontrar a query no texto
        try:
             # Busca simples do termo
             match_index = text_lower.find(query_lower)
             
             if match_index == -1:
                 # Tenta encontrar palavras individuais se a frase exata falhar
                 words = query_lower.split()
                 for w in words:
                      if len(w) > 3: # Ignora palavras pequenas
                           match_index = text_lower.find(w)
                           if match_index != -1:
                               query_lower = w # Atualiza para destacar esta palavra
                               break
             
             if match_index != -1:
                 start = max(0, match_index - window)
                 end = min(len(text), match_index + len(query_lower) + window)
                 
                 prefix = "..." if start > 0 else ""
                 suffix = "..." if end < len(text) else ""
                 
                 snippet_raw = text[start:end]
                 
                 # Highlight simplificado (apenas insere <mark>)
                 # Usa regex com ignore case para substituir mantendo o case original do texto
                 snippet_highlighted = re.sub(
                     f"({re.escape(query_lower)})", 
                     r"<mark>\1</mark>", 
                     snippet_raw, 
                     flags=re.IGNORECASE
                 )
                 
                 return f"{prefix}{snippet_highlighted}{suffix}"
             else:
                 # Se não achar nada, retorna o começo
                 return text[:100] + "..."
                 
        except Exception:
             return text[:100] + "..."

    @classmethod
    def format_results_to_html(cls, results: list, elapsed: float) -> str:
        """
        Formata a lista de resultados da busca semântica em HTML para a coluna esquerda.
        """
        if not results:
            return '<div class="p-3 text-muted text-center">Nenhum resultado encontrado.</div>'
            
        from helpers.globals import global_config

        # --- Determinar Documentos Permitidos (Scope) ---
        allowed_papers = set()
        has_restriction = False

        if global_config.SemanticSearchParts:
            has_restriction = True
            if global_config.SemanticSearchIntroduction: allowed_papers.add(0)
            if global_config.SemanticSearchPartI: allowed_papers.update(range(1, 32))   # 1 a 31
            if global_config.SemanticSearchPartII: allowed_papers.update(range(32, 57)) # 32 a 56
            if global_config.SemanticSearchPartIII: allowed_papers.update(range(57, 120)) # 57 a 119
            if global_config.SemanticSearchPartIV: allowed_papers.update(range(120, 197)) # 120 a 196
            
        elif global_config.SemanticSearchDocuments:
            has_restriction = True
            doc_str = global_config.SemanticSearchDocumentsList
            if doc_str:
                parts_str = doc_str.split(';') # Suporte a separador ;
                # Mas o prompt menciona separador virgula? "numeros vêm separados por vírgula"
                # Vamos suportar , e ; substituindo antes
                doc_str = doc_str.replace(',', ';')
                parts_str = doc_str.split(';')
                
                for p_str in parts_str:
                    p_str = p_str.strip()
                    if not p_str: continue
                    
                    # Suporte a range com - ou :
                    if '-' in p_str or ':' in p_str:
                        try:
                            clean = p_str.replace(':', '-')
                            start, end = map(int, clean.split('-'))
                            allowed_papers.update(range(start, end + 1))
                        except: pass
                    else:
                        try:
                            allowed_papers.add(int(p_str))
                        except: pass

        # # Se não há flag de restrição ativa, assume TODOS (allowed_papers = None)
        # if not has_restriction:
        #     print("DEBUG: Restrição INATIVA")
        #     allowed_papers = None
        # else:
        #     print(f"DEBUG: Restrição ATIVA.allowed_papers: {allowed_papers}")
            
        html_parts = []
        html_parts.append('<div class="list-group list-group-flush p-2">')
        
        # Header / Status (moved) 
        # But sort first!
        
        # Ordenação
        # Por padrão (True) = Relevância (já vem do FAISS assim)
        # Se False = Parágrafos (ordenar pelo primeiro link)
        # Assumindo que global_config tem SemanticSearchSortOrder. Se não tiver, default True.
        
        sort_by_relevance = getattr(global_config, 'SemanticSearchSortOrder', True)
        
        if not sort_by_relevance:
            def get_sort_key(item):
                links_str = item.get('links', '')
                if not links_str: return (9999, 0, 0)
                
                # Pega primeiro código
                first_code = links_str.split()[0]
                triplet = Paper.extract_code_triplet(first_code)
                if triplet:
                    return triplet
                return (9999, 0, 0)
            
            # Ordenar lista in-place
            results.sort(key=get_sort_key)
            
        html_parts.append(f'<div class="text-muted small mb-2 text-end">Encontrados {len(results)} resultados em {elapsed:.2f}s</div>')

        for item in results:
            rank = item.get('rank', 0)
            score_pct = item.get('score', 0) * 100
            assunto = item.get('assunto', '')
            links_str = item.get('links', '')
            
            # Processar links (ex: "100:1.1 100:2.1")
            links_html = ""
            valid_links_count = 0 
            
            if links_str:
                code_list = links_str.split()
                for code in code_list:
                    c = code.strip()
                    if c:
                        # 1. Extrair ID do Paper e Validar
                        triplet = Paper.extract_code_triplet(c)
                        if not triplet:
                            continue
                        
                        paper_id, _, _ = triplet
                        
                        # 2. Check de Restrição
                        if allowed_papers is not None:
                            if paper_id not in allowed_papers:
                                # print(f"DEBUG: Paper {paper_id} não está no allowed_papers")
                                continue
                            # else:
                            #     print(f"DEBUG: Paper {paper_id} está no allowed_papers")

                        valid_links_count += 1
                        
                        # Recuperar TTranslation
                        from helpers.translations import TTranslations
                        
                        # Obter texto completo (Idioma 0 = Inglês, ou PT=2?) 
                        texto_completo = TTranslations.get_text_content(0, c)
                        
                        # Gerar snippet leve
                        snippet = ""
                        if texto_completo:
                            snippet = cls.generate_light_snippet(texto_completo, item.get('assunto', ''))
                        
                        links_html += f'''
                        <div class="mb-2">
                            <a href="#" 
                               class="text-decoration-none d-block"
                               onclick="event.preventDefault(); navigateWithCode('{c}', true); return false;"
                               onmouseover="this.querySelector('.c-ref').style.textDecoration='underline'"
                               onmouseout="this.querySelector('.c-ref').style.textDecoration='none'">
                                <div class="small text-muted"><span class="c-ref fw-bold text-primary">{c}</span> {snippet}</div>
                            </a>
                        </div>
                        '''
            
            # Se após o filtro não sobrar nenhum link neste assunto, não exibimos o Card?
            # O prompt diz "somente exibirmos parágrafos dentro dos documentos". 
            # Se o assunto ficou sem parágrafos, melhor esconder o card todo para não poluir.
            if valid_links_count == 0:
                continue

            # Use Theme-Aware Bootstrap Classes
            card_class = "list-group-item mb-3 rounded shadow-sm border"

            card_html = f'''
            <div class="{card_class}">
                <div class="d-flex w-100 align-items-center mb-2 border-bottom pb-1">
                     <div class="text-nowrap flex-shrink-0 me-2">
                        <span class="badge bg-secondary">#{rank}</span>
                        <small class="text-success fw-bold ms-1">{score_pct:.1f}%</small>
                     </div>
                     <span class="fw-bold fst-italic fs-6 text-wrap">{assunto}</span>
                </div>
                <div class="mt-2">
                    {links_html}
                </div>
            </div>
            '''
            html_parts.append(card_html)

        html_parts.append('</div>')
        
        # Se filtrou tudo
        if len(html_parts) <= 2: # Só tem o div inicial e o status
             return '<div class="p-3 text-muted text-center">Nenhum parágrafo encontrado nos documentos selecionados.</div>'
             
        return "".join(html_parts)

if __name__ == "__main__":
    import json
    import os
    import sys
    
    # Adicionar raiz do projeto ao path para garantir que imports funcionem
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from helpers.globals import MODEL_PREFIX, SEMANTIC_RESULTS_FILE

    print("========================================================")
    print("       TESTE DO FORMATADOR SEMÂNTICO")
    print("========================================================")

    # Identificar o arquivo JSON de resultados
    # A variável MODEL_PREFIX dos globals aponta para ".../tub_modelo"
    # O comando do usuario diz "arquivo json em MODEL_PREFIX".
    # Pode ser ".../tub_modelo.json" ou user queria dizer "no diretório de dados".
    # O código original tentava ler semantic_results.json com um path hardcoded.
    
    possible_paths = [
        f"{MODEL_PREFIX}.json",      # Opção 1: Nome do modelo + .json
        SEMANTIC_RESULTS_FILE,       # Opção 2: Arquivo padrão de resultados
    ]
    
    json_path = None
    for p in possible_paths:
        if os.path.exists(p):
            json_path = p
            break
            
    if json_path:
        try:
            print(f"Lendo resultados de: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extrai os dados necessários para a função format_results_to_html
            results = data.get('results', [])
            elapsed = data.get('elapsed', 0.0)
            
            print(f"Processando {len(results)} resultados (tempo busca: {elapsed:.4f}s)...")
            
            # Chama a função estática
            html = SemanticFormatter.format_results_to_html(results, elapsed)
            
            print("\n--- HTML GERADO (Início) ---\n")
            print(html[:1000] + ("..." if len(html) > 1000 else ""))
            print("\n----------------------------")
            
        except Exception as e:
            print(f"Erro ao ler/processar o arquivo JSON: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ERRO: Nenhum arquivo de resultados encontrado.")
        print(f"Procurado em: {possible_paths}")
        print("Dica: Execute uma busca semântica no app para gerar o arquivo 'semantic_results.json'.")
