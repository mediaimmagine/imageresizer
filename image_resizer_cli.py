#!/usr/bin/env python3
"""
Image Resizer - Command Line Interface
A reliable, cross-platform version that works on all systems
"""

import argparse
import sys
import os
from pathlib import Path
from PIL import Image
import json

def resize_image(input_path, output_path, width, height, quality=85, format='jpg', crop=False):
    """Resize an image with the specified parameters"""
    
    try:
        # Open the image
        with Image.open(input_path) as img:
            print(f"Original image: {img.size[0]}x{img.size[1]} pixels")
            print(f"Original format: {img.format}")
            
            # Calculate aspect ratios
            orig_ratio = img.size[0] / img.size[1]
            target_ratio = width / height
            
            # Determine if cropping is needed
            needs_crop = abs(orig_ratio - target_ratio) > 0.01
            
            if crop and needs_crop:
                print(f"Cropping image to fit {width}x{height}...")
                
                # Calculate crop box for center cropping
                if orig_ratio > target_ratio:
                    # Image is wider than target - crop sides
                    new_width = int(img.size[1] * target_ratio)
                    left = (img.size[0] - new_width) // 2
                    crop_box = (left, 0, left + new_width, img.size[1])
                else:
                    # Image is taller than target - crop top/bottom
                    new_height = int(img.size[0] / target_ratio)
                    top = (img.size[1] - new_height) // 2
                    crop_box = (0, top, img.size[0], top + new_height)
                
                # Crop and resize
                cropped = img.crop(crop_box)
                resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
                print(f"Cropped from: {crop_box[2]-crop_box[0]}x{crop_box[3]-crop_box[1]} pixels")
                
            else:
                # Simple resize
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                if needs_crop:
                    print("Warning: Image will be stretched to fit dimensions")
            
            # Convert format if needed
            if format.lower() == 'jpg' and resized.mode == 'RGBA':
                # Convert RGBA to RGB for JPEG
                background = Image.new('RGB', resized.size, (255, 255, 255))
                background.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
                resized = background
            
            # Save with appropriate settings
            save_kwargs = {}
            
            if format.lower() == 'jpg':
                save_kwargs = {
                    'quality': quality,
                    'optimize': True
                }
            elif format.lower() == 'webp':
                save_kwargs = {
                    'quality': quality,
                    'method': 6
                }
            elif format.lower() == 'png':
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
            
            # Save the image
            resized.save(output_path, **save_kwargs)
            
            # Get file size
            file_size = os.path.getsize(output_path) / 1024
            
            print(f"Resized image: {width}x{height} pixels")
            print(f"Output format: {format.upper()}")
            print(f"Quality: {quality}%")
            print(f"File size: {file_size:.1f} KB")
            print(f"Saved to: {output_path}")
            
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_copyright(input_path):
    """Check for copyright information in image metadata"""
    try:
        with Image.open(input_path) as img:
            # Check EXIF data
            exif_data = img.getexif()
            
            if exif_data:
                # EXIF tag 33432 is Copyright
                copyright_tag = 33432
                if copyright_tag in exif_data:
                    return exif_data[copyright_tag]
                
                # Try Artist tag (315)
                artist_tag = 315
                if artist_tag in exif_data:
                    return f"Artist: {exif_data[artist_tag]}"
            
            # Check image info
            if hasattr(img, 'info'):
                info = img.info
                
                for key in ['copyright', 'Copyright', 'COPYRIGHT', 'author', 'Author', 'creator', 'Creator']:
                    if key in info:
                        return info[key]
            
            return None
            
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Image Resizer - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 image_resizer_cli.py input.jpg -w 1920 -h 1080
  python3 image_resizer_cli.py input.jpg -w 1920 -h 1080 -q 85 -f jpg -c
  python3 image_resizer_cli.py input.jpg -w 1920 -h 1080 -o output.jpg
  python3 image_resizer_cli.py input.jpg -w 1920 -h 1080 --check-copyright
        """
    )
    
    parser.add_argument('input', help='Input image file')
    parser.add_argument('-w', '--width', type=int, required=True, help='Target width in pixels')
    parser.add_argument('--height', type=int, required=True, help='Target height in pixels')
    parser.add_argument('-o', '--output', help='Output file path (default: auto-generated)')
    parser.add_argument('-q', '--quality', type=int, default=85, help='Quality (1-100, default: 85)')
    parser.add_argument('-f', '--format', choices=['jpg', 'png', 'webp'], default='jpg', help='Output format (default: jpg)')
    parser.add_argument('-c', '--crop', action='store_true', help='Crop to fit dimensions instead of stretching')
    parser.add_argument('--check-copyright', action='store_true', help='Check for copyright information')
    parser.add_argument('--preset', choices=['2k', 'fullhd', 'hd', 'web', 'instagram', 'thumbnail'], help='Use a preset size')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Apply preset if specified
    presets = {
        '2k': (2048, 1366),
        'fullhd': (1920, 1080),
        'hd': (1280, 720),
        'web': (1024, 683),
        'instagram': (1080, 1080),
        'thumbnail': (400, 300)
    }
    
    if args.preset:
        args.width, args.height = presets[args.preset]
        print(f"Using preset '{args.preset}': {args.width}x{args.height}")
    
    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input)
        output_name = f"trieste@news_{input_path.stem}.{args.format}"
        args.output = str(input_path.parent / output_name)
    
    # Check copyright if requested
    if args.check_copyright:
        copyright_info = check_copyright(args.input)
        if copyright_info:
            print(f"⚠️  WARNING: COPYRIGHT PROTECTED IMAGE")
            print(f"Copyright info: {copyright_info}")
        else:
            print("✓ No copyright information found")
    
    # Resize the image
    print(f"Resizing image: {args.input}")
    print(f"Target size: {args.width}x{args.height} pixels")
    print(f"Quality: {args.quality}%")
    print(f"Format: {args.format.upper()}")
    print(f"Crop mode: {'Yes' if args.crop else 'No'}")
    print()
    
    success = resize_image(
        args.input,
        args.output,
        args.width,
        args.height,
        args.quality,
        args.format,
        args.crop
    )
    
    if success:
        print("\n✅ Image resized successfully!")
    else:
        print("\n❌ Failed to resize image")
        sys.exit(1)

if __name__ == "__main__":
    main()
