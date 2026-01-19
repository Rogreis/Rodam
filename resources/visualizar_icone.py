import webbrowser
import os
import base64
import io
from PIL import Image

def image_to_base64(path, format_override=None):
    """
    Lê uma imagem do disco e retorna uma string base64 pronta para HTML.
    Se for ICNS, converte para PNG em memória primeiro.
    """
    try:
        if not os.path.exists(path):
            return None
            
        # Para ICNS, precisamos converter usando Pillow
        if path.lower().endswith('.icns'):
            img = Image.open(path)
            # O ICNS tem vários tamanhos, pegamos o atual (geralmente o maior aberto pelo Pillow)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{img_str}"
        
        # Para ICO e PNG, lemos os bytes diretos
        # Nota: Navegadores modernos abrem ICO, mas base64 é mais seguro para garantir visualização
        with open(path, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode("utf-8")
            
        mime_type = "image/x-icon" if path.endswith(".ico") else "image/png"
        return f"data:{mime_type};base64,{img_str}"
        
    except Exception as e:
        print(f"Erro ao ler {path}: {e}")
        return None

def gerar_preview():
    # Caminhos dos arquivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_svg = os.path.join(base_dir, "rodam_logo.svg")
    path_png = os.path.join(base_dir, "icon.png")
    path_ico = os.path.join(base_dir, "icon.ico")
    path_icns = os.path.join(base_dir, "icon.icns")

    # Verifica SVG (Texto)
    svg_content = "Arquivo não encontrado"
    if os.path.exists(path_svg):
        with open(path_svg, "r", encoding="utf-8") as f:
            svg_content = f.read()

    # Gera Base64 dos binários
    b64_png = image_to_base64(path_png)
    b64_ico = image_to_base64(path_ico)
    b64_icns = image_to_base64(path_icns) # Aqui acontece a mágica da conversão

    # HTML Template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Auditoria de Ícones Rodam</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #f0f2f5; padding: 40px; }}
            h1 {{ text-align: center; color: #333; margin-bottom: 40px; }}
            .container {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                max-width: 1200px; 
                margin: 0 auto; 
            }}
            .card {{ 
                background: white; 
                padding: 20px; 
                border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
                text-align: center; 
                transition: transform 0.2s;
            }}
            .card:hover {{ transform: translateY(-5px); }}
            .preview-box {{ 
                height: 150px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                border-bottom: 1px solid #eee;
                margin-bottom: 15px;
            }}
            img, svg {{ max-width: 128px; max-height: 128px; }}
            .label {{ font-weight: bold; color: #555; display: block; }}
            .sublabel {{ font-size: 0.85em; color: #888; }}
            .status-ok {{ color: green; font-weight: bold; }}
            .status-err {{ color: red; font-weight: bold; }}
            .note {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>Auditoria de Ícones Gerados</h1>
        
        <div class="container">
            <div class="card">
                <div class="preview-box">
                    {svg_content}
                </div>
                <span class="label">Original Vetorial</span>
                <span class="sublabel">rodam_logo.svg</span>
            </div>

            <div class="card">
                <div class="preview-box">
                    {f'<img src="{b64_png}">' if b64_png else '<span class="status-err">Arquivo não encontrado</span>'}
                </div>
                <span class="label">Linux / Web</span>
                <span class="sublabel">icon.png (256x256)</span>
            </div>

            <div class="card">
                <div class="preview-box">
                    {f'<img src="{b64_ico}">' if b64_ico else '<span class="status-err">Arquivo não encontrado</span>'}
                </div>
                <span class="label">Windows Installer</span>
                <span class="sublabel">icon.ico (Multi-size)</span>
            </div>

            <div class="card">
                <div class="preview-box">
                    {f'<img src="{b64_icns}">' if b64_icns else '<span class="status-err">Arquivo não encontrado</span>'}
                </div>
                <span class="label">MacOS App</span>
                <span class="sublabel">icon.icns (Apple Format)</span>
                <br><small style="color:#d9534f">Convertido p/ PNG para visualização</small>
            </div>
        </div>

        <div class="note">
            <p>Se você consegue ver as imagens acima, seus arquivos binários foram gerados corretamente.</p>
        </div>
    </body>
    </html>
    """

    # Salvar e Abrir
    file_path = "auditoria_icones.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Relatório gerado em: {os.path.abspath(file_path)}")
    webbrowser.open('file://' + os.path.realpath(file_path))

if __name__ == "__main__":
    gerar_preview()
