import sys
import os

# Fix path to run directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from helpers.globals import translations_manager, format_table
from helpers.translations import FormatEntry
from typing import List, Tuple, Optional

def github_link(paper: int, section: int, paragraphNo: int, display_text: str = None) -> str:
    paper_str = str(paper).zfill(3)
    section_str = str(section).zfill(3)
    par_str = str(paragraphNo).zfill(3)
    url = f"https://github.com/Rogreis/PtAlternative/blob/correcoes/Doc{paper_str}/Par_{paper_str}_{section_str}_{par_str}.md"
    text = display_text if display_text else "Git"
    return f'<a href="{url}" target="_blank">{text}</a>'

def paper_display(paperNo: int) -> Optional[List[Tuple[int, int, int, str, str, int, Optional[FormatEntry]]]]:
    # 1. Verifica se a tradução solicitada existe (neste caso, usamos a padrão em PT-BR id=2 para validar o índice)
    # A lógica aqui assume que as traduções estão sincronizadas em estrutura.
    
    # Carrega Inglês (0) e Português (2)
    # Se não estiverem carregadas, o 'load' as carrega. Se já estiverem, retorna do cache.
    tr_en = translations_manager.load(0)
    tr_pt = translations_manager.load(2)
    
    if not tr_en or not tr_pt:
        return None # Erro ao carregar traduções

    # Verifica limites. O array 'papers' geralmente contém 197 papéis (0 a 196)
    # ATENÇÃO: A estrutura pode variar. Se for uma lista direta:
    if paperNo < 0 or paperNo >= len(tr_en.papers):
        return None

    paper_en = tr_en.papers[paperNo]
    paper_pt = tr_pt.papers[paperNo]
    
    # Garante que estamos olhando para o mesmo Paper (segurança)
    # No json original, dentro de "Paragraphs", o primeiro item é o título do Paper?
    # Vamos assumir que as listas de parágrafos estão alinhadas.
    
    paragraphs_en = paper_en.get("Paragraphs", [])
    paragraphs_pt = paper_pt.get("Paragraphs", [])
    
    # Combina os parágrafos
    # Retorno: Lista de tuplas (Paper, Section, ParagraphNo, Text_Left (EN), Text_Right (PT), Format, FormatEntry)
    
    result = []
    
    # Itera pelo maior tamanho para não perder dado, mas idealmente são iguais
    max_len = max(len(paragraphs_en), len(paragraphs_pt))
    
    for i in range(max_len):
        p_en = paragraphs_en[i] if i < len(paragraphs_en) else {}
        p_pt = paragraphs_pt[i] if i < len(paragraphs_pt) else {}
        
        # Dados de identificação (usamos do EN como base, mas são iguais)
        paper_idx = p_en.get("Paper", paperNo)
        section_idx = p_en.get("Section", 0)
        paragraph_no = p_en.get("ParagraphNo", 0)
        
        text_left = p_en.get("Text", "")
        text_right = p_pt.get("Text", "")
        
        # Obtém o formato (inteiro), padrão 0 se não existir
        fmt = p_en.get("Format", 0)

        # Obtém FormatEntry da tabela global
        format_entry = format_table.get_by_id(paper_idx, section_idx, paragraph_no)

        if format_entry:
             ident_text = format_entry.identication()
             link_html = github_link(paper_idx, section_idx, paragraph_no, ident_text)
             text_left = f"{ident_text} {text_left}"
             text_right = f"{link_html} {text_right}"
        else:
             # Fallback if no format entry found, though ideally shouldn't happen for valid existing papers
             text_left = f"{text_left}"
             text_right = f"{text_right}"
            
        # Adiciona à lista
        result.append((paper_idx, section_idx, paragraph_no, text_left, text_right, fmt, format_entry))
        
    return result

def main():
    print("--- Testing paper_display(1) ---")
    try:
        # Test with Paper 1 (usually "The Universal Father")
        data = paper_display(1)
        
        if data is None:
            print("Error: paper_display returned None (Check translations loading).")
            return
            
        print(f"Total items returned: {len(data)}")
        print("-" * 60)
        print(f"{'Paper':<5} {'Sec':<5} {'Par':<5} {'Format':<6} {'FmtEntry':<30} {'Text Snippet (EN)'}")
        print("-" * 60)
        
        for i, row in enumerate(data[:20]):
            # row = (Paper, Section, ParagraphNo, Text_Left, Text_Right, Format, FormatEntry)
            paper, section, par, text_en, text_pt, fmt, f_entry = row
            snippet = (text_en[:40] + '...') if len(text_en) > 40 else text_en
            f_entry_str = str(f_entry) if f_entry else "None"
            print(f"{paper:<5} {section:<5} {par:<5} {fmt:<6} {f_entry_str:<30} {snippet}")
            
        print("-" * 60)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
