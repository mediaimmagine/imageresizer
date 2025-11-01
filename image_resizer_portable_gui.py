#!/usr/bin/env python3
"""
Image Resizer - Portable GUI Version
Simple, reliable GUI that works on all systems
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path

# macOS-specific fixes
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer - Portable Version")
        
        # Set window size and make it resizable
        self.root.geometry("900x600")
        self.root.minsize(600, 400)
        
        # Variables
        self.original_image = None
        self.original_path = None
        self.resized_image = None
        self.keep_aspect_ratio = tk.BooleanVar(value=True)
        self.crop_mode = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.quality_var = tk.IntVar(value=85)
        self.output_format = tk.StringVar(value="jpg")
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Image Resizer & Web Optimizer",
            font=("Arial", 16, "bold"),
            fg="blue"
        )
        title_label.pack(pady=10)
        
        # Create main content area
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        left_panel = tk.Frame(content_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right panel for preview
        right_panel = tk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup left panel
        self.setup_controls(left_panel)
        
        # Setup right panel
        self.setup_preview(right_panel)
        
        # Footer
        footer_label = tk.Label(
            main_frame,
            text="Image Resizer v1.0 - Portable Version | Built with Python & Tkinter",
            font=("Arial", 9),
            fg="gray"
        )
        footer_label.pack(pady=5)
        
    def setup_controls(self, parent):
        """Setup the control panel"""
        
        # Upload section
        upload_frame = tk.LabelFrame(parent, text="Upload Image", padx=10, pady=10)
        upload_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = tk.Label(upload_frame, text="No file selected", fg="gray")
        self.file_label.pack(pady=5)
        
        upload_btn = tk.Button(
            upload_frame,
            text="Browse...",
            command=self.upload_image,
            bg="blue",
            fg="white",
            font=("Arial", 10, "bold")
        )
        upload_btn.pack(pady=5)
        
        # Dimensions section
        dim_frame = tk.LabelFrame(parent, text="Dimensions", padx=10, pady=10)
        dim_frame.pack(fill=tk.X, pady=5)
        
        # Width
        width_frame = tk.Frame(dim_frame)
        width_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        width_entry = tk.Entry(width_frame, textvariable=self.width_var, width=10)
        width_entry.pack(side=tk.RIGHT)
        width_entry.bind('<KeyRelease>', self.on_width_change)
        
        # Height
        height_frame = tk.Frame(dim_frame)
        height_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(height_frame, text="Height:").pack(side=tk.LEFT)
        height_entry = tk.Entry(height_frame, textvariable=self.height_var, width=10)
        height_entry.pack(side=tk.RIGHT)
        height_entry.bind('<KeyRelease>', self.on_height_change)
        
        # Options section
        options_frame = tk.LabelFrame(parent, text="Options", padx=10, pady=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        aspect_check = tk.Checkbutton(
            options_frame,
            text="Keep aspect ratio",
            variable=self.keep_aspect_ratio,
            command=self.toggle_aspect_ratio
        )
        aspect_check.pack(anchor=tk.W)
        
        crop_check = tk.Checkbutton(
            options_frame,
            text="Crop to fit",
            variable=self.crop_mode,
            command=self.toggle_crop_mode
        )
        crop_check.pack(anchor=tk.W)
        
        # Quality section
        quality_frame = tk.LabelFrame(parent, text="Quality", padx=10, pady=10)
        quality_frame.pack(fill=tk.X, pady=5)
        
        quality_slider = tk.Scale(
            quality_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            command=self.on_quality_change
        )
        quality_slider.pack(fill=tk.X)
        
        self.quality_label = tk.Label(quality_frame, text="85%")
        self.quality_label.pack()
        
        # Format section
        format_frame = tk.LabelFrame(parent, text="Output Format", padx=10, pady=10)
        format_frame.pack(fill=tk.X, pady=5)
        
        formats = [("JPG", "jpg"), ("PNG", "png"), ("WebP", "webp")]
        for text, value in formats:
            rb = tk.Radiobutton(
                format_frame,
                text=text,
                variable=self.output_format,
                value=value
            )
            rb.pack(anchor=tk.W)
        
        # Presets section
        presets_frame = tk.LabelFrame(parent, text="Quick Presets", padx=10, pady=10)
        presets_frame.pack(fill=tk.X, pady=5)
        
        presets = [
            ("Full HD", 1920, 1080),
            ("HD", 1280, 720),
            ("Web", 1024, 683),
            ("Instagram", 1080, 1080),
            ("Thumbnail", 400, 300)
        ]
        
        for name, w, h in presets:
            btn = tk.Button(
                presets_frame,
                text=name,
                command=lambda w=w, h=h: self.apply_preset(w, h),
                bg="lightgray",
                fg="black"
            )
            btn.pack(fill=tk.X, pady=2)
        
        # Action buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.preview_btn = tk.Button(
            button_frame,
            text="Update Preview",
            command=self.update_preview,
            bg="orange",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.preview_btn.pack(fill=tk.X, pady=2)
        
        self.save_btn = tk.Button(
            button_frame,
            text="Save Image",
            command=self.save_image,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.save_btn.pack(fill=tk.X, pady=2)
        
        # Info section
        info_frame = tk.LabelFrame(parent, text="Image Info", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_label = tk.Label(info_frame, text="Upload an image to see details", fg="gray", wraplength=250)
        self.info_label.pack(anchor=tk.W)
        
        # Copyright warning
        self.copyright_warning_label = tk.Label(
            info_frame,
            text="",
            fg="red",
            wraplength=250
        )
        self.copyright_warning_label.pack(anchor=tk.W, pady=5)
        
    def setup_preview(self, parent):
        """Setup the preview panel"""
        
        # Preview title
        preview_title = tk.Label(
            parent,
            text="Preview",
            font=("Arial", 12, "bold")
        )
        preview_title.pack(pady=5)
        
        # Preview info
        self.preview_info_label = tk.Label(
            parent,
            text="No preview yet - Upload an image and click 'Update Preview'",
            fg="gray"
        )
        self.preview_info_label.pack(pady=5)
        
        # Canvas for image preview
        canvas_frame = tk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white", height=300)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
    def upload_image(self):
        """Upload and load an image"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.original_path = file_path
                
                # Update file label
                filename = os.path.basename(file_path)
                self.file_label.config(text=f"✓ {filename}", fg="green")
                
                # Update dimensions
                width, height = self.original_image.size
                self.width_var.set(str(width))
                self.height_var.set(str(height))
                
                # Update info
                file_size = os.path.getsize(file_path) / 1024
                info_text = f"Original: {width}x{height} px\nSize: {file_size:.1f} KB\nFormat: {self.original_image.format}"
                self.info_label.config(text=info_text, fg="black")
                
                # Check for copyright metadata
                copyright_info = self.extract_copyright_metadata()
                if copyright_info:
                    warning_text = f"WARNING: COPYRIGHT PROTECTED\n{copyright_info}"
                    self.copyright_warning_label.config(text=warning_text)
                else:
                    self.copyright_warning_label.config(text="")
                
                # Enable buttons
                self.preview_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
                
                # Auto-update preview
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
    
    def extract_copyright_metadata(self):
        """Extract copyright information from image metadata"""
        if not self.original_image:
            return None
        
        try:
            exif_data = self.original_image.getexif()
            
            if exif_data:
                copyright_tag = 33432
                if copyright_tag in exif_data:
                    return exif_data[copyright_tag]
                
                artist_tag = 315
                if artist_tag in exif_data:
                    return f"Artist: {exif_data[artist_tag]}"
            
            if hasattr(self.original_image, 'info'):
                info = self.original_image.info
                
                for key in ['copyright', 'Copyright', 'COPYRIGHT', 'author', 'Author', 'creator', 'Creator']:
                    if key in info:
                        return info[key]
            
            return None
            
        except Exception:
            return None
    
    def on_width_change(self, event=None):
        """Handle width change when aspect ratio is locked"""
        if self.keep_aspect_ratio.get() and self.original_image:
            try:
                new_width = int(self.width_var.get())
                orig_width, orig_height = self.original_image.size
                aspect_ratio = orig_height / orig_width
                new_height = int(new_width * aspect_ratio)
                self.height_var.set(str(new_height))
            except ValueError:
                pass
    
    def on_height_change(self, event=None):
        """Handle height change when aspect ratio is locked"""
        if self.keep_aspect_ratio.get() and self.original_image:
            try:
                new_height = int(self.height_var.get())
                orig_width, orig_height = self.original_image.size
                aspect_ratio = orig_width / orig_height
                new_width = int(new_height * aspect_ratio)
                self.width_var.set(str(new_width))
            except ValueError:
                pass
    
    def toggle_aspect_ratio(self):
        """Toggle aspect ratio lock"""
        if self.keep_aspect_ratio.get() and self.original_image:
            self.on_width_change()
    
    def toggle_crop_mode(self):
        """Toggle crop mode"""
        if self.original_image:
            self.update_preview()
    
    def on_quality_change(self, value):
        """Handle quality slider change"""
        self.quality_label.config(text=f"{value}%")
        if self.original_image and self.resized_image:
            if hasattr(self, '_quality_update_id'):
                self.root.after_cancel(self._quality_update_id)
            self._quality_update_id = self.root.after(300, self.update_preview)
    
    def apply_preset(self, width, height):
        """Apply a preset dimension"""
        if not self.original_image:
            self.width_var.set(str(width))
            self.height_var.set(str(height))
            return
        
        orig_width, orig_height = self.original_image.size
        orig_ratio = orig_width / orig_height
        preset_ratio = width / height
        
        if abs(orig_ratio - preset_ratio) > 0.01:
            self.keep_aspect_ratio.set(False)
            self.width_var.set(str(width))
            self.height_var.set(str(height))
            self.crop_mode.set(True)
            self.toggle_crop_mode()
        else:
            if self.keep_aspect_ratio.get():
                orig_ratio = orig_width / orig_height
                preset_ratio = width / height
                
                if orig_ratio > preset_ratio:
                    self.width_var.set(str(width))
                    self.on_width_change()
                else:
                    self.height_var.set(str(height))
                    self.on_height_change()
            else:
                self.width_var.set(str(width))
                self.height_var.set(str(height))
    
    def update_preview(self):
        """Update the preview with resized image"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please upload an image first")
            return
        
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                messagebox.showerror("Invalid Dimensions", "Width and height must be positive numbers")
                return
            
            # Calculate aspect ratios
            orig_width, orig_height = self.original_image.size
            orig_ratio = orig_width / orig_height
            target_ratio = new_width / new_height
            
            needs_crop = abs(orig_ratio - target_ratio) > 0.01
            
            if self.crop_mode.get() and needs_crop:
                # Calculate crop box for center cropping
                if orig_ratio > target_ratio:
                    new_width_crop = int(orig_height * target_ratio)
                    left = (orig_width - new_width_crop) // 2
                    crop_box = (left, 0, left + new_width_crop, orig_height)
                else:
                    new_height_crop = int(orig_width / target_ratio)
                    top = (orig_height - new_height_crop) // 2
                    crop_box = (0, top, orig_width, top + new_height_crop)
                
                cropped = self.original_image.crop(crop_box)
                self.resized_image = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                self.resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate estimated file size
            import io
            temp_buffer = io.BytesIO()
            temp_img = self.resized_image.copy()
            
            if temp_img.mode == 'RGBA':
                temp_img = temp_img.convert('RGB')
            
            temp_img.save(temp_buffer, format='JPEG', quality=self.quality_var.get(), optimize=True)
            estimated_size_kb = len(temp_buffer.getvalue()) / 1024
            temp_buffer.close()
            
            # Update preview info
            crop_text = ""
            if self.crop_mode.get() and needs_crop:
                crop_text = f"\nCropped to fit"
            
            info_text = (
                f"Dimensions: {new_width} x {new_height} px\n"
                f"Estimated Size: {estimated_size_kb:.1f} KB\n"
                f"Quality: {self.quality_var.get()}%"
                f"{crop_text}"
            )
            self.preview_info_label.config(text=info_text, fg="black")
            
            # Display preview
            self.preview_canvas.delete("all")
            
            max_preview_size = (300, 300)
            display_img = self.resized_image.copy()
            display_img.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_img)
            img_label = tk.Label(self.preview_canvas, image=photo, bg="white")
            img_label.image = photo
            img_label.pack(pady=10)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for width and height")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview image:\n{str(e)}")
    
    def save_image(self):
        """Save the resized image"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please upload an image first")
            return
        
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                messagebox.showerror("Invalid Dimensions", "Width and height must be positive numbers")
                return
            
            original_name = Path(self.original_path).stem
            
            format_extensions = {
                'jpg': '.jpg',
                'png': '.png',
                'webp': '.webp'
            }
            selected_ext = format_extensions.get(self.output_format.get(), '.jpg')
            
            default_name = f"trieste@news_{original_name}{selected_ext}"
            
            if self.output_format.get() == 'jpg':
                filetypes = [("JPEG", "*.jpg *.jpeg"), ("All files", "*.*")]
                defaultextension = '.jpg'
            elif self.output_format.get() == 'png':
                filetypes = [("PNG", "*.png"), ("All files", "*.*")]
                defaultextension = '.png'
            else:
                filetypes = [("WebP", "*.webp"), ("All files", "*.*")]
                defaultextension = '.webp'
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=defaultextension,
                initialfile=default_name,
                filetypes=filetypes
            )
            
            if save_path:
                if self.resized_image:
                    resized = self.resized_image
                else:
                    resized = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                save_kwargs = {}
                
                if save_path.lower().endswith(('.jpg', '.jpeg')):
                    save_kwargs = {
                        'quality': self.quality_var.get(),
                        'optimize': True
                    }
                    if resized.mode == 'RGBA':
                        background = Image.new('RGB', resized.size, (255, 255, 255))
                        background.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
                        resized = background
                
                elif save_path.lower().endswith('.webp'):
                    save_kwargs = {
                        'quality': self.quality_var.get(),
                        'method': 6
                    }
                
                elif save_path.lower().endswith('.png'):
                    quality = self.quality_var.get()
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
                
                resized.save(save_path, **save_kwargs)
                
                file_size = os.path.getsize(save_path) / 1024
                messagebox.showinfo(
                    "Success",
                    f"Image saved successfully!\n\n"
                    f"Location: {save_path}\n"
                    f"Dimensions: {new_width}x{new_height} px\n"
                    f"File size: {file_size:.1f} KB"
                )
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for width and height")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
    
    def on_closing(self):
        """Handle window closing properly"""
        self.root.quit()
        self.root.destroy()


def main():
    print("Starting Image Resizer - Portable GUI Version...")
    
    try:
        root = tk.Tk()
        app = ImageResizerApp(root)
        
        print("GUI created successfully")
        print("This version uses simple, reliable GUI elements")
        
        root.mainloop()
        print("Application closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()









