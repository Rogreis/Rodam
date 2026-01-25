import os
import requests
import sys
from dataclasses import dataclass
from typing import List, Optional
from rodam_exception import RodamException

# Fix path to run directly if executed as main script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.append(root_dir)
from helpers.globals import TUB_FILES_DIR
from helpers.checksum_verifier import ChecksumVerifier

@dataclass
class RodamManifestItem:
    FileName: str = ""
    FilePath: str = ""
    Optional: bool = False
    Hash256: str = ""

    def get_relative_path(self) -> str:
        """
        Retorna o caminho relativo do arquivo combinando FilePath e FileName.
        Ex: 'semantic/model/tub_modelo.index'
        """
        if self.FilePath:
            return os.path.join(self.FilePath, self.FileName)
        return self.FileName

class GitHubRequests:
    # Use 'github.com/.../raw/...' instead of 'raw.githubusercontent.com' to ensure LFS (Large File Storage) 
    # pointers are correctly resolved to the actual binary content.
    BASE_URL = "https://github.com/Rogreis/TUB_Files/raw/main"

    def __init__(self):
        # Determine destination directory
        self.download_dir = TUB_FILES_DIR
        self.manifest_items: List[RodamManifestItem] = []
        
        # Ensure directory exists
        if not os.path.exists(self.download_dir):
            try:
                os.makedirs(self.download_dir)
            except OSError as e:
                print(f"Error creating directory {self.download_dir}: {e}")

        # Fetch manifest immediately
        self._fetch_manifest()

    def _create_manifest_item(self, item: dict) -> Optional[RodamManifestItem]:
        """Creates a RodamManifestItem from a dictionary, handling specific fields."""
        try:
            return RodamManifestItem(
                FileName=item.get('FileName', ''),
                FilePath=item.get('FilePath', ''),
                Optional=item.get('Optional', False),
                Hash256=item.get('Hash256', '')
            )
        except Exception as e:
            print(f"Erro na criação do item do manifesto: {e}")
            return None

    def _fetch_manifest(self):
        """
        Downloads the manifest file (rodam_manifest.json) from GitHub and parses it
        into self.manifest_items. Does NOT save to disk.
        """
        file_name = "rodam_manifest.json"
        url_raw = f"{self.BASE_URL}/{file_name}"
        print(f"Obtendo manifesto de: {url_raw}")
        
        try:
            # Manifest is small, stream=False is fine, but following redirects is key.
            response = requests.get(url_raw, allow_redirects=True)
            response.raise_for_status()
            
            data = response.json()
            self.manifest_items = [RodamManifestItem(**item) for item in data]

            # print(f"\nSucesso! {len(self.manifest_items)} itens carregados:\n")
            # print(f"{'FILENAME':<25} | {'HASH (Início)':<15} | {'OPTIONAL'}")
            # print("-" * 55)
            
            # for item in self.manifest_items:
            #     print(f"{item.FileName:<25} | {item.Hash256[:12]}... | {item.Optional} ! {item.FilePath}")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar manifesto: {e}")
            # If manifest fails, we might want to handle it (e.g., raise error or empty list)
            # For now, leaving as empty list but logging error.
        except Exception as e:
            print(f"Erro ao processar manifesto: {e}")

    def _download_file(self, file_name, caminho_destino):
        """
        Baixa um arquivo da URL do GitHub.
    
        Args:
            file_name (str): O caminho relativo do arquivo no repositório.
            caminho_destino (str): Onde o arquivo será salvo localmente.
            
        Returns:
            bool: True se sucesso, False se falha.
        """
        try:
            # Construct URL
            url_path = file_name.replace('\\', '/')
            url_raw = f"{self.BASE_URL}/{url_path}"

            print(f"Baixando de: {url_raw}")
            # stream=True is critical for large LFS files to save memory
            response = requests.get(url_raw, stream=True, allow_redirects=True)
            
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

            # Write content in chunks
            with open(caminho_destino, 'wb') as arquivo:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        arquivo.write(chunk)
                
            print(f"Sucesso! Arquivo salvo em: {caminho_destino}")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP: O arquivo não foi encontrado ou a URL está errada. Detalhes: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
        
        return False

    def _download_task(self, item: RodamManifestItem):
        """Metodo auxiliar para download em background."""
        try:
             destination_path = os.path.join(self.download_dir, item.FilePath, item.FileName)
             # Use relative path for URL construction
             self._download_file(item.get_relative_path(), destination_path)
        except Exception as dt_e:
             print(f"Erro no download em background de {item.FileName}: {dt_e}")

    def _manage_download(self, item: RodamManifestItem, is_valid: bool):
        """Gerencia se o download será síncrono ou assíncrono."""
        import threading
        from helpers.globals import RodamException

        if is_valid:
            print(f"{item.FileName} está atualizado.")
            return

        full_path = os.path.join(self.download_dir, item.FilePath, item.FileName)
        exists = os.path.exists(full_path)
        
        if exists:
            print(f"Atualizando {item.FileName} em background...")
            # Threaded download (Silent update)
            # Calls internal method
            t = threading.Thread(target=self._download_task, args=(item,))
            t.daemon = True # Daemon thread exits when main program exits
            t.start()
        else:
            # Synchronous download (First install / Missing file)
            if not item.Optional:
                print(f"Baixando {item.FileName} (Bloqueante)...")
                # Use relative path for URL construction
                success = self._download_file(item.get_relative_path(), full_path)
                if not success:
                    raise RodamException(f"Falha ao baixar arquivo crítico: {item.FileName}")
            else:
                print(f"Arquivo opcional {item.FileName} não encontrado localmente.")

    def download_specific_file(self, file_name: str) -> bool:
        """
        Baixa um arquivo específico pelo nome, se ele estiver no manifesto.
        
        Args:
            file_name (str): O nome do arquivo a ser baixado (deve corresponder ao FileName no manifesto).
            
        Returns:
            bool: True se o download foi bem-sucedido, False caso contrário (ex: arquivo não está no manifesto ou erro de download).
        """
        # Find the item in the manifest
        # We search case-insensitively or exactly? Typically exact match based on manifest definition.
        target_item = next((item for item in self.manifest_items if item.FileName == file_name), None)
        
        if not target_item:
            print(f"Arquivo '{file_name}' não encontrado no manifesto. Impossível baixar.")
            return False
            
        destination_path = os.path.join(self.download_dir, target_item.FilePath, target_item.FileName)
        print(f"Solicitado download específico de: {file_name}")
        
        # We need the relative path for the URL construction
        relative_path = target_item.get_relative_path()
        return self._download_file(relative_path, destination_path)

    def check_semantic_files(self) -> tuple:
        """
        Verifica e baixa os arquivos necessários para a busca semântica.
        Arquivos: 'tub_modelo_meta.pkl' e 'tub_modelo.index'
        
        Returns:
            (success: bool, errors: list[str])
        """
        required_files = ["tub_modelo_meta.pkl", "tub_modelo.index"]
        errors = []
        
        print("--- Verificando Arquivos de Semântica ---")
        
        # We need to make sure manifest is loaded
        if not self.manifest_items:
            self._fetch_manifest()
            if not self.manifest_items:
                 return False, ["Falha ao baixar manifesto."]

        # Create a partial verification for just these files
        verifier = ChecksumVerifier(self.download_dir)
        # Filter manifest items for these files
        semantic_items = [item for item in self.manifest_items if item.FileName in required_files]
        
        if len(semantic_items) != len(required_files):
             missing = set(required_files) - set(i.FileName for i in semantic_items)
             return False, [f"Arquivos não encontrados no manifesto: {missing}"]
             
        results = verifier.verify_files(semantic_items)
        
        for item in semantic_items:
             is_valid = results.get(item.FileName, False)
             if is_valid:
                 print(f"Semântica: {item.FileName} já está correto.")
             else:
                 print(f"Semântica: Baixando {item.FileName}...")
                 success = self.download_specific_file(item.FileName)
                 if not success:
                     errors.append(f"Falha ao baixar {item.FileName}")
        
        return (len(errors) == 0), errors

    def check_semantic_files_existence(self) -> bool:
        """
        Verifica se os arquivos necessários para a busca semântica existem localmente.
        Arquivos: 'tub_modelo_meta.pkl' e 'tub_modelo.index'
        Não faz download, apenas checa existência.
        
        Returns:
            bool: True se ambos existirem, False caso contrário.
        """
        required_files = [
            ("tub_modelo_meta.pkl", "semantic/model"), 
            ("tub_modelo.index", "semantic/model")
        ]
        
        # Local paths logic: We need to know where they should be.
        # Ideally we'd look up in manifest, but for pure existence check we assume standard paths 
        # or we reuse manifest if loaded. Use manifest if available, else guess?
        # The user request says "ver se os arquivos da semântica existem".
        # Let's rely on manifest to be safe about paths, or just hardcode checking the download_dir recursive?
        # The manifest items for these are:
        # FileName: tub_modelo_meta.pkl, FilePath: semantic\model
        
        # Checking manifest first
        if not self.manifest_items:
             self._fetch_manifest()
             
        for filename, _ in required_files:
             # Find item
             item = next((i for i in self.manifest_items if i.FileName == filename), None)
             if item:
                 full_path = os.path.join(self.download_dir, item.FilePath, item.FileName)
                 if not os.path.exists(full_path):
                     print(f"Semântica: Arquivo ausente detectado: {full_path}")
                     return False
             else:
                 # Fallback if manifest fails or file not in it (unlikely)
                 pass

        return True

    def sync_data_files(self):
        """
        Sincroniza os arquivos de dados (baseado no manifesto baixado) com o GitHub.
        1. Usa o manifesto já carregado em memória.
        2. Verifica integridade (checksum) via ChecksumVerifier.
        3. Baixa arquivos desatualizados.
           - Se o arquivo já existe localmente (update), baixa em background (thread).
           - Se o arquivo NÃO existe (instalação), baixa bloqueando a execução.
        """
        from helpers.globals import RodamException
        
        try:
            if not self.manifest_items:
                print("Abortando sincronização: Manifesto não carregado.")
                if not self.manifest_items:
                     # Check if we can fetch again
                     self._fetch_manifest()
                     if not self.manifest_items:
                         raise RodamException("Não foi possível carregar o manifesto de arquivos do GitHub.")

            print("--- Iniciando Sincronização ---")
            
            # 2. Verify Files using the in-memory manifest
            verifier = ChecksumVerifier(self.download_dir)
            # Pass the manifest items to the verifier
            verification_results = verifier.verify_files(self.manifest_items)
            
            print(f"Status da Verificação: {verification_results}")

            # 3. Download Missing/Invalid Files
            # We iterate over the manifest items and check against verification results
            for item in self.manifest_items:
                # Assuming verification_results is a dict keyed by FileName
                is_valid = verification_results.get(item.FileName, False)
                self._manage_download(item, is_valid)
                
            print("--- Sincronização Concluída (Threads podem estar rodando) ---")
            
        except RodamException:
            raise
        except Exception as e:
            # Wrap unexpected errors
            print(f"Erro crítico na sincronização: {e}")
            raise RodamException(f"Erro crítico ao sincronizar arquivos: {str(e)}") from e

# --- Exemplo de Uso ---
if __name__ == "__main__":
    downloader = GitHubRequests()
    print(f"Diretório de destino Configurado: {downloader.download_dir}")
    downloader.sync_data_files()