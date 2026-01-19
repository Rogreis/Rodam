import os
from PIL import Image

def criar_icones():
    # Verifica se a imagem master existe
    if not os.path.exists("rodam_master.png"):
        print("Erro: Por favor, coloque o arquivo 'rodam_master.png' (1024x1024) na pasta.")
        return

    # Cria diretório resources se não existir
    if not os.path.exists("resources"):
        os.makedirs("resources")

    img = Image.open("rodam_master.png")

    print("Gerando ícones...")

    # 1. LINUX (icon.png - 256x256)
    # O Linux gosta de PNGs simples
    icon_linux = img.resize((256, 256), Image.Resampling.LANCZOS)
    icon_linux.save("resources/icon.png")
    print("✅ Linux: resources/icon.png criado.")

    # 2. WINDOWS (icon.ico)
    # O Windows precisa de múltiplas resoluções empacotadas
    sizes_win = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("resources/icon.ico", format="ICO", sizes=sizes_win)
    print("✅ Windows: resources/icon.ico criado.")

    # 3. MACOS (icon.icns)
    # O Pillow consegue salvar ICNS se estiver em um Mac ou Linux com dependências,
    # mas às vezes falha no Windows. Vamos tentar o método padrão.
    try:
        # Para Mac, o ideal é ter tamanhos até 512 ou 1024
        img.save("resources/icon.icns", format="ICNS")
        print("✅ MacOS: resources/icon.icns criado.")
    except Exception as e:
        print(f"⚠️  Aviso MacOS: Não foi possível gerar .icns nativamente via Pillow ({e}).")
        print("   Alternativa: O create-dmg no GitHub Actions muitas vezes aceita o .png ou .app bundle.")
        # Se falhar, salvamos um PNG grande para o Mac usar
        img.save("resources/icon_mac.png")

    print("\nConcluído! Verifique a pasta 'resources'.")

if __name__ == "__main__":
    criar_icones()
    