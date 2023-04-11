from flask import Flask, request, send_file, Response
from ppf.datamatrix import DataMatrix
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO, StringIO
import os
from urllib.request import urlopen
from werkzeug.wsgi import FileWrapper, wrap_file



# http://127.0.0.1:5000/generate?p=Tddsasddd&s=xxx&t=nadfadf&q=mmM

app = Flask(__name__)


@app.route('/tmp')
def hello():
    return "Hello world!"


@app.route('/')
def generate():
    # Get parameters from the URL
    primary_title = request.args.get('p')
    secondary_title = request.args.get('s')
    tertiary_title = request.args.get('t')
    quaternary_title = request.args.get('q')
    initials = request.args.get('i')

    # could just \n each of the subtitles?
    # tertiary_title = f"{tertiary_title} \n {initials}"

    tertiary_title = f"{tertiary_title} {initials}"

    # Generate the datamatrix code
    myDataMatrix = DataMatrix(primary_title)

    # Set the desired size of the output image
    output_width = 1200
    output_height = output_width // 2

    datamatrix_width = output_width // 4
    datamatrix_height = datamatrix_width
    title_x = output_width // 3
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
    font_path = os.path.join(os.path.dirname(__file__), 'ArialBold.ttf')
    print(font_path)

    # Determine font size for primary title based on available width
    primary_title_size = int(((output_height - 3 * padding)) / 4)
    while primary_title_size > 0:
        temp_font = ImageFont.truetype(font_path, layout_engine=ImageFont.LAYOUT_BASIC, size=primary_title_size)
        if draw.textbbox((0, 0), primary_title, font=temp_font)[2] < available_width:
            primary_title_font = temp_font
        break
        primary_title_size -= 1
    # Set font styles
    secondary_title_font = ImageFont.truetype(font_path, layout_engine=ImageFont.LAYOUT_BASIC, size=int(((output_height) - primary_title_size) / 4))
    tertiary_title_font = ImageFont.truetype(font_path, layout_engine=ImageFont.LAYOUT_BASIC, size=int(((output_height) - primary_title_size) / 4))
    quaternary_title_font = ImageFont.truetype(font_path, layout_engine=ImageFont.LAYOUT_BASIC, size=int(((output_height) - primary_title_size) / 4))

    # Calculate y positions for secondary, tertiary, and quaternary titles
    line_spacing = int(((output_height) - primary_title_size) / 4)
    primary_title_y = 0  # - 19
    secondary_title_y = primary_title_y + primary_title_size
    tertiary_title_y = secondary_title_y + line_spacing
    quaternary_title_y = tertiary_title_y + line_spacing

    # Print titles
    draw.text((datamatrix_width + padding * 2, primary_title_y), primary_title, font=primary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, secondary_title_y), secondary_title, font=secondary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, tertiary_title_y), tertiary_title, font=tertiary_title_font, fill=0)
    draw.text((datamatrix_width + padding * 2, quaternary_title_y), quaternary_title, font=quaternary_title_font,
              fill=0)

    # Save the image to a buffer
    buffer = BytesIO()
    canvas.save(buffer, "PNG")
    buffer.seek(0)
    w = FileWrapper(buffer)
    return Response(w, mimetype="image/png", direct_passthrough=True)

    #canvas.save(buffer, "PNG")
    #buffer.seek(0)

    # Return the image to the user
    #return send_file(buffer, mimetype="image/png")


if __name__ == "__main__":
    app.run()
    
    
