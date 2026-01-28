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
from helpers.globals import resource_path, get_data_dir, CONFIG_FILE, global_config
from helpers.config import Config
from helpers.paper_format import FormatPaper
from helpers.bs5_treeview import GenerateTreeView
from helpers.html_content_generator import HtmlContentGenerator
from rodam_exception import RodamException

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

# Initialize Search Engine and Fragments (LAZY)
search_engine = None
paper_formatter = None

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
    logger.info("get_application_title Context code: ", context_code)

    if not context_code:
        return 'Rodam'

    try:
        # 1. Extract Paper ID using new static method
        triplet = Paper.extract_code_triplet(context_code)
        if not triplet: return 'Rodam'
        paper_id, _, _ = triplet
        lang_id = getattr(global_config, 'LanguageForToc', 0)
        translation = helpers.globals.translations_manager.get(lang_id)
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
        RodamException.warning(f"Error generating title: {e}")
        return 'Rodam'


def _generate_right_content(code: str):
    """
    Helper to generate the right column HTML for a given ID code.
    Returns the HTML string or None if failed/empty.
    """
    try:
        global paper_formatter
        if paper_formatter is None:
            paper_formatter = FormatPaper()

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

    left_content, right_content = HtmlContentGenerator.webview_page(initial_node)
 
    
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
            logger.info(f"Paper changed from {global_config.CurrentPaper} to {new_paper_id}. Updating ToC.")
            global_config.CurrentPaper = new_paper_id
            global_config.save()
            
            # Regenerate ToC
            #updated_toc_html = GenerateTreeView().generate()

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
    show_semantics: bool
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
        global_config.ShowSemantics = settings.show_semantics
        
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
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/search")
async def get_search_ui(page: Optional[int] = None):
    from helpers.globals import global_config
    
    # Only open modal automatically if it's the first load (page is None) AND there is no previous query
    is_initial_load = (page is None)
    has_previous_query = bool(global_config.query and global_config.query.strip())
    
    should_open_modal = is_initial_load and not has_previous_query

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

        # Fix: Pass integer directly. 
        # Frontend sends 0 (EN) or 2 (PT).
        # helper.process_form_data casts to int.
        lang_id = global_config.LanguageIdToSearch
        
        # Lazy Init Search Engine
        global search_engine
        if search_engine is None:
             search_engine = RodamSearch()

        results = search_engine.search(
            query_str=global_config.query,
            lang=lang_id,
            max_results=global_config.SearchMaxResults
        )
        return results

    except Exception as e:
        import traceback
        traceback.print_exc()
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

class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 50
    # Search Options
    scopeType: str = "parts" # "parts" or "docs"
    SemanticSearchIntroduction: bool = True
    SemanticSearchPartI: bool = True
    SemanticSearchPartII: bool = True
    SemanticSearchPartIII: bool = True
    SemanticSearchPartIV: bool = True
    SemanticSearchDocumentsList: str = ""

@app.post("/api/semantic_search")
async def semantic_search_endpoint(req: SemanticSearchRequest):
    """
    Executa a busca semântica via SubjectSearch com filtros de escopo.
    """
    from helpers.globals import global_config
    
    if not hasattr(global_config, 'semantic_engine') or global_config.semantic_engine is None:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Motor de busca semântica não incializado."})

    try:
        # 1. Update Config (Persist user choices)
        # Note: 'scopeType' itself isn't stored in global_config explicitly as a preference? 
        # The logic usually relies on "SemanticSearchParts" vs "SemanticSearchDocuments" flags.
        # But the UI sends a 'scopeType' radio value. We should map this to the booleans if possible or just use them for this request.
        # Let's update the specific booleans.
        
        has_changes = False
        if global_config.SemanticQuery != req.query:
             global_config.SemanticQuery = req.query
             has_changes = True
             
        # Config has: SemanticSearchPartI, etc.
        # Map fields
        if global_config.SemanticSearchIntroduction != req.SemanticSearchIntroduction: global_config.SemanticSearchIntroduction = req.SemanticSearchIntroduction; has_changes=True
        if global_config.SemanticSearchPartI != req.SemanticSearchPartI: global_config.SemanticSearchPartI = req.SemanticSearchPartI; has_changes=True
        if global_config.SemanticSearchPartII != req.SemanticSearchPartII: global_config.SemanticSearchPartII = req.SemanticSearchPartII; has_changes=True
        if global_config.SemanticSearchPartIII != req.SemanticSearchPartIII: global_config.SemanticSearchPartIII = req.SemanticSearchPartIII; has_changes=True
        if global_config.SemanticSearchPartIV != req.SemanticSearchPartIV: global_config.SemanticSearchPartIV = req.SemanticSearchPartIV; has_changes=True
        
        if global_config.SemanticSearchDocumentsList != req.SemanticSearchDocumentsList: global_config.SemanticSearchDocumentsList = req.SemanticSearchDocumentsList; has_changes=True
        
        # Max results persistence
        if global_config.SemanticSearchMaxResults != req.top_k: global_config.SemanticSearchMaxResults = req.top_k; has_changes=True
        
        # Based on scopeType, we might want to store which mode was last used?
        # For now, we respect the incoming request for filtering, and update config fields for next time UI load.
        # But UI Logic (SearchModal) handles this by setting "Parts" vs "Docs" bools?
        # In Semantic Search we have a Radio. We should set "SemanticSearchParts" = (scopeType == 'parts')
        new_parts_mode = (req.scopeType == 'parts')
        if global_config.SemanticSearchParts != new_parts_mode:
            global_config.SemanticSearchParts = new_parts_mode
            global_config.SemanticSearchDocuments = not new_parts_mode
            has_changes = True

        if has_changes:
             global_config.save()

        # 2. Build allowed_papers list based on Request
        allowed_papers = []
        
        if req.scopeType == 'parts':
            if req.SemanticSearchIntroduction: allowed_papers.append(0)
            if req.SemanticSearchPartI: allowed_papers.extend(range(1, 32))   # 1 to 31
            if req.SemanticSearchPartII: allowed_papers.extend(range(32, 57)) # 32 to 56
            if req.SemanticSearchPartIII: allowed_papers.extend(range(57, 120)) # 57 to 119
            if req.SemanticSearchPartIV: allowed_papers.extend(range(120, 197)) # 120 to 196
        
        elif req.scopeType == 'docs': # e.g. "manual docs entry"
             doc_str = req.SemanticSearchDocumentsList
             if doc_str:
                parts_str = doc_str.split(';')
                for p_str in parts_str:
                    p_str = p_str.strip()
                    if not p_str: continue
                    # Support both : and - as range separators
                    if ':' in p_str or '-' in p_str:
                        try:
                            p_str_clean = p_str.replace('-', ':')
                            start, end = map(int, p_str_clean.split(':'))
                            allowed_papers.extend(range(start, end + 1))
                        except: pass
                    else:
                        try:
                            allowed_papers.append(int(p_str))
                        except: pass

        # Deduplicate
        allowed_papers = sorted(list(set(allowed_papers)))
        
        # Optimization: If list is empty (Select All implied if Parts mode?) or Full (197 items)
        # However, if allowed_papers is empty AND scope was specific, maybe it means NO papers?
        # Typically in search logic: Empty List = ALL.
        # But here valid selection might result in empty list (uncheck all parts).
        # If user unchecked all parts, allowed_papers is empty. Should return empty?
        # Let's assume: If parts mode and NO check is true -> Empty result.
        # But if docs mode and Empty String -> Empty result?
        # To avoid confusion, let's treat Empty List as "Restrict to Nothing" if scopeType was active?
        # Re-using logic from SearchFragment:
        # "If len(allowed_papers) >= 197 -> None (All)"
        
        # Correction on ranges:
        # Part I: 1-31. range(1, 32)
        # Part II: 32-56. range(32, 57)
        # Part III: 57-119. range(57, 120)
        # Part IV: 120-196. range(120, 197)
        # Total papers: 0 to 196 = 197 papers.
        
        final_filter = None
        if len(allowed_papers) > 0 and len(allowed_papers) < 197:
             final_filter = allowed_papers
        elif len(allowed_papers) == 0:
             # If user explicitly unselected all parts, we probably should return nothing?
             # But usually defaults to ALL on intial load.
             # If req says "parts" mode but all bools false -> intended 0 results.
             if req.scopeType == 'parts' and not (req.SemanticSearchIntroduction or req.SemanticSearchPartI or req.SemanticSearchPartII or req.SemanticSearchPartIII or req.SemanticSearchPartIV):
                   return {"status": "success", "left_html": "<div class='alert alert-warning'>Nenhuma parte selecionada.</div>", "navigate_to": None}
             
             # If docs mode and empty string -> intended 0?
             if req.scopeType == 'docs' and not req.SemanticSearchDocumentsList.strip():
                   # fallback to all? or error?
                   # SearchFragment treats empty list as all?
                   pass

        # Chama a função de busca
        results, elapsed = global_config.semantic_engine.buscar(
            req.query, 
            top_k=req.top_k, 
            allowed_papers=final_filter
        )
        
        # Save results to file for persistence
        from helpers.globals import SEMANTIC_RESULTS_FILE
        import json
        try:
             with open(SEMANTIC_RESULTS_FILE, 'w', encoding='utf-8') as f:
                 json.dump({
                     "results": results, 
                     "elapsed": elapsed,
                     "query": req.query,
                     "timestamp": "" # simplified
                 }, f, indent=4)
        except Exception as save_err:
             RodamException.warning(f"Error saving semantic results: {save_err}")
             
        # ... rest of function ...
        
        # Formatar resultados em HTML (server-side rendering)
        from helpers.semantic_formatter import SemanticFormatter
        formatted_results = SemanticFormatter.format_results_to_html(results, elapsed)
        
        # Envelopar em placeholder para consistência
        results_html = f'<div id="semanticResultsPlaceholder" class="mt-4 w-100">{formatted_results}</div>'
        
        # Gerar a View Completa (com inputs, headers, etc) usando o Fragment
        from ui_fragments.subject import SubjectFragment
        left_html = SubjectFragment.render_view(results_html)
        
        # Determinar melhor candidato para navegação (1º link do 1º resultado)
        navigate_to = None
        if results:
            # Precisamos percorrer até achar um permitido
            for item in results:
                links_str = item.get('links', '')
                codes = links_str.split()
                for c in codes:
                     # Check validade
                     if final_filter:
                         # Parse ID
                         try:
                             pid = int(c.split(':')[0])
                             if pid in final_filter:
                                 navigate_to = c
                                 break
                         except: pass
                     else:
                         navigate_to = c
                         break
                if navigate_to: break

        return {
            "status": "success",
            "left_html": left_html,
            "navigate_to": navigate_to,
            "elapsed": elapsed
        }
    except Exception as e:
        logger.error(f"Erro na busca semântica: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

class SemanticSortRequest(BaseModel):
    sort_relevance: bool

@app.post("/api/update_semantic_sort")
async def update_semantic_sort(req: SemanticSortRequest):
    from helpers.globals import global_config, SEMANTIC_RESULTS_FILE
    import json
    import os
    
    try:
        # 1. Update Config
        if global_config.SemanticSearchSortOrder != req.sort_relevance:
            global_config.SemanticSearchSortOrder = req.sort_relevance
            global_config.save()
            
        # 2. Reload Results
        if not os.path.exists(SEMANTIC_RESULTS_FILE):
             return {"status": "error", "message": "No search results found to sort."}
             
        with open(SEMANTIC_RESULTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get('results', [])
            elapsed = data.get('elapsed', 0)
            
        # 3. Re-render
        from helpers.semantic_formatter import SemanticFormatter
        formatted_results = SemanticFormatter.format_results_to_html(results, elapsed)
        
        results_html = f'<div id="semanticResultsPlaceholder" class="mt-4 w-100">{formatted_results}</div>'
        
        from ui_fragments.subject import SubjectFragment
        # No script needed usually, as we are already on the page
        left_html = SubjectFragment.render_view(results_html, script="")
        
        return {
            "status": "success",
            "left_html": left_html
        }
            
    except Exception as e:
        logger.error(f"Error sorting semantic results: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

class LogParagraphRequest(BaseModel):
    code: str

@app.post("/api/log_paragraph_click")
async def log_paragraph_click_endpoint(req: LogParagraphRequest):
    """
    Salva o parágrafo no histórico recente sem gerar conteúdo HTML HTML.
    """
    try:
        from helpers.globals import global_config
        from helpers.paper_format import FormatPaper
        
        # Validar formato
        triplet = FormatPaper.extract_code_triplet(req.code)
        if triplet:
            paper, section, paragraph = triplet
            canonical_ref = f"{paper}:{section}-{paragraph}"
            
            # Adicionar ao histórico
            global_config.add_recent_paragraph(canonical_ref)
            
            # Atualiza o último selecionado também (para persistência entre sessões)
            global_config.LastSelectedParagraph = canonical_ref
            global_config.save()
            
            return {"status": "success", "canonical_code": canonical_ref}
            
        return {"status": "error", "message": "Invalid code"}
    except Exception as e:
        logger.error(f"Error logging paragraph: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/window_loaded")
async def window_loaded():
    """
    Called by the frontend when the main window/local is fully loaded.
    """
    logger.info("Frontend reports: Window Loaded")
    from helpers.globals import global_config
    
    # Placeholder for future logic
    if global_config.IsInicialization:
        logger.info("Executing Initialization Logic...")
        global_config.IsInicialization = False
        global_config.save()
    
    left_content, right_content = HtmlContentGenerator.webview_page(global_config.LastSelectedParagraph)
 
    return {
        "left": left_content,
        "right": right_content,
        "navbar_title": get_application_title(global_config.LastSelectedParagraph),
        "current_query": global_config.query
    }

@app.post("/api/check_semantic_resources")
async def check_semantic_resources_endpoint():
    try:
        from helpers.github_requests import GitHubRequests
        # Run in thread/background to avoid blocking? 
        # The user said "isto pode demorar minutos", so we probably shouldn't block the async loop if it's synchronous IO.
        # But 'requests' is synchronous.
        # Ideally we'd use run_in_executor or similar.
        # For simplicity in this stack, we'll just run it. The user interface "alert" is displayed.
        
        downloader = GitHubRequests()
        success, errors = downloader.check_semantic_files()
        
        if success:
             return {"status": "success"}
        else:
             return {"status": "error", "message": "; ".join(errors)}
    except Exception as e:
        logger.error(f"Error checking semantic resources: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


# --- Endpoints ---

@app.get("/")
async def read_root(request: Request, p: str = Query("indexToc", alias="p")):
    """
    Rota principal que renderiza a página baseada no argumento 'p'.
    Executa na inicialização ou reload.
    Verifica LastVisitedPage e LastSelectedParagraph para restaurar o estado anterior.
    """
    # Load Config
    from helpers.globals import global_config
    config = global_config

    # 1. Verificar LastVisitedPage para restaurar a última página visitada
    # Se o usuário acessou a raiz (p="indexToc"), tentamos restaurar o estado salvo.
    if p == "indexToc":
        if config.LastVisitedPage and config.LastVisitedPage != "settings":
             # Restaura a página salva (ex: "indexToc", "indexSubject", "search")
             p = config.LastVisitedPage

    logger.info(f"Rendering page: {p} (LastVisited: {config.LastVisitedPage})")
    
    # Definição dos itens do menu
    nav_items = [
        {
            "id": "indexToc", 
            "label": "Documentos", 
            "title": "Abre o recurso de navegação por documentos", 
            "href": "javascript:loadContent('/toc', 'indexToc')"
        },
        {
            "id": "indexSemantic", 
            "label": "Assuntos", 
            "title": "Abre o recurso de navegação por assuntos", 
            "href": "javascript:loadContent('/subject', 'indexSemantic')",
            "visible": config.ShowSemantics
        },
        {
            "id": "indexArticles", 
            "label": "Artigos", 
            "title": "Abre o recurso de navegação por artigos", 
            "href": "javascript:loadContent('/articles', 'indexArticles')",
            "visible": False
        },
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

    # 2. Verificar LastSelectedParagraph para definir o título e contexto inicial
    # O "jump" para o parágrafo ocorre no carregamento assíncrono do conteúdo (via /toc -> _generate_right_content)
    initial_title = get_application_title(config.LastSelectedParagraph)

    if config.IsInicialization:
        config.IsInicialization = False
        await get_toc_ui(request)

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
    import os
    import sys
    import helpers.globals
    from helpers.globals import global_config 
    from helpers.subject_search import SubjectSearch
    from helpers.globals import MODEL_PREFIX
    
    # --- GLOBAL INITIALIZATION ---
    # Must be called before any major component usage
    helpers.globals.initialize()

    # Init Semantic Search Engine (Lazy - it loads on first 'buscar')
    global_config.semantic_engine = SubjectSearch(MODEL_PREFIX)

    logger.info("Starting Rodam (FastAPI + Whoosh)...")
    
    # Start Server Thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Give it a moment
    time.sleep(1.5)
    
    # Start WebView
    webview.create_window('Rodam', 'http://127.0.0.1:5000', maximized=True, text_select=True)

    # 2. O Controle do "Inspecionar Elemento"
    # debug=True (Desenvolvimento): Quando o usuário (ou você) clica com o botão direito na janela do app, aparece o menu "Inspect" ou "Inspecionar". Isso abrirá as ferramentas de desenvolvedor (DevTools) acopladas àquela janela.
    # debug=False (Produção): O botão direito é desativado ou não mostra o menu de inspeção. O usuário vê apenas o app, sem saber como ele foi feito.
    webview.start(debug=False)
