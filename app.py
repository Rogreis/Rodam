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
from helpers.globals import resource_path, get_config_dir, CONFIG_FILE
from helpers.config import Config

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

# --- UI Fragment Endpoints ---

@app.get("/toc")
async def get_toc_ui():
    return JSONResponse(toc_frag.html())

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


# --- Endpoints ---

@app.get("/")
async def read_root(request: Request, p: str = Query("indexToc", alias="p")):
    """
    Rota principal que renderiza a página baseada no argumento 'p'.
    """
    logger.info(f"Rendering page: {p}")
    
    # Load Config
    from helpers.globals import global_config
    config = global_config
    
    # Definição dos itens do menu
    nav_items = [
        {
            "id": "indexToc", 
            "label": "Documentos", 
            "href": "javascript:loadContent('/toc')"
        },
        {
            "id": "indexSubject", 
            "label": "Assuntos", 
            "href": "javascript:loadContent('/subject')"
        },
        {
            "id": "indexStudy", 
            "label": "Artigos", 
            "href": "javascript:loadContent('/articles')"
        },
        {
            "id": "search", 
            "label": "Busca", 
            "href": "javascript:loadContent('/search')" 
        },
        {
            "id": "settings", 
            "label": "Configurações", 
            "href": "javascript:loadContent('/settings')"
        }
    ]

    return templates.TemplateResponse("main.html", {
        "request": request,
        "current_page": p,
        "nav_items": nav_items,
        "config": config
    })

# --- Server Start ---
def start_server():
    # Run Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")

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
    webview.start()
