from helpers.globals import global_config

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
    def html(self):
        from helpers.search_engine import RodamSearch
        
        last_query = global_config.query
        max_results = global_config.SearchMaxResults
        lang_id = global_config.LanguageIdToSearch
        
        # Map Language ID to Code
        # Assuming 1 = PT, 2 = EN based on UI, defaulting to PT
        lang_code = 'pt'
        if lang_id == 2:
            lang_code = 'en'
            
        script = "<script>showSearchModal();</script>"
        
        msg_left = f"<h4>Busca</h4><p>Query: {last_query}</p>"
        
        if not last_query:
            return {
                "left": f"{msg_left} {script}",
                "right": "<div class='alert alert-info'>Use o menu de busca para pesquisar.</div>"
            }

        # Perform Search
        searcher = RodamSearch()
        results = searcher.search(last_query, lang=lang_code, max_results=max_results)
        
        count = len(results)
        msg_left += f"<p>Encontrados: {count} resultados.</p>"
        
        # Format Results for Right Column
        html_right = f"<h3>Resultados: {count}</h3><div class='list-group'>"
        
        if count == 0:
             html_right += "<div class='alert alert-warning'>Nenhum resultado encontrado.</div>"
        else:
            for item in results:
                # item keys: id, title, text, paper, section, paragraph
                ref = item.get('title', '???')
                text = item.get('text', '')
                
                # Highlight logic could be added here or handled by Whoosh highlights if enabled
                # Simple snippet generation
                snippet = text[:300] + "..." if len(text) > 300 else text
                
                # Link logic: We want to load the paragraph when clicked
                # We can use the 'secret' (id) to load content
                secret_code = item.get('id')
                
                html_right += f"""
                <a href="#" class="list-group-item list-group-item-action bg-dark text-white border-secondary mb-2"
                   onclick="loadDynamicContent('{secret_code}'); return false;">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1 text-info">{ref}</h5>
                    </div>
                    <p class="mb-1">{snippet}</p>
                </a>
                """
        
        html_right += "</div>"
        
        return {
            "left": f"{msg_left} {script}",
            "right": html_right
        }
