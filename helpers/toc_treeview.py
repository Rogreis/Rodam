import sys
import os

# Fix path to run directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from helpers.globals import global_config, translations_manager
import json

node_id= -1

# Generate the secret code for a node
def make_code(p_item):
    _p = str(p_item.get('Paper')).zfill(3)
    _s = str(p_item.get('Section')).zfill(3)
    _pn = str(p_item.get('ParagraphNo')).zfill(3)
    code= f"{_p}_{_s}_{_pn}"
    return code

def generate_node_id(): 
    global node_id
    if (node_id == -1):
        node_id= 0
    else:
        node_id= node_id + 1
    return str(node_id).zfill(4)

def fill_paper_entry(paper):
    """
    Processes a Paper object to create a Tree Node (Folder) with Sections (Files).
    """
    paragraphs = paper.get("Paragraphs", [])

    # 1. Identify Paper Title (Folder)
    # Usually ParagraphNo=0 and SectionIndex=0
    p_paper= paragraphs[0].get("Paper", -1)
    # Use single quotes inside f-string for compatibility
    title= f"{p_paper} - {paragraphs[0].get('Text', '<unknown>')}"
    secret_code= make_code(paragraphs[0])
    folder_entry = {
        "id": generate_node_id(),
        "title": title,
        "type": "folder",
        "secret_code": secret_code,
        "children": []
    }

    
    # 2. Iterate for Sections (Files) -> ParagraphNo=0 AND SectionIndex > 0
    for p in paragraphs:
        p_paragraph= p.get("ParagraphNo", -1)
        if (p_paragraph == 0):
            title= p.get("Text", "<unknown>")
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

    # Buffers for each part
    content_intro = []
    content_part_i = []
    content_part_ii = []
    content_part_iii = []
    content_part_iv = []

    if tr.papers:
        for paper in tr.papers:
            # Create the tree node for this paper
            
            node = fill_paper_entry(paper)
            if not node:
                continue
            
            p_idx = int(paper.get("Paragraphs")[0].get("Paper", -1))
            if p_idx == 0:
                content_intro.append(node)
            elif 1 <= p_idx <= 31:
                content_part_i.append(node)
            elif 32 <= p_idx <= 56:
                content_part_ii.append(node)
            elif 57 <= p_idx <= 119:
                content_part_iii.append(node)
            elif 120 <= p_idx <= 196:
                content_part_iv.append(node)

    documents = []

    documents.extend(content_intro)
    documents.extend(content_part_i)
    documents.extend(content_part_ii)
    documents.extend(content_part_iii)
    documents.extend(content_part_iv)
    
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
