import webbrowser
import os
import base64
import io
from PIL import Image

def file_to_base64_html(path):
    """
    Lê o arquivo e retorna uma string pronta para ser usada no src da tag <img>.
    Trata conversão de ICNS e leitura de ICO/PNG.
    """
    try:
        if not os.path.exists(path):
            return None
            
        # Tratamento especial para ICNS (Converter para PNG em memória)
        if path.lower().endswith('.icns'):
            img = Image.open(path)
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{img_str}"
        
        # Leitura padrão para PNG e ICO
        with open(path, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode("utf-8")
            
        mime_type = "image/x-icon" if path.endswith(".ico") else "image/png"
        return f"data:{mime_type};base64,{img_str}"
        
    except Exception as e:
        print(f"Erro ao processar {path}: {e}")
        return None

def gerar_auditoria_completa():
    # Caminhos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = {
        "SVG (Vetorial Original)": "rodam_logo.svg", # Está na raiz
        "Linux/Web (.png)": os.path.join(base_dir, "icon.png"),
        "Windows (.ico)": os.path.join(base_dir, "icon.ico"),
        "MacOS (.icns)": os.path.join(base_dir, "icon.icns")
    }


    # Gera o HTML dinâmico
    rows_html = ""
    
    for label, filepath in files.items():
        # Prepara o conteúdo visual
        img_tag = ""
        
        if label == "SVG (Vetorial Original)":
            # Para SVG lemos o texto direto
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    svg_raw = f.read()
                    # Força tamanho para caber na caixa
                    img_tag = f'<div style="width:128px; height:128px">{svg_raw}</div>'
            else:
                img_tag = "<span class='err'>Arquivo não encontrado</span>"
        else:
            # Para binários, usamos Base64
            src = file_to_base64_html(filepath)
            if src:
                img_tag = f'<img src="{src}" alt="{label}">'
            else:
                img_tag = "<span class='err'>Arquivo não encontrado</span>"

        # Adiciona a linha na tabela (Light vs Dark)
        rows_html += f"""
        <tr>
            <td class="meta">
                <strong>{label}</strong><br>
                <small>{filepath}</small>
            </td>
            <td class="preview light-mode">
                {img_tag}
                <div class="caption">Light Mode</div>
            </td>
            <td class="preview dark-mode">
                {img_tag}
                <div class="caption">Dark Mode</div>
            </td>
        </tr>
        """

    # HTML Template Completo
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Auditoria Visual: Rodam</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f4f9; padding: 20px; }}
            h1 {{ text-align: center; color: #333; }}
            table {{ 
                width: 100%; max-width: 1000px; margin: 0 auto; 
                border-collapse: collapse; background: white;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;
            }}
            th, td {{ padding: 20px; text-align: center; vertical-align: middle; }}
            
            /* Coluna de Metadados */
            .meta {{ text-align: left; width: 200px; border-bottom: 1px solid #eee; }}
            .meta strong {{ font-size: 1.1em; color: #2c3e50; }}
            .meta small {{ color: #7f8c8d; }}
            
            /* Colunas de Preview */
            .preview {{ border-bottom: 1px solid #eee; position: relative; }}
            img {{ max-width: 128px; max-height: 128px; }}
            
            /* MODO CLARO (Simula janelas padrão) */
            .light-mode {{ background-color: #ffffff; background-image: linear-gradient(45deg, #f0f0f0 25%, transparent 25%), linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f0f0f0 75%), linear-gradient(-45deg, transparent 75%, #f0f0f0 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px; }}
            
            /* MODO ESCURO (Simula temas Dark) */
            .dark-mode {{ background-color: #2b2b2b; color: #fff; }}
            
            .caption {{ 
                margin-top: 10px; font-size: 0.8em; text-transform: uppercase; 
                letter-spacing: 1px; opacity: 0.6; 
            }}
            .err {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Auditoria de Ícones (Claro vs Escuro)</h1>
        <p style="text-align:center">Verifique se há bordas brancas indesejadas no lado escuro.</p>
        <table>
            {rows_html}
        </table>
    </body>
    </html>
    """

    # Salvar e Abrir
    output_file = "auditoria_final.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Relatório gerado: {os.path.abspath(output_file)}")
    webbrowser.open('file://' + os.path.realpath(output_file))

if __name__ == "__main__":
    gerar_auditoria_completa()