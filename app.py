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
# --- Configuration & Paths ---

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
    elif sys.platform == 'darwin':
        base = os.path.join(os.environ.get('HOME'), 'Library', 'Application Support')
    else:
        base = os.path.join(os.environ.get('HOME'), '.config')
    return os.path.join(base, 'Rodam')

CONFIG_FILE = os.path.join(get_config_dir(), 'Rodam.json')

# Ensure config dir
if not os.path.exists(get_config_dir()):
    os.makedirs(get_config_dir())

# Import UI Fragments
from ui_fragments import (
    TocFragment,
    SubjectFragment,
    ArticlesFragment,
    SearchFragment,
    SettingsFragment
)

# 1. Configuração Básica
import logging
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
class SearchRequest(BaseModel):
    query: str
    lang: str = 'pt'
    sort: str = 'sequential'
    scope_type: str = 'parts'
    parts: List[str] = []
    docs: str = ''
    max_results: int = 100
    page_size: int = 50

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
    # Save Settings
    config = request.dict()
    # Remove query from saved config to keep it generic
    config_to_save = config.copy()
    if 'query' in config_to_save:
        del config_to_save['query']
        
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

    # Perform Search
    if not request.query:
        return []

    return search_engine.search(
        query_str=request.query,
        lang=request.lang,
        max_results=request.max_results
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
        "nav_items": nav_items
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
