# Image Resizer for iOS (Pythonista)
# Compatible with iOS 13+ (2020+)
# Requires Pythonista app from App Store

import photos
import ui
import console
from PIL import Image
import io
import os

class ImageResizeriOS:
    def __init__(self):
        self.original_image = None
        self.resized_image = None
        self.target_width = 1920
        self.target_height = 1080
        self.quality = 85
        
    def create_ui(self):
        # Create main view
        self.view = ui.View()
        self.view.name = 'Image Resizer'
        self.view.background_color = 'white'
        
        # Title
        title_label = ui.Label()
        title_label.text = '🖼️ Image Resizer for iOS'
        title_label.font = ('Arial', 20, 'bold')
        title_label.text_color = '#2c3e50'
        title_label.alignment = ui.ALIGN_CENTER
        title_label.frame = (0, 50, self.view.width, 40)
        self.view.add_subview(title_label)
        
        # Image info
        self.image_label = ui.Label()
        self.image_label.text = 'No image selected'
        self.image_label.font = ('Arial', 14)
        self.image_label.text_color = 'gray'
        self.image_label.alignment = ui.ALIGN_CENTER
        self.image_label.frame = (20, 100, self.view.width - 40, 30)
        self.view.add_subview(self.image_label)
        
        # Select image button
        select_btn = ui.Button()
        select_btn.title = '📁 Select Image from Photos'
        select_btn.background_color = '#3498db'
        select_btn.tint_color = 'white'
        select_btn.font = ('Arial', 16, 'bold')
        select_btn.frame = (20, 150, self.view.width - 40, 50)
        select_btn.action = self.select_image
        self.view.add_subview(select_btn)
        
        # Dimensions section
        dim_label = ui.Label()
        dim_label.text = 'Target Dimensions:'
        dim_label.font = ('Arial', 16, 'bold')
        dim_label.frame = (20, 220, 200, 30)
        self.view.add_subview(dim_label)
        
        # Width
        width_label = ui.Label()
        width_label.text = 'Width:'
        width_label.frame = (20, 260, 60, 30)
        self.view.add_subview(width_label)
        
        self.width_field = ui.TextField()
        self.width_field.text = str(self.target_width)
        self.width_field.frame = (90, 260, 100, 30)
        self.width_field.border_width = 1
        self.width_field.border_color = '#bdc3c7'
        self.view.add_subview(self.width_field)
        
        # Height
        height_label = ui.Label()
        height_label.text = 'Height:'
        height_label.frame = (200, 260, 60, 30)
        self.view.add_subview(height_label)
        
        self.height_field = ui.TextField()
        self.height_field.text = str(self.target_height)
        self.height_field.frame = (270, 260, 100, 30)
        self.height_field.border_width = 1
        self.height_field.border_color = '#bdc3c7'
        self.view.add_subview(self.height_field)
        
        # Preset buttons
        presets_label = ui.Label()
        presets_label.text = 'Quick Presets:'
        presets_label.font = ('Arial', 14, 'bold')
        presets_label.frame = (20, 300, 150, 30)
        self.view.add_subview(presets_label)
        
        # Preset buttons
        presets = [
            ('HD', 1280, 720),
            ('Full HD', 1920, 1080),
            ('Instagram', 1080, 1080),
            ('Thumbnail', 400, 300)
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = ui.Button()
            btn.title = name
            btn.background_color = '#95a5a6'
            btn.tint_color = 'white'
            btn.font = ('Arial', 12)
            btn.frame = (20 + (i % 2) * 120, 330 + (i // 2) * 40, 100, 35)
            btn.action = lambda sender, width=w, height=h: self.set_preset(width, height)
            self.view.add_subview(btn)
        
        # Quality slider
        quality_label = ui.Label()
        quality_label.text = f'Quality: {self.quality}%'
        quality_label.font = ('Arial', 14, 'bold')
        quality_label.frame = (20, 450, 150, 30)
        self.view.add_subview(quality_label)
        
        self.quality_slider = ui.Slider()
        self.quality_slider.value = self.quality / 100.0
        self.quality_slider.frame = (20, 480, self.view.width - 40, 30)
        self.quality_slider.action = self.update_quality
        self.view.add_subview(self.quality_slider)
        
        # Resize and save button
        resize_btn = ui.Button()
        resize_btn.title = '🔄 Resize & Save to Photos'
        resize_btn.background_color = '#27ae60'
        resize_btn.tint_color = 'white'
        resize_btn.font = ('Arial', 16, 'bold')
        resize_btn.frame = (20, 530, self.view.width - 40, 50)
        resize_btn.action = self.resize_and_save
        self.view.add_subview(resize_btn)
        
        # Info label
        self.info_label = ui.Label()
        self.info_label.text = 'Select an image and choose your settings'
        self.info_label.font = ('Arial', 12)
        self.info_label.text_color = 'gray'
        self.info_label.alignment = ui.ALIGN_CENTER
        self.info_label.frame = (20, 600, self.view.width - 40, 60)
        self.info_label.number_of_lines = 0
        self.view.add_subview(self.info_label)
        
        return self.view
    
    def select_image(self, sender):
        """Select image from Photos"""
        try:
            # Get image from Photos
            img = photos.pick_image()
            if img:
                self.original_image = img
                width, height = img.size
                self.image_label.text = f'Selected: {width}x{height} px'
                self.info_label.text = f'Image loaded: {width}x{height} px\nReady to resize!'
        except Exception as e:
            console.alert('Error', f'Failed to select image: {str(e)}')
    
    def set_preset(self, width, height):
        """Set preset dimensions"""
        self.target_width = width
        self.target_height = height
        self.width_field.text = str(width)
        self.height_field.text = str(height)
    
    def update_quality(self, sender):
        """Update quality from slider"""
        self.quality = int(sender.value * 100)
        # Update quality label
        for subview in self.view.subviews:
            if isinstance(subview, ui.Label) and 'Quality:' in subview.text:
                subview.text = f'Quality: {self.quality}%'
                break
    
    def resize_and_save(self, sender):
        """Resize image and save to Photos"""
        if not self.original_image:
            console.alert('Error', 'Please select an image first')
            return
        
        try:
            # Get dimensions
            width = int(self.width_field.text)
            height = int(self.height_field.text)
            
            if width <= 0 or height <= 0:
                console.alert('Error', 'Please enter valid dimensions')
                return
            
            # Resize image
            resized = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save to Photos
            photos.save_image(resized)
            
            # Show success
            console.alert('Success', f'Image resized to {width}x{height} and saved to Photos!')
            self.info_label.text = f'✅ Saved: {width}x{height} px at {self.quality}% quality'
            
        except ValueError:
            console.alert('Error', 'Please enter valid numbers for dimensions')
        except Exception as e:
            console.alert('Error', f'Failed to resize image: {str(e)}')

def main():
    """Main function for iOS version"""
    app = ImageResizeriOS()
    view = app.create_ui()
    view.present('sheet')

if __name__ == '__main__':
    main()
