import os
import sys
import json
import zipfile
import shutil
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer, StandardAnalyzer

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

    def get_schema(self, lang: str):
        if lang == 'pt':
            # PT: StandardAnalyzer (Case Insensitive, Tokenization)
            analyzer = StandardAnalyzer()
        else:
            # EN: StemmingAnalyzer (English Porter Stemmer)
            analyzer = StemmingAnalyzer()
            
        return Schema(
            id=ID(stored=True, unique=True),
            content=TEXT(analyzer=analyzer, stored=True),
            title=STORED
        )

    def get_index_path(self, lang: str):
        return os.path.join(self.index_base_dir, f"index_{lang}")

    def build_index(self, lang):
        print(f"Indexing content for language: {lang}...")
        index_path = self.get_index_path(lang)
        schema = self.get_schema(lang)
        
        # Access global translations
        from helpers.globals import tr_pt, tr_en
        
        if lang == 'pt':
            source_tr = tr_pt
        elif lang == 'en':
            source_tr = tr_en
        else:
            source_tr = tr_pt # Default
            
        if not source_tr:
             raise ValueError(f"Translation for '{lang}' is not loaded in globals.")

        # Create Index Object
        if not os.path.exists(index_path):
            os.makedirs(index_path)
            
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
            print(f"Indexing complete for {lang}. Indexed {count} documents.")
            return ix
            
        except Exception as e:
            writer.cancel()
            raise e

    def ensure_index(self, lang: str):
        index_path = self.get_index_path(lang)
        
        if exists_in(index_path):
            try:
                ix = open_dir(index_path)
                if ix.doc_count() > 0:
                    return ix
                else:
                    print(f"Index for {lang} is empty/corrupt. Rebuilding...")
                    ix.close()
            except Exception as e:
                print(f"Error opening index {lang}: {e}. Rebuilding...")
        
        return self.build_index(lang)

    def search(self, query_str: str, lang: str = 'pt', max_results: int = 100):
        if lang not in ['pt', 'en']:
            lang = 'pt'
            
        try:
            ix = self.ensure_index(lang)
            results_data = []
            
            with ix.searcher() as searcher:
                qp = QueryParser("content", ix.schema)
                q = qp.parse(query_str)
                
                results = searcher.search(q, limit=max_results)
                
                for hit in results:
                    id_parts = hit['id'].split('_')
                    if len(id_parts) == 3:
                        paper = int(id_parts[0])
                        section = int(id_parts[1])
                        # paragraph = int(id_parts[2]) # Not used directly if we just return ID
                        
                        results_data.append({
                            "id": hit['id'],        # PPP_SSS_VVV
                            "title": hit.get('title', hit['id']), # Reference P:S-V
                            "text": hit['content'], # Matched text
                            # "score": hit.score,   # Optional
                            "paper": paper,
                            "section": section,
                            "paragraph": int(id_parts[2])
                        })
            return results_data
            
        except Exception as e:
            print(f"Search failed: {e}")
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
    results = searcher.search(query, lang='pt', max_results=15)
    
    print(f"\nFound {len(results)} results (showing top 15):")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['title']}")
