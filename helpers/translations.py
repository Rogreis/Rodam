import os
import sys
import zipfile
import json
from typing import Dict, Any, Optional, List
from enum import IntEnum
import re
import urllib.request
import shutil
import hashlib



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
        self.title = self.extract_title()

    def extract_title(self) -> str:
        """Extracts the title from the paragraph where Section=0 and ParagraphNo=0."""
        for p in self.paragraphs:
            if p.section == 0 and p.paragraph_no == 0:
                title= f"{p.paper} - {p.text}"
                return title
        return ""

    @staticmethod
    def extract_code_triplet(ref_string: str):
        """
        Static helper to parse any reference string into (paper, section, paragraph).
        Returns Tuple[int, int, int] or None.
        """
        if not ref_string:
            return None
            
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
            return (target_paper, target_section, target_paragraph)
        except ValueError:
            return None

    def get_paragraph_from_string(self, ref_string: str) -> Optional[Paragraph]:
        """
        Parses a string containing paper, section, and paragraph numbers 
        separated by { '_', ',', '-', '.', ' ', ':'} and returns the 
        corresponding Paragraph object.
        """
        triplet = Paper.extract_code_triplet(ref_string)
        if not triplet:
            return None
            
        target_paper, target_section, target_paragraph = triplet
            
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
    Represents the translation object structure found in translation
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

    @staticmethod
    def make_github_url(relative_file_path: str) -> str:
        return f"https://raw.githubusercontent.com/Rogreis/TUB_Files/main/{relative_file_path}"

    @staticmethod
    def _download_static(url: str, save_path: str) -> bool:
        try:
            print(f"Downloading {url} to {save_path}...")
            with urllib.request.urlopen(url) as response, open(save_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            return True
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return False

    def download_github_file(self, relative_path: str, destination_name: str = None) -> bool:
        """
        Downloads a file from the TUB_Files GitHub repository.
        Uses instance base_dir.
        """
        url = self.make_github_url(relative_path)
        filename = destination_name if destination_name else os.path.basename(relative_path)
        save_path = os.path.join(self.base_dir, filename)
        return self._download_static(url, save_path)

    @staticmethod
    def _calculate_sha256(file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return ""

    @staticmethod
    def check_files(tub_files_dir: str):

        from helpers.github_requests import GitHubRequests
        from helpers.globals import TUB_FILES_DIR
        
        print("Checking critical data files...")
        downloader = GitHubRequests()
        downloader.sync_data_files()
        
        # Verify critical files exist
        required_files = ["FormatTable.gz", "TR000.zip", "TR002.zip"]
        missing_files = []
        
        for f in required_files:
            if not os.path.exists(os.path.join(TUB_FILES_DIR, f)):
                missing_files.append(f)
                
        if missing_files:
            print(f"CRITICAL ERROR: The following required files are missing in {TUB_FILES_DIR}:")
            for f in missing_files:
                print(f" - {f}")
            print("Application cannot start. Please check your internet connection and try again.")
            sys.exit(1)

        # # 1. rodam_available.json
        # ra_name = "rodam_available.json"
        # ra_path = os.path.join(tub_files_dir, ra_name)
        # ra_url = TTranslations.make_github_url(ra_name)
        # TTranslations._download_static(ra_url, ra_path)
        
        # # Read rodam_available.json to get checksums
        # available_data = {}
        # if os.path.exists(ra_path):
        #     try:
        #         with open(ra_path, 'r', encoding='utf-8') as f:
        #             available_data = json.load(f)
        #     except Exception as e:
        #         print(f"Error reading {ra_name}: {e}")
        
        # # Iterate and Validate/Download
        # for filename, expected_hash in available_data.items():
        #     file_path = os.path.join(tub_files_dir, filename)
            
        #     # Check existence and hash
        #     should_download = False
        #     if not os.path.exists(file_path):
        #         print(f"File missing: {filename}")
        #         should_download = True
        #     else:
        #         existing_hash = TTranslations._calculate_sha256(file_path)
        #         if existing_hash.lower() != expected_hash.lower():
        #             print(f"Checksum mismatch for {filename}. Local: {existing_hash}, Expected: {expected_hash}")
        #             should_download = True
            
        #     if should_download:
        #         url = TTranslations.make_github_url(filename)
        #         success = TTranslations._download_static(url, file_path)
        #         if success:
        #             print(f"Downloaded updated {filename}")
        #         else:
        #             print(f"Failed to download {filename}")
        #     else:
        #         # print(f"File {filename} is up to date.") 
        #         pass

        # print("Control files validation complete.")

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
        return self.load(language_id)
    def get_text_content(language_id: int, ref_string: str) -> str:
        """
        Retorna o texto (sem HTML) do parágrafo especificado pela ref_string (ex: '100:2.3')
        para o idioma especificado.
        """
        import helpers.globals
        
        # 1. Obter a instância da tradução correta
        translation = None
        # Na verdade, precisamos ver como estão carregadas em globals.py
        # tr_en = translations_manager.load(0) -> Geralmente ID 0 é Inglês Original
        # tr_pt = translations_manager.load(2) -> Geralmente ID 2 é Português
        
        if language_id == 0:
             translation = helpers.globals.tr_en
        elif language_id == 2:
             translation = helpers.globals.tr_pt
        
        # Fallback: tentar carregar via translations_manager se não estiver nas variáveis
        if not translation:
             # Isso requer acesso ao 'translations_manager' global
             if helpers.globals.translations_manager:
                 translation = helpers.globals.translations_manager.load(language_id)
        
        if not translation:
            return ""

        # 2. Obter trio (Paper, Section, Paragraph)
        triplet = Paper.extract_code_triplet(ref_string)
        if not triplet:
            return ""
            
        target_paper, target_section, target_paragraph = triplet
        
        # 3. Localizar e retornar texto
        # Precisamos achar o paper correto na lista de papers
        # Papers geralmente estão ordenados, mas nem sempre o índice bate com o número do paper (Introdução é 0, Paper 1 é 1...)
        # Mas translation.papers é uma lista. O Paper 0 é o primeiro?
        # É mais seguro iterar ou usar um map se fosse otimizado. Como são ~197 papers, iterar é rápido o suficiente.
        # Ou acessar direto se o papers[i].paper == i ? Geralmente sim, Paper 0 é indice 0.
        
        # Tentativa de acesso direto (Otimização)
        if 0 <= target_paper < len(translation.papers):
             cand = translation.papers[target_paper]
             # Verifica se é o paper certo (pode haver deslocamento se faltar algum paper no JSON, improvável no TUB)
             # O Paper 0 é o Foreword. Paper 1 é o Paper 1.
             # O índice do array costuma casar. No entanto, Paper.paper é o ID.
             # O translation.papers é uma lista de Paper objects.
             # Vamos verificar o primeiro parágrafo para confirmar o ID do paper.
             if cand.paragraphs and cand.paragraphs[0].paper == target_paper:
                 target_p_obj = cand.get_paragraph_from_string(ref_string)
                 if target_p_obj:
                     return target_p_obj.text
        
        # Fallback de busca linear (se acesso direto falhar)
        for p in translation.papers:
            if p.paragraphs and p.paragraphs[0].paper == target_paper:
                found = p.get_paragraph_from_string(ref_string)
                if found:
                    return found.text
                break
                
        return ""



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
