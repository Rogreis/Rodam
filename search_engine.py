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
        
        # Source ZIP
        zip_filename = "TR002.zip" if lang == 'pt' else "TR000.zip"
        zip_path = os.path.join(self.data_dir, zip_filename)
        
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Source file not found: {zip_path}")
            
        # Create Index Object
        if not os.path.exists(index_path):
            os.makedirs(index_path)
            
        ix = create_in(index_path, schema)
        writer = ix.writer(limitmb=512)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # Assuming translation.json is at root of zip
                with z.open('translation.json') as f:
                    data = json.load(f)
                    
                    papers = data.get('Papers', [])
                    for paper in papers:
                        paper_id = paper.get('PaperIndex', 0)
                        
                        paragraphs = paper.get('Paragraphs', [])
                        for p in paragraphs:
                            # Extract Text
                            p_text = p.get('Text', p.get('Content', ''))
                            
                            # IDs
                            p_paper = int(p.get('PaperIndex', paper_id))
                            p_section = int(p.get('SectionIndex', 0))
                            p_para = int(p.get('ParagraphIndex', 0))
                            
                            id_str = f"{str(p_paper).zfill(3)}_{str(p_section).zfill(3)}_{str(p_para).zfill(3)}"
                            
                            writer.add_document(
                                id=id_str,
                                content=p_text,
                                title=""
                            )
                            
            count = writer.doc_count()
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
                        paragraph = int(id_parts[2])
                        
                        results_data.append({
                            "id": hit['id'],
                            "paper": paper,
                            "section": section,
                            "paragraph": paragraph,
                            "content": hit['content']
                        })
            return results_data
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
