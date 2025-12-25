from flask import Flask, send_from_directory, request, jsonify
import os
import glob
from bs4 import BeautifulSoup
import re
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Initialize Flask app
# static_folder will be set dynamically or we use send_from_directory with explicit paths
app = Flask(__name__, static_folder=resource_path('.'))

# Global Search Index
SEARCH_INDEX = []

def load_content():
    """Parses all content/Doc*.html files and builds the search index."""
    print("Loading content for search index...")
    global SEARCH_INDEX
    SEARCH_INDEX = []
    
    # Use resource_path for globbing
    search_path = resource_path(os.path.join('content', 'Doc*.html'))
    files = glob.glob(search_path)
    print(f"Searching in {search_path}, found {len(files)} files")
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            rows = soup.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    # English Column
                    div_en = cols[0].find('div')
                    if not div_en: continue
                    
                    id_str = div_en.get('id') # e.g., p001_000_001
                    if not id_str: continue
                    
                    # Parse ID
                    parts = id_str.split('_')
                    if len(parts) != 3: continue
                    
                    try:
                        paper = int(parts[0][1:])
                        section = int(parts[1])
                        paragraph = int(parts[2])
                    except ValueError:
                        continue
                        
                    text_en = div_en.get_text(strip=True)
                    
                    # Portuguese Column
                    div_pt = cols[1].find('div')
                    text_pt = ""
                    if div_pt:
                        text_pt = div_pt.get_text(strip=True)
                    
                    SEARCH_INDEX.append({
                        'id': id_str,
                        'paper': paper,
                        'section': section,
                        'paragraph': paragraph,
                        'text_en': text_en,
                        'text_pt': text_pt
                    })
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
    print(f"Index built with {len(SEARCH_INDEX)} paragraphs.")

@app.route('/')
def index():
    return send_from_directory(resource_path('.'), 'indexToc.html')

@app.route('/<path:path>')
def serve_static(path):
    file_path = resource_path(path)
    if os.path.exists(file_path):
        return send_from_directory(resource_path('.'), path)
    return "File not found", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    results = []
    # Simple case-insensitive contains search
    for item in SEARCH_INDEX:
        if query in item['text_pt'].lower() or query in item['text_en'].lower():
            # Highlight match ? (Optional, maybe later)
            results.append(item)
            if len(results) > 50: # Limit results
                break
    
    return jsonify(results)

@app.route('/save_paragraph', methods=['POST'])
def save_paragraph():
    data = request.json
    paper = data.get('paper')
    section = data.get('section')
    paragraph = data.get('paragraph')
    new_text = data.get('text')
    
    if paper is None or section is None or paragraph is None or new_text is None:
        return jsonify({'error': 'Missing fields'}), 400
        
    # Construct Filename
    filename = f"Doc{str(paper).zfill(3)}.html"
    filepath = resource_path(os.path.join('content', filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
        
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # IDs are on the EN div: pPPP_SSS_PPP
        id_str = f"p{str(paper).zfill(3)}_{str(section).zfill(3)}_{str(paragraph).zfill(3)}"
        
        div_en = soup.find('div', id=id_str)
        if not div_en:
             return jsonify({'error': 'Paragraph ID not found'}), 404
             
        # Find the parent row
        td_en = div_en.find_parent('td')
        tr = td_en.find_parent('tr')
        
        # Get the PT col (index 1)
        td_pt = tr.find_all('td')[1]
        div_pt = td_pt.find('div')
        
        # Update text
        # Strategy: We want to preserve the <a ...><small>...</small></a> part if it exists
        # But for now, we assume the user is editing the 'text' part.
        # Let's see structure again:
        # <div ...> <a ...><small>1:0-1 (21.1)</small></a>  TEXT IS HERE </div>
        
        # Simple approach: Rebuild the innerHTML.
        # Find the anchor/small tag
        anchor = div_pt.find('a')
        
        # Create new content
        # Note: 'new_text' from frontend should be just the text, or HTML?
        # User said "search and editing of paragraphs".
        # Assuming plain text update for now, but preserving the ID tag.
        
        if anchor:
            # Clear div content but keep anchor
            # This is tricky with BS4.
            # Let's clean the div and re-append.
            anchor_soup = BeautifulSoup(str(anchor), 'html.parser').body.next
            div_pt.clear()
            div_pt.append(anchor_soup)
            div_pt.append("  " + new_text) # Add space
        else:
            div_pt.string = new_text
            
        # Write back
        # Use soup.prettify() or str(soup)?
        # HTML files might have specific formatting. str(soup) usually works but might change formatting.
        # Given it's a "Bootstrap 5" site, might be robust enough.
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        # Update Index
        for item in SEARCH_INDEX:
            if item['id'] == id_str:
                item['text_pt'] = new_text
                break
                
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import sys
import threading
import webview
import time

# Initialize Index on Start
load_content()

def start_flask():
    # Run Flask without the reloader to avoid MainThread issues in pywebview
    app.run(debug=False, port=5000, use_reloader=False)

if __name__ == '__main__':
    print("Starting Standalone App...")
    
    # Start Flask in a background thread
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    
    # Give Flask a moment to start
    time.sleep(1)
    
    # Create the standalone window
    # Validates if local server is up, otherwise points to static file or error
    webview.create_window('Rodam', 'http://localhost:5000', maximized=True)
    webview.start()
