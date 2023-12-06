from flask import Flask, request, send_file, Response
from ppf.datamatrix import DataMatrix
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from werkzeug.wsgi import FileWrapper

from typing import Tuple

def calculate_font_size(draw, text: str, font_path: str, max_width: int, output_height: int, padding: int) -> Tuple[int, ImageFont.FreeTypeFont]:
    font_size = int((output_height - 3 * padding) / 4)

    while font_size > 0:
        temp_font = ImageFont.truetype(font_path, layout_engine=ImageFont.LAYOUT_BASIC, size=font_size)

        # Get the total width and height of the title
        title_width, title_height = draw.textsize(text, font=temp_font)

        if title_width < max_width:
            return font_size, title_height, temp_font

        font_size -= 1

    # Return default values if none is found
    return 12, 0, ImageFont.load_default()

app = Flask(__name__)

@app.route('/')
def generate():
    # Get parameters from the URL
    dm = request.args.get('dm')
    primary_title = request.args.get('p')
    secondary_title = request.args.get('s')
    tertiary_title = request.args.get('t')
    quaternary_title = request.args.get('q')
    quinary_title = request.args.get('a5')
    initials = request.args.get('i')

    # Combine tertiary_title and initials
    tertiary_title = f"{tertiary_title} {initials}"

    # Generate the datamatrix code
    myDataMatrix = DataMatrix(dm)

    # Set the desired size of the output image
    output_width = 2400
    output_height = output_width // 2

    datamatrix_width = output_width // 4
    datamatrix_height = datamatrix_width
    padding = output_width // 48

    available_width = output_width - (datamatrix_width + (padding))

    # Create the blank output image
    canvas = Image.new(mode="1", size=(output_width, output_height), color=1)

    # Create the datamatrix image and paste it onto the output image
    img = Image.new('1', (len(myDataMatrix.matrix), len(myDataMatrix.matrix)))
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[j, i] = (myDataMatrix.matrix[i][j] == 0)
    img = img.resize((datamatrix_width, datamatrix_height), Image.LANCZOS)
    canvas.paste(img, (padding, padding))

    # Add titles to the right of the datamatrix
    draw = ImageDraw.Draw(canvas)
    font_path_bold = os.path.join(os.path.dirname(__file__), 'ArialBold.ttf')
    font_path = os.path.join(os.path.dirname(__file__), 'Arial.ttf')

    # Determine font sizes and heights for all titles
    max_primary_title_width = available_width - (padding * 2)
    primary_title_size, primary_title_height, primary_title_font = calculate_font_size(draw, primary_title, font_path_bold, max_primary_title_width, output_height, padding)
    
    max_secondary_title_width = available_width - (padding * 2)
    secondary_title_size, secondary_title_height, secondary_title_font = calculate_font_size(draw, secondary_title, font_path, max_secondary_title_width, output_height - primary_title_size - padding, padding)
    
    max_tertiary_title_width = available_width - (padding * 2)
    tertiary_title_size, tertiary_title_height, tertiary_title_font = calculate_font_size(draw, tertiary_title, font_path, max_tertiary_title_width, output_height - primary_title_size - padding, padding)
    
    max_quaternary_title_width = available_width - (padding * 2)
    quaternary_title_size, quaternary_title_height, quaternary_title_font = calculate_font_size(draw, quaternary_title, font_path, max_quaternary_title_width, output_height - primary_title_size - padding, padding)
    
    max_quinary_title_width = available_width - (padding * 2)
    quinary_title_size, quinary_title_height, quinary_title_font = calculate_font_size(draw, quinary_title, font_path, max_quinary_title_width, output_height - primary_title_size - padding, padding)

    # Set font styles
    secondary_title_font = ImageFont.truetype(font_path, size=secondary_title_size)
    tertiary_title_font = ImageFont.truetype(font_path, size=tertiary_title_size)
    quaternary_title_font = ImageFont.truetype(font_path, size=quaternary_title_size)
    quinary_title_font = ImageFont.truetype(font_path, size=quinary_title_size)

    # Calculate total height occupied by titles
    total_height = primary_title_height + secondary_title_height + tertiary_title_height + quaternary_title_height + quinary_title_height
    
    # Calculate line spacing for single spacing
    line_spacing = int((output_height - total_height) / 5)
    
    # Calculate y positions for titles with single spacing
    primary_title_y = 0
    secondary_title_y = primary_title_y + primary_title_height + line_spacing
    tertiary_title_y = secondary_title_y + secondary_title_height + line_spacing
    quaternary_title_y = tertiary_title_y + tertiary_title_height + line_spacing
    quinary_title_y = quaternary_title_y + quaternary_title_height + line_spacing
    
    # Print titles
    draw.text((datamatrix_width + padding * 2, primary_title_y), primary_title, font=primary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, secondary_title_y), secondary_title, font=secondary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, tertiary_title_y), tertiary_title, font=tertiary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, quaternary_title_y), quaternary_title, font=quaternary_title_font,
              fill=0)
    draw.text((datamatrix_width + padding * 2, quinary_title_y), quinary_title, font=quinary_title_font,
              fill=0)

    # Save the image to a buffer
    buffer = BytesIO()
    canvas.save(buffer, "PNG")
    buffer.seek(0)

    # Set the filename for the downloaded image
    filename = "label.png"

    # Create a FileWrapper and return a Response with the appropriate headers
    w = FileWrapper(buffer)
    response = Response(w, mimetype="image/png", direct_passthrough=True)
    response.headers.set('Content-Disposition', 'attachment', filename=filename)


    return response

if __name__ == "__main__":
    app.run()
