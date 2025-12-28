# Action para Windows, Mac e Linux (GitHub Actions + PyInstaller)


O segredo para usar um único arquivo .spec para todos é não usar caminhos fixos (como C:\Users\...). Use o módulo os do Python dentro do .spec.

Passos:

1. Você dá um `git push origin v1.0.0`.
2. O GitHub Actions acorda, constrói os executáveis para Windows, Mac e Linux.
3. Ele cria uma **Release** na aba "Releases" do GitHub.
4. O título da Release será **"v1.0.0"** (ou o que você quiser formatar).
5. Os arquivos `Rodam.exe`, `Rodam.dmg`, etc., estarão lá prontos para download.


---

### Passo 1: Ajustar o `Rodam.spec` (Receita do PyInstaller)

Você deve renomear seu arquivo `.spec` ou gerar um novo para garantir que o executável final se chame "Rodam".

Crie/Edite o arquivo `Rodam.spec` na raiz do projeto:

```python
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

```

---

### Passo 2: O Workflow do GitHub (`.github/workflows/release.yml`)

Este arquivo faz a mágica. Ele lê a tag (ex: `v1.2.0`) e usa isso para nomear a Release e os arquivos.

Crie o arquivo: `.github/workflows/release.yml`

```yaml
name: Build e Release do Rodam

# Gatilho: Apenas quando uma tag começando com 'v' for enviada
on:
  push:
    tags:
      - 'v*' 

jobs:
  create-release:
    name: Build para ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        # Cria 3 máquinas virtuais simultâneas
        include:
          - os: ubuntu-latest
            TARGET_OS: Linux
            FILE_EXT: ""   # Linux não tem extensão padrão
            MIME_TYPE: application/x-executable
          - os: windows-latest
            TARGET_OS: Windows
            FILE_EXT: .exe
            MIME_TYPE: application/vnd.microsoft.portable-executable
          - os: macos-latest
            TARGET_OS: MacOS
            FILE_EXT: .dmg # No Mac vamos empacotar depois
            MIME_TYPE: application/x-apple-diskimage

    steps:
      - name: Checkout do Código
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      # Dependências de sistema para o Linux (necessário para pywebview)
      - name: Instalar Deps Linux
        if: runner.os == 'Linux'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev

      - name: Instalar Python Requirements
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      # Compilar com PyInstaller
      - name: Build com PyInstaller
        run: pyinstaller Rodam.spec

      # --- TRATAMENTO PÓS-BUILD ---

      # 1. WINDOWS: Renomeia para Rodam-Windows-v1.0.0.exe
      - name: Preparar Windows
        if: runner.os == 'Windows'
        run: |
          move dist\Rodam.exe dist\Rodam-${{ matrix.TARGET_OS }}-${{ github.ref_name }}.exe

      # 2. LINUX: Renomeia para Rodam-Linux-v1.0.0
      - name: Preparar Linux
        if: runner.os == 'Linux'
        run: |
          mv dist/Rodam dist/Rodam-${{ matrix.TARGET_OS }}-${{ github.ref_name }}

      # 3. MAC: Cria DMG e renomeia
      - name: Preparar Mac (Criar DMG)
        if: runner.os == 'macOS'
        run: |
          npm install -g create-dmg
          create-dmg dist/Rodam.app dist/ || true
          mv dist/Rodam\ 0.0.0.dmg dist/Rodam-${{ matrix.TARGET_OS }}-${{ github.ref_name }}.dmg

      # --- PUBLICAR NO GITHUB RELEASES ---
      
      - name: Publicar Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          # AQUI ESTÁ O QUE VOCÊ PEDIU:
          # O nome da Release será a Tag (ex: v1.0.2)
          name: Versão ${{ github.ref_name }}
          draft: false
          prerelease: false
          files: |
            dist/Rodam-${{ matrix.TARGET_OS }}-${{ github.ref_name }}${{ matrix.FILE_EXT }}

```

---

### Como funciona a numeração automática:

1. **`${{ github.ref_name }}`**: Essa variável mágica do GitHub contém exatamente o texto da tag que você enviou. Se você enviou `git tag v1.0.5`, essa variável vale `v1.0.5`.
2. **No YAML acima:**
* Na linha `name: Versão ${{ github.ref_name }}`, o título na página do GitHub será **"Versão v1.0.5"**.
* Nos comandos `move` e `mv`, estamos criando arquivos como: `Rodam-Windows-v1.0.5.exe`. Isso é ótimo para o usuário saber o que baixou.



### Como disparar o processo (Seu fluxo de trabalho)

No seu terminal local, quando estiver pronto para lançar uma versão nova:

1. **Salvar tudo:**
```bash
git add .
git commit -m "Finalizando funcionalidades para release"
git push

```


2. **Criar a Tag (A "Etiqueta" da versão):**
```bash
# Crie a tag com o número que você quer
git tag v1.0.0

```


3. **Enviar a Tag (O Gatilho):**
```bash
# Isso avisa o GitHub para rodar o script 'release.yml'
git push origin v1.0.0

```


4. **Aguardar:**
* Vá na aba **Actions** do seu repositório. Você verá um workflow rodando.
* Espere uns 3 a 5 minutos (o Windows demora um pouco).
* Quando ficar verde, vá na aba **Releases** (geralmente na barra lateral direita da página inicial do repo). Sua nova versão estará lá com os 3 arquivos para download.
  