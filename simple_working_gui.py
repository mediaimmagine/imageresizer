#!/usr/bin/env python3
"""
Simple working GUI that forces visibility on macOS
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path

# macOS-specific fixes
if sys.platform == "darwin":
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

class SimpleImageResizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer - Simple Version")
        self.root.geometry("1000x700")
        
        # Force window to be visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        
        # Variables
        self.original_image = None
        self.original_path = None
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.quality_var = tk.IntVar(value=50)
        
        self.create_ui()
        
    def create_ui(self):
        """Create a simple, visible UI"""
        
        # HEADER - Force visibility
        header_frame = tk.Frame(self.root, bg="darkblue", height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="🖼️ Image Resizer & Web Optimizer", 
                               bg="darkblue", 
                               fg="white", 
                               font=("Arial", 16, "bold"))
        header_label.pack(expand=True)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg="lightgray")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - Controls
        left_frame = tk.Frame(main_frame, bg="white", width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        # Upload section
        upload_label = tk.Label(left_frame, text="📁 Upload Image", font=("Arial", 12, "bold"), bg="white")
        upload_label.pack(pady=10)
        
        self.file_label = tk.Label(left_frame, text="No file selected", fg="red", bg="white")
        self.file_label.pack(pady=5)
        
        upload_btn = tk.Button(left_frame, text="Browse...", command=self.upload_image, 
                              bg="blue", fg="white", font=("Arial", 10, "bold"))
        upload_btn.pack(pady=10)
        
        # Dimensions
        dim_label = tk.Label(left_frame, text="Dimensions", font=("Arial", 12, "bold"), bg="white")
        dim_label.pack(pady=(20, 10))
        
        # Width
        width_frame = tk.Frame(left_frame, bg="white")
        width_frame.pack(pady=5)
        tk.Label(width_frame, text="Width:", bg="white").pack(side=tk.LEFT)
        width_entry = tk.Entry(width_frame, textvariable=self.width_var, width=10)
        width_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(width_frame, text="px", bg="white").pack(side=tk.LEFT)
        
        # Height
        height_frame = tk.Frame(left_frame, bg="white")
        height_frame.pack(pady=5)
        tk.Label(height_frame, text="Height:", bg="white").pack(side=tk.LEFT)
        height_entry = tk.Entry(height_frame, textvariable=self.height_var, width=10)
        height_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(height_frame, text="px", bg="white").pack(side=tk.LEFT)
        
        # Quality
        quality_label = tk.Label(left_frame, text="Quality", font=("Arial", 12, "bold"), bg="white")
        quality_label.pack(pady=(20, 10))
        
        quality_slider = tk.Scale(left_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.quality_var, length=300)
        quality_slider.pack(pady=5)
        
        # Presets
        presets_label = tk.Label(left_frame, text="Presets", font=("Arial", 12, "bold"), bg="white")
        presets_label.pack(pady=(20, 10))
        
        preset_frame = tk.Frame(left_frame, bg="white")
        preset_frame.pack()
        
        presets = [
            ("HD", 1280, 720),
            ("Full HD", 1920, 1080),
            ("Instagram", 1080, 1080)
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = tk.Button(preset_frame, text=name, 
                           command=lambda w=w, h=h: self.set_dimensions(w, h),
                           bg="gray", fg="white")
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
        
        # Buttons
        preview_btn = tk.Button(left_frame, text="Update Preview", command=self.update_preview,
                               bg="orange", fg="white", font=("Arial", 10, "bold"))
        preview_btn.pack(pady=10)
        
        save_btn = tk.Button(left_frame, text="Save Image", command=self.save_image,
                            bg="green", fg="white", font=("Arial", 10, "bold"))
        save_btn.pack(pady=5)
        
        # Right side - Preview
        right_frame = tk.Frame(main_frame, bg="lightyellow")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_label = tk.Label(right_frame, text="📸 Preview", font=("Arial", 14, "bold"), bg="lightyellow")
        preview_label.pack(pady=10)
        
        self.preview_label = tk.Label(right_frame, text="No preview yet", bg="lightyellow", fg="gray")
        self.preview_label.pack(pady=10)
        
        # Canvas for image
        self.canvas = tk.Canvas(right_frame, bg="white", height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # FOOTER - Force visibility
        footer_frame = tk.Frame(self.root, bg="darkgreen", height=40)
        footer_frame.pack(fill=tk.X, padx=5, pady=5)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, 
                               text="Image Resizer v1.0 - Cross-Platform Tool | Built with Python & Tkinter", 
                               bg="darkgreen", 
                               fg="white", 
                               font=("Arial", 10, "bold"))
        footer_label.pack(expand=True)
        
        # Force update
        self.root.update_idletasks()
        self.root.update()
        
    def set_dimensions(self, width, height):
        """Set dimensions from preset"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        
    def upload_image(self):
        """Upload an image"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.original_path = file_path
                
                filename = os.path.basename(file_path)
                self.file_label.config(text=f"✓ {filename}", fg="green")
                
                # Set dimensions
                width, height = self.original_image.size
                self.width_var.set(str(width))
                self.height_var.set(str(height))
                
                self.update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def update_preview(self):
        """Update the preview"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please upload an image first")
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Resize image
            resized = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Display in canvas
            self.canvas.delete("all")
            
            # Scale image to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                scale = min(canvas_width/width, canvas_height/height, 1.0)
                display_width = int(width * scale)
                display_height = int(height * scale)
                
                display_img = resized.resize((display_width, display_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(display_img)
                
                # Center the image
                x = (canvas_width - display_width) // 2
                y = (canvas_height - display_height) // 2
                
                self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
                self.canvas.image = photo  # Keep reference
            
            # Update info
            file_size = os.path.getsize(self.original_path) / 1024
            info_text = f"Dimensions: {width}x{height} px | Quality: {self.quality_var.get()}% | Size: {file_size:.1f} KB"
            self.preview_label.config(text=info_text, fg="black")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview: {str(e)}")
    
    def save_image(self):
        """Save the resized image"""
        if not self.original_image:
            messagebox.showwarning("No Image", "Please upload an image first")
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Resize image
            resized = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save dialog
            original_name = Path(self.original_path).stem
            default_name = f"trieste@news_{original_name}.jpg"
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                initialfile=default_name,
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
            )
            
            if save_path:
                # Convert RGBA to RGB if needed
                if resized.mode == 'RGBA':
                    background = Image.new('RGB', resized.size, (255, 255, 255))
                    background.paste(resized, mask=resized.split()[3])
                    resized = background
                
                resized.save(save_path, quality=self.quality_var.get(), optimize=True)
                
                file_size = os.path.getsize(save_path) / 1024
                messagebox.showinfo("Success", 
                    f"Image saved successfully!\n\n"
                    f"Location: {save_path}\n"
                    f"Dimensions: {width}x{height} px\n"
                    f"File size: {file_size:.1f} KB")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

def main():
    print("Starting Simple Image Resizer...")
    
    try:
        root = tk.Tk()
        app = SimpleImageResizer(root)
        
        print("GUI created successfully")
        print("You should see:")
        print("- Dark blue header at top")
        print("- White left panel with controls")
        print("- Light yellow right panel with preview")
        print("- Dark green footer at bottom")
        
        root.mainloop()
        print("Application closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()







