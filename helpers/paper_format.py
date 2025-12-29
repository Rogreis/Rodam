import sys
import os

# Fix path to run directly
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from helpers.globals import translations_manager, format_table, notes_list
from helpers.format_table import FormatEntry, ParagraphExportHtmlType
from typing import List, Tuple, Optional


class FormatParagraph:
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int):
        self.paper = paper
        self.section = section
        self.paragraph = paragraph

        self.paper_str = str(self.paper).zfill(3)
        self.section_str = str(self.section).zfill(3)
        self.par_str = str(self.paragraph).zfill(3)
        self.id_paragraph = f"p{self.paper_str}_{self.section_str}_{self.par_str}"

        self.format_entry = format_table.get_by_id(paper, section, paragraph)
        self.ident_text = "<small>" + self.format_entry.identication() + "</small>"

        self.text= text
        self.fmt= fmt

class FormatParagraphLeft(FormatParagraph):
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int):
        super().__init__(paper, section, paragraph, text, fmt)
        self.id_paragraph= self.id_paragraph + "_L"

    def format(self) -> str:
        return f'<div id="{self.id_paragraph}" class="p-3 mb-2">{self.ident_text} {self.text}</div>'

    def html_text(self):
        if self.fmt == ParagraphExportHtmlType.BookTitle:
            return f"<h2>{self.text}</h2>"
        elif self.fmt == ParagraphExportHtmlType.PaperTitle:
            return f"<h3>{self.text}</h3>"
        elif self.fmt == ParagraphExportHtmlType.SectionTitle:
            return f"<h4>{self.text}</h4>"
        elif self.fmt == ParagraphExportHtmlType.NormalParagraph:
            return self.format()
        elif self.fmt == ParagraphExportHtmlType.IdentedParagraph:
            return f"<blockquote>{self.format()}</blockquote>"
        elif self.fmt == ParagraphExportHtmlType.Separator:
            return f"<h3 class='text-center'>{self.text}</h3>"
        elif self.fmt == ParagraphExportHtmlType.PartIntroduction:
            return f"<h5>{self.text}</h5>"

class FormatParagraphRight(FormatParagraph):
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int):
        super().__init__(paper, section, paragraph, text, fmt)
        self.id_paragraph= self.id_paragraph + "_R"
        self.css_class = notes_list.get_css_class(paper, section, paragraph)

    def github_link(self, display_text: str) -> str:
        url = f"https://github.com/Rogreis/PtAlternative/blob/correcoes/Doc{self.paper_str}/Par_{self.paper_str}_{self.section_str}_{self.par_str}.md"
        return f'<small><a href="{url}" class="{self.css_class}" target="_blank">{display_text}</a></small>'

    def format(self) -> str:
        link_html = self.github_link(self.ident_text)
        css_class = notes_list.get_css_class(self.paper, self.section, self.paragraph)
        return f'<div id="{self.id_paragraph}" class="p-3 mb-2 {css_class}">{link_html} {self.text}</div>'

    def html_text(self):
        if self.fmt == ParagraphExportHtmlType.BookTitle:
            return f"<h2>{self.text}</h2>"
        elif self.fmt == ParagraphExportHtmlType.PaperTitle:
            return f"<h3>{self.text}</h3>"
        elif self.fmt == ParagraphExportHtmlType.SectionTitle:
            return f"<h4>{self.text}</h4>"
        elif self.fmt == ParagraphExportHtmlType.NormalParagraph:
            return self.format()
        elif self.fmt == ParagraphExportHtmlType.IdentedParagraph:
            return "<blockquote>" + self.format() + "</blockquote>"
        elif self.fmt == ParagraphExportHtmlType.Separator:
            return f"<h3 class='text-center'>{self.text}</h3>"
        elif self.fmt == ParagraphExportHtmlType.PartIntroduction:
            return f"<h5>{self.text}</h5>"


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
    
    paragraphs_en = paper_en.paragraphs
    paragraphs_pt = paper_pt.paragraphs
    
    # Combina os parágrafos
    # Retorno: Lista de tuplas (Text_Left_HTML, Text_Right_HTML)
    
    result = []
    
    # Itera pelo maior tamanho para não perder dado, mas idealmente são iguais
    max_len = max(len(paragraphs_en), len(paragraphs_pt))
    
    for i in range(max_len):
        p_en = paragraphs_en[i] if i < len(paragraphs_en) else None
        p_pt = paragraphs_pt[i] if i < len(paragraphs_pt) else None
        
        # Dados de identificação (usamos do EN como base, mas são iguais)
        paper = p_en.paper if p_en else paperNo
        section = p_en.section if p_en else 0
        paragraph = p_en.paragraph_no if p_en else 0
        text_left = p_en.text if p_en else ""
        text_right = p_pt.text if p_pt else ""

        # Obtém o formato (inteiro), padrão 0 se não existir
        fmt_val = p_en.format if p_en else 0
        fmt = ParagraphExportHtmlType(fmt_val)

        p_left= FormatParagraphLeft(paper, section, paragraph, text_left, fmt)
        p_right= FormatParagraphRight(paper, section, paragraph, text_right, fmt)

        # Adiciona à lista
        result.append((p_left.html_text(), p_right.html_text()))
        
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
        print(f"{'Text Left (HTML)':<60} | {'Text Right (HTML)':<60}")
        print("-" * 60)
        
        for i, row in enumerate(data[:5]):
            html_left, html_right = row
            snippet_left = (html_left[:55] + '...') if len(html_left) > 55 else html_left
            snippet_right = (html_right[:55] + '...') if len(html_right) > 55 else html_right
            print(f"{snippet_left:<60} | {snippet_right:<60}")
            
        print("-" * 60)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
