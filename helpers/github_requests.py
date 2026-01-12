import os
import requests
import sys

# Fix path to run directly if executed as main script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)
from helpers.globals import TUB_FILES_DIR
from helpers.checksum_verifier import ChecksumVerifier

class GitHubRequests:
    BASE_URL = "https://raw.githubusercontent.com/Rogreis/TUB_Files/main"

    def __init__(self):
        # Determine destination directory
        self.download_dir = TUB_FILES_DIR
        
        # Ensure directory exists
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir)
            except OSError as e:
                print(f"Error creating directory {self.download_dir}: {e}")

    def _download_file(self, file_name, caminho_destino):
        """
        Baixa um arquivo de uma URL 'Raw' do GitHub.
    
        Args:
            file_name (str): O nome do arquivo no repositório (ex: 'rodam_available.json').
            caminho_destino (str): Onde o arquivo será salvo localmente.
            
        Returns:
            bool: True se sucesso, False se falha.
        """
        try:
            # Construct URL (avoiding os.path.join for URLs to prevent backslashes on Windows)
            url_raw = f"{self.BASE_URL}/{file_name}"

            print(f"Baixando de: {url_raw}")
            response = requests.get(url_raw)
            
            # Verifica se a requisição foi bem sucedida (código 200)
            response.raise_for_status()
            
            # Escreve o conteúdo no arquivo (modo 'wb' serve para texto e binários)
            with open(caminho_destino, 'wb') as arquivo:
                arquivo.write(response.content)
                
            print(f"Sucesso! Arquivo salvo em: {caminho_destino}")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: O arquivo não foi encontrado ou a URL está errada. Detalhes: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
        
        return False

    def _download_rodam_available(self):
        """
        Baixa o arquivo 'rodam_available.json' para o diretório de dados da aplicação.
        """
        target_file = "rodam_available.json"
        destination_path = os.path.join(self.download_dir, target_file)
        
        return self._download_file(target_file, destination_path)

    def sync_data_files(self):
        """
        Sincroniza os arquivos de dados (manifesto e zips) com o GitHub.
        1. Baixa o manifesto.
        2. Verifica integridade (checksum).
        3. Baixa arquivos desatualizados.
           - Se o arquivo já existe localmente (update), baixa em background (thread).
           - Se o arquivo NÃO existe (instalação), baixa bloqueando a execução.
        """
        import threading

        print("--- Iniciando Sincronização ---")
        
        # 1. Download Manifest (Always blocking as it's small and crucial)
        if not self._download_rodam_available():
            print("Falha crítica: Não foi possível baixar o manifesto.")
            return

        # 2. Verify Files
        verifier = ChecksumVerifier(self.download_dir)
        valid_format, valid_tr000, valid_tr002 = verifier.verify_files()
        
        print(f"Status da Verificação: FormatTable={valid_format}, TR000={valid_tr000}, TR002={valid_tr002}")

        def download_task(filename):
             self._download_file(filename, os.path.join(self.download_dir, filename))

        # Helper to decide sync vs async
        def manage_download(filename, is_valid):
            if is_valid:
                print(f"{filename} está atualizado.")
                return

            full_path = os.path.join(self.download_dir, filename)
            exists = os.path.exists(full_path)
            
            if exists:
                print(f"Atualizando {filename} em background...")
                # Threaded download (Silent update)
                t = threading.Thread(target=download_task, args=(filename,))
                t.daemon = True # Daemon thread exits when main program exits
                t.start()
            else:
                print(f"Baixando {filename} (Bloqueante)...")
                # Synchronous download (First install / Missing file)
                self._download_file(filename, full_path)

        # 3. Download Missing/Invalid Files
        manage_download("FormatTable.gz", valid_format)
        manage_download("TR000.zip", valid_tr000)
        manage_download("TR002.zip", valid_tr002)
            
        print("--- Sincronização Concluída (Threads podem estar rodando) ---")

# --- Exemplo de Uso ---
if __name__ == "__main__":
    downloader = GitHubRequests()
    print(f"Diretório de destino Configurado: {downloader.download_dir}")
    downloader.sync_data_files()