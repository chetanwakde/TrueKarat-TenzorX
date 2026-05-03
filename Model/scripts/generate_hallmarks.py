import os
import random
import string
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_metallic_texture(width, height):
    # Create base golden color
    base_color = (200, 160, 50)
    img = Image.new('RGB', (width, height), color=base_color)
    
    # Add noise
    pixels = img.load()
    for i in range(width):
        for j in range(height):
            noise = random.randint(-30, 30)
            r = min(255, max(0, base_color[0] + noise))
            g = min(255, max(0, base_color[1] + noise))
            b = min(255, max(0, base_color[2] + noise))
            pixels[i, j] = (r, g, b)
            
    # Apply blur to smooth out noise
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    
    # Add scratches
    draw = ImageDraw.Draw(img)
    for _ in range(random.randint(5, 15)):
        pt1 = (random.randint(0, width), random.randint(0, height))
        pt2 = (pt1[0] + random.randint(-50, 50), pt1[1] + random.randint(-50, 50))
        draw.line([pt1, pt2], fill=(220, 180, 100), width=1)
        
    return img

def engrave_text(img, text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Use default font
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font = ImageFont.load_default()
        
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (width - text_w) // 2
    y = (height - text_h) // 2
    
    # Draw engraved effect
    draw.text((x-2, y-2), text, font=font, fill=(30, 30, 30))  # shadow
    draw.text((x+2, y+2), text, font=font, fill=(255, 230, 150)) # highlight
    draw.text((x, y), text, font=font, fill=(100, 80, 30)) # main
    
    return img

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    images_out_dir = os.path.join(out_dir, "images")
    os.makedirs(images_out_dir, exist_ok=True)
    
    num_samples = 500
    hallmarks = ["916", "22K", "BIS", "750", "18K", "585", "14K", "999", "24K"]
    
    print(f"Generating {num_samples} synthetic hallmark images using PIL...")
    
    for i in range(num_samples):
        width, height = random.randint(200, 300), random.randint(100, 150)
        img = create_metallic_texture(width, height)
        
        mark = random.choice(hallmarks)
        img = engrave_text(img, mark)
        
        # Add rotation
        angle = random.uniform(-15, 15)
        img = img.rotate(angle, resample=Image.BICUBIC, fillcolor=(200, 160, 50))
        
        # Add random blur for macro out-of-focus effect
        if random.random() > 0.5:
            img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 2.0)))
            
        filename = f"Synthetic_Hallmark_{i}.jpg"
        filepath = os.path.join(images_out_dir, filename)
        img.save(filepath, "JPEG")

    print(f"Successfully generated {num_samples} synthetic hallmarks for OCR training.")

if __name__ == "__main__":
    main()
