from PIL import Image, ImageDraw
import os

def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_icon(size, color=(37, 99, 235), background=(255, 255, 255, 0)):
    # Create a new image with a transparent background
    img = Image.new('RGBA', (size, size), background)
    draw = ImageDraw.Draw(img)
    
    # Draw a circle
    padding = size // 10
    circle_bbox = (padding, padding, size - padding, size - padding)
    draw.ellipse(circle_bbox, fill=color)
    
    return img

def generate_icons():
    # Create icons directory
    create_directory_if_not_exists('static/icons')
    
    # Generate different sized icons
    sizes = {
        'favicon-16x16.png': 16,
        'favicon-32x32.png': 32,
        'apple-touch-icon.png': 180,
        'icon-192.png': 192,
        'maskable-icon.png': 192,
        'icon-512.png': 512
    }
    
    for filename, size in sizes.items():
        icon = create_icon(size)
        icon.save(f'static/icons/{filename}', 'PNG')
        
        # Create favicon.ico (contains both 16x16 and 32x32)
        if size == 16:
            icon16 = icon
        elif size == 32:
            icon32 = icon
            
    # Save favicon.ico with both sizes
    icon16.save('static/icons/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32)])

if __name__ == '__main__':
    generate_icons() 