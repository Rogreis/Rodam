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
                 LanguageIdToSearch: int = 1, # 1 for PT, 2 for AR, etc. (assuming 1 is default PT)
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
                 LastSelectedParagraph: str = "",
                 RecentParagraphs: List[str] = None,
                 LastVisitedPage: str = "indexToc"):
        
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
        self._autosave = True

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if getattr(self, '_autosave', False) and key != '_autosave':
            self.save()

    @classmethod
    def load(cls):
        """Loads configuration from the Rodam.json file."""
        if not os.path.exists(CONFIG_FILE):
            print(f"Config file not found at {CONFIG_FILE}, returning defaults.")
            return cls()
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return cls(
                    query=data.get("query", ""),
                    LanguageIdToSearch=data.get("LanguageIdToSearch", 1),
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
                    LastSelectedParagraph=data.get("LastSelectedParagraph", ""),
                    RecentParagraphs=data.get("RecentParagraphs", []),
                    LastVisitedPage=data.get("LastVisitedPage", "indexToc")
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
            "LastVisitedPage": self.LastVisitedPage
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Config saved to {CONFIG_FILE}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def __repr__(self):
        return f"Config(lang='{self.lang}', sort='{self.sort}', max_results={self.max_results}, page_size={self.page_size}, ...)"

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
