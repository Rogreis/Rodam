from PIL import Image, ImageDraw, ImageFont
import os

def create_splash():
    # Dimensions
    width = 600
    height = 300
    
    # Colors
    bg_color = (255, 255, 255) # White
    text_color = (50, 50, 50) # Dark Gray
    accent_color = (0, 120, 215) # Blue
    
    # Create Image
    img = Image.new('RGB', (width, height), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Text
    title = "RODAM"
    subtitle = "Inicializando aplicação..."
    message = "Expandindo arquivos temporários.\nIsso pode levar alguns instantes."
    
    # Fonts (Try default, otherwise load specific if needed but default is safer for script)
    # To look good we usually need a .ttf. 
    # Let's try to find a ttf or use default.
    try:
        # Windows standard font
        title_font = ImageFont.truetype("arial.ttf", 48)
        sub_font = ImageFont.truetype("arial.ttf", 20)
        msg_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        msg_font = ImageFont.load_default()

    # Calculate positions
    # Title
    bbox = d.textbbox((0,0), title, font=title_font)
    w = bbox[2] - bbox[0]
    d.text(((width - w)/2, 60), title, font=title_font, fill=accent_color)
    
    # Subtitle
    bbox = d.textbbox((0,0), subtitle, font=sub_font)
    w = bbox[2] - bbox[0]
    d.text(((width - w)/2, 130), subtitle, font=sub_font, fill=text_color)
    
    # Message (Multiline)
    lines = message.split('\n')
    y_text = 180
    for line in lines:
        bbox = d.textbbox((0,0), line, font=msg_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        d.text(((width - w)/2, y_text), line, font=msg_font, fill=text_color)
        y_text += h + 10
        
    # Border
    d.rectangle([0, 0, width-1, height-1], outline=accent_color, width=4)
    
    # Save
    output_path = os.path.join("resources", "splash_text.png")
    img.save(output_path)
    print(f"Splash saved to: {output_path}")

if __name__ == "__main__":
    create_splash()
