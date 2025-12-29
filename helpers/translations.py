import os
import sys
import zipfile
import json
from typing import Dict, Any, Optional, List
from enum import IntEnum
import re



class Paragraph:
    def __init__(self, data: Dict[str, Any]):
        self.translation_id = data.get("TranslationID")
        self.paper = data.get("Paper")
        self.pk_seq = data.get("PK_Seq")
        self.section = data.get("Section")
        self.paragraph_no = data.get("ParagraphNo")
        self.page = data.get("Page")
        self.line = data.get("Line")
        self.text = data.get("Text")
        self.format = data.get("Format")

    # Generate the secret code for a paragraph
    def secret(self):
        _p = str(self.paper).zfill(3)
        _s = str(self.section).zfill(3)
        _pn = str(self.paragraph_no).zfill(3)
        code= f"{_p}_{_s}_{_pn}"
        return code

    # Generate the reference for a paragraph
    def reference(self):
        _p = str(self.paper)
        _s = str(self.section)
        _pn = str(self.paragraph_no)
        code= f"{_p}:{_s}-{_pn}"
        return code

    # Generate the full_reference code for a paragraph
    def full_reference(self):
        return reference() + f"{self.page}.{self.line}"


    def __repr__(self):
        return f"<Paragraph {self.paper}:{self.section}.{self.paragraph_no}>"

class Paper:
    def __init__(self, data: Dict[str, Any]):
        self.paragraphs = [Paragraph(p) for p in data.get("Paragraphs", [])]

    def get_paragraph_from_string(self, ref_string: str) -> Optional[Paragraph]:
        """
        Parses a string containing paper, section, and paragraph numbers 
        separated by { '_', ',', '-', '.', ' ', ':'} and returns the 
        corresponding Paragraph object.
        """
        # Split by the defined separators
        tokens = re.split(r'[_,.\- :]+', ref_string.strip())
        # Filter empty strings
        tokens = [t for t in tokens if t]
        
        if len(tokens) < 3:
            return None
            
        try:
            target_paper = int(tokens[0])
            target_section = int(tokens[1])
            target_paragraph = int(tokens[2])
        except ValueError:
            return None
            
        for p in self.paragraphs:
            if (p.paper == target_paper and 
                p.section == target_section and 
                p.paragraph_no == target_paragraph):
                return p
        return None

    def __getitem__(self, item: int) -> Paragraph:
        return self.paragraphs[item]

    def __len__(self) -> int:
        return len(self.paragraphs)

    def __repr__(self):
        return f"<Paper with {len(self.paragraphs)} paragraphs>"

class Translation:
    """
    Represents the translation object structure found in translation.json.
    """
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        # Mapping attributes to JSON fields
        self.language_id = data.get("LanguageID")
        self.description = data.get("Description")
        self.tub = data.get("TUB")
        self.culture_id = data.get("CultureID")
        self.use_bold = data.get("UseBold")
        self.right_to_left = data.get("RightToLeft")
        self.paper_translation = data.get("PaperTranslation")
        self.introductory_texts = data.get("IntroductoryTexts", [])
        self.papers = [Paper(p) for p in data.get("Papers", [])]

    def __getitem__(self, item):
        return self.data.get(item)

class TTranslations:
    """
    Manages a collection of Translation objects, keyed by LanguageID.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._translations: Dict[int, Translation] = {}

    def load(self, language_id: int) -> Optional[Translation]:
        """
        Loads a translation from the TR<languageId>.zip file in base_dir.
        If already loaded, returns the cached instance.
        """
        if language_id in self._translations:
            return self._translations[language_id]

        zip_filename = f"TR{language_id:03d}.zip"
        zip_path = os.path.join(self.base_dir, zip_filename)

        if not os.path.exists(zip_path):
            print(f"Translation file not found: {zip_path}")
            return None

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                with zf.open('translation.json') as f:
                    data = json.load(f)
                    translation = Translation(data)
                    self._translations[language_id] = translation
                    return translation
        except Exception as e:
            print(f"Error loading translation from {zip_path}: {e}")
            return None

    def get(self, language_id: int) -> Optional[Translation]:
        """
        Retrieves a loaded translation.
        """
        return self._translations.get(language_id)



def main():
    # Only for testing purposes
    # We need to manually calculate the path here since we don't import from globals
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
    elif sys.platform == 'darwin':
        base = os.path.join(os.environ.get('HOME'), 'Library', 'Application Support')
    else:
        base = os.path.join(os.environ.get('HOME'), '.config')
    
    config_dir = os.path.join(base, 'Rodam')
    tub_files_dir = os.path.join(config_dir, 'TUB_Files')

    # Variable to define which translation to load for testing
    test_language_id = 2
    
    print(f"--- Loading Translation ID: {test_language_id} ---")
    
    manager = TTranslations(tub_files_dir)
    translation = manager.load(test_language_id)
    
    if not translation:
        print("Failed to load translation.")
        return

    print("\n--- General Properties ---")
    print(f"LanguageID: {translation.language_id}")
    print(f"Description: {translation.description}")
    print(f"TUB: {translation.tub}")
    print(f"CultureID: {translation.culture_id}")
    print(f"UseBold: {translation.use_bold}")
    print(f"RightToLeft: {translation.right_to_left}")
    print(f"PaperTranslation: {translation.paper_translation}")
    
    print("\n--- IntroductoryTexts (First 4) ---")
    # Pretty print the first 4 items
    for item in translation.introductory_texts[:4]:
        print(json.dumps(item, ensure_ascii=True))

    print("\n--- Papers (First 4) ---")
    for i, paper in enumerate(translation.papers[:4]):
        print(f"Paper {i}: {paper}")
        if len(paper) > 0:
            print(f"  First Paragraph: {paper[0]}")
            print(f"  Last Paragraph: {paper[-1]}")


    print("\n--- Testing FormatTable ---")
    
    # Calculate path to assets/FormatTable.json assuming script is in /helpers/
    # root is one level up
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    assets_path = os.path.join(root_dir, 'assets', 'FormatTable.json')
    
    print(f"Loading FormatTable from: {assets_path}")
    from helpers.format_table import FormatTable
    format_table = FormatTable(assets_path)
    
    data = format_table.get_all()
    if data:
        print(f"FormatTable loaded. Type: {type(data)}")
        print(f"Total items: {len(data)}")
        print("First 10 items:")
        for item in data[:10]:
            # Print the object representation, or specific fields
            print(item)
    else:
        print("FormatTable is empty or failed to load.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    main()
