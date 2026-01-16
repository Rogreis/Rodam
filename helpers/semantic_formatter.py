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
    nlp = None # Static class variable for lazy loading

    @staticmethod
    def _generate_github_url(self, display_text: str) -> str:
        return f'<small><a href="javascript:void(0)" onclick="openGithubLink(\'{self.paper_str}\', \'{self.section_str}\', \'{self.par_str}\')" class="{self.css_class}" title="Edita o conteúdo deste parágrafo no github">{display_text}</a></small>'


    @classmethod
    def format_results_to_html(self, results: list, elapsed: float) -> str:
        """
        Formata a lista de resultados da busca semântica em HTML para a coluna esquerda.
        """
        if not results:
            return '<div class="p-3 text-muted text-center">Nenhum resultado encontrado.</div>'
            
        # Lazy Load Spacy
        if self.nlp is None:
            try:
                print("Carregando modelo Spacy pt_core_news_sm...")
                import spacy
                self.nlp = spacy.load("pt_core_news_sm")
            except Exception as e:
                print(f"Erro ao carregar Spacy: {e}")
                self.nlp = None

        html_parts = []
        html_parts.append('<div class="list-group list-group-flush p-2">')
        
        # Header / Statas
        html_parts.append(f'<div class="text-muted small mb-2 text-end">Encontrados {len(results)} resultados em {elapsed:.2f}s</div>')

        for item in results:
            rank = item.get('rank', 0)
            score_pct = item.get('score', 0) * 100
            assunto = item.get('assunto', '')
            links_str = item.get('links', '')
            
            # contaimpressos = 0

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
                        
                        # Recuperar TTranslation
                        from helpers.translations import TTranslations
                        
                        # Obter texto completo (Idioma 0 = Inglês)
                        texto_completo = TTranslations.get_text_content(0, c)
                        
                        # Gerar snippet inteligente (se tivermos o nlp carregado e texto)
                        snippet = ""
                        if self.nlp and texto_completo:
                            snippet = self.gerar_snippet_inteligente(texto_completo, item.get('assunto', ''), self.nlp)

                        # if contaimpressos < 10:
                        #     contaimpressos += 1
                        #     print("\ntexto_completo:", texto_completo)
                        #     print("\nsnippet:", snippet)
                        
                        # onclick chama navigateWithCode (definido no main.html)
                        title_attr = f'data-bs-toggle="tooltip" data-bs-html="true"' if snippet else ""
                        
                        links_html += f'''
                        <a href="#" 
                           {title_attr}
                           onclick="event.preventDefault(); navigateWithCode('{c}', true); return false;">{c}{snippet}</a>
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


    @staticmethod
    def gerar_snippet_inteligente(texto_completo, assunto, nlp_model, janela=5):
        """
        Gera um resumo destacando o assunto e mostrando o contexto ao redor (janela).
        Faz a fusão de trechos se as palavras estiverem próximas.
        
        :param texto_completo: O parágrafo original.
        :param assunto: O termo de busca (assunto limpo).
        :param nlp_model: O modelo Spacy carregado.
        :param janela: Quantas palavras mostrar antes e depois do termo.
        """
        if not nlp_model:
            return texto_completo[:150] + "..." if len(texto_completo) > 150 else texto_completo
            
        doc = nlp_model(texto_completo)
        doc_assunto = nlp_model(assunto)
        
        # 1. Identificar os lemas do assunto (para bater singular/plural/verbos)
        lemas_assunto = {t.lemma_.lower() for t in doc_assunto if not t.is_stop and not t.is_punct}
        
        # 2. Encontrar índices dos tokens que dão match
        indices_match = [t.i for t in doc if t.lemma_.lower() in lemas_assunto]
        
        if not indices_match:
            # Se não achou nada (estranho, pois veio da busca), retorna o início do texto
            return texto_completo[:100] + "..."

        # 3. Criar intervalos (spans) baseados na janela
        # Ex: se achou na pos 10 e janela é 5, o span é (5, 15)
        spans = []
        total_tokens = len(doc)
        
        for i in indices_match:
            inicio = max(0, i - janela)
            fim = min(total_tokens, i + janela + 1)
            spans.append((inicio, fim))
        
        # 4. Mesclar intervalos sobrepostos (A parte mais importante!)
        # Se temos (5, 15) e (12, 20), eles se sobrepõem. Viram um só: (5, 20).
        spans_mesclados = []
        if spans:
            spans_ordenados = sorted(spans, key=lambda x: x[0])
            atual_inicio, atual_fim = spans_ordenados[0]
            
            for i in range(1, len(spans_ordenados)):
                prox_inicio, prox_fim = spans_ordenados[i]
                
                if prox_inicio <= atual_fim: # Há sobreposição ou estão colados
                    atual_fim = max(atual_fim, prox_fim) # Estende o fim
                else:
                    spans_mesclados.append((atual_inicio, atual_fim))
                    atual_inicio, atual_fim = prox_inicio, prox_fim
            
            spans_mesclados.append((atual_inicio, atual_fim))

        # 5. Construir o texto final com ellipses (...) e highlight
        resultado_final = []
        
        for i, (inicio, fim) in enumerate(spans_mesclados):
            trecho = []
            
            # Adiciona reticências se não for o começo absoluto do texto
            if inicio > 0:
                trecho.append("...")
                
            # Percorre os tokens dentro do span para reconstruir o texto
            for token in doc[inicio:fim]:
                # Aplica o highlight se for uma das palavras do assunto
                if token.i in indices_match:
                    trecho.append(f"<mark>{token.text}</mark>{token.whitespace_}")
                else:
                    trecho.append(token.text_with_ws)
            
            # Transforma lista de tokens em string
            fragmento = "".join(trecho).strip()
            resultado_final.append(fragmento)

        # Se o último span não vai até o fim do texto original, adiciona reticências
        if spans_mesclados[-1][1] < total_tokens:
            resultado_final.append("...")

        # Junta todos os fragmentos
        return " ".join(resultado_final)

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
