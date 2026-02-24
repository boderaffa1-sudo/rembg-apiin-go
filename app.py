from flask import Flask, request, Response
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        return {'error': 'No image file provided. Use field name: image'}, 400
    
    file = request.files['image']
    
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    try:
        input_bytes = file.read()
        output_bytes = remove(input_bytes)
        
        # Convert to white background JPEG
        img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))
        background.paste(img, mask=img.split()[3])
        final = background.convert("RGB")
        
        output = io.BytesIO()
        final.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='image/jpeg',
            headers={'Content-Disposition': 'attachment; filename=removed_bg.jpg'}
        )
    
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
