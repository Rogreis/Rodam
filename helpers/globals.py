import os
import sys

# Define resource_path and get_config_dir first as they are fundamental

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_dir():
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
    elif sys.platform == 'darwin':
        base = os.path.join(os.environ.get('HOME'), 'Library', 'Application Support')
    else:
        base = os.path.join(os.environ.get('HOME'), '.config')
    return os.path.join(base, 'Rodam')

# Global Constants and Paths
CONFIG_FILE = os.path.join(get_config_dir(), 'Rodam.json')
TUB_FILES_DIR = os.path.join(get_config_dir(), 'TUB_Files')

# Ensure config dir exists
if not os.path.exists(get_config_dir()):
    try:
        os.makedirs(get_config_dir())
    except OSError:
        pass # Handle permission errors or race conditions if necessary

# Imports from other helpers
from helpers.translations import TTranslations

# Global Objects
translations_manager = TTranslations(TUB_FILES_DIR)
print(f"Carregando traduções")
translation = translations_manager.load(0)
translation = translations_manager.load(2)
print(f"Traduções carregadas")

# Load Global Format Table
from helpers.translations import TTranslations, FormatTable

FORMAT_TABLE_FILE = resource_path(os.path.join('assets', 'FormatTable.json'))
format_table = FormatTable(FORMAT_TABLE_FILE)
print(f"Tabela de Formatos carregada de: {FORMAT_TABLE_FILE}")

# Import Config after defining paths to avoid circular issues, though Config is independent mostly.
# Note: helpers.config imports CONFIG_FILE from here, so we must be careful.
# Ideally, we import Config here but Config needs CONFIG_FILE from here.
# Config.py has 'from helpers.globals import CONFIG_FILE'.
# So if we import Config here, it's circular.
# However, Python handles this if done inside functions or carefully.
# But Config class is at top level.
# To break circle, we can use a getter or deferred import.
# Actually, the user asked to "force read in globals.py".
# Let's import it inside the file but after definitions.

from helpers.config import Config
global_config = Config.load()
