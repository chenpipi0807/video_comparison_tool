from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with dark background
    img = Image.new('RGBA', (256, 256), (45, 45, 45, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a play icon in the center
    draw.polygon([(80, 60), (80, 196), (196, 128)], fill=(30, 144, 255, 255))
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "视频对比", font=font, fill=(255, 255, 255, 255))
    
    # Save the image as .ico
    img.save('logo.ico', format='ICO', sizes=[(256, 256)])
    print("Icon created successfully!")

if __name__ == "__main__":
    create_icon()
