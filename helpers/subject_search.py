import pickle
import os
import sys
import time

from helpers.globals import MODEL_PREFIX

class SubjectSearch:
    def __init__(self, model_prefix):
        self.index_path = f"{model_prefix}.index"
        self.meta_path = f"{model_prefix}_meta.pkl"
        self.model = None
        self.index = None
        self.metadata = None

    def carregar(self, status_callback=None, cancel_check=None):
        """
        Carrega os arquivos do modelo e inicializa a IA.
        :param status_callback: Função para reportar progresso (ex: lambda msg: print(msg))
        :param cancel_check: Função que retorna True se o usuário cancelou
        """
        # Função auxiliar para feedback seguro
        def report(msg):
            if status_callback:
                status_callback(msg)
            else:
                print(msg) # Fallback

        # Check se já está carregado
        if self.model is not None and self.index is not None and self.metadata is not None:
            return True

        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            report(f"Erro Crítico: Arquivos do modelo não encontrados em '{MODEL_PREFIX}'.")
            report("Certifique-se de executar o script 'treinar_modelo.py' primeiro.")
            return False

        if cancel_check and cancel_check(): return False
        report("Carregando IA (Isso pode demorar um pouco na primeira vez)...")
        # Imports tardios para acelerar startup
        import faiss
        from sentence_transformers import SentenceTransformer

        # Carrega o modelo de linguagem
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

        if cancel_check and cancel_check(): return False
        report("Carregando Índice de Busca Rápida (FAISS)...")
        self.index = faiss.read_index(self.index_path)

        if cancel_check and cancel_check(): return False
        report("Carregando Metadados...")
        with open(self.meta_path, "rb") as f:
            self.metadata = pickle.load(f)
            
        report("Sistema Pronto!")
        return True

    def buscar(self, query, top_k=5, status_callback=None, cancel_check=None):
        """Executa a busca e retorna os resultados formatados."""
        # --- Lazy Loading ---
        # Se não estiver carregado, tenta carregar agora, repassando os callbacks
        if self.model is None:
            success = self.carregar(status_callback, cancel_check)
            if not success:
                return [], 0.0 # Falha ou cancelamento

        if not query.strip():
            return [], 0.0

        if cancel_check and cancel_check(): return [], 0.0

        start_time = time.time()

        # 1. Converter pergunta em vetor
        vector = self.model.encode([query])
        
        # 2. Normalizar
        import faiss
        faiss.normalize_L2(vector)
        
        # 3. Buscar no índice
        scores, indices = self.index.search(vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            score = scores[0][i]
            if idx < len(self.metadata):
                item = self.metadata[idx]
                results.append({
                    "rank": i + 1,
                    "score": float(score), # float nativo para JSON
                    "assunto": item[0],
                    "links": item[1]
                })
        
        elapsed = time.time() - start_time
        return results, elapsed

def main():
    print("========================================================")
    print("       BUSCA SEMÂNTICA - INTERFACE INTERATIVA")
    print("========================================================")

    buscador = MotorBusca(MODEL_PREFIX)
    sucesso = buscador.carregar()

    if not sucesso:
        sys.exit(1)

    print("Instruções: Digite sua pesquisa e tecle ENTER.")
    print("            Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            termo = input("\nO que você deseja buscar? > ").strip()
            
            if termo.lower() in ['sair', 'exit', 'quit']:
                print("Encerrando...")
                break
            
            if not termo:
                continue

            resultados, tempo = buscador.buscar(termo)

            print(f"\n--- Resultados para: '{termo}' ({tempo:.4f}s) ---")
            
            if not resultados:
                print("Nenhum resultado relevante encontrado.")
            else:
                for res in resultados:
                    # Formatação visual do score (Ex: 0.75 -> 75%)
                    score_pct = res['score'] * 100
                    print(f"#{res['rank']} [{score_pct:.1f}%] {res['assunto']}")
                    print(f"      Link(s): {res['links']}")
                    print("-" * 40)

        except KeyboardInterrupt:
            print("\nEncerrando...")
            break
        except Exception as e:
            print(f"Ocorreu um erro na busca: {e}")

if __name__ == "__main__":
    main()
