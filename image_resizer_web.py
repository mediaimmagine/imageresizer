#!/usr/bin/env python3
"""
Image Resizer - Web Interface
A reliable web-based version that works on all systems
"""

from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import os
import io
import tempfile
from pathlib import Path
import base64

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_copyright_metadata(image):
    """Extract copyright information from image metadata"""
    try:
        exif_data = image.getexif()
        
        if exif_data:
            copyright_tag = 33432
            if copyright_tag in exif_data:
                return exif_data[copyright_tag]
            
            artist_tag = 315
            if artist_tag in exif_data:
                return f"Artist: {exif_data[artist_tag]}"
        
        if hasattr(image, 'info'):
            info = image.info
            
            for key in ['copyright', 'Copyright', 'COPYRIGHT', 'author', 'Author', 'creator', 'Creator']:
                if key in info:
                    return info[key]
        
        return None
        
    except Exception:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Open image and get info
            with Image.open(filepath) as img:
                width, height = img.size
                file_size = os.path.getsize(filepath) / 1024
                
                # Check for copyright
                copyright_info = extract_copyright_metadata(img)
                
                # Convert to base64 for preview
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'width': width,
                    'height': height,
                    'file_size': round(file_size, 1),
                    'format': img.format,
                    'copyright': copyright_info,
                    'preview': f"data:image/jpeg;base64,{img_str}"
                })
                
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/resize', methods=['POST'])
def resize_image():
    data = request.get_json()
    
    try:
        filename = data['filename']
        width = int(data['width'])
        height = int(data['height'])
        quality = int(data['quality'])
        output_format = data['format']
        crop = data.get('crop', False)
        
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with Image.open(input_path) as img:
            # Calculate aspect ratios
            orig_ratio = img.size[0] / img.size[1]
            target_ratio = width / height
            needs_crop = abs(orig_ratio - target_ratio) > 0.01
            
            if crop and needs_crop:
                # Calculate crop box for center cropping
                if orig_ratio > target_ratio:
                    new_width = int(img.size[1] * target_ratio)
                    left = (img.size[0] - new_width) // 2
                    crop_box = (left, 0, left + new_width, img.size[1])
                else:
                    new_height = int(img.size[0] / target_ratio)
                    top = (img.size[1] - new_height) // 2
                    crop_box = (0, top, img.size[0], top + new_height)
                
                cropped = img.crop(crop_box)
                resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
            else:
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert format if needed
            if output_format.lower() == 'jpg' and resized.mode == 'RGBA':
                background = Image.new('RGB', resized.size, (255, 255, 255))
                background.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
                resized = background
            
            # Save with appropriate settings
            save_kwargs = {}
            
            if output_format.lower() == 'jpg':
                save_kwargs = {
                    'quality': quality,
                    'optimize': True
                }
            elif output_format.lower() == 'webp':
                save_kwargs = {
                    'quality': quality,
                    'method': 6
                }
            elif output_format.lower() == 'png':
                if quality >= 80:
                    compress_level = 3
                elif quality >= 50:
                    compress_level = 6
                else:
                    compress_level = 9
                
                save_kwargs = {
                    'optimize': True,
                    'compress_level': compress_level
                }
            
            # Generate output filename
            original_name = Path(filename).stem
            output_filename = f"trieste@news_{original_name}.{output_format}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            resized.save(output_path, **save_kwargs)
            
            # Get file size
            file_size = os.path.getsize(output_path) / 1024
            
            # Create preview
            preview_img = resized.copy()
            preview_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            preview_img.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return jsonify({
                'success': True,
                'output_filename': output_filename,
                'file_size': round(file_size, 1),
                'preview': f"data:image/jpeg;base64,{img_str}",
                'crop_info': f"Cropped to fit" if crop and needs_crop else None
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to resize image: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    print("Starting Image Resizer Web Interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)









