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
        target_item = next((item for item in self.manifest_items if item.FileName == file_name), None)
        
        if not target_item:
            print(f"Erro: Arquivo {file_name} não encontrado no manifesto.")
            return False
            
        # Determine full path
        if target_item.FilePath:
            dest_dir = os.path.join(self.download_dir, target_item.FilePath)
        else:
            dest_dir = self.download_dir
            
        os.makedirs(dest_dir, exist_ok=True)
        full_path = os.path.join(dest_dir, target_item.FileName)
        
        return self._download_file(target_item.get_relative_path(), full_path)

    def check_semantic_files(self) -> "tuple[bool, list[str]]":
        """
        Verifica se os arquivos necessários para a busca semântica estão presentes e válidos.
        Se não estiverem, tenta baixá-los.
        
        Returns:
            tuple[bool, list[str]]: (Sucesso, Lista de Erros)
        """
        required_files = ["tub_modelo_meta.pkl", "tub_modelo.index"]
        errors = []
        
        # Filter manifest for semantic files
        target_items = [item for item in self.manifest_items if item.FileName in required_files]
        
        if not target_items:
            return False, ["Manifesto não contém arquivos de semântica."]

        # Verify items
        verifier = ChecksumVerifier(self.download_dir)
        results = verifier.verify_files(target_items)
        
        for item in target_items:
            is_valid = results.get(item.FileName, False)
            if not is_valid:
                print(f"[Semantic Check] Arquivo ausente ou inválido: {item.FileName}. Iniciando download...")
                try:
                    success = self.download_specific_file(item.FileName)
                    if not success:
                        errors.append(f"Falha ao baixar {item.FileName}")
                except Exception as e:
                    errors.append(f"Erro ao baixar {item.FileName}: {str(e)}")
            else:
                 print(f"[Semantic Check] Arquivo {item.FileName} verificado OK.")
                 
        if errors:
            return False, errors
            
        return True, []


    def check_semantic_files_existence(self) -> bool:
        """
        Verifica se os arquivos necessários para a busca semântica existem localmente.
        Arquivos: 'tub_modelo_meta.pkl' e 'tub_modelo.index'
        Não faz download, apenas checa existência.
        
        Returns:
            bool: True se ambos existirem, False caso contrário.
        """
        required_files = ["tub_modelo_meta.pkl", "tub_modelo.index"]
        
        # Load manifest if needed
        if not self.manifest_items:
             self._fetch_manifest()

        # Check each required file
        for filename in required_files:
             # Find item in manifest to get correct path
             item = next((i for i in self.manifest_items if i.FileName == filename), None)
             
             if item:
                 full_path = os.path.join(self.download_dir, item.FilePath, item.FileName)
             else:
                 # Fallback if manifest fails or file not in it (unlikely)
                 # Assume standard structure if not found
                 full_path = os.path.join(self.download_dir, "semantic", "model", filename)
                 
             if not os.path.exists(full_path):
                 print(f"Semântica: Arquivo ausente: {filename}")
                 return False

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