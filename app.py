from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO
import io
import random

app = Flask(__name__)

# Initialize the download count
download_count = 0
def generate_image(width, height, image_type='png'):
    global download_count
    download_count += 1

    # Create a blank white image
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Add small grey dots to the image
    for _ in range(100):  # Adjust the number of dots as needed
        x = random.randint(0, width)
        y = random.randint(0, height)
        grey_level = 128  # Adjust the grey level as needed
        draw.point((x, y), fill=(grey_level, grey_level, grey_level))

    # Apply a slight blur to the image (optional)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    if image_type.lower() == 'png':
        image.save(img_io, 'PNG')
    elif image_type.lower() == 'svg':
         # Create an SVG string
        svg_content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'

        # Add small grey circles to the SVG
        for _ in range(100):  # Adjust the number of circles as needed
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            r = 2  # Radius of the circle (adjust as needed)
            grey_level = random.randint(200, 255)  # Adjust the grey level as needed
            svg_content += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgb({grey_level}, {grey_level}, {grey_level})" />'

        # Close the SVG tag
        svg_content += '</svg>'

        # Save the SVG content to a BytesIO object
        img_io = BytesIO(svg_content.encode())

    elif image_type.lower() == 'jpeg':
        image.save(img_io, 'JPEG')
    elif image_type.lower() == 'ico':
        image.save(img_io, 'ICO')
    else:
        raise ValueError("Unsupported image type")

    # Save the download count to a text file
    with open('download_count.txt', 'w') as count_file:
        count_file.write(str(download_count))

    img_io.seek(0)
    return img_io

@app.route('/')
def index():
    try:
        # Read the download count from the text file
        with open('download_count.txt', 'r') as count_file:
            download_count = int(count_file.read())
    except FileNotFoundError:
        download_count = 0

    return render_template('index.html', download_count=download_count)

@app.route('/download', methods=['POST'])
def download():
    try:
        width = int(request.form['width'])
        height = int(request.form['height'])
        image_type = request.form['image_type']

        if image_type.lower() not in ['png', 'svg', 'jpeg', 'ico']:
            raise ValueError("Unsupported image type")

        img_io = generate_image(width, height, image_type)

        if image_type.lower() == 'png':
            return send_file(img_io, mimetype='image/png', download_name='generated_image.png', as_attachment=True)
        elif image_type.lower() == 'svg':
            return send_file(img_io, mimetype='image/svg+xml', download_name='generated_image.svg', as_attachment=True)
        elif image_type.lower() == 'jpeg':
            return send_file(img_io, mimetype='image/jpeg', download_name='generated_image.jpeg', as_attachment=True)
        elif image_type.lower() == 'ico':
            return send_file(img_io, mimetype='image/x-icon', download_name='generated_image.ico', as_attachment=True)
    except ValueError as e:
        return render_template('error.html', error_message=str(e))

if __name__ == '__main__':
    app.run(debug=False,host=0.0.0.0)
