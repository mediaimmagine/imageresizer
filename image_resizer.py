#!/usr/bin/env python3
"""
Image Resizer - macOS Native Version using PyQt5
Forked from the Windows Tkinter version for better macOS compatibility
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw
import io

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                                 QLineEdit, QCheckBox, QSlider, QRadioButton, 
                                 QButtonGroup, QGroupBox, QScrollArea, QFileDialog, 
                                 QMessageBox, QProgressBar, QSpinBox, QTextEdit,
                                 QSplitter, QFrame, QSizePolicy)
    from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
    from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QPainter, QPen
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class CropCanvas(QLabel):
    """Custom canvas widget for interactive crop positioning"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.crop_box = None
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.manual_offset_x = 0
        self.manual_offset_y = 0
        
    def set_crop_box(self, crop_box, scale_x, scale_y):
        """Set the crop box and scale factors"""
        self.crop_box = crop_box
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.update()
        
    def set_manual_offset(self, offset_x, offset_y):
        """Set manual offset for dragging"""
        self.manual_offset_x = offset_x
        self.manual_offset_y = offset_y
        self.update()
        
    def paintEvent(self, event):
        """Override paint event to draw crop box overlay"""
        super().paintEvent(event)
        
        if not self.crop_box or not self.pixmap():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate scaled crop box
        left, top, right, bottom = self.crop_box
        scaled_left = (left + self.manual_offset_x) * self.scale_x
        scaled_top = (top + self.manual_offset_y) * self.scale_y
        scaled_right = (right + self.manual_offset_x) * self.scale_x
        scaled_bottom = (bottom + self.manual_offset_y) * self.scale_y
        
        # Draw crop box with orange border (matching Windows version)
        pen = QPen(QColor(255, 165, 0), 3)  # Orange color, 3px width
        painter.setPen(pen)
        painter.drawRect(int(scaled_left), int(scaled_top), 
                        int(scaled_right - scaled_left), int(scaled_bottom - scaled_top))
        
        # Draw center crosshair
        center_x = (scaled_left + scaled_right) / 2
        center_y = (scaled_top + scaled_bottom) / 2
        crosshair_size = 20
        
        painter.drawLine(int(center_x - crosshair_size), int(center_y),
                        int(center_x + crosshair_size), int(center_y))
        painter.drawLine(int(center_x), int(center_y - crosshair_size),
                        int(center_x), int(center_y + crosshair_size))

class ImageResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.original_path = None
        self.resized_image = None
        self.keep_aspect_ratio = True
        self.crop_mode = False
        self.manual_crop = False
        self.needs_crop = False
        self.crop_box = None
        self.manual_crop_offset_x = 0
        self.manual_crop_offset_y = 0
        self.zoom_factor = 1.0
        self.original_pixmap = None
        self.zoom_label = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Image Resizer - Web Optimizer (macOS)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set macOS-specific styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton#previewBtn {
                background-color: #f39c12;
            }
            QPushButton#previewBtn:hover {
                background-color: #e67e22;
            }
            QPushButton#saveBtn {
                background-color: #27ae60;
            }
            QPushButton#saveBtn:hover {
                background-color: #229954;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (controls)
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel (preview)
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Upload section
        upload_group = QGroupBox("📁 Upload Image")
        upload_layout = QHBoxLayout(upload_group)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        upload_layout.addWidget(self.file_label)
        
        upload_btn = QPushButton("Browse...")
        upload_btn.clicked.connect(self.upload_image)
        upload_layout.addWidget(upload_btn)
        
        layout.addWidget(upload_group)
        
        # Settings section
        settings_group = QGroupBox("⚙️ Resize Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Dimensions
        dim_layout = QGridLayout()
        dim_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_input = QLineEdit("1920")
        self.width_input.textChanged.connect(self.on_width_change)
        dim_layout.addWidget(self.width_input, 0, 1)
        dim_layout.addWidget(QLabel("px"), 0, 2)
        
        dim_layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_input = QLineEdit("1080")
        self.height_input.textChanged.connect(self.on_height_change)
        dim_layout.addWidget(self.height_input, 1, 1)
        dim_layout.addWidget(QLabel("px"), 1, 2)
        
        settings_layout.addLayout(dim_layout)
        
        # Options
        self.aspect_check = QCheckBox("🔒 Keep aspect ratio (maintain proportions)")
        self.aspect_check.setChecked(True)
        self.aspect_check.toggled.connect(self.toggle_aspect_ratio)
        settings_layout.addWidget(self.aspect_check)
        
        self.crop_check = QCheckBox("✂️ Crop to fit (when aspect ratio differs)")
        self.crop_check.toggled.connect(self.toggle_crop_mode)
        settings_layout.addWidget(self.crop_check)
        
        self.manual_crop_check = QCheckBox("🎯 Manual crop positioning (drag to adjust)")
        self.manual_crop_check.setEnabled(False)
        self.manual_crop_check.toggled.connect(self.toggle_manual_crop)
        settings_layout.addWidget(self.manual_crop_check)
        
        # Crop info label
        self.crop_info_label = QLabel("")
        self.crop_info_label.setStyleSheet("color: orange; font-style: italic;")
        self.crop_info_label.setWordWrap(True)
        settings_layout.addWidget(self.crop_info_label)
        
        layout.addWidget(settings_group)
        
        # Quality section
        quality_group = QGroupBox("🎚️ Quality Settings")
        quality_layout = QVBoxLayout(quality_group)
        
        # Quick presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Quick presets:"))
        
        preset_30 = QPushButton("30% (Small)")
        preset_30.setStyleSheet("background-color: #e74c3c;")
        preset_30.clicked.connect(lambda: self.set_quality(30))
        preset_layout.addWidget(preset_30)
        
        preset_50 = QPushButton("50% (Medium)")
        preset_50.setStyleSheet("background-color: #f39c12;")
        preset_50.clicked.connect(lambda: self.set_quality(50))
        preset_layout.addWidget(preset_50)
        
        preset_85 = QPushButton("85% (High)")
        preset_85.setStyleSheet("background-color: #27ae60;")
        preset_85.clicked.connect(lambda: self.set_quality(85))
        preset_layout.addWidget(preset_85)
        
        quality_layout.addLayout(preset_layout)
        
        # Quality slider
        slider_layout = QHBoxLayout()
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(50)
        self.quality_slider.valueChanged.connect(self.on_quality_change)
        slider_layout.addWidget(self.quality_slider)
        
        self.quality_label = QLabel("50%")
        self.quality_label.setMinimumWidth(40)
        slider_layout.addWidget(self.quality_label)
        
        quality_layout.addLayout(slider_layout)
        layout.addWidget(quality_group)
        
        # Output format section
        format_group = QGroupBox("💾 Output Format")
        format_layout = QVBoxLayout(format_group)
        
        format_buttons = QButtonGroup()
        self.jpg_radio = QRadioButton("JPG/JPEG")
        self.jpg_radio.setChecked(True)
        self.png_radio = QRadioButton("PNG")
        self.webp_radio = QRadioButton("WebP")
        
        format_buttons.addButton(self.jpg_radio, 0)
        format_buttons.addButton(self.png_radio, 1)
        format_buttons.addButton(self.webp_radio, 2)
        
        # Connect format change to preview update
        self.jpg_radio.toggled.connect(self.on_format_change)
        self.png_radio.toggled.connect(self.on_format_change)
        self.webp_radio.toggled.connect(self.on_format_change)
        
        format_layout.addWidget(self.jpg_radio)
        format_layout.addWidget(self.png_radio)
        format_layout.addWidget(self.webp_radio)
        
        # Format info
        format_info = QLabel("JPG: Lossy, best for photos | PNG: Lossless, supports transparency | WebP: Modern, smaller files")
        format_info.setStyleSheet("color: gray; font-style: italic;")
        format_info.setWordWrap(True)
        format_layout.addWidget(format_info)
        
        layout.addWidget(format_group)
        
        # Web presets section
        presets_group = QGroupBox("🌐 Web Presets")
        presets_layout = QGridLayout(presets_group)
        
        presets = [
            ("2K (2048x1366)", 2048, 1366),
            ("Full HD (1920x1080)", 1920, 1080),
            ("HD (1280x720)", 1280, 720),
            ("Web (1024x683)", 1024, 683),
            ("Instagram (1080x1080)", 1080, 1080),
            ("Thumbnail (400x300)", 400, 300)
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: #95a5a6; color: white;")
            btn.clicked.connect(lambda checked, w=w, h=h: self.apply_preset(w, h))
            presets_layout.addWidget(btn, i//2, i%2)
        
        layout.addWidget(presets_group)
        
        # Info section
        info_group = QGroupBox("ℹ️ Original Image Info")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("Upload an image to see details")
        self.info_label.setStyleSheet("color: gray;")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        # Copyright warning
        self.copyright_warning_label = QLabel("")
        self.copyright_warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.copyright_warning_label.setWordWrap(True)
        info_layout.addWidget(self.copyright_warning_label)
        
        layout.addWidget(info_group)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.preview_btn = QPushButton("🔄 Update Preview")
        self.preview_btn.setObjectName("previewBtn")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(self.preview_btn)
        
        self.save_btn = QPushButton("💾 Save Resized Image")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """Create the right preview panel"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #f0f0f0; border: 2px solid #cccccc;")
        layout = QVBoxLayout(panel)
        
        # Preview title
        title = QLabel("📸 Preview")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Preview info
        self.preview_info_label = QLabel("No preview yet - Upload an image and click 'Update Preview'")
        self.preview_info_label.setStyleSheet("color: gray; font-weight: bold;")
        self.preview_info_label.setAlignment(Qt.AlignCenter)
        self.preview_info_label.setWordWrap(True)
        layout.addWidget(self.preview_info_label)
        
        # Scroll area for image preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: 2px solid #cccccc;")
        
        # Create a widget to hold multiple preview images
        self.preview_widget = QWidget()
        self.preview_widget.setStyleSheet("background-color: white;")
        self.preview_layout = QVBoxLayout(self.preview_widget)
        self.preview_layout.setAlignment(Qt.AlignCenter)
        
        # Create labels for crop area and final result
        self.crop_title_label = QLabel("📍 Crop Area (orange border shows what will be kept)")
        self.crop_title_label.setAlignment(Qt.AlignCenter)
        self.crop_title_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        
        self.crop_preview_label = QLabel()
        self.crop_preview_label.setAlignment(Qt.AlignCenter)
        self.crop_preview_label.setStyleSheet("background-color: white;")
        self.crop_preview_label.setMinimumSize(400, 300)
        
        self.separator_label = QLabel("↓")
        self.separator_label.setAlignment(Qt.AlignCenter)
        self.separator_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 5px;")
        
        self.result_title_label = QLabel("✅ Final Result")
        self.result_title_label.setAlignment(Qt.AlignCenter)
        self.result_title_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        
        self.result_preview_label = QLabel()
        self.result_preview_label.setAlignment(Qt.AlignCenter)
        self.result_preview_label.setStyleSheet("background-color: white;")
        self.result_preview_label.setMinimumSize(400, 300)
        
        # Add labels to layout
        self.preview_layout.addWidget(self.crop_title_label)
        self.preview_layout.addWidget(self.crop_preview_label)
        self.preview_layout.addWidget(self.separator_label)
        self.preview_layout.addWidget(self.result_title_label)
        self.preview_layout.addWidget(self.result_preview_label)
        
        scroll_area.setWidget(self.preview_widget)
        layout.addWidget(scroll_area)
        
        # Metadata area below preview
        metadata_group = QGroupBox("📊 Image Metadata & EXIF Data")
        metadata_layout = QVBoxLayout(metadata_group)
        
        self.metadata_label = QLabel("No metadata available")
        self.metadata_label.setStyleSheet("color: gray; font-family: 'Courier New', monospace; font-size: 11px;")
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setMaximumHeight(120)  # Limit height to save space
        metadata_layout.addWidget(self.metadata_label)
        
        layout.addWidget(metadata_group)
        
        return panel
        
    def upload_image(self):
        """Upload and load an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an image",
            "",
            "Image files (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All files (*.*)"
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.original_path = file_path
                
                # Update file label
                filename = os.path.basename(file_path)
                self.file_label.setText(f"✓ {filename}")
                self.file_label.setStyleSheet("color: green; font-weight: bold;")
                
                # Update dimensions
                width, height = self.original_image.size
                self.width_input.setText(str(width))
                self.height_input.setText(str(height))
                
                # Update info
                file_size = os.path.getsize(file_path) / 1024
                info_text = f"Original: {width}x{height} px | Size: {file_size:.1f} KB | Format: {self.original_image.format}"
                self.info_label.setText(info_text)
                self.info_label.setStyleSheet("color: black;")
                
                # Check for copyright metadata
                copyright_info = self.extract_copyright_metadata()
                if copyright_info:
                    warning_text = f"WARNING: COPYRIGHT PROTECTED IMAGE\n{copyright_info}"
                    self.copyright_warning_label.setText(warning_text)
                else:
                    self.copyright_warning_label.setText("")
                
                # Extract and display metadata
                metadata_text = self.extract_image_metadata()
                self.metadata_label.setText(metadata_text)
                self.metadata_label.setStyleSheet("color: black; font-family: 'Courier New', monospace; font-size: 11px;")
                
                # Enable buttons
                self.preview_btn.setEnabled(True)
                self.save_btn.setEnabled(True)
                
                # Auto-update preview
                self.update_preview()
                
                self.statusBar().showMessage(f"Loaded: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image:\n{str(e)}")
    
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
    
    def extract_image_metadata(self):
        """Extract comprehensive image metadata and EXIF data"""
        if not self.original_image:
            return "No metadata available"
        
        try:
            metadata_lines = []
            
            # Basic image info
            width, height = self.original_image.size
            metadata_lines.append(f"Dimensions: {width} x {height} pixels")
            metadata_lines.append(f"Mode: {self.original_image.mode}")
            metadata_lines.append(f"Format: {self.original_image.format}")
            
            # File size
            if self.original_path:
                file_size = os.path.getsize(self.original_path)
                metadata_lines.append(f"File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # EXIF data
            exif_data = self.original_image.getexif()
            if exif_data:
                metadata_lines.append("\nEXIF Data:")
                
                # Common EXIF tags
                exif_tags = {
                    271: "Make",
                    272: "Model", 
                    274: "Orientation",
                    282: "X Resolution",
                    283: "Y Resolution",
                    306: "DateTime",
                    315: "Artist",
                    33432: "Copyright",
                    36867: "DateTime Original",
                    36868: "DateTime Digitized"
                }
                
                for tag_id, tag_name in exif_tags.items():
                    if tag_id in exif_data:
                        value = exif_data[tag_id]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:47] + "..."
                        metadata_lines.append(f"  {tag_name}: {value}")
            
            # Image info dict
            if hasattr(self.original_image, 'info') and self.original_image.info:
                metadata_lines.append("\nImage Info:")
                for key, value in self.original_image.info.items():
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    metadata_lines.append(f"  {key}: {value}")
            
            return "\n".join(metadata_lines) if metadata_lines else "No metadata available"
            
        except Exception as e:
            return f"Error reading metadata: {str(e)}"
    
    def on_width_change(self):
        """Handle width change when aspect ratio is locked"""
        if self.keep_aspect_ratio and self.original_image:
            try:
                new_width = int(self.width_input.text())
                orig_width, orig_height = self.original_image.size
                aspect_ratio = orig_height / orig_width
                new_height = int(new_width * aspect_ratio)
                self.height_input.setText(str(new_height))
            except ValueError:
                pass
        if self.original_image:
            self.check_crop_needed()
            # Update preview with debouncing to avoid too many rapid updates
            if hasattr(self, '_dimension_timer'):
                self._dimension_timer.stop()
            self._dimension_timer = QTimer()
            self._dimension_timer.timeout.connect(self.update_preview)
            self._dimension_timer.setSingleShot(True)
            self._dimension_timer.start(300)
    
    def on_height_change(self):
        """Handle height change when aspect ratio is locked"""
        if self.keep_aspect_ratio and self.original_image:
            try:
                new_height = int(self.height_input.text())
                orig_width, orig_height = self.original_image.size
                aspect_ratio = orig_width / orig_height
                new_width = int(new_height * aspect_ratio)
                self.width_input.setText(str(new_width))
            except ValueError:
                pass
        if self.original_image:
            self.check_crop_needed()
            # Update preview with debouncing to avoid too many rapid updates
            if hasattr(self, '_dimension_timer'):
                self._dimension_timer.stop()
            self._dimension_timer = QTimer()
            self._dimension_timer.timeout.connect(self.update_preview)
            self._dimension_timer.setSingleShot(True)
            self._dimension_timer.start(300)
    
    def toggle_aspect_ratio(self, checked):
        """Toggle aspect ratio lock"""
        self.keep_aspect_ratio = checked
        if checked and self.original_image:
            self.on_width_change()
        if self.original_image:
            self.check_crop_needed()
    
    def toggle_crop_mode(self, checked):
        """Toggle crop mode"""
        self.crop_mode = checked
        if self.original_image:
            self.check_crop_needed()
            if checked and self.needs_crop:
                self.manual_crop_check.setEnabled(True)
            else:
                self.manual_crop_check.setEnabled(False)
                self.manual_crop_check.setChecked(False)
            if checked:
                self.update_preview()
    
    def toggle_manual_crop(self, checked):
        """Toggle manual crop positioning"""
        self.manual_crop = checked
        if checked and self.original_image and self.crop_mode:
            self.manual_crop_offset_x = 0
            self.manual_crop_offset_y = 0
            self.open_interactive_crop()
        else:
            self.manual_crop_offset_x = 0
            self.manual_crop_offset_y = 0
            if self.original_image:
                self.update_preview()
    
    def open_interactive_crop(self):
        """Open interactive crop window"""
        if not self.original_image:
            return
        
        # Create new window for interactive crop
        self.crop_interactive_window = QMainWindow()
        self.crop_interactive_window.setWindowTitle("Interactive Crop Positioning")
        
        # Create central widget
        central_widget = QWidget()
        self.crop_interactive_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Instructions
        instructions = QLabel("Drag the white rectangle to adjust crop position. Click 'Apply & Close' when done.")
        instructions.setStyleSheet("color: blue; font-weight: bold; padding: 10px;")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # Create scroll area for crop preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: 2px solid #cccccc;")
        
        # Create canvas for crop preview - show FULL original image
        self.crop_canvas = CropCanvas()
        self.crop_canvas.setAlignment(Qt.AlignCenter)
        self.crop_canvas.setStyleSheet("background-color: white;")
        
        # Show the full original image with crop overlay
        self.update_interactive_crop_display()
        
        scroll_area.setWidget(self.crop_canvas)
        layout.addWidget(scroll_area)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset Position")
        reset_btn.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 8px 16px;")
        reset_btn.clicked.connect(self.reset_crop_position)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        apply_btn = QPushButton("Apply & Close")
        apply_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 16px;")
        apply_btn.clicked.connect(self.apply_and_close_crop)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # Enable mouse tracking for dragging
        self.crop_canvas.setMouseTracking(True)
        self.crop_canvas.mousePressEvent = self.on_crop_drag_start
        self.crop_canvas.mouseMoveEvent = self.on_crop_drag_motion
        self.crop_canvas.mouseReleaseEvent = self.on_crop_drag_end
        
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Initialize zoom
        self.zoom_factor = 1.0
        self.original_pixmap = None
        
        self.crop_interactive_window.show()
    
    def on_crop_drag_start(self, event):
        """Handle start of crop drag"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_x = event.x()
            self.drag_start_y = event.y()
    
    def on_crop_drag_motion(self, event):
        """Handle crop drag motion"""
        if not self.dragging:
            return
        
        # Calculate offset
        dx = event.x() - self.drag_start_x
        dy = event.y() - self.drag_start_y
        
        # Update crop offset
        self.manual_crop_offset_x += dx
        self.manual_crop_offset_y += dy
        
        # Update canvas with new offset
        self.crop_canvas.set_manual_offset(self.manual_crop_offset_x, self.manual_crop_offset_y)
        
        # Update drag start position
        self.drag_start_x = event.x()
        self.drag_start_y = event.y()
    
    def on_crop_drag_end(self, event):
        """Handle end of crop drag"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def update_interactive_crop_display(self):
        """Update the interactive crop display - matches Windows version behavior"""
        if not self.original_image or not self.crop_canvas:
            return
        
        try:
            # Calculate crop box
            target_width = int(self.width_input.text())
            target_height = int(self.height_input.text())
            crop_box = self.calculate_center_crop_box(target_width, target_height)
            
            # Scale image to fit canvas (max 800x600) - same as Windows version
            display_img = self.original_image.copy()
            max_size = (800, 600)
            display_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Calculate scale factor
            orig_width, orig_height = self.original_image.size
            display_width, display_height = display_img.size
            scale_x = display_width / orig_width
            scale_y = display_height / orig_height
            
            # Store scale for mouse calculations
            self.crop_scale_x = scale_x
            self.crop_scale_y = scale_y
            
            # Convert to QPixmap
            buffer = io.BytesIO()
            display_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # Set the image
            self.crop_canvas.setPixmap(pixmap)
            self.crop_canvas.setMinimumSize(display_width, display_height)
            self.crop_canvas.resize(display_width, display_height)
            
            # Set crop box and scale factors for the canvas
            self.crop_canvas.set_crop_box(crop_box, scale_x, scale_y)
            
            # Store crop box for dragging
            self.crop_box = crop_box
            self.crop_x, self.crop_y, self.crop_right, self.crop_bottom = crop_box
            self.crop_width = self.crop_right - self.crop_x
            self.crop_height = self.crop_bottom - self.crop_y
            
            # Calculate window size: image size + 15% border on each side + space for controls
            border_factor = 0.15  # 15% border
            window_width = int(display_width * (1 + 2 * border_factor))
            window_height = int(display_height * (1 + 2 * border_factor) + 120)  # +120 for controls
            
            # Set window size
            self.crop_interactive_window.resize(window_width, window_height)
            
            # Center the window on screen
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - window_width) // 2
            y = (screen.height() - window_height) // 2
            self.crop_interactive_window.move(x, y)
            
        except Exception as e:
            print(f"Error updating interactive crop display: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_zoom(self):
        """Apply the current zoom factor to the image"""
        if not self.original_pixmap or not self.crop_canvas:
            return
        
        try:
            # Calculate new size
            original_size = self.original_pixmap.size()
            new_width = int(original_size.width() * self.zoom_factor)
            new_height = int(original_size.height() * self.zoom_factor)
            
            # Scale the pixmap
            scaled_pixmap = self.original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Set the pixmap and adjust canvas size
            self.crop_canvas.setPixmap(scaled_pixmap)
            self.crop_canvas.setMinimumSize(scaled_pixmap.size())
            self.crop_canvas.resize(scaled_pixmap.size())
            
            # Update zoom label if it exists
            if self.zoom_label:
                self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
        except Exception as e:
            print(f"Error applying zoom: {e}")
            # Fallback: just set the original pixmap
            if self.original_pixmap:
                self.crop_canvas.setPixmap(self.original_pixmap)
    
    def on_zoom_slider_changed(self, value):
        """Handle zoom slider change"""
        self.zoom_factor = value / 100.0  # Convert percentage to factor
        self.apply_zoom()
    
    def fit_to_window(self):
        """Fit the image to the window size"""
        if not self.original_pixmap or not self.crop_interactive_window:
            return
        
        try:
            # Get the scroll area size
            scroll_area = self.crop_canvas.parent().parent()  # Get the QScrollArea
            if scroll_area and hasattr(scroll_area, 'size'):
                scroll_size = scroll_area.size()
                original_size = self.original_pixmap.size()
                
                # Calculate zoom to fit
                zoom_x = scroll_size.width() / original_size.width()
                zoom_y = scroll_size.height() / original_size.height()
                self.zoom_factor = min(zoom_x, zoom_y) * 0.9  # 90% to leave some margin
                
                # Update slider
                if self.zoom_slider:
                    self.zoom_slider.setValue(int(self.zoom_factor * 100))
                
                self.apply_zoom()
            else:
                # Fallback: set to 50% zoom
                self.zoom_factor = 0.5
                if self.zoom_slider:
                    self.zoom_slider.setValue(50)
                self.apply_zoom()
        except Exception as e:
            # Fallback: set to 50% zoom
            self.zoom_factor = 0.5
            if self.zoom_slider:
                self.zoom_slider.setValue(50)
            self.apply_zoom()
    
    def reset_crop_position(self):
        """Reset crop position to center"""
        self.manual_crop_offset_x = 0
        self.manual_crop_offset_y = 0
        self.update_interactive_crop_display()
    
    def apply_and_close_crop(self):
        """Apply crop settings and close interactive window"""
        if self.crop_interactive_window:
            self.crop_interactive_window.close()
            self.crop_interactive_window = None
        
        # Update main preview
        self.update_preview()
    
    def check_crop_needed(self):
        """Check if cropping is needed based on aspect ratios"""
        if not self.original_image or self.keep_aspect_ratio:
            self.needs_crop = False
            self.crop_info_label.setText("")
            self.manual_crop_check.setEnabled(False)
            return
        
        try:
            target_width = int(self.width_input.text())
            target_height = int(self.height_input.text())
            orig_width, orig_height = self.original_image.size
            
            orig_ratio = orig_width / orig_height
            target_ratio = target_width / target_height
            
            if abs(orig_ratio - target_ratio) > 0.01:
                self.needs_crop = True
                if self.crop_mode:
                    if orig_ratio > target_ratio:
                        new_width = int(orig_height * target_ratio)
                        crop_percent = ((orig_width - new_width) / orig_width) * 100
                        self.crop_info_label.setText(f"⚠️ Will crop {crop_percent:.1f}% from sides")
                    else:
                        new_height = int(orig_width / target_ratio)
                        crop_percent = ((orig_height - new_height) / orig_height) * 100
                        self.crop_info_label.setText(f"⚠️ Will crop {crop_percent:.1f}% from top/bottom")
                else:
                    self.crop_info_label.setText("ℹ️ Enable 'Crop to fit' to crop image instead of stretching")
            else:
                self.needs_crop = False
                self.crop_info_label.setText("")
        except (ValueError, ZeroDivisionError):
            self.needs_crop = False
            self.crop_info_label.setText("")
    
    def on_quality_change(self, value):
        """Handle quality slider change"""
        self.quality_label.setText(f"{value}%")
        if self.original_image and self.resized_image:
            # Debounce the update
            if hasattr(self, '_quality_timer'):
                self._quality_timer.stop()
            self._quality_timer = QTimer()
            self._quality_timer.timeout.connect(self.update_preview)
            self._quality_timer.setSingleShot(True)
            self._quality_timer.start(300)
    
    def set_quality(self, quality):
        """Set quality to a specific value"""
        self.quality_slider.setValue(quality)
        self.quality_label.setText(f"{quality}%")
        if self.original_image and self.resized_image:
            self.update_preview()
    
    def on_format_change(self):
        """Handle format selection change"""
        # Update preview if image is loaded
        if self.original_image:
            self.update_preview()
    
    def apply_preset(self, width, height):
        """Apply a preset dimension"""
        if not self.original_image:
            self.width_input.setText(str(width))
            self.height_input.setText(str(height))
            return
        
        orig_width, orig_height = self.original_image.size
        orig_ratio = orig_width / orig_height
        preset_ratio = width / height
        
        if abs(orig_ratio - preset_ratio) > 0.01:
            self.keep_aspect_ratio = False
            self.aspect_check.setChecked(False)
            self.width_input.setText(str(width))
            self.height_input.setText(str(height))
            self.crop_mode = True
            self.crop_check.setChecked(True)
            self.toggle_crop_mode(True)
        else:
            if self.keep_aspect_ratio:
                orig_ratio = orig_width / orig_height
                preset_ratio = width / height
                
                if orig_ratio > preset_ratio:
                    self.width_input.setText(str(width))
                    self.on_width_change()
                else:
                    self.height_input.setText(str(height))
                    self.on_height_change()
            else:
                self.width_input.setText(str(width))
                self.height_input.setText(str(height))
                self.check_crop_needed()
                # Update preview immediately for preset buttons
                if self.original_image:
                    self.update_preview()
    
    def calculate_center_crop_box(self, target_width, target_height):
        """Calculate the crop box for center cropping"""
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
    
    def create_crop_preview_image(self):
        """Create a preview image showing the crop area with white rectangle overlay"""
        if not self.original_image:
            return None
        
        try:
            target_width = int(self.width_input.text())
            target_height = int(self.height_input.text())
            crop_box = self.calculate_center_crop_box(target_width, target_height)
            
            # Create a copy of the original image
            preview_img = self.original_image.copy()
            
            # Draw crop rectangle with white border and thicker width
            draw = ImageDraw.Draw(preview_img)
            
            # Draw multiple rectangles to create a thicker border
            for i in range(6):  # 6-pixel thick border
                draw.rectangle(
                    (crop_box[0] - i, crop_box[1] - i, crop_box[2] + i, crop_box[3] + i),
                    outline="white",
                    width=1
                )
            
            # Add text with white background for better visibility
            text_bbox = draw.textbbox((crop_box[0] + 5, crop_box[1] + 5), "Crop Area")
            draw.rectangle(text_bbox, fill="white", outline="black")
            draw.text((crop_box[0] + 5, crop_box[1] + 5), "Crop Area", fill="black")
            
            return preview_img
            
        except Exception:
            return None

    def update_preview(self):
        """Update the preview with resized image"""
        if not self.original_image:
            QMessageBox.warning(self, "No Image", "Please upload an image first")
            return
        
        try:
            new_width = int(self.width_input.text())
            new_height = int(self.height_input.text())
            
            if new_width <= 0 or new_height <= 0:
                QMessageBox.critical(self, "Invalid Dimensions", "Width and height must be positive numbers")
                return
            
            self.check_crop_needed()
            
            if self.crop_mode and self.needs_crop:
                crop_box = self.calculate_center_crop_box(new_width, new_height)
                self.crop_box = crop_box
                cropped = self.original_image.crop(crop_box)
                self.resized_image = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                self.resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate estimated file size based on selected format
            # Use quick heuristic estimation instead of actual compression for speed
            width, height = self.resized_image.size
            pixels = width * height
            
            if self.jpg_radio.isChecked():
                format_name = 'JPEG'
                format_ext = 'JPG'
                # JPEG heuristic: ~0.5-2 bytes per pixel depending on quality
                quality_factor = self.quality_slider.value() / 100.0
                bytes_per_pixel = 0.5 + (1.5 * quality_factor)
                estimated_size_kb = (pixels * bytes_per_pixel) / 1024
            elif self.png_radio.isChecked():
                format_name = 'PNG'
                format_ext = 'PNG'
                # PNG heuristic: ~3-4 bytes per pixel (lossless)
                channels = 4 if self.resized_image.mode == 'RGBA' else 3
                bytes_per_pixel = 3.5 + (channels * 0.1)
                estimated_size_kb = (pixels * bytes_per_pixel) / 1024
            else:  # WebP
                format_name = 'WebP'
                format_ext = 'WebP'
                # WebP heuristic: ~0.3-1.5 bytes per pixel depending on quality
                quality_factor = self.quality_slider.value() / 100.0
                bytes_per_pixel = 0.3 + (1.2 * quality_factor)
                estimated_size_kb = (pixels * bytes_per_pixel) / 1024
            
            crop_text = ""
            if self.crop_mode and self.needs_crop and self.crop_box:
                left, top, right, bottom = self.crop_box
                crop_text = f"\n✂️ Cropped from: {right-left} x {bottom-top} px"
            
            info_text = (
                f"📐 Dimensions: {new_width} x {new_height} px\n"
                f"📊 Estimated Size ({format_ext}): {estimated_size_kb:.1f} KB\n"
                f"🎚️ Quality: {self.quality_slider.value()}%"
                f"{crop_text}"
            )
            self.preview_info_label.setText(info_text)
            self.preview_info_label.setStyleSheet("color: black; font-weight: bold;")
            
            # Display preview - show both crop area and final result like Windows version
            max_preview_size = (450, 300)
            
            # Clear previous previews
            self.crop_preview_label.clear()
            self.result_preview_label.clear()
            
            if self.crop_mode and self.needs_crop:
                # Show crop area with orange rectangle overlay
                crop_preview = self.create_crop_preview_image()
                if crop_preview:
                    crop_display = crop_preview.copy()
                    crop_display.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                    
                    # Convert to QPixmap
                    buffer = io.BytesIO()
                    crop_display.save(buffer, format='PNG')
                    buffer.seek(0)
                    
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    self.crop_preview_label.setPixmap(pixmap)
                
                # Show final result
                result_display = self.resized_image.copy()
                result_display.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                buffer = io.BytesIO()
                result_display.save(buffer, format='PNG')
                buffer.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                self.result_preview_label.setPixmap(pixmap)
                
                # Show both labels and titles
                self.crop_title_label.show()
                self.crop_preview_label.show()
                self.separator_label.show()
                self.result_title_label.show()
                self.result_preview_label.show()
            else:
                # Show only final result
                result_display = self.resized_image.copy()
                result_display.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                buffer = io.BytesIO()
                result_display.save(buffer, format='PNG')
                buffer.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                self.result_preview_label.setPixmap(pixmap)
                
                # Hide crop preview and titles, show only result
                self.crop_title_label.hide()
                self.crop_preview_label.hide()
                self.separator_label.hide()
                self.result_title_label.show()
                self.result_preview_label.show()
            
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter valid numbers for width and height")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to preview image:\n{str(e)}")
    
    def save_image(self):
        """Save the resized image"""
        if not self.original_image:
            QMessageBox.warning(self, "No Image", "Please upload an image first")
            return
        
        try:
            new_width = int(self.width_input.text())
            new_height = int(self.height_input.text())
            
            if new_width <= 0 or new_height <= 0:
                QMessageBox.critical(self, "Invalid Dimensions", "Width and height must be positive numbers")
                return
            
            original_name = Path(self.original_path).stem
            
            # Determine output format
            if self.jpg_radio.isChecked():
                format_ext = '.jpg'
                file_filter = "JPEG files (*.jpg *.jpeg);;All files (*.*)"
            elif self.png_radio.isChecked():
                format_ext = '.png'
                file_filter = "PNG files (*.png);;All files (*.*)"
            else:
                format_ext = '.webp'
                file_filter = "WebP files (*.webp);;All files (*.*)"
            
            default_name = f"trieste@news_{original_name}{format_ext}"
            
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Resized Image",
                default_name,
                file_filter
            )
            
            if save_path:
                if self.resized_image:
                    resized = self.resized_image
                else:
                    resized = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                save_kwargs = {}
                
                if save_path.lower().endswith(('.jpg', '.jpeg')):
                    save_kwargs = {
                        'quality': self.quality_slider.value(),
                        'optimize': True
                    }
                    if resized.mode == 'RGBA':
                        background = Image.new('RGB', resized.size, (255, 255, 255))
                        background.paste(resized, mask=resized.split()[3] if len(resized.split()) == 4 else None)
                        resized = background
                
                elif save_path.lower().endswith('.webp'):
                    save_kwargs = {
                        'quality': self.quality_slider.value(),
                        'method': 6
                    }
                
                elif save_path.lower().endswith('.png'):
                    quality = self.quality_slider.value()
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
                QMessageBox.information(
                    self,
                    "Success",
                    f"Image saved successfully!\n\n"
                    f"Location: {save_path}\n"
                    f"Dimensions: {new_width}x{new_height} px\n"
                    f"File size: {file_size:.1f} KB"
                )
                
                self.statusBar().showMessage(f"Saved: {os.path.basename(save_path)}")
                
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Please enter valid numbers for width and height")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image:\n{str(e)}")


def main():
    if not PYQT_AVAILABLE:
        print("PyQt5 is not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
            print("PyQt5 installed successfully. Please restart the application.")
            return
        except subprocess.CalledProcessError:
            print("Failed to install PyQt5. Please install it manually: pip install PyQt5")
            return
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Image Resizer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Image Resizer")
    
    # Create and show main window
    window = ImageResizerApp()
    window.show()
    
    print("Image Resizer - macOS Native Version started")
    print("This version uses PyQt5 for better macOS compatibility")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
