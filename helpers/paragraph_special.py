import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class ParagraphSpecial:
    paper: int
    pk_seq: int
    text: str
    format_type: int

    @classmethod
    def from_dict(cls, data: dict):
        """
        Cria uma instância a partir de um dicionário (do JSON),
        mapeando as chaves do estilo C# para os atributos Python.
        """
        return cls(
            paper=data.get("Paper", 0),
            pk_seq=data.get("pk_seq", 0),
            text=data.get("Text", ""),
            # Mapeia a chave 'Format' do JSON para 'format_type' da classe
            format_type=data.get("Format", 0) 
        )

class SpecialPartsRepository:
    def __init__(self, json_path):
        """
        Inicializa o repositório.
        :param json_path: Caminho para os dados
        """
          
        self.file_path = Path(json_path)
        print(f"Caminho json: {self.file_path}")
        self.parts_introduction_english: List[ParagraphSpecial] = []
        self.parts_introduction_pt_br: List[ParagraphSpecial] = []
        
        # Executa a leitura ao instanciar
        self._load_from_json()

    def _load_from_json(self):
        if not self.file_path.exists():
            print(f"Aviso: Arquivo não encontrado em {self.file_path}")
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Carrega lista em Inglês
                raw_english = data.get("PartsIntroductionForEnglish", [])
                self.parts_introduction_english = [
                    ParagraphSpecial.from_dict(item) for item in raw_english
                ]

                # Carrega lista em Português
                raw_ptbr = data.get("PartsIntroductionForPtBr", [])
                self.parts_introduction_pt_br = [
                    ParagraphSpecial.from_dict(item) for item in raw_ptbr
                ]
                
            print(f"Sucesso: {len(self.parts_introduction_english)} itens (EN) e {len(self.parts_introduction_pt_br)} itens (PT) carregados.")

        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"Erro inesperado ao ler arquivo: {e}")

    def part_titles(self, lang_id: int = 2) -> List[str]:
        """
        Retorna uma lista de strings com os títulos das partes (pk_seq == -3).
        lang_id: 0 para Inglês, 2 para Português (padrão 2).
        """
        source_list = self.parts_introduction_english if lang_id == 0 else self.parts_introduction_pt_br
        
        return [item.text for item in source_list if item.pk_seq == -3]

# --- Exemplo de Uso ---
if __name__ == "__main__":
    repo = SpecialPartsRepository("assets\intro_texts.json")
    if repo.parts_introduction_pt_br:
        primeiro_item = repo.parts_introduction_pt_br[0]
        print(f"\nTeste de Leitura:")
        print(f"Texto: {primeiro_item.text}")
        print(f"Paper: {primeiro_item.paper}")
    
    print("\nTeste part_titles (EN):")
    titulos = repo.part_titles(0)
    for t in titulos:
        print(f" - {t}")


    print("\nTeste part_titles (PT):")
    titulos = repo.part_titles(2)
    for t in titulos:
        print(f" - {t}")
