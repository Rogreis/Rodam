import os
import sys
import traceback
import inspect
from rodam_exception import RodamException

# Define resource_path and get_data_dir first as they are fundamental
APP_VERSION = "1.0.0"

def log_exception(e: Exception, msg: str = ""):
    """
    Imprime detalhes da exceção na console identificando Classe.metodo chamador,
    sem interromper a execução do programa.
    """
    try:
        # Pega o frame anterior (quem chamou esta função)
        frame = inspect.currentframe().f_back
        if not frame:
            print(f"[ERRO] {msg}: {e}")
            return

        # Nome da função/método
        func_name = frame.f_code.co_name
        
        # Tenta descobrir a classe (olhando se existe 'self' ou 'cls' nos locais)
        class_name = ""
        if 'self' in frame.f_locals:
            class_name = frame.f_locals['self'].__class__.__name__ + "."
        elif 'cls' in frame.f_locals:
             obj = frame.f_locals['cls']
             if hasattr(obj, '__name__'):
                 class_name = obj.__name__ + "."
            
        full_context = f"{class_name}{func_name}"
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"⚠️  ERRO CAPTURADO em [{full_context}]")
        if msg:
            print(f"ℹ️  Contexto: {msg}")
        print(f"❌  Exceção: {type(e).__name__}: {str(e)}")
        # print(f"📍  Arquivo: {frame.f_code.co_filename}:{frame.f_lineno}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
    except Exception as inner_e:
        print(f"Erro crítico ao tentar logar erro: {inner_e}")
    finally:
        # Importante para evitar ciclos de referência no Garbage Collector
        del frame

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_data_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
    elif sys.platform == 'darwin':
        base = os.path.join(os.environ.get('HOME'), 'Library', 'Application Support')
    else:
        base = os.path.join(os.environ.get('HOME'), '.config')
    return os.path.join(base, 'Rodam')

# Global Constants and Paths
# Global Constants and Paths
TUB_FILES='TUB_Files'
CONFIG_FILE = os.path.join(get_data_dir(), 'Rodam.json')
TUB_FILES_DIR = os.path.join(get_data_dir(), 'TUB_Files')
MODEL_PREFIX = os.path.join(get_data_dir(), 'TUB_Files', 'semantic', 'model', 'tub_modelo')

# Ensure config dir exists
if not os.path.exists(get_data_dir()):
    try:
        os.makedirs(get_data_dir())
    except OSError:
        pass # Handle permission errors or race conditions if necessary

# --- Load Config Early ---
# Import Config after defining paths to avoid circular issues
from helpers.config import Config
global_config = Config.load()

# Global variables (initialized in initialize())
tr_pt = None
tr_en = None
logger = None
translations_manager = None
format_table = None
notes_list = None
semantic_engine = None

SEMANTIC_RESULTS_FILE = os.path.join(get_data_dir(), 'semantic_results.json')

def initialize():
    """
    Inicializa as variáveis globais, carrega arquivos de tradução e tabelas.
    Deve ser chamado explicitamente no início da aplicação.
    """
    global translations_manager, tr_en, tr_pt, format_table, notes_list, logger
    
    print(">>> Initializing Globals...")

    # Check Semantic Files Existence & Update Config
    from helpers.github_requests import GitHubRequests
    gh = GitHubRequests()

    try:
        # Sync data files (format and translations)
        # Isso pode demorar (download), por isso é bom estar no init controlado
        gh.sync_data_files()
    except RodamException as e:
        print(f"[ERROR] Sync Failed: {e}")
        # Could exit or continue partial? User said "mais forte", usually implies handling.
        # But if core data missing, maybe bad.
        # However, let's just log and continue for now as 'gh.check_semantic_files_existence' follows.


    if not gh.check_semantic_files_existence():
        print(">>> Arquivos de semântica ausentes. Desabilitando recurso 'ShowSemantics'.")
        # Ensure config is loaded
        if 'global_config' in globals() and global_config:
            if global_config.ShowSemantics:
                global_config.ShowSemantics = False
                global_config.save()
    else:
        print(">>> Arquivos de semântica presente.")

    # Imports locais para evitar dependências circulares precoces
    from helpers.translations import TTranslations
    from helpers.format_table import FormatTable
    from helpers.notes import NotesList
    
    # Initialize Managers
    translations_manager = TTranslations(TUB_FILES_DIR)
    
    print(f"Carregando traduções...")
    tr_en = translations_manager.load(0)
    tr_pt = translations_manager.load(2)
    print(f"Traduções carregadas.")

    # Load Global Format Table
    FORMAT_TABLE_FILE = resource_path(os.path.join('assets', 'FormatTable.json'))
    format_table = FormatTable(FORMAT_TABLE_FILE)
    print(f"Tabela de Formatos carregada de: {FORMAT_TABLE_FILE}")

    # Load Notes
    NOTES_FILE = resource_path(os.path.join('assets', 'notes.json'))
    notes_list = NotesList(NOTES_FILE)
    print(f"Lista de Notas carregada de: {NOTES_FILE}")
    

    print(">>> Globals Initialized.")
