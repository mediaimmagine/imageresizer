"""
Image Resizer - macOS Fixed Sizing Version
Fixes window sizing issues on macOS
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
        
        # Force proper window sizing for macOS
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # macOS-specific window setup
        if sys.platform == "darwin":
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(lambda: self.root.attributes('-topmost', False))
            
            # Force window to be visible and properly sized
            self.root.update_idletasks()
            self.root.deiconify()
            self.root.focus_force()
        
        # Variables
        self.original_image = None
        self.original_path = None
        self.preview_image = None
        self.resized_image = None
        self.crop_preview_image = None
        self.keep_aspect_ratio = tk.BooleanVar(value=True)
        self.crop_mode = tk.BooleanVar(value=False)
        self.manual_crop = tk.BooleanVar(value=False)
        self.width_var = tk.StringVar(value="1920")
        self.height_var = tk.StringVar(value="1080")
        self.quality_var = tk.IntVar(value=50)
        self.output_format = tk.StringVar(value="jpg")
        self.needs_crop = False
        self.crop_box = None
        self.manual_crop_offset_x = 0
        self.manual_crop_offset_y = 0
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.crop_interactive_window = None
        
        self.setup_ui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Force final update
        self.root.update_idletasks()
        self.root.update()
        
    def setup_ui(self):
        """Setup the user interface with forced visibility"""
        
        # Force update to ensure GUI renders
        self.root.update_idletasks()
        
        # Title - FORCE VISIBILITY
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60, relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🖼️ Image Resizer & Web Optimizer",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white",
            relief=tk.RAISED,
            bd=1
        )
        title_label.pack(pady=15)
        
        # Main container with two columns
        main_container = tk.Frame(self.root, relief=tk.SUNKEN, bd=2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, padx=10, pady=10, relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Right panel - Preview
        right_panel = tk.Frame(main_container, padx=10, pady=10, bg="#f0f0f0", relief=tk.SUNKEN, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup left panel controls
        self.setup_controls(left_panel)
        
        # Setup right panel preview
        self.setup_preview_panel(right_panel)
        
        # FOOTER - FORCE VISIBILITY
        footer_frame = tk.Frame(self.root, bg="#34495e", height=40, relief=tk.RAISED, bd=2)
        footer_frame.pack(fill=tk.X, padx=5, pady=5)
        footer_frame.pack_propagate(False)
        
        credits_label = tk.Label(
            footer_frame,
            text="Image Resizer v1.0 - Cross-Platform Image Optimization Tool | Built with Python & Tkinter | Copyright Detection | Smart Cropping",
            font=("Arial", 10, "bold"),
            bg="#34495e",
            fg="white",
            relief=tk.RAISED,
            bd=1
        )
        credits_label.pack(pady=8)
        
        # Force GUI update
        self.root.update_idletasks()
        self.root.update()
        
    def setup_controls(self, parent):
        """Setup the control panel with forced visibility"""
        
        # Upload section
        upload_frame = tk.LabelFrame(parent, text="📁 Upload Image", font=("Arial", 11, "bold"), padx=10, pady=10, relief=tk.RAISED, bd=2)
        upload_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.file_label = tk.Label(upload_frame, text="No file selected", fg="gray", font=("Arial", 10, "bold"))
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        upload_btn = tk.Button(
            upload_frame,
            text="Browse...",
            command=self.upload_image,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        upload_btn.pack(side=tk.RIGHT)
        
        # Settings section
        settings_frame = tk.LabelFrame(parent, text="⚙️ Resize Settings", font=("Arial", 11, "bold"), padx=10, pady=10, relief=tk.RAISED, bd=2)
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Dimensions
        dim_frame = tk.Frame(settings_frame)
        dim_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(dim_frame, text="Width:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        width_entry = tk.Entry(dim_frame, textvariable=self.width_var, width=10, font=("Arial", 10), relief=tk.SUNKEN, bd=2)
        width_entry.grid(row=0, column=1, padx=5)
        width_entry.bind('<KeyRelease>', self.on_width_change)
        
        tk.Label(dim_frame, text="px", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
        
        tk.Label(dim_frame, text="Height:", font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        height_entry = tk.Entry(dim_frame, textvariable=self.height_var, width=10, font=("Arial", 10), relief=tk.SUNKEN, bd=2)
        height_entry.grid(row=0, column=4, padx=5)
        height_entry.bind('<KeyRelease>', self.on_height_change)
        
        tk.Label(dim_frame, text="px", font=("Arial", 10, "bold")).grid(row=0, column=5, padx=5)
        
        # Aspect ratio checkbox
        aspect_check = tk.Checkbutton(
            settings_frame,
            text="🔒 Keep aspect ratio (maintain proportions)",
            variable=self.keep_aspect_ratio,
            font=("Arial", 10, "bold"),
            command=self.toggle_aspect_ratio
        )
        aspect_check.pack(anchor=tk.W, pady=5)
        
        # Crop mode checkbox
        crop_check = tk.Checkbutton(
            settings_frame,
            text="✂️ Crop to fit (when aspect ratio differs)",
            variable=self.crop_mode,
            font=("Arial", 10, "bold"),
            command=self.toggle_crop_mode
        )
        crop_check.pack(anchor=tk.W, pady=5)
        
        # Manual crop positioning checkbox
        self.manual_crop_check = tk.Checkbutton(
            settings_frame,
            text="🎯 Manual crop positioning (drag to adjust)",
            variable=self.manual_crop,
            font=("Arial", 10, "bold"),
            command=self.toggle_manual_crop,
            state=tk.DISABLED
        )
        self.manual_crop_check.pack(anchor=tk.W, pady=5)
        
        # Crop info label
        self.crop_info_label = tk.Label(
            settings_frame,
            text="",
            font=("Arial", 9, "italic", "bold"),
            fg="orange",
            wraplength=380,
            justify=tk.LEFT
        )
        self.crop_info_label.pack(anchor=tk.W, pady=2)
        
        # Quality slider
        quality_frame = tk.Frame(settings_frame)
        quality_frame.pack(fill=tk.X, pady=10)
        
        self.quality_title_label = tk.Label(quality_frame, text="Quality (compression):", font=("Arial", 10, "bold"))
        self.quality_title_label.pack(anchor=tk.W)
        
        # Quick quality presets
        preset_quality_frame = tk.Frame(quality_frame)
        preset_quality_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(preset_quality_frame, text="Quick presets:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        quality_30_btn = tk.Button(
            preset_quality_frame,
            text="30% (Small)",
            command=lambda: self.set_quality(30),
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        quality_30_btn.pack(side=tk.LEFT, padx=2)
        
        quality_50_btn = tk.Button(
            preset_quality_frame,
            text="50% (Medium)",
            command=lambda: self.set_quality(50),
            bg="#f39c12",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        quality_50_btn.pack(side=tk.LEFT, padx=2)
        
        quality_85_btn = tk.Button(
            preset_quality_frame,
            text="85% (High)",
            command=lambda: self.set_quality(85),
            bg="#27ae60",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=3,
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        )
        quality_85_btn.pack(side=tk.LEFT, padx=2)
        
        # Slider
        slider_frame = tk.Frame(quality_frame)
        slider_frame.pack(fill=tk.X, pady=5)
        
        quality_slider = tk.Scale(
            slider_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.quality_var,
            length=300,
            command=self.on_quality_change,
            relief=tk.SUNKEN,
            bd=2
        )
        quality_slider.pack(side=tk.LEFT)
        
        self.quality_label = tk.Label(slider_frame, text="50%", font=("Arial", 10, "bold"))
        self.quality_label.pack(side=tk.LEFT, padx=10)
        
        # Output format selection
        format_frame = tk.LabelFrame(parent, text="💾 Output Format", font=("Arial", 11, "bold"), padx=10, pady=10, relief=tk.RAISED, bd=2)
        format_frame.pack(fill=tk.X, pady=(0, 15))
        
        format_options_frame = tk.Frame(format_frame)
        format_options_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(format_options_frame, text="Save as:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
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
                font=("Arial", 10, "bold")
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Format info
        format_info = tk.Label(
            format_frame,
            text="JPG: Lossy, best for photos | PNG: Lossless, supports transparency | WebP: Modern, smaller files",
            font=("Arial", 8, "italic", "bold"),
            fg="gray"
        )
        format_info.pack(anchor=tk.W, pady=(5, 0))
        
        # Web presets
        presets_frame = tk.LabelFrame(parent, text="🌐 Web Presets", font=("Arial", 11, "bold"), padx=10, pady=10, relief=tk.RAISED, bd=2)
        presets_frame.pack(fill=tk.X, pady=(0, 15))
        
        preset_buttons_frame = tk.Frame(presets_frame)
        preset_buttons_frame.pack()
        
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
                bg="#95a5a6",
                fg="white",
                font=("Arial", 9, "bold"),
                padx=10,
                pady=5,
                cursor="hand2",
                relief=tk.RAISED,
                bd=2
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=tk.EW)
        
        # Info section
        self.info_frame = tk.LabelFrame(parent, text="ℹ️ Original Image Info", font=("Arial", 11, "bold"), padx=10, pady=10, relief=tk.RAISED, bd=2)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.info_label = tk.Label(self.info_frame, text="Upload an image to see details", fg="gray", justify=tk.LEFT, font=("Arial", 10, "bold"))
        self.info_label.pack(anchor=tk.W)
        
        # Copyright warning label
        self.copyright_warning_label = tk.Label(
            self.info_frame,
            text="",
            fg="red",
            font=("Arial", 10, "bold"),
            justify=tk.LEFT,
            wraplength=380
        )
        self.copyright_warning_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Action buttons
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_btn = tk.Button(
            button_frame,
            text="🔄 Update Preview",
            command=self.update_preview,
            bg="#f39c12",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=2
        )
        self.preview_btn.pack(fill=tk.X, pady=5)
        
        self.save_btn = tk.Button(
            button_frame,
            text="💾 Save Resized Image",
            command=self.save_image,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=2
        )
        self.save_btn.pack(fill=tk.X, pady=5)
        
        # Force update
        self.root.update_idletasks()
    
    def setup_preview_panel(self, parent):
        """Setup the preview panel with forced visibility"""
        
        # Preview title
        preview_title = tk.Label(
            parent,
            text="📸 Preview",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="black",
            relief=tk.RAISED,
            bd=1
        )
        preview_title.pack(pady=(0, 10))
        
        # Preview info label
        self.preview_info_label = tk.Label(
            parent,
            text="No preview yet - Upload an image and click 'Update Preview'",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0",
            fg="gray",
            wraplength=450,
            justify=tk.CENTER,
            relief=tk.SUNKEN,
            bd=1
        )
        self.preview_info_label.pack(pady=10)
        
        # Canvas for image preview with scrollbar
        canvas_frame = tk.Frame(parent, bg="#f0f0f0")
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=2, highlightbackground="black", relief=tk.SUNKEN, bd=2)
        scrollbar_y = tk.Scrollbar(canvas_frame, orient="vertical", command=self.preview_canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Force update
        self.root.update_idletasks()
    
    # Include all the essential methods from the original file
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
                
                # Check for copyright metadata and show RED warning
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
            # Try to get EXIF data
            exif_data = self.original_image.getexif()
            
            if exif_data:
                # EXIF tag 33432 is Copyright
                copyright_tag = 33432
                if copyright_tag in exif_data:
                    return exif_data[copyright_tag]
                
                # Try Artist tag (305)
                artist_tag = 315
                if artist_tag in exif_data:
                    return f"Artist: {exif_data[artist_tag]}"
            
            # Try to get info from image info dict
            if hasattr(self.original_image, 'info'):
                info = self.original_image.info
                
                # Check common metadata keys
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
            if self.crop_mode.get() and self.needs_crop:
                self.manual_crop_check.config(state=tk.NORMAL)
            else:
                self.manual_crop_check.config(state=tk.DISABLED)
                self.manual_crop.set(False)
            if self.crop_mode.get():
                self.update_preview()
    
    def toggle_manual_crop(self):
        """Toggle manual crop positioning"""
        if self.manual_crop.get() and self.original_image and self.crop_mode.get():
            self.manual_crop_offset_x = 0
            self.manual_crop_offset_y = 0
            # For simplicity, skip interactive crop in this version
            self.update_preview()
        else:
            self.manual_crop_offset_x = 0
            self.manual_crop_offset_y = 0
            if self.original_image:
                self.update_preview()
    
    def check_crop_needed(self):
        """Check if cropping is needed based on aspect ratios"""
        if not self.original_image or self.keep_aspect_ratio.get():
            self.needs_crop = False
            self.crop_info_label.config(text="")
            self.manual_crop_check.config(state=tk.DISABLED)
            return
        
        try:
            target_width = int(self.width_var.get())
            target_height = int(self.height_var.get())
            orig_width, orig_height = self.original_image.size
            
            orig_ratio = orig_width / orig_height
            target_ratio = target_width / target_height
            
            if abs(orig_ratio - target_ratio) > 0.01:
                self.needs_crop = True
                if self.crop_mode.get():
                    if orig_ratio > target_ratio:
                        new_width = int(orig_height * target_ratio)
                        crop_percent = ((orig_width - new_width) / orig_width) * 100
                        self.crop_info_label.config(
                            text=f"⚠️ Will crop {crop_percent:.1f}% from sides",
                            fg="orange"
                        )
                    else:
                        new_height = int(orig_width / target_ratio)
                        crop_percent = ((orig_height - new_height) / orig_height) * 100
                        self.crop_info_label.config(
                            text=f"⚠️ Will crop {crop_percent:.1f}% from top/bottom",
                            fg="orange"
                        )
                else:
                    self.crop_info_label.config(
                        text="ℹ️ Enable 'Crop to fit' to crop image instead of stretching",
                        fg="blue"
                    )
            else:
                self.needs_crop = False
                self.crop_info_label.config(text="")
        except (ValueError, ZeroDivisionError):
            self.needs_crop = False
            self.crop_info_label.config(text="")
    
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
                self.check_crop_needed()
    
    def calculate_center_crop_box(self, target_width, target_height):
        """Calculate the crop box for center cropping with optional manual offset"""
        orig_width, orig_height = self.original_image.size
        orig_ratio = orig_width / orig_height
        target_ratio = target_width / target_height
        
        if orig_ratio > target_ratio:
            new_width = int(orig_height * target_ratio)
            center_left = (orig_width - new_width) // 2
            left = center_left + self.manual_crop_offset_x
            left = max(0, min(left, orig_width - new_width))
            top = 0
            right = left + new_width
            bottom = orig_height
        else:
            new_height = int(orig_width / target_ratio)
            left = 0
            center_top = (orig_height - new_height) // 2
            top = center_top + self.manual_crop_offset_y
            top = max(0, min(top, orig_height - new_height))
            right = orig_width
            bottom = top + new_height
        
        return (left, top, right, bottom)
    
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
    
    def on_closing(self):
        """Handle window closing properly"""
        self.root.quit()
        self.root.destroy()


def main():
    print("Starting Image Resizer with fixed sizing...")
    
    try:
        root = tk.Tk()
        app = ImageResizerApp(root)
        
        print("GUI created successfully")
        print("Window should now be properly sized and visible")
        
        root.mainloop()
        print("Application closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()







