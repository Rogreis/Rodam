import sys
import os
import markdown
from typing import Optional

# Fix path to run directly if executed as main script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)
else:
     # When imported, root_dir is relative to where it was imported or calculated
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

class MarkdownRenderer:
    def __init__(self):
        pass

    def render_file(self, file_path: str) -> str:
        """
        Reads a markdown file and converts it to HTML.
        """
        if not os.path.exists(file_path):
            return f"<div class='alert alert-danger'>Arquivo não encontrado: {file_path}</div>"
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Using basic extensions for better formatting
            # 'extra' includes tables, fences, etc.
            html = markdown.markdown(text, extensions=['extra', 'nl2br'])
            return html
        except Exception as e:
            return f"<div class='alert alert-danger'>Erro ao renderizar markdown: {str(e)}</div>"

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI()
    
    import sys

    # Check for command line argument
    if len(sys.argv) < 2:
        print("Uso: python helpers/render_markdown.py <caminho_para_arquivo_markdown>")
        sys.exit(1)

    target_file = sys.argv[1]
    
    # Normalize path for Windows if needed, though python usually handles it
    target_file = os.path.abspath(target_file)
    
    @app.get("/", response_class=HTMLResponse)
    async def index():
        renderer = MarkdownRenderer()
        content = renderer.render_file(target_file)
        
        # Simple HTML wrapper
        html_page = f"""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <title>Markdown Preview: {os.path.basename(target_file)}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 2rem; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 1rem; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                pre {{ background: #f4f4f4; padding: 1rem; border-radius: 5px; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                {content}
            </div>
        </body>
        </html>
        """
        return html_page

    print(f"Iniciando servidor de teste em http://127.0.0.1:8081 para exibir: {target_file}")
    uvicorn.run(app, host="127.0.0.1", port=8081)
