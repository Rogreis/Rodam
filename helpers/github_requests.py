import os
import requests
from helpers.globals import TUB_FILES_DIR

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

    def download_rodam_available(self):
        """
        Baixa o arquivo 'rodam_available.json' para o diretório de dados da aplicação.
        """
        target_file = "rodam_available.json"
        destination_path = os.path.join(self.download_dir, target_file)
        
        return self._download_file(target_file, destination_path)

# --- Exemplo de Uso ---
if __name__ == "__main__":
    downloader = GitHubRequests()
    print(f"Diretório de destino Configurado: {downloader.download_dir}")
    downloader.download_rodam_available()