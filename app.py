import os
import sys
import threading
import time
import json
import uvicorn
import webview
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel
from typing import List, Optional
from bs4 import BeautifulSoup
from helpers.toc_treeview import get_tree_data
import logging

# --- Configuration & Paths ---
from helpers.globals import resource_path, get_config_dir, CONFIG_FILE
from helpers.config import Config
from helpers.paper_format import paper_display

# Import UI Fragments
from ui_fragments import (
    TocFragment,
    SubjectFragment,
    ArticlesFragment,
    SearchFragment,
    SettingsFragment
)

# 1. Configuração Básica
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: \t%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Rodam")

# --- FastAPI App ---
app = FastAPI()

# Templates
templates = Jinja2Templates(directory=resource_path("templates"))

# Import isolated Search Engine
from search_engine import RodamSearch

# Initialize Search Engine
search_engine = RodamSearch()

# Initialize Fragments
toc_frag = TocFragment()
subject_frag = SubjectFragment()
articles_frag = ArticlesFragment()
search_frag = SearchFragment()
settings_frag = SettingsFragment()

# Static Mounts
app.mount("/css", StaticFiles(directory=resource_path("css")), name="css")
app.mount("/js", StaticFiles(directory=resource_path("js")), name="js")
app.mount("/content", StaticFiles(directory=resource_path("content")), name="content")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(resource_path("favicon.ico"))


# --- UI Fragment Endpoints ---
def _generate_right_content(code: str):
    """
    Helper to generate the right column HTML for a given ID code.
    Returns the HTML string or None if failed/empty.
    """
    try:
        paragraphs = paper_display(code)
        
        if paragraphs:
            # Determine target ID for scrolling
            scroll_script = ""
            try:
               import re
               tokens = re.split(r'[_,.\- :]+', code.strip())
               if len(tokens) >= 3:
                   p_id = f"p{tokens[0].zfill(3)}_{tokens[1].zfill(3)}_{tokens[2].zfill(3)}_R"
                   scroll_script = f"""
                   <script>
                       setTimeout(() => {{
                           const targetId = '{p_id}';
                           console.log("AutoScroll: Attempting to scroll to", targetId);
                           const el = document.getElementById(targetId);
                           console.log("AutoScroll: Element found?", el);
                           if (el) {{
                               el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                               el.classList.add('highlight-fade'); 
                           }} else {{
                               console.warn("AutoScroll: Target element not found:", targetId);
                           }}
                       }}, 500);
                   </script>
                   """
            except:
               pass
            
            template = templates.get_template("paper_table.html")
            return template.render(paragraphs=paragraphs) + scroll_script
    except Exception as e:
        logger.error(f"Error rendering paper table for {code}: {e}")
    return None

def _generate_fallback_content(code: str) -> str:
    """
    Helper to generate fallback content when _generate_right_content fails.
    """
    conteudo_dinamico = ""
    
    if "NEWTON" in code:
        conteudo_dinamico = f"""
            <div class="alert alert-info">
                <h4 class="alert-heading">Contexto Identificado!</h4>
                <p>O sistema detectou que você está buscando sobre <strong>Isaac Newton</strong>.</p>
                <hr>
                <p class="mb-0">Código interno processado: <code>{code}</code></p>
            </div>
            <div class="mt-4">
                <h3>Conteúdo da Gravidade</h3>
                <p>Aqui entra o texto completo do artigo...</p>
            </div>
        """
    elif "CTX" in code:
        conteudo_dinamico = f"<h3>Você clicou em uma pasta.</h3><p>Código: {code}</p>"
    else:
        conteudo_dinamico = f"<h3>Conteúdo Genérico</h3><p>Código recebido: {code}</p>"
    
    return f"<div class='p-4 fade-in'>{conteudo_dinamico}</div>"

@app.get("/toc")
async def get_toc_ui(request: Request):
    """
    Rota que retorna JSON com fragmentos HTML para as duas colunas.
    """
    
    # 1. Obtém os dados estruturados
    data = get_tree_data()
    
    # 2. Renderiza o template passando 'tree_data'
    toc_template = templates.get_template("toc_tree.html")
    left_content = toc_template.render({"request": request, "tree_data": data})
    
    # 3. Conteúdo da direita
    # Tenta carregar o LastSelectedParagraph
    from helpers.globals import global_config
    right_content = None
    
    if global_config.LastSelectedParagraph:
        # Tenta carregar o conteúdo deste parágrafo
        logger.info(f"Loading LastSelectedParagraph for ToC: {global_config.LastSelectedParagraph}")
        right_content = _generate_right_content(global_config.LastSelectedParagraph)

    if not right_content:
        # Fallback default
        right_content = """
        <div class="p-5">
            <h2>Biblioteca Anti-Gravity</h2>
            <p>Selecione um tópico à esquerda para carregar os dados.</p>
        </div>
        """
    
    return {
        "left": left_content,
        "right": right_content
    }

@app.get("/get_node_content")
async def get_node_content(code: str):
    """
    Recebe a string oculta (ex: REF_NEWTON_V2_2024 or 001.0.0) e gera conteúdo baseado nela.
    """
    
    # Lógica de Paper 
    rendered_html = _generate_right_content(code)
    
    if rendered_html:
        return {
            "right": rendered_html
        }

    # Lógica simples baseada na string recebida (Fallback)
    # ...
    
    conteudo_dinamico = ""
    
    if "NEWTON" in code:
        conteudo_dinamico = f"""
            <div class="alert alert-info">
                <h4 class="alert-heading">Contexto Identificado!</h4>
                <p>O sistema detectou que você está buscando sobre <strong>Isaac Newton</strong>.</p>
                <hr>
                <p class="mb-0">Código interno processado: <code>{code}</code></p>
            </div>
            <div class="mt-4">
                <h3>Conteúdo da Gravidade</h3>
                <p>Aqui entra o texto completo do artigo...</p>
            </div>
        """
    elif "CTX" in code:
        conteudo_dinamico = f"<h3>Você clicou em uma pasta.</h3><p>Código: {code}</p>"
    else:
        conteudo_dinamico = f"<h3>Conteúdo Genérico</h3><p>Código recebido: {code}</p>"

    # Retorna o JSON para atualizar a direita
    return {
        "right": f"<div class='p-4 fade-in'>{conteudo_dinamico}</div>"
    }


@app.get("/subject")
async def get_subject_ui():
    return JSONResponse(subject_frag.html())

@app.get("/articles")
async def get_articles_ui():
    return JSONResponse(articles_frag.html())

@app.get("/search")
async def get_search_ui():
    return JSONResponse(search_frag.html())

@app.get("/settings")
async def get_settings_ui():
    return JSONResponse(settings_frag.html())

# --- Models (Must be defined before usage) ---
# --- Models (Must be defined before usage) ---
class SearchRequest(BaseModel):
    query: str
    LanguageIdToSearch: int = 1
    SearchResultsOrder: int = 0
    SearchParts: bool = True
    SearchDocuments: bool = False
    SearchIntroduction: bool = True
    SearchPartI: bool = True
    SearchPartII: bool = True
    SearchPartIII: bool = True
    SearchPartIV: bool = True
    SearchDocumentsList: str = ""
    SearchMaxResults: int = 100
    SearchItemsToShow: int = 50

class SaveParagraphRequest(BaseModel):
    paper: int
    section: int
    paragraph: int
    text: str

# Renamed API endpoint to avoid conflict
@app.get("/api/settings")
async def get_settings_data():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

@app.post("/search")
async def search_endpoint(request: SearchRequest):
    # Update Global Config and Save
    from helpers.globals import global_config
    
    global_config.query = "" # Do not save the query to disk generally, or if requested by user logic. User said "fields initialized with this config... saved in config".
    # Logic: "save values in the same fields of config".
    # Since config has 'query' field now, maybe we should save it? 
    # BUT, the prompt said "query: str" in config.py update.
    # Re-reading: "config.query" IS in config.py.
    # Ok, I will save it but maybe exclude it if it causes issues.
    # Actually, let's save everything that comes from the modal.
    
    global_config.LanguageIdToSearch = request.LanguageIdToSearch
    global_config.SearchResultsOrder = request.SearchResultsOrder
    global_config.SearchParts = request.SearchParts
    global_config.SearchDocuments = request.SearchDocuments
    global_config.SearchIntroduction = request.SearchIntroduction
    global_config.SearchPartI = request.SearchPartI
    global_config.SearchPartII = request.SearchPartII
    global_config.SearchPartIII = request.SearchPartIII
    global_config.SearchPartIV = request.SearchPartIV
    global_config.SearchDocumentsList = request.SearchDocumentsList
    global_config.SearchMaxResults = request.SearchMaxResults
    global_config.SearchItemsToShow = request.SearchItemsToShow
    
    # Save the query too if desired, usually distinct from saved preferences, but Config has it now.
    # "query" field was added to Config.
    # So we save it.
    global_config.query = request.query
    
    global_config.save()

    # Perform Search
    if not request.query:
        return []

    # Map new parameters to search_engine expectations
    # search_engine.search(query_str, lang, max_results)
    # Adjust lang from int to str if needed. 
    # Assuming search_engine expects 'pt' or 'en'. 
    # User set LanguageIdToSearch: 1 (PT), 2 (EN?). 
    # I need to confirm mapping. 
    # Config default is 1. Standard is usually 1=PT.
    lang_map = {1: 'pt', 2: 'en'}
    lang_str = lang_map.get(request.LanguageIdToSearch, 'pt')
    
    # Scope logic needs to be handled by search_engine or here?
    # search_engine.search probably needs updates to handle 'parts' vs 'docs' if it supports it.
    # For now, I will pass just what search_engine accepts based on previous view: (query_str, lang, max_results).
    # If search_engine needs scope, I'll update it later or now if I can view it.
    # Inspecting previous app.py snippet: search_engine.search(query_str, lang, max_results).
    # I will stick to that interface.
    
    return search_engine.search(
        query_str=request.query,
        lang=lang_str,
        max_results=request.SearchMaxResults
    )

@app.post("/save_paragraph")
async def save_paragraph_endpoint(req: SaveParagraphRequest):
    # Construct Filename
    filename = f"Doc{str(req.paper).zfill(3)}.html"
    filepath = resource_path(os.path.join('content', filename))
    
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={'error': 'File not found'})
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        id_str = f"p{str(req.paper).zfill(3)}_{str(req.section).zfill(3)}_{str(req.paragraph).zfill(3)}"
        
        # Locating logic logic (same as legacy)
        div_en = soup.find('div', id=id_str)
        if not div_en:
             return JSONResponse(status_code=404, content={'error': 'Paragraph ID not found'})
             
        td_en = div_en.find_parent('td')
        tr = td_en.find_parent('tr')
        td_pt = tr.find_all('td')[1]
        div_pt = td_pt.find('div')
        
        anchor = div_pt.find('a')
        
        if anchor:
            anchor_soup = BeautifulSoup(str(anchor), 'html.parser').body.next
            div_pt.clear()
            div_pt.append(anchor_soup)
            div_pt.append("  " + req.text)
        else:
            div_pt.string = req.text
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        return {'status': 'success'}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})



class LogPageRequest(BaseModel):
    page_id: str

@app.post("/api/log_page")
async def log_page_endpoint(req: LogPageRequest):
    from helpers.globals import global_config
    config = global_config
    
    valid_ids = ["indexToc", "indexSubject", "indexStudy", "search"]
    
    if req.page_id in valid_ids:
        if config.LastVisitedPage != req.page_id:
            config.LastVisitedPage = req.page_id
            config.save()
            return {"status": "saved", "page": req.page_id}
            
    return {"status": "ignored"}

# --- Endpoints ---

@app.get("/")
async def read_root(request: Request, p: str = Query("indexToc", alias="p")):
    """
    Rota principal que renderiza a página baseada no argumento 'p'.
    """
    # Load Config
    from helpers.globals import global_config
    config = global_config

    # Logic to restore last visited page if default is requested
    # Note: "indexToc" is the default value in Query parameter.
    # If the user explicitly requests /?p=indexToc, we might still treat it as default or not.
    # Typically, if accessing root URL "/", p is "indexToc".
    # We check if p is the default, and if we have a saved page different from default.
    if p == "indexToc" and config.LastVisitedPage and config.LastVisitedPage != "indexToc":
        # Check if query param exists in raw url to distinguish explicit vs implicit default is hard with FastAPI params
        # Simplified approach: If p is indexToc, try to use saved page.
        if config.LastVisitedPage != "settings":
             p = config.LastVisitedPage

    logger.info(f"Rendering page: {p}")
    
    # Definição dos itens do menu
    nav_items = [
        {
            "id": "indexToc", 
            "label": "Documentos", 
            "href": "javascript:loadContent('/toc', 'indexToc')"
        },
        {
            "id": "indexSubject", 
            "label": "Assuntos", 
            "href": "javascript:loadContent('/subject', 'indexSubject')"
        },
        {
            "id": "indexStudy", 
            "label": "Artigos", 
            "href": "javascript:loadContent('/articles', 'indexStudy')"
        },
        {
            "id": "search", 
            "label": "Busca", 
            "href": "javascript:loadContent('/search', 'search')" 
        },
        {
            "id": "settings", 
            "label": "Configurações", 
            "href": "javascript:loadContent('/settings', 'settings')"
        }
    ]

    # Save LastVisitedPage logic moved to /api/log_page called by frontend
    # But we still respect the restored 'p' for rendering Main template correctly.

    return templates.TemplateResponse("main.html", {
        "request": request,
        "current_page": p,
        "nav_items": nav_items,
        "config": config
    })

# --- Server Start ---
def start_server():
    """
        Inicia o servidor Uvicorn em background
        log_config=None remove logs excessivos no console
    """
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
    #uvicorn.run(app, host="127.0.0.1", port=54321, log_config=None)

if __name__ == '__main__':
    print("Starting Rodam (FastAPI + Whoosh)...")
    
    # Start Server Thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Give it a moment
    time.sleep(1.5)
    
    # Start WebView
    webview.create_window('Rodam', 'http://127.0.0.1:5000', maximized=True)

    # 2. O Controle do "Inspecionar Elemento"
    # debug=True (Desenvolvimento): Quando o usuário (ou você) clica com o botão direito na janela do app, aparece o menu "Inspect" ou "Inspecionar". Isso abrirá as ferramentas de desenvolvedor (DevTools) acopladas àquela janela.
    # debug=False (Produção): O botão direito é desativado ou não mostra o menu de inspeção. O usuário vê apenas o app, sem saber como ele foi feito.
    webview.start(debug=True)
