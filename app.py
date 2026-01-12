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
import logging

# --- Configuration & Paths ---
from helpers.globals import resource_path, get_data_dir, CONFIG_FILE, global_config, translations_manager
from helpers.config import Config
from helpers.paper_format import FormatPaper
from helpers.bs5_treeview import GenerateTreeView

# Import UI Fragments
from ui_fragments import (

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
import helpers.globals
helpers.globals.logger = logger

# --- FastAPI App ---
app = FastAPI()

# Templates
templates = Jinja2Templates(directory=resource_path("templates"))

# Import isolated Search Engine
from helpers.search_engine import RodamSearch

# Initialize Search Engine
search_engine = RodamSearch()

# Initialize FormatPaper
paper_formatter = FormatPaper()

# Initialize Fragments

subject_frag = SubjectFragment()
articles_frag = ArticlesFragment()
search_frag = SearchFragment()
settings_frag = SettingsFragment()

# Static Mounts
app.mount("/css", StaticFiles(directory=resource_path("css")), name="css")
app.mount("/js", StaticFiles(directory=resource_path("js")), name="js")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(resource_path("favicon.ico"))


# --- UI Fragment Endpoints ---

def get_application_title(context_code: str = None) -> str:
    """
    Retorna o título para a barra de navegação.
    Pode ser customizado com base no contexto (código do parágrafo, etc).
    """
    import helpers.globals
    from helpers.translations import Paper
    print("get_application_title Context code: ", context_code)

    if not context_code:
        return 'Rodam'

    try:
        # 1. Extract Paper ID using new static method
        triplet = Paper.extract_code_triplet(context_code)
        if not triplet: return 'Rodam'
        paper_id, _, _ = triplet
        lang_id = getattr(global_config, 'LanguageForToc', 0)
        translation = translations_manager.get(lang_id)
        if not translation: return 'Rodam'
        if paper_id < 0 or paper_id >= len(translation.papers):
            return 'Rodam'
      
        paper = translation.papers[paper_id]
        if paper:
            paper.extract_title()
            if lang_id == 0:
                return f"Paper {paper.title}"
            else:
                return f"Documento {paper.title}"
        else:
            return 'Rodam'
    except Exception as e:
        print(f"Error generating title: {e}")
        return 'Rodam'


def _generate_right_content(code: str):
    """
    Helper to generate the right column HTML for a given ID code.
    Returns the HTML string or None if failed/empty.
    """
    try:
        paragraphs = paper_formatter.paper_display(code)
        
        if paragraphs:
            # Determine target ID for scrolling
            scroll_script = ""
            try:
               from helpers.translations import Paper
               triplet = Paper.extract_code_triplet(code)
               if triplet:
                   p0, p1, p2 = triplet
                   p_id = f"p{str(p0).zfill(3)}_{str(p1).zfill(3)}_{str(p2).zfill(3)}_R"
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
        import traceback
        traceback.print_exc()
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
    # data = get_tree_data()
    
    # 2. Renderiza o template passando 'tree_data'
    # toc_template = templates.get_template("bs5_treeview.html")
    # left_content = toc_template.render({"request": request, "tree_data": data})
    print("Generating ToC")
    # Determine initial node from LastSelectedParagraph
    from helpers.globals import global_config
    initial_node = None
    if global_config.LastSelectedParagraph:
        # We likely want to select the Paper node, typically XXX_000_000
        # Parsing logic:
        try:
             # Using same logic as extract_code_triplet, simplified or reused
             # We can use the Paper class method if available or simple split
             # Assuming '56:1-2', splitting by non-digits
             import re
             tokens = re.split(r'[_,.\- :]+', global_config.LastSelectedParagraph.strip())
             if len(tokens) >= 1:
                 p_id = int(tokens[0])
                 # Construct valid href for Paper Node: e.g. 056_000_000
                 initial_node = f"{p_id:03d}_000_000"
        except:
             pass

    left_content = GenerateTreeView().generate(initial_node=initial_node)
    print("ToC generated")
    if left_content:
        print(f"DEBUG app.py line 159 - left_content start: {left_content[:500]}")
    else:
        print("DEBUG app.py line 159 - left_content is empty or None")
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
        "right": right_content,
        "navbar_title": get_application_title(global_config.LastSelectedParagraph),
        "current_query": global_config.query
    }

@app.get("/get_node_content")
async def get_node_content(code: str):
    """
    Recebe a string oculta (ex: REF_NEWTON_V2_2024 or 001.0.0) e gera conteúdo baseado nela.
    """
    
    # Lógica de Paper 
    rendered_html = _generate_right_content(code)
    
    if rendered_html:
        from helpers.globals import global_config
        return {
            "right": rendered_html,
            "current_query": global_config.query
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
    from helpers.globals import global_config
    return {
        "right": f"<div class='p-4 fade-in'>{conteudo_dinamico}</div>",
        "current_query": global_config.query
    }


@app.get("/subject")
async def get_subject_ui():
    return JSONResponse(subject_frag.html())

@app.get("/articles")
async def get_articles_ui():
    return JSONResponse(articles_frag.html())

@app.get("/api/navigate")
async def navigate_to_paragraph(code: str, request: Request):
    """
    Validates the code, updates recent history, and returns content.
    Updates ToC if the paper ID changes.
    """
    try:
        # 1. Validate using static method
        triplet = FormatPaper.extract_code_triplet(code)
        if not triplet:
             return JSONResponse(status_code=400, content={"status": "error", "message": "Código inválido."})
             
        # Import config inside
        from helpers.globals import global_config
        
        # Detect if paper changed
        paper_id_str = triplet[0]
        try:
            new_paper_id = int(paper_id_str)
        except:
             new_paper_id = 0

        updated_toc_html = None
        
        # Check if paper changed
        if new_paper_id != global_config.CurrentPaper:
            print(f"Paper changed from {global_config.CurrentPaper} to {new_paper_id}. Updating ToC.")
            global_config.CurrentPaper = new_paper_id
            global_config.save()
            
            # Regenerate ToC
            # Regenerate ToC
            updated_toc_html = GenerateTreeView().generate()

        # 2. Update Config (Recent History)
        paper, section, paragraph = triplet
        canonical_ref = f"{paper}:{section}-{paragraph}"
        
        global_config.add_recent_paragraph(canonical_ref)
        
        # 3. Generate Right Content
        right_content = _generate_right_content(canonical_ref)
        
        if right_content:
            # Create Code Secret for TreeView (format 000_000_000)
            # Always force 000 for paragraph part to match TreeView nodes (Section granularity)
            code_secret = f"{str(paper).zfill(3)}_{str(section).zfill(3)}_000"

            return {
                "status": "success",
                "right": right_content,
                "final_code": canonical_ref,
                "final_code_secret": code_secret,
                "current_query": global_config.query,
                "updated_toc": updated_toc_html, # May be None or HTML string
                "navbar_title": get_application_title(canonical_ref)
            }
        else:
             return JSONResponse(status_code=404, content={"status": "error", "message": "Conteúdo não encontrado."})
             
    except Exception as e:
        logger.error(f"Error navigating: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

class SettingsModel(BaseModel):
    highlight_color: str
    dark_mode: bool
    show_bg_colors: bool
    splitter_position: Optional[int] = None
    language_for_toc: Optional[int] = None

@app.post("/api/save_settings")
async def save_settings(settings: SettingsModel):
    try:
        # Batch update: disable autosave to prevent 3 sequential disk writes
        current_autosave = getattr(global_config, '_autosave', True)
        global_config._autosave = False
        
        global_config.HighlightColor = settings.highlight_color
        global_config.DarkMode = settings.dark_mode
        global_config.ShowBgColors = settings.show_bg_colors
        
        if settings.language_for_toc is not None:
             global_config.LanguageForToc = settings.language_for_toc
        
        if settings.splitter_position is not None:
            global_config.SplitterPosition = settings.splitter_position
        
        global_config._autosave = current_autosave
        global_config.save() # Explicit save once
        
        return {"status": "success"}
    except Exception as e:
        import traceback
        traceback.print_exc() # Print full stack trace to console
        print(f"Error saving settings: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/search")
async def get_search_ui(page: Optional[int] = None):
    should_open_modal = (page is None)
    current_page = page if page is not None else 1
    return JSONResponse(search_frag.html(page=current_page, open_modal=should_open_modal, templates=templates))

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

@app.post("/search")
async def search_endpoint(request: Request):
    """
    Receives search form data, updates config via Helper, and performs search.
    """
    from helpers.globals import global_config
    from helpers.search_modal import SearchModalHelper

    try:
        data = await request.json()
        
        # 1. Update Config using Helper
        SearchModalHelper.process_form_data(data, global_config)
        
        # 2. Perform Search using values now in valid type in global_config
        # Note: global_config.query is updated by helper.
        
        if not global_config.query:
            return []

        lang_map = {1: 'pt', 2: 'en'}
        lang_str = lang_map.get(global_config.LanguageIdToSearch, 'pt')
        
        return search_engine.search(
            query_str=global_config.query,
            lang=lang_str,
            max_results=global_config.SearchMaxResults
        )

    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})





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
            "title": "Abre o recurso de navegação por documentos", 
            "href": "javascript:loadContent('/toc', 'indexToc')"
        },
        # {
        #     "id": "indexSubject", 
        #     "label": "Assuntos", 
        #     "title": "Abre o recurso de navegação por assuntos", 
        #     "href": "javascript:loadContent('/subject', 'indexSubject')"
        # },
        # {
        #     "id": "indexStudy", 
        #     "label": "Artigos", 
        #     "title": "Abre o recurso de navegação por artigos", 
        #     "href": "javascript:loadContent('/articles', 'indexStudy')"
        # },
        {
            "id": "search", 
            "label": "Busca", 
            "title": "Abre o recurso de busca", 
            "href": "javascript:loadContent('/search', 'search')" 
        },
        {
            "id": "settings", 
            "label": "Configurações", 
            "title": "Abre o recurso de configurações", 
            "href": "javascript:openSettingsModal()"
        }
    ]

    # Save LastVisitedPage logic moved to /api/log_page called by frontend
    # But we still respect the restored 'p' for rendering Main template correctly.

    # Calculate Initial Title
    initial_title = get_application_title(config.LastSelectedParagraph)

    return templates.TemplateResponse("main.html", {
        "request": request,
        "current_page": p,
        "nav_items": nav_items,
        "config": config,
        "initial_title": initial_title
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
    from helpers.github_requests import GitHubRequests
    from helpers.globals import TUB_FILES_DIR
    import os
    import sys

    print("Checking critical data files...")
    downloader = GitHubRequests()
    downloader.sync_data_files()
    
    # Verify critical files exist
    required_files = ["FormatTable.gz", "TR000.zip", "TR002.zip"]
    missing_files = []
    
    for f in required_files:
        if not os.path.exists(os.path.join(TUB_FILES_DIR, f)):
            missing_files.append(f)
            
    if missing_files:
        print(f"CRITICAL ERROR: The following required files are missing in {TUB_FILES_DIR}:")
        for f in missing_files:
            print(f" - {f}")
        print("Application cannot start. Please check your internet connection and try again.")
        sys.exit(1)

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
    webview.start(debug=False)
