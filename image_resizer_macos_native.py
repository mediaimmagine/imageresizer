"""
Image Resizer - macOS Native GUI Version
Uses system-native GUI elements for maximum compatibility
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
        self.root.title("Image Resizer - Web Optimizer")
        
        # Force window to be visible and properly sized
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # macOS-specific window setup
        if sys.platform == "darwin":
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(lambda: self.root.attributes('-topmost', False))
            
        # Variables
        self.original_image = None
        self.original_path = None
        self.preview_image = None
        self.resized_image = None
        self.keep_aspect_ratio = tk.BooleanVar(value=True)
        self.crop_mode = tk.BooleanVar(value=False)
        self.manual_crop = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.quality_var = tk.IntVar(value=50)
        self.output_format = tk.StringVar(value="jpg")
        self.needs_crop = False
        self.crop_box = None
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Setup the user interface using native GUI elements"""
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🖼️ Image Resizer & Web Optimizer",
            font=("Arial", 16, "bold"),
            fg="blue"
        )
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Upload tab
        upload_frame = ttk.Frame(notebook)
        notebook.add(upload_frame, text="📁 Upload")
        
        # Upload section
        upload_section = ttk.LabelFrame(upload_frame, text="Upload Image", padding=10)
        upload_section.pack(fill=tk.X, pady=5)
        
        self.file_label = tk.Label(upload_section, text="No file selected", fg="gray")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        upload_btn = tk.Button(
            upload_section,
            text="Browse...",
            command=self.upload_image,
            bg="blue",
            fg="white",
            font=("Arial", 10, "bold")
        )
        upload_btn.pack(side=tk.RIGHT)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # Dimensions section
        dim_section = ttk.LabelFrame(settings_frame, text="Dimensions", padding=10)
        dim_section.pack(fill=tk.X, pady=5)
        
        dim_frame = tk.Frame(dim_section)
        dim_frame.pack(fill=tk.X)
        
        tk.Label(dim_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=5)
        width_entry = tk.Entry(dim_frame, textvariable=self.width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5)
        width_entry.bind('<KeyRelease>', self.on_width_change)
        
        tk.Label(dim_frame, text="px").grid(row=0, column=2, padx=5)
        
        tk.Label(dim_frame, text="Height:").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        height_entry = tk.Entry(dim_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=4, padx=5)
        height_entry.bind('<KeyRelease>', self.on_height_change)
        
        tk.Label(dim_frame, text="px").grid(row=0, column=5, padx=5)
        
        # Options section
        options_section = ttk.LabelFrame(settings_frame, text="Options", padding=10)
        options_section.pack(fill=tk.X, pady=5)
        
        aspect_check = tk.Checkbutton(
            options_section,
            text="Keep aspect ratio",
            variable=self.keep_aspect_ratio,
            command=self.toggle_aspect_ratio
        )
        aspect_check.pack(anchor=tk.W)
        
        crop_check = tk.Checkbutton(
            options_section,
            text="Crop to fit",
            variable=self.crop_mode,
            command=self.toggle_crop_mode
        )
        crop_check.pack(anchor=tk.W)
        
        # Quality section
        quality_section = ttk.LabelFrame(settings_frame, text="Quality", padding=10)
        quality_section.pack(fill=tk.X, pady=5)
        
        quality_slider = tk.Scale(
            quality_section,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            command=self.on_quality_change
        )
        quality_slider.pack(fill=tk.X)
        
        self.quality_label = tk.Label(quality_section, text="50%")
        self.quality_label.pack()
        
        # Format section
        format_section = ttk.LabelFrame(settings_frame, text="Output Format", padding=10)
        format_section.pack(fill=tk.X, pady=5)
        
        format_frame = tk.Frame(format_section)
        format_frame.pack(fill=tk.X)
        
        formats = [("JPG", "jpg"), ("PNG", "png"), ("WebP", "webp")]
        for text, value in formats:
            rb = tk.Radiobutton(
                format_frame,
                text=text,
                variable=self.output_format,
                value=value
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Preview tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="📸 Preview")
        
        # Preview section
        preview_section = ttk.LabelFrame(preview_frame, text="Image Preview", padding=10)
        preview_section.pack(fill=tk.BOTH, expand=True)
        
        self.preview_info_label = tk.Label(
            preview_section,
            text="No preview yet - Upload an image and click 'Update Preview'",
            fg="gray"
        )
        self.preview_info_label.pack(pady=10)
        
        # Canvas for image preview
        self.preview_canvas = tk.Canvas(preview_section, bg="white", height=300)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Action buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.preview_btn = tk.Button(
            button_frame,
            text="🔄 Update Preview",
            command=self.update_preview,
            bg="orange",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.preview_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = tk.Button(
            button_frame,
            text="💾 Save Image",
            command=self.save_image,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Info section
        info_section = ttk.LabelFrame(main_frame, text="Image Info", padding=10)
        info_section.pack(fill=tk.X, pady=5)
        
        self.info_label = tk.Label(info_section, text="Upload an image to see details", fg="gray")
        self.info_label.pack(anchor=tk.W)
        
        # Copyright warning
        self.copyright_warning_label = tk.Label(
            info_section,
            text="",
            fg="red",
            wraplength=800
        )
        self.copyright_warning_label.pack(anchor=tk.W, pady=5)
        
        # Credits
        credits_label = tk.Label(
            main_frame,
            text="Image Resizer v1.0 - Built with Python & Tkinter",
            font=("Arial", 9),
            fg="gray"
        )
        credits_label.pack(pady=5)
        
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
                info_text = f"Original: {width}x{height} px | Size: {file_size:.1f} KB | Format: {self.original_image.format}"
                self.info_label.config(text=info_text, fg="black")
                
                # Check for copyright metadata
                copyright_info = self.extract_copyright_metadata()
                if copyright_info:
                    warning_text = f"WARNING: COPYRIGHT PROTECTED IMAGE\n{copyright_info}"
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
        if self.original_image:
            self.check_crop_needed()
    
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
        if self.original_image:
            self.check_crop_needed()
    
    def toggle_aspect_ratio(self):
        """Toggle aspect ratio lock"""
        if self.keep_aspect_ratio.get() and self.original_image:
            self.on_width_change()
        if self.original_image:
            self.check_crop_needed()
    
    def toggle_crop_mode(self):
        """Toggle crop mode"""
        if self.original_image:
            self.check_crop_needed()
            if self.crop_mode.get():
                self.update_preview()
    
    def check_crop_needed(self):
        """Check if cropping is needed based on aspect ratios"""
        if not self.original_image or self.keep_aspect_ratio.get():
            self.needs_crop = False
            return
        
        try:
            target_width = int(self.width_var.get())
            target_height = int(self.height_var.get())
            orig_width, orig_height = self.original_image.size
            
            orig_ratio = orig_width / orig_height
            target_ratio = target_width / target_height
            
            if abs(orig_ratio - target_ratio) > 0.01:
                self.needs_crop = True
            else:
                self.needs_crop = False
        except (ValueError, ZeroDivisionError):
            self.needs_crop = False
    
    def on_quality_change(self, value):
        """Handle quality slider change"""
        self.quality_label.config(text=f"{value}%")
        if self.original_image and self.resized_image:
            if hasattr(self, '_quality_update_id'):
                self.root.after_cancel(self._quality_update_id)
            self._quality_update_id = self.root.after(300, self.update_preview)
    
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
            
            self.check_crop_needed()
            
            if self.crop_mode.get() and self.needs_crop:
                crop_box = self.calculate_center_crop_box(new_width, new_height)
                self.crop_box = crop_box
                cropped = self.original_image.crop(crop_box)
                self.resized_image = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                self.resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            import io
            temp_buffer = io.BytesIO()
            temp_img = self.resized_image.copy()
            
            if temp_img.mode == 'RGBA':
                temp_img = temp_img.convert('RGB')
            
            temp_img.save(temp_buffer, format='JPEG', quality=self.quality_var.get(), optimize=True)
            estimated_size_kb = len(temp_buffer.getvalue()) / 1024
            temp_buffer.close()
            
            crop_text = ""
            if self.crop_mode.get() and self.needs_crop and self.crop_box:
                left, top, right, bottom = self.crop_box
                crop_text = f"\n✂️ Cropped from: {right-left} x {bottom-top} px"
            
            info_text = (
                f"📐 Dimensions: {new_width} x {new_height} px\n"
                f"📊 Estimated Size (JPG): {estimated_size_kb:.1f} KB\n"
                f"🎚️ Quality: {self.quality_var.get()}%"
                f"{crop_text}"
            )
            self.preview_info_label.config(text=info_text, fg="black")
            
            # Display preview
            self.preview_canvas.delete("all")
            
            max_preview_size = (400, 400)
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
    
    def calculate_center_crop_box(self, target_width, target_height):
        """Calculate the crop box for center cropping"""
        orig_width, orig_height = self.original_image.size
        orig_ratio = orig_width / orig_height
        target_ratio = target_width / target_height
        
        if orig_ratio > target_ratio:
            new_width = int(orig_height * target_ratio)
            center_left = (orig_width - new_width) // 2
            left = center_left
            top = 0
            right = left + new_width
            bottom = orig_height
        else:
            new_height = int(orig_width / target_ratio)
            left = 0
            center_top = (orig_height - new_height) // 2
            top = center_top
            right = orig_width
            bottom = top + new_height
        
        return (left, top, right, bottom)
    
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
    print("Starting Image Resizer with native GUI...")
    
    try:
        root = tk.Tk()
        app = ImageResizerApp(root)
        
        print("GUI created successfully")
        print("Using native GUI elements for maximum compatibility")
        
        root.mainloop()
        print("Application closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()







