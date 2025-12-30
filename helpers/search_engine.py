import os
import sys
import json
import zipfile
import shutil
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer
from whoosh.query import Or, Prefix

class RodamSearch:
    def __init__(self):
        # Base config paths
        if sys.platform == 'win32':
            self.base_dir = os.path.join(os.environ.get('APPDATA'), 'Rodam')
        elif sys.platform == 'darwin':
            self.base_dir = os.path.join(os.environ.get('HOME'), 'Library', 'Application Support', 'Rodam')
        else:
            self.base_dir = os.path.join(os.environ.get('HOME'), '.config', 'Rodam')

        self.data_dir = self.base_dir  # Zips expected here
        self.index_base_dir = os.path.join(self.base_dir, 'indexes')
        
        # Ensure directories exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        if not os.path.exists(self.index_base_dir):
            os.makedirs(self.index_base_dir)

    def get_schema(self, lang: int):
        if lang == 2:
            # PT (2): StandardAnalyzer (Case Insensitive, Tokenization)
            analyzer = StandardAnalyzer()
        else:
            # EN (0): StemmingAnalyzer (English Porter Stemmer)
            analyzer = StemmingAnalyzer()
            
        return Schema(
            id=ID(stored=True, unique=True),
            content=TEXT(analyzer=analyzer, stored=True),
            title=STORED
        )

    def get_index_path(self, lang: int):
        # Format with 2 decimal places, padded with zero (e.g. index_00, index_02)
        lang_str = str(lang).zfill(2)
        return os.path.join(self.index_base_dir, f"index_{lang_str}")

    def build_index(self, lang: int):
        helpers.globals.logger.debug(f"Indexing content for language ID: {lang}...")
        index_path = self.get_index_path(lang)
        schema = self.get_schema(lang)
        
        # Access global translations
        from helpers.globals import tr_pt, tr_en
        
        if lang == 2:
            source_tr = tr_pt
        elif lang == 0:
            source_tr = tr_en
        else:
            # Default fallback if unknown, or raise error
            source_tr = tr_pt 
            
        if not source_tr:
            # If specifically requested ID is not loaded
            if lang in [0, 2]:
                 raise ValueError(f"Translation for ID {lang} is not loaded in globals.")
            else:
                 raise ValueError(f"Invalid Language ID {lang}. Must be 0 or 2.")

        # Create Index Object
        if not os.path.exists(index_path):
            try:
                os.makedirs(index_path)
            except OSError:
                pass # Already exists race condition
            
        ix = create_in(index_path, schema)
        writer = ix.writer(limitmb=512)
        
        try:
            count = 0
            # Iterate through papers and paragraphs
            for paper in source_tr.papers:
                for p in paper.paragraphs:
                    # p is a Paragraph object
                    p_text = p.text
                    if not p_text:
                        continue
                        
                    # Use secret() for ID (format PPP_SSS_VVV)
                    id_str = p.secret()
                    
                    # Use reference() for Title (format P:S-V)
                    ref_str = p.reference()
                    
                    writer.add_document(
                        id=id_str,
                        content=p_text,
                        title=ref_str
                    )
                    count += 1
                            
            writer.commit()
            helpers.globals.logger.debug(f"Indexing complete for {lang}. Indexed {count} documents.")
            return ix
            
        except Exception as e:
            writer.cancel()
            raise e

    def ensure_index(self, lang: int):
        index_path = self.get_index_path(lang)
        
        if exists_in(index_path):
            try:
                ix = open_dir(index_path)
                if ix.doc_count() > 0:
                    return ix
                else:
                    helpers.globals.logger.debug(f"Index for {lang} is empty/corrupt. Rebuilding...")
                    ix.close()
            except Exception as e:
                helpers.globals.logger.debug(f"Error opening index {lang}: {e}. Rebuilding...")
        
        return self.build_index(lang)

    def search(self, query_str: str, lang: int = 2, max_results: int = 100):
        # Validate/Force restricted values 0 or 2
        if lang not in [0, 2]:
            # Fallback or strict? 
            # User said "possiveis valores sejam 0 ou 2, apenas estes."
            # We default to 2 (PT) if invalid
            lang = 2
            
        try:
            ix = self.ensure_index(lang)
            results_data = []
            
            with ix.searcher() as searcher:
                qp = QueryParser("content", ix.schema)
                q = qp.parse(query_str)

                index_path = self.get_index_path(lang)
                
                # Perform search
                results = searcher.search(q, limit=max_results)
                
                for hit in results:
                    id_parts = hit['id'].split('_')
                    if len(id_parts) == 3:
                        paper = int(id_parts[0])
                        section = int(id_parts[1])
                        
                        # Generate highlighted snippet (HTML)
                        # The default formatter uses <b> and </b> tags with classes match term0 etc.
                        highlighted = hit.highlights("content", top=3) 
                        
                        # If highlights returns empty (e.g. matched on hidden field or weirdness), fallback to text
                        if not highlighted:
                            highlighted = hit['content'][:250] + "..." if len(hit['content']) > 250 else hit['content']
                        
                        results_data.append({
                            "id": hit['id'],
                            "title": hit.get('title', hit['id']),
                            "text": hit['content'],
                            "snippet_html": highlighted, # New field with HTML highlights
                            "paper": paper,
                            "section": section,
                            "paragraph": int(id_parts[2])
                        })
            return results_data
            
        except Exception as e:
            helpers.globals.logger.debug(f"Search failed: {e}")
            return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helpers/search_engine.py <query>")
        sys.exit(1)
        
    query = sys.argv[1]
    
    # Ensure root dir is in path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)
        
    print(f"Searching for: '{query}'")
    
    # Importing globals triggers translation loading
    import helpers.globals
    
    searcher = RodamSearch()
    # Test with lang=2 (PT) default
    results = searcher.search(query, lang=2, max_results=15)
    
    print(f"\nFound {len(results)} results (showing top 15):")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['title']}")
