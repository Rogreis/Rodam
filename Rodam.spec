# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# --- CONFIGURAÇÃO DO NOME ---
app_name = 'Rodam'

# --- ARQUIVOS EXTRAS ---
# (source_folder, dest_folder)
datas = [
    ('templates', 'templates'),
    ('static', 'static')
]

# --- SELEÇÃO DE ÍCONE ---
# Coloque seus ícones numa pasta 'assets'
icon_path = None
if sys.platform == 'win32':
    icon_path = 'assets/icon.ico'
elif sys.platform == 'darwin':
    icon_path = 'assets/icon.icns'
else:
    icon_path = 'assets/icon.png'

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['uvicorn.loops.auto', 'uvicorn.protocols.http.auto'],
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

exe = EXE(
    pyz,
    a.scripts,
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
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path
)

# Apenas para Mac (Bundle .app)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name=f'{app_name}.app',
        icon=icon_path,
        bundle_identifier='com.rodam.app'
    )