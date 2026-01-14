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
from typing import List, Tuple, Optional, Union

SEPARATOR_TEXT= "* * * * * *"

class FormatParagraph:
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int, is_highlighted: bool = False):
        self.paper = paper
        self.section = section
        self.paragraph = paragraph
        self.is_highlighted = is_highlighted

        self.paper_str = str(self.paper).zfill(3)
        self.section_str = str(self.section).zfill(3)
        self.par_str = str(self.paragraph).zfill(3)
        self.id_paragraph = f"p{self.paper_str}_{self.section_str}_{self.par_str}"

        self.format_entry = format_table.get_by_id(paper, section, paragraph)
        if self.format_entry:
            self.ident_text = "<small>" + self.format_entry.identication() + "</small>"
        else:
            self.ident_text = f"<small>{paper}:{section}.{paragraph}</small>"

        self.text= text
        self.fmt= fmt

    def book_title_text(self, id_paragraph, text):
        return self.format_nolink_text(id_paragraph, f"<h2>{self.text}</h2>")

    def format_nolink_text(self, id_paragraph, text, ident_text= ""):
        if (ident_text != ""):
            ident_text= ident_text + " "
            
        style = ""
        if self.is_highlighted:
            style = 'style="border: 2px solid var(--highlight-color, magenta); border-radius: 5px;"'
            
        return f'<div id="{id_paragraph}" class="p-3 mb-2" {style}>{ident_text}{text}</div>'

class FormatParagraphLeft(FormatParagraph):
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int, is_highlighted: bool = False):
        super().__init__(paper, section, paragraph, text, fmt, is_highlighted)
        self.id_paragraph= self.id_paragraph + "_L"

    def html_text(self):
        if self.fmt == ParagraphExportHtmlType.BookTitle:
            return self.format_nolink_text(self.id_paragraph, f"<h2>{self.text}</h2>")

        elif self.fmt == ParagraphExportHtmlType.PaperTitle:
            return self.format_nolink_text(self.id_paragraph, f"<h3>{self.text}</h3>")

        elif self.fmt == ParagraphExportHtmlType.SectionTitle:
            return self.format_nolink_text(self.id_paragraph, f"<h4>{self.text}</h4>")

        elif self.fmt == ParagraphExportHtmlType.NormalParagraph:
            return self.format_nolink_text(self.id_paragraph, f"{self.text}", self.ident_text)

        elif self.fmt == ParagraphExportHtmlType.IdentedParagraph:
            return self.format_nolink_text(self.id_paragraph, f"<blockquote>{self.ident_text} {self.text}</blockquote>")

        elif self.fmt == ParagraphExportHtmlType.Separator:
            return f"<h3>" + SEPARATOR_TEXT + "</h3>"

        elif self.fmt == ParagraphExportHtmlType.PartIntroduction:
            return f"<h5>{self.text}</h5>"

class FormatParagraphRight(FormatParagraph):
    def __init__(self, paper: int, section: int, paragraph: int, text: str, fmt:int, is_highlighted: bool = False):
        super().__init__(paper, section, paragraph, text, fmt, is_highlighted)
        self.id_paragraph= self.id_paragraph + "_R"
        self.css_class = notes_list.get_css_class(paper, section, paragraph)

    def _generate_github_url(self, display_text: str) -> str:
        return f'<small><a href="javascript:void(0)" onclick="openGithubLink(\'{self.paper_str}\', \'{self.section_str}\', \'{self.par_str}\')" class="{self.css_class}" title="Edita o conteúdo deste parágrafo no github">{display_text}</a></small>'

    def format_link_text(self, display_text: str, text= "") -> str:
            
        style = ""
        if self.is_highlighted:
            style = 'style="border: 2px solid var(--highlight-color, magenta); border-radius: 5px;"'
            
        return f'<div id="{self.id_paragraph}" class="p-3 mb-2 {self.css_class}" {style}>{self._generate_github_url(display_text)} {text}</div>'

    def html_text(self):
        if self.fmt == ParagraphExportHtmlType.BookTitle:
            return self.format_nolink_text(self.id_paragraph, f"<h2>{self.text}</h2>")

        elif self.fmt == ParagraphExportHtmlType.PaperTitle:
            return self.format_link_text(f"<h3>{self.text}</h3>")

        elif self.fmt == ParagraphExportHtmlType.SectionTitle:
            return self.format_link_text(f"<h4>{self.text}</h4>")

        elif self.fmt == ParagraphExportHtmlType.NormalParagraph:
            return self.format_link_text(self.ident_text, self.text)

        elif self.fmt == ParagraphExportHtmlType.IdentedParagraph:
            return self.format_link_text(f"<blockquote>{self.ident_text} {self.text}</blockquote>")

        elif self.fmt == ParagraphExportHtmlType.Separator:
            return f"<h3>" + SEPARATOR_TEXT + "</h3>"
            
        elif self.fmt == ParagraphExportHtmlType.PartIntroduction:
            return f"<h5>{self.text}</h5>"



import re

class FormatPaper:
    def __init__(self):
        # Garante a carga das traduções, como solicitado
        self.tr_en = translations_manager.load(0)
        self.tr_pt = translations_manager.load(2)

    @staticmethod
    def extract_code_triplet(code: str) -> Optional[Tuple[int, int, int]]:
        """
        Parses a string code, removes letters, splits by separators, 
        and returns a tuple of 3 integers (Paper, Section, Paragraph).
        """
        # Remove letters
        clean_code = re.sub(r'[a-zA-Z]', '', str(code))
        
        # Split using the requested regex
        tokens = re.split(r'[_,.\- :]+', clean_code.strip())
        
        # Filter empty strings resulting from split
        tokens = [t for t in tokens if t]
        
        if len(tokens) >= 3:
            return (int(tokens[0]), int(tokens[1]), int(tokens[2]))
        
        return None

    def format_paragraph(self, code, is_target: bool = False) -> Tuple[str, str]:
        """
        Formats a single paragraph pair (EN/PT) into HTML tuple.
        Arg code is a reference to a paragraph
        """
        # Resolve ID from triplet
        paper, section, paragraph = 0, 0, 0
        triplet = FormatPaper.extract_code_triplet(str(code))
        if triplet:
            paper, section, paragraph = triplet
        else:
            print(f"Código inválido {code}")
            return ("", "ERRO: Código inválido {code}")

        # Load specific paragraph objects
        # Note: Triplet is 1-indexed or 0-indexed? 
        # extract_code_triplet parses user strings (usually 1-indexed display?) or internal IDs?
        # The internal objects use .paper, .section, .paragraph properties.
        # We need to find the paragraph in the list that matches these numbers.
        # Accessing by index `papers[paper]` provides the Paper object.
        # Accessing the specific paragraph inside the paper requires iteration or knowing the index.
        # Since we have (paper, section, paragraph), we can use `get_paragraph_from_string` logic or similar iteration.
        
        # Access Paper Objects
        if paper < 0 or paper >= len(self.tr_en.papers):
             return ("", "")

        paper_obj_en = self.tr_en.papers[paper]
        paper_obj_pt = self.tr_pt.papers[paper]
        
        # Find Paragraph Logic
        # Assuming triplet reflects (P, S, ParaNo) matching properties of objects
        p_en = None
        p_pt = None
        
        # Optimized search vs Iteration? 
        # Using `get_paragraph_from_string` logic implemented locally for speed/direct match
        for p in paper_obj_en.paragraphs:
            if p.paper == paper and p.section == section and p.paragraph_no == paragraph:
                p_en = p
                break
        
        for p in paper_obj_pt.paragraphs:
            if p.paper == paper and p.section == section and p.paragraph_no == paragraph:
                p_pt = p
                break
        
        text_left = p_en.text if p_en else ""
        text_right = p_pt.text if p_pt else ""

        # Obtém o formato (inteiro), padrão 0 se não existir
        fmt_val = p_en.format if p_en else 0
        fmt = ParagraphExportHtmlType(fmt_val)

        p_left= FormatParagraphLeft(paper, section, paragraph, text_left, fmt, is_target)
        p_right= FormatParagraphRight(paper, section, paragraph, text_right, fmt, is_target)

        return (p_left.html_text(), p_right.html_text())

    def paper_display(self, code) -> Optional[List[Tuple[str, str]]]:
        # Resolve PaperNo/Triplet from item
        print(f"DEBUG: paper_display called with item={code!r} type={type(code)}")
        
        result = []  # Returned data collection

        # Extract PaperNo, ignoring Section and Paragraph
        triplet = FormatPaper.extract_code_triplet(str(code))
        
        paperNo = None
        target_triplet = None
        if triplet:
            paperNo, target_section, target_paragraph = triplet
            target_triplet = (paperNo, target_section, target_paragraph)
        else:
            result.append("", f"ERRO: Código inválido {code}")
            return result
        
        # Access translations loaded in __init__
        if not self.tr_en or not self.tr_pt:
            result.append("", "ERRO: Erro ao carregar traduções")
            return result

        # Verifica limites
        if paperNo is None or paperNo < 0 or paperNo >= len(self.tr_en.papers):
            result.append("", f"ERRO: Número de documento inválido {paperNo}")
            return result

        paper_en = self.tr_en.papers[paperNo]
        paper_pt = self.tr_pt.papers[paperNo]

        if isinstance(code, str):
            # If we have a full string, try to find the specific paragraph object
            
            p_instance_en = paper_en.get_paragraph_from_string(code)
            
            if p_instance_en:
                 from helpers.globals import global_config
                 # Save the reference of the selected paragraph to config
                 ref = p_instance_en.reference()
                 
                 if global_config.LastSelectedParagraph != ref:
                     global_config.add_recent_paragraph(ref)
        
        paragraphs_en = paper_en.paragraphs
        paragraphs_pt = paper_pt.paragraphs
        
       
        # Itera pelo maior tamanho
        max_len = max(len(paragraphs_en), len(paragraphs_pt))
        
        for i in range(max_len):
            p_en = paragraphs_en[i] if i < len(paragraphs_en) else None
            p_pt = paragraphs_pt[i] if i < len(paragraphs_pt) else None
            
            # Construct a code for the current paragraph to match new format_paragraph signature
            # Use p_en as source of truth for ID, or p_pt if p_en missing
            current_code = ""
            current_triplet = None
            
            if p_en:
                current_code = f"{p_en.paper}_{p_en.section}_{p_en.paragraph_no}"
                current_triplet = (p_en.paper, p_en.section, p_en.paragraph_no)
            elif p_pt:
                current_code = f"{p_pt.paper}_{p_pt.section}_{p_pt.paragraph_no}"
                current_triplet = (p_pt.paper, p_pt.section, p_pt.paragraph_no)
            
            # Determine if this is the target paragraph
            is_target = False
            if target_triplet and current_triplet:
                is_target = (target_triplet == current_triplet)

            if current_code:
                result.append(self.format_paragraph(current_code, is_target))
            
        return result

def main():
    print("--- Testing paper_display(1) ---")
    try:
        # Test with Paper 1 (usually "The Universal Father")
        fmt = FormatPaper()
        data = fmt.paper_display(1)
        
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
