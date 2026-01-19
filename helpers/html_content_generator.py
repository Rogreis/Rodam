import logging
from fastapi.templating import Jinja2Templates
from helpers.globals import resource_path, translations_manager
from helpers.bs5_treeview import GenerateTreeView
from helpers.paper_format import FormatPaper

logger = logging.getLogger("Rodam")

# Initialize shared resources for this module
# Initialize shared resources for this module
templates = Jinja2Templates(directory=resource_path("templates"))
# paper_formatter = FormatPaper() - REMOVED: Will be instantiated on demand or in methods to ensure globals are ready

class HtmlContentGenerator:
    def __init__(self):
        pass

    @staticmethod
    def _generate_right_content(code: str):
        """
        Helper to generate the right column HTML for a given ID code.
        Returns the HTML string or None if failed/empty.
        """
        try:
            # Instantiate here to ensure globals are loaded
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

    @staticmethod
    def webview_page(secret: str) -> tuple[str, str]:
        '''
            Retorna o HTML para a página webview: code, left_content e right_content  
        '''
        left_content = GenerateTreeView().generate(initial_node=secret)
        print("ToC generated")

        # 3. Conteúdo da direita
        # Tenta carregar o LastSelectedParagraph
        from helpers.globals import global_config
        right_content = None
        
        print(f">>> LastSelectedParagraph: {global_config.LastSelectedParagraph}")
        if global_config.LastSelectedParagraph:
            # Tenta carregar o conteúdo deste parágrafo
            logger.info(f"Loading LastSelectedParagraph for ToC: {global_config.LastSelectedParagraph}")
            print(f"Loading LastSelectedParagraph for ToC: {global_config.LastSelectedParagraph}")
            right_content = HtmlContentGenerator._generate_right_content(global_config.LastSelectedParagraph)

        if not right_content:
            # Fallback default
            right_content = """
            <div class="p-5">
                <h2>Biblioteca Anti-Gravity</h2>
                <p>Selecione um tópico à esquerda para carregar os dados.</p>
            </div>
            """
        return left_content, right_content
