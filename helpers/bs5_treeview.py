import sys
import os
import json
from fastapi.templating import Jinja2Templates

template_name= "bs5_treeview.html"

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

# Initialize templates - Configured to look at root/templates
templates_dir = os.path.join(root_dir, 'templates')
templates = Jinja2Templates(directory=templates_dir)

# Ensure tojson filter is available (Flask has it by default, Jinja2 standalone needs it)
def tojson_filter(value):
    return json.dumps(value)

templates.env.filters['tojson'] = tojson_filter

from typing import Optional, List, Dict, Any
from helpers.translations import Paper, Paragraph
from helpers.globals import global_config, translations_manager
from helpers.paragraph_special import SpecialPartsRepository


class TreeNode:

    def __init__(self, node_id, text):
        self.id = node_id
        self.text = text
        self.nodes = []

    def add_child(self, child_node):
        if isinstance(child_node, TreeNode):
            self.nodes.append(child_node)

    def to_dict(self):
        result = {
            "id": self.id,
            "text": self.text,
            "href": self.href
        }
        if self.nodes:
            result["nodes"] = [node.to_dict() for node in self.nodes]
        return result

class TreeNodePart(TreeNode):
    def __init__(self, node_id, text):
        # Chama o construtor da classe base
        super().__init__(node_id, text)
        self.href = ""

class TreeNodeParagraph(TreeNode):
    def __init__(self, paragraph_instance: Paragraph):
        # Validação de segurança em tempo de execução
        if not isinstance(paragraph_instance, Paragraph):
            raise TypeError("O argumento 'paragraph_instance' deve ser uma instância da classe Paragraph")
        
        if paragraph_instance.section == 0 and paragraph_instance.paragraph_no == 0:
            title= f"{paragraph_instance.paper} - {paragraph_instance.text}"
        else:
            title= paragraph_instance.text

        super().__init__(paragraph_instance.secret(), title)
        self.href = paragraph_instance.secret()


class GenerateTreeView:
    def __init__(self):
        # Determine language (Config or Default 0)
        self.lang_id = getattr(global_config, 'LanguageForToc', 0)
        # Load Translation
        self.translation = translations_manager.get(self.lang_id)

    def _generate_root_part_nodes(self):
        repo = SpecialPartsRepository("assets/intro_texts.json")
        
        parts_en = repo.part_titles(0)
        parts_pt = repo.part_titles(2)
        current_parts = parts_en if self.lang_id == 0 else parts_pt

        # Ensure we have titles, fallback if missing
        t_i   = current_parts[0] if len(current_parts) > 0 else "PART I"
        t_ii  = current_parts[1] if len(current_parts) > 1 else "PART II"
        t_iii = current_parts[2] if len(current_parts) > 2 else "PART III"
        t_iv  = current_parts[3] if len(current_parts) > 3 else "PART IV"

        self.content_part_i   = TreeNodePart("PartI", t_i)
        self.content_part_ii  = TreeNodePart("PartII", t_ii)
        self.content_part_iii = TreeNodePart("PartIII", t_iii)
        self.content_part_iv  = TreeNodePart("PartIV", t_iv)

       
    def _generate_paper_nodes(self, node: TreeNode, paper: Paper):
        """
        Processes a Paper object to create a Tree Node (Folder) with Sections (Files).
        """
        paragraphs = paper.paragraphs

        first_p = paragraphs[0]
        mainNode= TreeNodeParagraph(first_p)
        for paragraph in paragraphs:
            if (paragraph.section > 0 and paragraph.paragraph_no == 0):  # Generate toc entry only until sections
                mainNode.add_child(TreeNodeParagraph(paragraph))

        node.add_child(mainNode)


    def _generate_children_part_nodes(self, node, paper_no_init, paper_no_end):
        for paperNo in range(paper_no_init, paper_no_end + 1):
            paper = self.translation.papers[paperNo]
            node.add_child(self._generate_paper_nodes(node, paper))


    def generate(self, template_name_override: Optional[str] = None, initial_node=None):
        if not self.translation:
            return f"<div class='alert alert-warning'>Translation ID {self.lang_id} not loaded.</div>"

        # Buffers for each part (Now Nodes)
        content_intro = []
        template_name = "bs5_treeview.html"

        self._generate_root_part_nodes()
        content_intro.append(self.content_part_i)
        self._generate_children_part_nodes(self.content_part_i, 1, 31)
        content_intro.append(self.content_part_ii)
        self._generate_children_part_nodes(self.content_part_ii, 32, 56)
        content_intro.append(self.content_part_iii)
        self._generate_children_part_nodes(self.content_part_iii, 57, 119)
        content_intro.append(self.content_part_iv)
        self._generate_children_part_nodes(self.content_part_iv, 120, 196)

        # Serialização para lista de dicionários
        tree_data = [node.to_dict() for node in content_intro]
        
        # Determine strict template to use
        # Priority: Override > Global var > Default
        target_template = template_name_override if template_name_override else template_name
        
        # Using Jinja2Templates from FastAPI to render string (not response)
        t = templates.get_template(target_template)
        return t.render({"data": tree_data, "initial_node": initial_node})


if __name__ == '__main__':
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index():
        # Force the debug template here
        return GenerateTreeView().generate(template_name_override="bs5_treeviewDebug.html")

    print("Starting Uvicorn server on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)
