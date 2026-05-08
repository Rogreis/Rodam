# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# --- CONFIGURAÇÃO DO NOME ---
app_name = 'Rodam'

# --- ARQUIVOS EXTRAS ---
# (source_folder, dest_folder)
_raw_datas = [
    ('templates', 'templates'),
    ('css', 'css'),
    ('js', 'js'),
    ('assets', 'assets'),
    ('resources', 'resources'),
    ('favicon.ico', '.')
]

# Filtrar apenas arquivos/diretórios que realmente existem, para evitar falhas durante o build
datas = [(src, dest) for src, dest in _raw_datas if os.path.exists(src)]

# --- SELEÇÃO DE ÍCONE ---
# Coloque seus ícones numa pasta 'assets' ou use o favicon da raiz
icon_path = 'favicon.ico'
if sys.platform == 'win32':
    if os.path.exists('resources/icon.ico'):
        icon_path = 'resources/icon.ico'
    elif os.path.exists('assets/icon.ico'):
        icon_path = 'assets/icon.ico'
elif sys.platform == 'darwin':
    if os.path.exists('resources/icon.icns'):
        icon_path = 'resources/icon.icns'
    elif os.path.exists('assets/icon.icns'):
        icon_path = 'assets/icon.icns'

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'uvicorn.loops.auto', 
        'uvicorn.protocols.http.auto',
        'webview',
        'bs4',
        'requests',
        'numpy',
        'faiss',
        'sentence_transformers',
        # Dependencies often missed by hook
        'sklearn.neighbors._typedefs',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors._quad_tree',
        'sklearn.tree._utils',
        'scipy.special.cython_special',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

splash = Splash(
    'resources/splash_text.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,  # AQUI O NOME DO EXECUTÁVEL
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # False = Sem tela preta
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=os.environ.get('CODESIGN_IDENTITY', None),
    entitlements_file='entitlements.plist' if sys.platform == 'darwin' and os.path.exists('entitlements.plist') else None,
    icon=icon_path
)

# Apenas para Mac (Bundle .app)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{app_name}.app',
        icon=icon_path,
        bundle_identifier='com.rodam.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            # Requisito para App Store / Notarização: Declarar uso de microfone/câmera se for usado pelo engine web
            'NSMicrophoneUsageDescription': 'O aplicativo precisa de acesso ao microfone, caso solicitado.',
            'NSCameraUsageDescription': 'O aplicativo precisa de acesso à câmera, caso solicitado.'
        },
        # É fundamental aplicar a identidade e os entitlements também na raiz do App Bundle
        entitlements_file='entitlements.plist' if os.path.exists('entitlements.plist') else None,
        codesign_identity=os.environ.get('CODESIGN_IDENTITY', None),
    )