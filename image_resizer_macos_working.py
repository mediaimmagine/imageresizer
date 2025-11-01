#!/usr/bin/env python3
"""
Image Resizer - Working macOS Version
Handles GUI properly without getting stuck
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path
import threading
import time

# macOS-specific fixes
if sys.platform == "darwin":
    import os
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer - Web Optimizer")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
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
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.quality_var = tk.IntVar(value=50)
        self.output_format = tk.StringVar(value="jpg")
        
        self.setup_ui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Handle window closing properly"""
        print("Closing application...")
        self.root.quit()
        self.root.destroy()
        
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # HEADER
        header_frame = tk.Frame(main_frame, relief=tk.RAISED, bd=2, bg="lightblue")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="🖼️ Image Resizer & Web Optimizer",
            font=("Arial", 16, "bold"),
            bg="lightblue",
            fg="black"
        )
        title_label.pack(pady=15)
        
        # Main content area
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = tk.Frame(content_frame, relief=tk.SUNKEN, bd=2, bg="lightgray")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # Right panel - Preview
        right_panel = tk.Frame(content_frame, relief=tk.SUNKEN, bd=2, bg="white")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Setup panels
        self.setup_controls(left_panel)
        self.setup_preview_panel(right_panel)
        
        # FOOTER
        footer_frame = tk.Frame(main_frame, relief=tk.RAISED, bd=2, bg="lightgray")
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        credits_label = tk.Label(
            footer_frame,
            text="Image Resizer v1.0 - Cross-Platform Image Optimization Tool | Built with Python & Tkinter",
            font=("Arial", 9),
            bg="lightgray",
            fg="black"
        )
        credits_label.pack(pady=5)
        
        # Force GUI update
        self.root.update_idletasks()
        self.root.update()
        
    def setup_controls(self, parent):
        """Setup the control panel"""
        
        # Upload section
        upload_frame = tk.LabelFrame(parent, text="📁 Upload Image", font=("Arial", 10, "bold"), bg="lightgray")
        upload_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.file_label = tk.Label(upload_frame, text="No file selected", fg="gray", bg="lightgray")
        self.file_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        upload_btn = tk.Button(
            upload_frame,
            text="Browse...",
            command=self.upload_image,
            bg="blue",
            fg="white",
            font=("Arial", 9, "bold")
        )
        upload_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Settings section
        settings_frame = tk.LabelFrame(parent, text="⚙️ Resize Settings", font=("Arial", 10, "bold"), bg="lightgray")
        settings_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Dimensions
        dim_frame = tk.Frame(settings_frame, bg="lightgray")
        dim_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dim_frame, text="Width:", font=("Arial", 9), bg="lightgray").grid(row=0, column=0, sticky=tk.W, padx=5)
        width_entry = tk.Entry(dim_frame, textvariable=self.width_var, width=10, font=("Arial", 9))
        width_entry.grid(row=0, column=1, padx=5)
        width_entry.bind('<KeyRelease>', self.on_width_change)
        
        tk.Label(dim_frame, text="px", font=("Arial", 9), bg="lightgray").grid(row=0, column=2, padx=5)
        
        tk.Label(dim_frame, text="Height:", font=("Arial", 9), bg="lightgray").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        height_entry = tk.Entry(dim_frame, textvariable=self.height_var, width=10, font=("Arial", 9))
        height_entry.grid(row=0, column=4, padx=5)
        height_entry.bind('<KeyRelease>', self.on_height_change)
        
        tk.Label(dim_frame, text="px", font=("Arial", 9), bg="lightgray").grid(row=0, column=5, padx=5)
        
        # Aspect ratio checkbox
        aspect_check = tk.Checkbutton(
            settings_frame,
            text="🔒 Keep aspect ratio (maintain proportions)",
            variable=self.keep_aspect_ratio,
            font=("Arial", 9),
            command=self.toggle_aspect_ratio,
            bg="lightgray"
        )
        aspect_check.pack(anchor=tk.W, pady=2, padx=5)
        
        # Crop mode checkbox
        crop_check = tk.Checkbutton(
            settings_frame,
            text="✂️ Crop to fit (when aspect ratio differs)",
            variable=self.crop_mode,
            font=("Arial", 9),
            command=self.toggle_crop_mode,
            bg="lightgray"
        )
        crop_check.pack(anchor=tk.W, pady=2, padx=5)
        
        # Quality slider
        quality_frame = tk.Frame(settings_frame, bg="lightgray")
        quality_frame.pack(fill=tk.X, pady=5)
        
        self.quality_title_label = tk.Label(quality_frame, text="Quality (compression):", font=("Arial", 9), bg="lightgray")
        self.quality_title_label.pack(anchor=tk.W, padx=5)
        
        # Quick quality presets
        preset_quality_frame = tk.Frame(quality_frame, bg="lightgray")
        preset_quality_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(preset_quality_frame, text="Quick presets:", font=("Arial", 8), bg="lightgray").pack(side=tk.LEFT, padx=(5, 10))
        
        quality_30_btn = tk.Button(
            preset_quality_frame,
            text="30% (Small)",
            command=lambda: self.set_quality(30),
            bg="red",
            fg="white",
            font=("Arial", 8)
        )
        quality_30_btn.pack(side=tk.LEFT, padx=2)
        
        quality_50_btn = tk.Button(
            preset_quality_frame,
            text="50% (Medium)",
            command=lambda: self.set_quality(50),
            bg="orange",
            fg="white",
            font=("Arial", 8)
        )
        quality_50_btn.pack(side=tk.LEFT, padx=2)
        
        quality_85_btn = tk.Button(
            preset_quality_frame,
            text="85% (High)",
            command=lambda: self.set_quality(85),
            bg="green",
            fg="white",
            font=("Arial", 8)
        )
        quality_85_btn.pack(side=tk.LEFT, padx=2)
        
        # Slider
        slider_frame = tk.Frame(quality_frame, bg="lightgray")
        slider_frame.pack(fill=tk.X, pady=2)
        
        quality_slider = tk.Scale(
            slider_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            length=250,
            command=self.on_quality_change,
            bg="lightgray"
        )
        quality_slider.pack(side=tk.LEFT, padx=5)
        
        self.quality_label = tk.Label(slider_frame, text="50%", font=("Arial", 9, "bold"), bg="lightgray")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        # Output format selection
        format_frame = tk.LabelFrame(parent, text="💾 Output Format", font=("Arial", 10, "bold"), bg="lightgray")
        format_frame.pack(fill=tk.X, pady=5, padx=5)
        
        format_options_frame = tk.Frame(format_frame, bg="lightgray")
        format_options_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(format_options_frame, text="Save as:", font=("Arial", 9), bg="lightgray").pack(side=tk.LEFT, padx=5)
        
        formats = [
            ("JPG/JPEG", "jpg"),
            ("PNG", "png"),
            ("WebP", "webp")
        ]
        
        for text, value in formats:
            rb = tk.Radiobutton(
                format_options_frame,
                text=text,
                variable=self.output_format,
                value=value,
                font=("Arial", 9),
                bg="lightgray"
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Web presets
        presets_frame = tk.LabelFrame(parent, text="🌐 Web Presets", font=("Arial", 10, "bold"), bg="lightgray")
        presets_frame.pack(fill=tk.X, pady=5, padx=5)
        
        preset_buttons_frame = tk.Frame(presets_frame, bg="lightgray")
        preset_buttons_frame.pack(pady=5)
        
        presets = [
            ("2K (2048x1366)", 2048, 1366),
            ("Full HD (1920x1080)", 1920, 1080),
            ("HD (1280x720)", 1280, 720),
            ("Web (1024x683)", 1024, 683),
            ("Instagram (1080x1080)", 1080, 1080),
            ("Thumbnail (400x300)", 400, 300)
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = tk.Button(
                preset_buttons_frame,
                text=name,
                command=lambda w=w, h=h: self.apply_preset(w, h),
                bg="gray",
                fg="white",
                font=("Arial", 8)
            )
            btn.grid(row=i//2, column=i%2, padx=3, pady=2, sticky=tk.EW)
        
        # Info section
        self.info_frame = tk.LabelFrame(parent, text="ℹ️ Original Image Info", font=("Arial", 10, "bold"), bg="lightgray")
        self.info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.info_label = tk.Label(self.info_frame, text="Upload an image to see details", fg="gray", justify=tk.LEFT, bg="lightgray")
        self.info_label.pack(anchor=tk.W, pady=5, padx=5)
        
        # Action buttons
        button_frame = tk.Frame(parent, bg="lightgray")
        button_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.preview_btn = tk.Button(
            button_frame,
            text="🔄 Update Preview",
            command=self.update_preview,
            bg="orange",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.preview_btn.pack(fill=tk.X, pady=2)
        
        self.save_btn = tk.Button(
            button_frame,
            text="💾 Save Resized Image",
            command=self.save_image,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            state=tk.DISABLED
        )
        self.save_btn.pack(fill=tk.X, pady=2)
        
        # Force update
        self.root.update_idletasks()
    
    def setup_preview_panel(self, parent):
        """Setup the preview panel"""
        
        # Preview title
        preview_title = tk.Label(
            parent,
            text="📸 Preview",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        preview_title.pack(pady=5)
        
        # Preview info label
        self.preview_info_label = tk.Label(
            parent,
            text="No preview yet - Upload an image and click 'Update Preview'",
            font=("Arial", 9),
            fg="gray",
            wraplength=400,
            justify=tk.CENTER,
            bg="white"
        )
        self.preview_info_label.pack(pady=5)
        
        # Canvas for image preview with scrollbar
        canvas_frame = tk.Frame(parent, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg="lightyellow", highlightthickness=1, highlightbackground="gray")
        scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=self.preview_canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Force update
        self.root.update_idletasks()
    
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
                
                # Enable buttons
                self.preview_btn.config(state=tk.NORMAL)
                self.save_btn.config(state=tk.NORMAL)
                
                # Auto-update preview
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
    
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
            if self.crop_mode.get():
                self.update_preview()
    
    def update_quality_label(self, value):
        """Update quality percentage label"""
        self.quality_label.config(text=f"{value}%")
    
    def on_quality_change(self, value):
        """Handle quality slider change"""
        self.update_quality_label(value)
        if self.original_image and self.resized_image:
            if hasattr(self, '_quality_update_id'):
                self.root.after_cancel(self._quality_update_id)
            self._quality_update_id = self.root.after(300, self.update_preview)
    
    def set_quality(self, quality):
        """Set quality to a specific value"""
        self.quality_var.set(quality)
        self.update_quality_label(quality)
        if self.original_image and self.resized_image:
            self.update_preview()
    
    def apply_preset(self, width, height):
        """Apply a preset dimension"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        if self.original_image:
            self.update_preview()
    
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
            
            # Create resized image
            if self.crop_mode.get():
                # Simple center crop
                orig_width, orig_height = self.original_image.size
                orig_ratio = orig_width / orig_height
                target_ratio = new_width / new_height
                
                if orig_ratio > target_ratio:
                    # Crop width
                    new_width_crop = int(orig_height * target_ratio)
                    left = (orig_width - new_width_crop) // 2
                    crop_box = (left, 0, left + new_width_crop, orig_height)
                    cropped = self.original_image.crop(crop_box)
                    self.resized_image = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    # Crop height
                    new_height_crop = int(orig_width / target_ratio)
                    top = (orig_height - new_height_crop) // 2
                    crop_box = (0, top, orig_width, top + new_height_crop)
                    cropped = self.original_image.crop(crop_box)
                    self.resized_image = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                # Regular resize
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
            
            info_text = (
                f"📐 Dimensions: {new_width} x {new_height} px\n"
                f"📊 Estimated Size (JPG): {estimated_size_kb:.1f} KB\n"
                f"🎚️ Quality: {self.quality_var.get()}%"
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
            
            self.preview_canvas.update_idletasks()
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
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


def main():
    print("Starting Image Resizer...")
    
    try:
        root = tk.Tk()
        app = ImageResizerApp(root)
        
        print("GUI created successfully")
        print("Starting mainloop...")
        
        root.mainloop()
        
        print("Application closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()









