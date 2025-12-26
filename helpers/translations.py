import os
import sys
import zipfile
import json
from typing import Dict, Any, Optional, List

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
        self.papers = data.get("Papers", [])

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
    # Summarized print of the first 4 items to avoid huge output from Paragraphs content
    for i, paper in enumerate(translation.papers[:4]):
        # Create a shallow copy to modify for display purposes (showing paragraph count instead of full list)
        paper_display = paper.copy()
        if 'Paragraphs' in paper_display:
            count = len(paper_display['Paragraphs'])
            paper_display['Paragraphs'] = f"<{count} Paragraphs>"
        print(f"Paper {i}: {json.dumps(paper_display, ensure_ascii=True)}")

if __name__ == "__main__":
    main()
