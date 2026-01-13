import json
import os
import sys
from typing import List, Optional

# Add parent directory to path to allow imports from helpers.globals if run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from helpers.globals import CONFIG_FILE

class Config:
    def __init__(self, 
                 # Old params kept for compatibility if needed, but primary focus is new ones
                 query: str = "",
                 # New requested variables
                 LanguageIdToSearch: int = 2, # 2 for PT, 0 for EN
                 SearchResultsOrder: int = 0, # 0 for Sequential, 1 for Ranking
                 
                 # Boolean flags for search scope
                 SearchParts: bool = True,
                 SearchDocuments: bool = False,
                 
                 SearchIntroduction: bool = True,
                 SearchPartI: bool = True,
                 SearchPartII: bool = True,
                 SearchPartIII: bool = True,
                 SearchPartIV: bool = True,
                 
                 SearchDocumentsList: str = "",
                 
                 SearchMaxResults: int = 100,
                 SearchItemsToShow: int = 50,
                 
                 # ToC Configs
                 CurrentPaper: int = 0,
                 LanguageForToc: int = 0,
                 
                 # User History
                 LastSelectedParagraph: str = "0:0-1",
                 RecentParagraphs: List[str] = None,
                 LastVisitedPage: str = "indexToc",
                 
                 # UI Settings
                 HighlightColor: str = "magenta",
                 DarkMode: bool = True,
                 ShowBgColors: bool = False,
                 SplitterPosition: int = 300,
                 
                 # System State
                 IsInicialization: bool = True):
        
        self._autosave = False
        self.query = query
        self.LanguageIdToSearch = LanguageIdToSearch
        self.SearchResultsOrder = SearchResultsOrder
        
        self.SearchParts = SearchParts
        self.SearchDocuments = SearchDocuments
        
        self.SearchIntroduction = SearchIntroduction
        self.SearchPartI = SearchPartI
        self.SearchPartII = SearchPartII
        self.SearchPartIII = SearchPartIII
        self.SearchPartIV = SearchPartIV
        
        self.SearchDocumentsList = SearchDocumentsList
        
        self.SearchMaxResults = SearchMaxResults
        self.SearchItemsToShow = SearchItemsToShow
        
        self.CurrentPaper = CurrentPaper
        self.LanguageForToc = LanguageForToc
        
        self.LastSelectedParagraph = LastSelectedParagraph
        self.RecentParagraphs = RecentParagraphs
        self.LastVisitedPage = LastVisitedPage
        
        self.HighlightColor = HighlightColor
        self.DarkMode = DarkMode
        self.ShowBgColors = ShowBgColors
        self.SplitterPosition = SplitterPosition
        
        self.IsInicialization = IsInicialization
        
        self._autosave = True

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if getattr(self, '_autosave', False) and key != '_autosave':
            self.save()

    @classmethod
    def load(cls):
        """Loads configuration from the Rodam.json file."""
        if not os.path.exists(CONFIG_FILE):
            print(f"Config file not found at {CONFIG_FILE}, creating with defaults.")
            default_config = cls()
            default_config.save()
            return default_config
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return cls(
                    query=data.get("query", ""),
                    LanguageIdToSearch=data.get("LanguageIdToSearch", 0),
                    SearchResultsOrder=data.get("SearchResultsOrder", 0),
                    SearchParts=data.get("SearchParts", True),
                    SearchDocuments=data.get("SearchDocuments", False),
                    SearchIntroduction=data.get("SearchIntroduction", True),
                    SearchPartI=data.get("SearchPartI", True),
                    SearchPartII=data.get("SearchPartII", True),
                    SearchPartIII=data.get("SearchPartIII", True),
                    SearchPartIV=data.get("SearchPartIV", True),
                    SearchDocumentsList=data.get("SearchDocumentsList", ""),
                    SearchMaxResults=data.get("SearchMaxResults", 100),
                    SearchItemsToShow=data.get("SearchItemsToShow", 50),
                    CurrentPaper=data.get("CurrentPaper", 0),
                    LanguageForToc=data.get("LanguageForToc", 0),
                    LastSelectedParagraph=(data.get("LastSelectedParagraph") or "0:0-1"),
                    RecentParagraphs=data.get("RecentParagraphs", []),
                    LastVisitedPage=data.get("LastVisitedPage", "indexToc"),
                    HighlightColor=data.get("HighlightColor", "magenta"),
                    DarkMode=data.get("DarkMode", True),
                    ShowBgColors=data.get("ShowBgColors", False),
                    SplitterPosition=data.get("SplitterPosition", 300),
                    IsInicialization=data.get("IsInicialization", True)
                )
        except Exception as e:
            print(f"Error loading config: {e}")
            return cls()

    def save(self):
        """Saves current configuration to the Rodam.json file."""
        data = {
            "query": self.query,
            "LanguageIdToSearch": self.LanguageIdToSearch,
            "SearchResultsOrder": self.SearchResultsOrder,
            "SearchParts": self.SearchParts,
            "SearchDocuments": self.SearchDocuments,
            "SearchIntroduction": self.SearchIntroduction,
            "SearchPartI": self.SearchPartI,
            "SearchPartII": self.SearchPartII,
            "SearchPartIII": self.SearchPartIII,
            "SearchPartIV": self.SearchPartIV,
            "SearchDocumentsList": self.SearchDocumentsList,
            "SearchMaxResults": self.SearchMaxResults,
            "SearchItemsToShow": self.SearchItemsToShow,
            "CurrentPaper": self.CurrentPaper,
            "LanguageForToc": self.LanguageForToc,
            "LastSelectedParagraph": self.LastSelectedParagraph,
            "RecentParagraphs": self.RecentParagraphs,
            "LastVisitedPage": self.LastVisitedPage,
            "HighlightColor": self.HighlightColor,
            "DarkMode": self.DarkMode,
            "ShowBgColors": self.ShowBgColors,
            "SplitterPosition": self.SplitterPosition,
            "IsInicialization": self.IsInicialization
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            #print(f"Config saved to {CONFIG_FILE}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_recent_paragraph(self, ref: str):
        """
        Adds a paragraph reference to the RecentParagraphs list.
        - Adds to the beginning (stack behavior).
        - Moves to top if already exists (deduplicate).
        - Limits list to 20 items.
        """
        if not ref:
            return

        # Create a copy to work with, or modify directly. 
        # Modifying self.RecentParagraphs in place won't trigger __setattr__ if we just .append()
        # So we want to re-assign it to trigger autosave if enabled.
        
        current_list = self.RecentParagraphs if self.RecentParagraphs else []
        
        # Remove if exists (start fresh)
        if ref in current_list:
            current_list.remove(ref)
            
        # Add to beginning
        current_list.insert(0, ref)
        
        # Trim to max 20
        if len(current_list) > 20:
            current_list = current_list[:20]
            
        # Assign back to trigger save
        self.RecentParagraphs = current_list
        self.LastSelectedParagraph = ref

    def __repr__(self):
        return f"Config(lang='{self.query}', ...)"

def main():
    print("--- Reading Config ---")
    config = Config.load()
    print(f"Loaded from: {CONFIG_FILE}")
    print(f"Current State: {config.__dict__}")

    print("\n--- Modifying Config ---")
    # Toggle language for testing
    if config.lang == "pt":
        config.lang = "en"
    else:
        config.lang = "pt"
        
    # Increment max_results just to show change
    config.max_results += 10
    
    print(f"New 'lang': {config.lang}")
    print(f"New 'max_results': {config.max_results}")

    print("\n--- Saving Config ---")
    config.save()

    print("\n--- Re-reading to Verify ---")
    new_config = Config.load()
    print(f"Verified State: {new_config.__dict__}")

if __name__ == "__main__":
    main()
