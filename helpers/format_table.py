import os
import sys
import json
from typing import Dict, Any, Optional, List
from enum import IntEnum

class ParagraphExportHtmlType(IntEnum):
    BookTitle = 0
    PaperTitle = 1
    SectionTitle = 2
    NormalParagraph = 3
    IdentedParagraph = 4
    Separator = 5
    PartIntroduction = 6


class FormatEntry:
    def __init__(self, data: Dict[str, Any]):
        self.format_identity = data.get("FormatIdentity")
        self.paper = data.get("Paper")
        self.section = data.get("Section")
        self.paragraph = data.get("Paragraph")
        self.page = data.get("Page")
        self.line = data.get("Line")
        self.format_val = data.get("Format")

    @property
    def Format(self) -> ParagraphExportHtmlType:
        try:
            return ParagraphExportHtmlType(self.format_val)
        except ValueError:
            return ParagraphExportHtmlType.NormalParagraph
    
    def identication(self):
        return f"{self.paper}:{self.section}-{self.paragraph} ({self.page}.{self.line})"

    def __repr__(self):
        return f"<FormatEntry {self.identication()}>"

class FormatTable:
    """
    Loads and provides access to formatting rules from assets/FormatTable.json.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data = self._load_data()

    def _load_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            print(f"FormatTable file not found: {self.file_path}")
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "ParagraphsFormat" in data:
                    return data["ParagraphsFormat"]
                return []
        except Exception as e:
            print(f"Error loading FormatTable: {e}")
            return []

    def get_all(self) -> List['FormatEntry']:
        return [FormatEntry(d) for d in self._data]

    def format_identification(self, paper: int, section: int, paragraph_no: int):
        """
        Retrieves a format rule by generating the FormatIdentity key: "<paper>:<section>-<paragraphNo>".
        Example: "1:2-3"
        """
        ident= f"{paper}:{section}-{paragraph_no}"
        return ident

def main():
    print("--- Testing FormatTable ---")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    assets_path = os.path.join(root_dir, 'assets', 'FormatTable.json')
    
    print(f"Loading FormatTable from: {assets_path}")
    format_table = FormatTable(assets_path)
    
    entries = format_table.get_all()
    if entries:
        print(f"FormatTable loaded. Type: {type(entries)}")
        print(f"Total items: {len(entries)}")
        print("First 5 items:")
        for item in entries[:5]:
            print(item)
            print(f"   Identification: {item.identication()}")
            print(f"   Format Type: {item.Format}")
    else:
        print("FormatTable is empty or failed to load.")

if __name__ == "__main__":
    main()
