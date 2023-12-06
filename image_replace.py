from PIL import Image

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_close_enough(color1, color2, tolerance=50):
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

def replace_colors(image_path, color_replacements, tolerance=100):
    # Convert all hex colors to RGB
    color_replacements_rgb = [(hex_to_rgb(old_color), hex_to_rgb(new_color)) for old_color, new_color in color_replacements]
    
    # Load the image
    image = Image.open(image_path)
    
    # Ensure the image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert the image to a sequence of pixels
    pixels = image.load()

    # Iterate through each pixel and replace the colors
    for i in range(image.width):
        for j in range(image.height):
            current_color = pixels[i, j]
            for old_color, new_color in color_replacements_rgb:
                if is_close_enough(current_color, old_color, tolerance):
                    pixels[i, j] = new_color

    # Save the modified image
    image.save('Dau-replaced.png')

color_replacements = [('#82C2E5', '#262626'), ('#000000', '#FFFFFF'), ('#415188', '#FFFFFF')]
replace_colors('Dau.jpg', color_replacements)

