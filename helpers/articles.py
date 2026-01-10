import os
import markdown
from fastapi.templating import Jinja2Templates

# Setup templates (assuming run from root or app.py context)
# Adjust path logic as necessary if helpers/ is not root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
templates_dir = os.path.join(root_dir, 'templates')
templates = Jinja2Templates(directory=templates_dir)

class ArticlesManager:
    def __init__(self, root_articles_path: str = None):
        self.root_path = root_articles_path

    def render_markdown(self, relative_path: str) -> str:
        if not self.root_path:
             return "<div class='alert alert-danger'>Root path not configured</div>"
             
        full_path = os.path.join(self.root_path, relative_path)
        return self.render_file(full_path)

    def render_file(self, full_path: str) -> str:
        if not os.path.exists(full_path):
            return f"<div class='alert alert-error'>File not found: {full_path}</div>"
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                text = f.read()
            # Extensions for tables, etc
            return markdown.markdown(text, extensions=['extra', 'nl2br'])
        except Exception as e:
            return f"<div class='alert alert-danger'>Error rendering {full_path}: {e}</div>"

    def get_articles_view(self):
        # Specific requirement:
        # Left: artigos/README.md
        # Right: artigos/Theology/moral.md
        
        left_html = self.render_markdown("README.md")
        right_html = self.render_markdown(os.path.join("Theology", "moral.md"))
        
        template = templates.get_template("articles.html")
        return template.render(left_content=left_html, right_content=right_html)

if __name__ == "__main__":
    # Debug routine
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI()
    
    # Assuming the script is run from project root or helpers/
    # We need to find 'artigos' folder.
    # If run from root: 'artigos' is in root.
    # If run from helpers: '../artigos'.
    
    # Dynamic path finding for 'artigos'
    base_dir = os.getcwd() 
    # Check if 'artigos' is here
    if not os.path.exists(os.path.join(base_dir, 'artigos')):
        # Check parent
        if os.path.exists(os.path.join(os.path.dirname(base_dir), 'artigos')):
            base_dir = os.path.dirname(base_dir)
            
    articles_path = os.path.join(base_dir, 'artigos')
    manager = ArticlesManager(articles_path)

    @app.get("/", response_class=HTMLResponse)
    async def index():
        content = manager.get_articles_view()
        
        # Wrapper for standalone viewing
        return f"""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <title>Articles Debug</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                html, body {{ height: 100%; margin: 0; }}
                img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

    print("Starting Articles Debug Server on http://127.0.0.1:8082")
    uvicorn.run(app, host="127.0.0.1", port=8082)
