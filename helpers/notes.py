import os
import sys
import json
from typing import Dict, Any, Optional, List

class NoteEntry:
    def __init__(self, data: Dict[str, Any]):
        self.paper = data.get("Paper")
        self.section = data.get("Section")
        self.paragraph = data.get("Paragraph")
        self.status = data.get("Status")
        self.format_val = data.get("Format")
    
    def __repr__(self):
        return f"<NoteEntry P:{self.paper} S:{self.section} Par:{self.paragraph} Status:{self.status}>"

class NotesList:
    """
    Loads and provides access to notes from assets/notes.json.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = self._load_data()
        self.entries = [NoteEntry(d) for d in self._data]

    def _load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            print(f"Notes file not found: {self.file_path}")
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_notes = []
                    # structure is list of objects, each has "Notes" list
                    for item in data:
                         if "Notes" in item and isinstance(item["Notes"], list):
                             all_notes.extend(item["Notes"])
                    return all_notes
                return []
        except Exception as e:
            print(f"Error loading Notes: {e}")
            return []

    def get_all(self) -> List[NoteEntry]:
        return self.entries

    def get_by_paper(self, paper: int) -> List[NoteEntry]:
        """
        Returns a list of NoteEntries that belong to the specified paper.
        """
        # Could be optimized with a dictionary index if performance becomes an issue
        return [entry for entry in self.entries if entry.paper == paper]

    def get_status(self, paper: int, section: int, paragraph: int) -> Optional[int]:
        """
        Returns the Status for a specific Paper, Section, and Paragraph.
        Returns None if not found.
        """
        for entry in self.entries:
            if (entry.paper == paper and 
                entry.section == section and 
                entry.paragraph == paragraph):
                return entry.status
        return None

    def get_css_class(self, paper: int, section: int, paragraph: int) -> str:
        """
        Returns the CSS class string corresponding to the status of the note.
        0: .parStarted
        1: .parWorking
        2: .parDoubt
        3: .parOk
        4: .parClosed
        """
        status = self.get_status(paper, section, paragraph)
        if status is None:
            return ""
            
        status_map = {
            0: "parStarted",
            1: "parWorking",
            2: "parDoubt",
            3: "parOk",
            4: "parClosed"
        }
        return status_map.get(status, "")

def main():
    print("--- Testing NotesList ---")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    assets_path = os.path.join(root_dir, 'assets', 'notes.json')
    
    print(f"Loading NotesList from: {assets_path}")
    notes_list = NotesList(assets_path)
    
    entries = notes_list.get_all()
    if entries:
        print(f"NotesList loaded. Type: {type(entries)}")
        print(f"Total items: {len(entries)}")
        
        target_paper = 100
        if len(sys.argv) > 1:
            try:
                target_paper = int(sys.argv[1])
            except ValueError:
                print(f"Invalid paper number: {sys.argv[1]}. Using default: {target_paper}")

        print(f"Testing get_by_paper({target_paper}):")
        paper_notes = notes_list.get_by_paper(target_paper)
        print(f"Total notes for paper {target_paper}: {len(paper_notes)}")
        print(f"First 5 items for paper {target_paper}:")
        for item in paper_notes[:5]:
            print(item)
    else:
        print("NotesList is empty or failed to load.")

if __name__ == "__main__":
    main()
