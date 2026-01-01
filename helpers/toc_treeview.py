import sys
import os

# Fix path to run directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from helpers.globals import global_config, translations_manager
from helpers.paragraph_special import SpecialPartsRepository
import json

node_id= -1

# Generate the secret code for a node
def make_code(p_item):
    _p = str(p_item.paper).zfill(3)
    _s = str(p_item.section).zfill(3)
    _pn = str(p_item.paragraph_no).zfill(3)
    code= f"{_p}_{_s}_{_pn}"
    return code

def generate_node_id(): 
    global node_id
    if (node_id == -1):
        node_id= 0
    else:
        node_id= node_id + 1
    return str(node_id).zfill(4)

def get_paragraph_special():
    repo = SpecialPartsRepository("assets/intro_texts.json")
    
    parts_en = repo.part_titles(0)
    parts_pt = repo.part_titles(2)
    
    return (parts_en, parts_pt)

def fill_paper_entry(paper):
    """
    Processes a Paper object to create a Tree Node (Folder) with Sections (Files).
    """
    paragraphs = paper.paragraphs

    # 1. Identify Paper Title (Folder)
    # Usually ParagraphNo=0 and SectionIndex=0
    first_p = paragraphs[0]
    p_paper = first_p.paper
    
    # Use single quotes inside f-string for compatibility
    title= f"{p_paper} - {first_p.text}"
    secret_code= make_code(first_p)
    folder_entry = {
        "id": generate_node_id(),
        "title": title,
        "type": "folder",
        "secret_code": secret_code,
        "children": []
    }

    
    # 2. Iterate for Sections (Files) -> ParagraphNo=0 AND SectionIndex > 0
    for p in paragraphs:
        p_paragraph= p.paragraph_no
        if (p_paragraph == 0):
            title= p.text
            secret_code= make_code(p)
            file_entry = {
                "id": generate_node_id(),
                "title": title,
                "type": "file",
                "secret_code": secret_code,
            }
            folder_entry["children"].append(file_entry)
            
    return folder_entry


def get_tree_data():
    """
    Retorna a estrutura hierárquica da árvore.
    Suporta N níveis de profundidade.
    """

    # Reinicia a contagem de nodes
    global node_id
    node_id= -1

    # Determine language (Config or Default 0)
    lang_id = getattr(global_config, 'LanguageForToc', 0)
    
    # Load Translation
    tr = translations_manager.get(lang_id)
    if not tr:
        # Attempt load if not cached (though global.py loads them)
        tr = translations_manager.load(lang_id)
    
    if not tr:
        return {
            "left": f"<div class='alert alert-warning'>Translation ID {lang_id} not loaded.</div>", 
            "right": ""
        }

    # Get the parts titles
    parts_en, parts_pt= get_paragraph_special()

    # Get the parts titles
    parts_en, parts_pt = get_paragraph_special()
    current_parts = parts_en if lang_id == 0 else parts_pt

    # Buffers for each part (Now Nodes)
    content_intro = []
    
    # helper to create part node
    def create_part_node(title, code_suffix):
        # Ensure unique web-safe ID
        safe_suffix = code_suffix.lower().strip().replace(" ", "")
        return {
            "id": generate_node_id(), 
            "title": title,
            "type": "folder",
            "secret_code": f"tree_part_{safe_suffix}",
            "children": []
        }

    # Ensure we have titles, fallback if missing
    t_i   = current_parts[0] if len(current_parts) > 0 else "PART I"
    t_ii  = current_parts[1] if len(current_parts) > 1 else "PART II"
    t_iii = current_parts[2] if len(current_parts) > 2 else "PART III"
    t_iv  = current_parts[3] if len(current_parts) > 3 else "PART IV"

    content_part_i   = create_part_node(t_i, "I")
    content_part_ii  = create_part_node(t_ii, "II")
    content_part_iii = create_part_node(t_iii, "III")
    content_part_iv  = create_part_node(t_iv, "IV")

    if tr.papers:
        for paper in tr.papers:
            # Create the tree node for this paper
            
            node = fill_paper_entry(paper)
            if not node:
                continue
            
            p_idx = int(paper.paragraphs[0].paper)
            if p_idx == 0:
                content_intro.append(node)
            elif 1 <= p_idx <= 31:
                content_part_i["children"].append(node)
            elif 32 <= p_idx <= 56:
                content_part_ii["children"].append(node)
            elif 57 <= p_idx <= 119:
                content_part_iii["children"].append(node)
            elif 120 <= p_idx <= 196:
                content_part_iv["children"].append(node)

    documents = []

    documents.extend(content_intro)
    documents.append(content_part_i)
    documents.append(content_part_ii)
    documents.append(content_part_iii)
    documents.append(content_part_iv)
    
    documents_str = json.dumps(documents)

    return documents

def main():
    """
    Função de teste para execução direta do script.
    """
    import sys
    import os
    
    # Adiciona o diretório raiz ao PYTHONPATH para permitir imports de 'helpers'
    # Assume que o script está em /helpers/ e o root está um nível acima
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

    try:
        print("--- Iniciando Teste de get_tree_data ---")
        docs = get_tree_data()
        
        # Serialização embelezada conforme solicitado
        documents_str = json.dumps(docs, indent=4, ensure_ascii=False)
        
        # Salve em disco conforme solicitado
        output_file = os.path.join(current_dir, "debug_tree.json")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(documents_str)
            
        print(f"JSON salvo em: {output_file}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
