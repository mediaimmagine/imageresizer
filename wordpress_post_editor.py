#!/usr/bin/env python3
"""
WordPress Post Editor - Offline Article Creator
Create articles offline in a GUI, then publish them to WordPress via REST API

Features:
- Full offline editing (title, content, excerpt, categories, tags)
- Rich text editing with HTML support
- Image/media upload integration
- Secure authentication via Application Passwords
- Supports "Author" role privileges (standard WordPress sites)
- For MiniOrange-protected sites: Requires Editor or Administrator role
- Multi-site support (same as Image Resizer)
- Draft/Schedule/Publish options
- Save drafts locally for later editing

Authentication:
- Uses WordPress Application Passwords (same as Image Resizer)
- For MiniOrange-protected sites: Uses Basic Auth with Client ID/Secret
- No interactive login required - fully automated
- Secure REST API access
"""

import os
import json
import sys
import io
from typing import Optional, Dict, List
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QLabel, QPushButton, QMessageBox, QComboBox,
    QGroupBox, QWidget, QProgressBar, QSpinBox, QDateTimeEdit, QCheckBox,
    QListWidget, QListWidgetItem, QFileDialog, QSplitter, QScrollArea,
    QCalendarWidget, QTimeEdit, QInputDialog
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QDate, QTime, QUrl
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QPixmap, QTextCursor


def get_resource_path(filename: str) -> str:
    """Return an absolute path to a bundled resource.
    
    Tries multiple locations to work both in development and in a PyInstaller .app bundle.
    """
    candidates = []
    # 1) Next to this file (dev mode)
    candidates.append(os.path.join(os.path.dirname(__file__), filename))
    # 2) PyInstaller _MEIPASS temp dir
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(os.path.join(meipass, filename))
    # 3) Next to executable (inside .app/Contents/MacOS)
    candidates.append(os.path.join(os.path.dirname(sys.executable), filename))
    # 4) macOS Resources folder (when running inside .app)
    candidates.append(os.path.join(os.path.dirname(sys.executable), "..", "Resources", filename))
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    # Fallback: return first candidate (dev)
    return os.path.abspath(candidates[0])


def get_settings_path() -> str:
    """Get path to WordPress settings file (shared with Image Resizer)"""
    home = os.path.expanduser("~")
    cfg_dir = os.path.join(home, ".imageresizer")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "wp_settings.json")


def get_drafts_path() -> str:
    """Get path to store draft posts"""
    home = os.path.expanduser("~")
    drafts_dir = os.path.join(home, ".imageresizer", "wp_drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    return drafts_dir


class WordPressPostEditor(QMainWindow):
    """Main window for WordPress post editor"""
    
    def __init__(self):
        super().__init__()
        self.wp_sites = []
        self.current_site_index = 0
        self.current_draft_path = None
        self.featured_image_path = None
        self.featured_image_media_id = 0
        self.use_custom_author = False
        self.custom_author_name = ""
        self.custom_author_password = ""
        self.selected_site_indices = []  # List of selected site indices for multi-site publishing
        self.site_checkboxes = []  # List of site checkboxes
        self.last_selected_site_indices = []  # Remember last selected sites
        self._load_wp_settings()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("WordPress Post Editor - Offline Article Creator")
        self.setMinimumSize(900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar with logo and title
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(10)
        
        # Try to load logo if present
        self._has_logo = False
        logo_label = None
        try:
            # Prefer white graphic-only logo; fallback to previous names
            local_logo_path = get_resource_path("mediaimmagine_logo_white.png")
            if os.path.exists(local_logo_path):
                pm = QPixmap(local_logo_path)
                if not pm.isNull():
                    self._has_logo = True
                    logo_label = QLabel()
                    pm = pm.scaledToHeight(20, Qt.SmoothTransformation)
                    logo_label.setPixmap(pm)
                    logo_label.setContentsMargins(0, 0, 15, 0)
                    header_layout.addWidget(logo_label)
            else:
                fallback_logo = get_resource_path("mediaimmagine_logo.png")
                if os.path.exists(fallback_logo):
                    pm = QPixmap(fallback_logo)
                    if not pm.isNull():
                        self._has_logo = True
                        logo_label = QLabel()
                        pm = pm.scaledToHeight(20, Qt.SmoothTransformation)
                        logo_label.setPixmap(pm)
                        logo_label.setContentsMargins(0, 0, 15, 0)
                        header_layout.addWidget(logo_label)
        except Exception:
            self._has_logo = False
        
        # Title
        title_label = QLabel("WordPress Post Editor - Offline Article Creator")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addWidget(header)
        
        # Top toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Post editor
        left_panel = self._create_editor_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Settings and metadata
        right_panel = self._create_metadata_panel()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 2)  # Editor gets more space
        splitter.setStretchFactor(1, 1)  # Metadata panel
        
        main_layout.addWidget(splitter)
        
        # Footer credits (match Image Resizer style)
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)
        footer_layout.setSpacing(8)
        footer.setStyleSheet("background-color: #ecf0f1;")
        
        credits_text = (
            "mediaimmagine s.r.l. · COED Digital Editor · CUP D97H24001840007\n"
            "PR FESR 2021-27 · contributo di Regione Friuli Venezia Giulia\n"
            "sviluppato con l'ausilio di IA"
        )
        credits_label = QLabel(credits_text)
        credits_label.setStyleSheet("color: #2c3e50; font-size: 10px;")
        credits_label.setWordWrap(True)
        footer_layout.addWidget(credits_label, 1)
        main_layout.addWidget(footer)
        
        # Status bar
        self.statusBar().showMessage("Ready - Create your article offline")
        
    def _create_toolbar(self) -> QWidget:
        """Create top toolbar with site selector and actions"""
        toolbar = QWidget()
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        layout.addWidget(QLabel("|"))
        
        # Action buttons
        new_btn = QPushButton("📝 New Post")
        new_btn.clicked.connect(self._new_post)
        layout.addWidget(new_btn)
        
        load_btn = QPushButton("📂 Load Draft")
        load_btn.clicked.connect(self._load_draft)
        layout.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Save Draft")
        save_btn.clicked.connect(self._save_draft)
        layout.addWidget(save_btn)
        
        layout.addWidget(QLabel("|"))
        
        # Publish button
        self.publish_btn = QPushButton("🚀 Publish to WordPress")
        self.publish_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self.publish_btn.clicked.connect(self._publish_post)
        layout.addWidget(self.publish_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)
        
        return toolbar
    
    def _create_editor_panel(self) -> QWidget:
        """Create the main post editor panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Title:")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter article title...")
        self.title_input.setFont(QFont("Arial", 14))
        layout.addWidget(self.title_input)
        
        # Content editor
        content_label = QLabel("Content:")
        content_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(content_label)
        
        # Formatting toolbar
        format_toolbar = QWidget()
        format_toolbar_layout = QHBoxLayout(format_toolbar)
        format_toolbar_layout.setContentsMargins(5, 5, 5, 5)
        format_toolbar_layout.setSpacing(5)
        
        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold")
        self.bold_btn.clicked.connect(self._toggle_bold)
        format_toolbar_layout.addWidget(self.bold_btn)
        
        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFont(QFont("Arial", 12, QFont.StyleItalic))
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Italic")
        self.italic_btn.clicked.connect(self._toggle_italic)
        format_toolbar_layout.addWidget(self.italic_btn)
        
        # Underline button
        self.underline_btn = QPushButton("U")
        self.underline_btn.setFont(QFont("Arial", 12))
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Underline")
        self.underline_btn.clicked.connect(self._toggle_underline)
        format_toolbar_layout.addWidget(self.underline_btn)
        
        format_toolbar_layout.addWidget(QLabel("|"))
        
        # Heading buttons
        h2_btn = QPushButton("H2")
        h2_btn.setToolTip("Heading 2")
        h2_btn.clicked.connect(lambda: self._apply_heading(2))
        format_toolbar_layout.addWidget(h2_btn)
        
        h3_btn = QPushButton("H3")
        h3_btn.setToolTip("Heading 3")
        h3_btn.clicked.connect(lambda: self._apply_heading(3))
        format_toolbar_layout.addWidget(h3_btn)
        
        format_toolbar_layout.addWidget(QLabel("|"))
        
        # Link button
        link_btn = QPushButton("🔗 Link")
        link_btn.setToolTip("Insert/Edit Link")
        link_btn.clicked.connect(self._insert_link)
        format_toolbar_layout.addWidget(link_btn)
        
        format_toolbar_layout.addStretch()
        
        layout.addWidget(format_toolbar)
        
        # Content editor
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your article here... Use the formatting buttons above to style your text.")
        self.content_input.setFont(QFont("Arial", 14))  # Increased from 11 to 14 for better readability
        # Enable HTML support
        self.content_input.setAcceptRichText(True)
        # Connect cursor position change to update button states
        self.content_input.cursorPositionChanged.connect(self._update_format_buttons)
        layout.addWidget(self.content_input, 1)
        
        # Word and character count
        self.word_count_label = QLabel("Words: 0 | Characters: 0")
        self.content_input.textChanged.connect(self._update_word_count)
        layout.addWidget(self.word_count_label)
        
        return panel
    
    def _create_metadata_panel(self) -> QWidget:
        """Create metadata and settings panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # WordPress Sites Selection (moved to top for better visibility)
        sites_group = QGroupBox("WordPress Sites (Select one or more)")
        sites_layout = QVBoxLayout(sites_group)
        
        # Scrollable area for site checkboxes
        sites_scroll = QScrollArea()
        sites_scroll.setWidgetResizable(True)
        sites_scroll.setMaximumHeight(120)
        sites_scroll_widget = QWidget()
        sites_scroll_layout = QVBoxLayout(sites_scroll_widget)
        sites_scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        self.site_checkboxes = []
        self._update_site_checkboxes(sites_scroll_layout)
        
        sites_scroll.setWidget(sites_scroll_widget)
        sites_layout.addWidget(sites_scroll)
        
        # Add note about authentication methods
        auth_note = QLabel(
            "💡 <b>Note:</b> Authentication to triesteallnews.it will be performed via MiniOrange API.<br>"
            "Authentication to the other FVG.news sites will happen via WordPress REST API."
        )
        auth_note.setWordWrap(True)
        auth_note.setStyleSheet("color: #666; font-size: 10px; padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        sites_layout.addWidget(auth_note)
        
        layout.addWidget(sites_group)
        
        # Excerpt
        excerpt_group = QGroupBox("Excerpt")
        excerpt_layout = QVBoxLayout(excerpt_group)
        self.excerpt_input = QTextEdit()
        self.excerpt_input.setMaximumHeight(100)
        self.excerpt_input.setPlaceholderText("Optional: Short summary of the article...")
        excerpt_layout.addWidget(self.excerpt_input)
        layout.addWidget(excerpt_group)
        
        # Categories dropdown
        categories_group = QGroupBox("Category")
        categories_layout = QVBoxLayout(categories_group)
        self.categories_combo = QComboBox()
        self.categories_combo.setEditable(False)  # Non-editable dropdown
        # Predefined categories
        predefined_categories = ["CRONACA", "ATTUALITÀ", "EDITORIALI", "POLITICA"]
        self.categories_combo.addItems(predefined_categories)
        self.categories_combo.setCurrentIndex(0)  # Default to first category
        categories_layout.addWidget(self.categories_combo)
        layout.addWidget(categories_group)
        
        tags_group = QGroupBox("Tags (comma-separated, min 5, max 7)")
        tags_layout = QVBoxLayout(tags_group)
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g., breaking-news, local, update (minimum 5, maximum 7 tags)")
        tags_layout.addWidget(self.tags_input)
        layout.addWidget(tags_group)
        
        # Featured Image Upload
        featured_group = QGroupBox("Featured Image")
        featured_layout = QVBoxLayout(featured_group)
        
        # Image preview
        self.featured_image_preview = QLabel()
        self.featured_image_preview.setMinimumHeight(150)
        self.featured_image_preview.setMaximumHeight(200)
        self.featured_image_preview.setAlignment(Qt.AlignCenter)
        self.featured_image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.featured_image_preview.setText("No image selected\n\nClick 'Select Image' to choose\nJPEG or PNG (max 130KB)")
        self.featured_image_preview.setWordWrap(True)
        featured_layout.addWidget(self.featured_image_preview)
        
        # Image info label
        self.featured_image_info = QLabel("")
        self.featured_image_info.setStyleSheet("color: #666; font-size: 10px;")
        self.featured_image_info.setWordWrap(True)
        featured_layout.addWidget(self.featured_image_info)
        
        # Buttons
        featured_btn_layout = QHBoxLayout()
        
        self.select_image_btn = QPushButton("📷 Select Image")
        self.select_image_btn.clicked.connect(self._select_featured_image)
        featured_btn_layout.addWidget(self.select_image_btn)
        
        self.upload_image_btn = QPushButton("⬆ Upload to WordPress")
        self.upload_image_btn.setEnabled(False)
        self.upload_image_btn.clicked.connect(self._upload_featured_image)
        featured_btn_layout.addWidget(self.upload_image_btn)
        
        self.remove_image_btn = QPushButton("✕ Remove")
        self.remove_image_btn.setEnabled(False)
        self.remove_image_btn.clicked.connect(self._remove_featured_image)
        featured_btn_layout.addWidget(self.remove_image_btn)
        
        featured_layout.addLayout(featured_btn_layout)
        
        layout.addWidget(featured_group)
        
        # Author Selection
        author_group = QGroupBox("Author & Publishing")
        author_layout = QVBoxLayout(author_group)
        
        # Author selection radio buttons or checkbox
        self.use_custom_author_checkbox = QCheckBox("Publish as custom author (not Redazione user)")
        self.use_custom_author_checkbox.toggled.connect(self._on_custom_author_toggled)
        author_layout.addWidget(self.use_custom_author_checkbox)
        
        # Custom author fields (initially disabled)
        custom_author_layout = QFormLayout()
        
        self.custom_author_name_input = QLineEdit()
        self.custom_author_name_input.setPlaceholderText("WordPress username")
        self.custom_author_name_input.setEnabled(False)
        custom_author_layout.addRow("Author Username:", self.custom_author_name_input)
        
        self.custom_author_password_input = QLineEdit()
        self.custom_author_password_input.setPlaceholderText("Application Password")
        self.custom_author_password_input.setEchoMode(QLineEdit.Password)
        self.custom_author_password_input.setEnabled(False)
        custom_author_layout.addRow("Application Password:", self.custom_author_password_input)
        
        author_layout.addLayout(custom_author_layout)
        
        # Info label
        author_info = QLabel(
            "💡 <b>Redazione User:</b> Uses site credentials (COED Post Editor)<br>"
            "<b>Custom Author:</b> Enter author's WordPress username and Application Password"
        )
        author_info.setWordWrap(True)
        author_info.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        author_layout.addWidget(author_info)
        
        layout.addWidget(author_group)
        
        # Publish Status
        status_group = QGroupBox("Publish Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["draft", "publish", "pending"])
        self.status_combo.setCurrentText("draft")
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_combo)
        
        # Schedule post
        self.schedule_checkbox = QCheckBox("Schedule for later")
        self.schedule_checkbox.toggled.connect(self._on_schedule_toggled)
        status_layout.addWidget(self.schedule_checkbox)
        
        # Calendar widget for date selection
        self.schedule_calendar = QCalendarWidget()
        self.schedule_calendar.setMinimumDate(QDate.currentDate())
        self.schedule_calendar.setSelectedDate(QDate.currentDate().addDays(1))
        self.schedule_calendar.setEnabled(False)
        self.schedule_calendar.setMaximumHeight(200)
        status_layout.addWidget(self.schedule_calendar)
        
        # Time input (hour:minute)
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time:"))
        self.schedule_time = QTimeEdit()
        self.schedule_time.setTime(QTime.currentTime())
        self.schedule_time.setDisplayFormat("HH:mm")
        self.schedule_time.setEnabled(False)
        time_layout.addWidget(self.schedule_time)
        time_layout.addStretch()
        status_layout.addLayout(time_layout)
        
        layout.addWidget(status_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        return panel
    
    def _on_schedule_toggled(self, checked):
        """Enable/disable schedule calendar and time when checkbox is toggled"""
        self.schedule_calendar.setEnabled(checked)
        self.schedule_time.setEnabled(checked)
        if checked:
            self.status_combo.setCurrentText("future")  # WordPress uses "future" for scheduled
    
    def _get_schedule_datetime(self) -> QDateTime:
        """Get the combined date and time from calendar and time widgets"""
        selected_date = self.schedule_calendar.selectedDate()
        selected_time = self.schedule_time.time()
        return QDateTime(selected_date, selected_time)
    
    def _toggle_bold(self):
        """Toggle bold formatting"""
        fmt = QTextCharFormat()
        if self.bold_btn.isChecked():
            fmt.setFontWeight(QFont.Bold)
        else:
            fmt.setFontWeight(QFont.Normal)
        self.content_input.mergeCurrentCharFormat(fmt)
    
    def _toggle_italic(self):
        """Toggle italic formatting"""
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.content_input.mergeCurrentCharFormat(fmt)
    
    def _toggle_underline(self):
        """Toggle underline formatting"""
        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline if self.underline_btn.isChecked() else QTextCharFormat.NoUnderline)
        self.content_input.mergeCurrentCharFormat(fmt)
    
    def _apply_heading(self, level: int):
        """Apply heading format (H2 or H3)"""
        cursor = self.content_input.textCursor()
        if cursor.hasSelection():
            # Apply heading format to selected text
            fmt = QTextCharFormat()
            if level == 2:
                fmt.setFontPointSize(18)
                fmt.setFontWeight(QFont.Bold)
            elif level == 3:
                fmt.setFontPointSize(16)
                fmt.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(fmt)
        else:
            # Insert heading text at cursor position
            cursor.insertText(f"Heading {level}")
            # Select the inserted text and apply formatting
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(f"Heading {level}"))
            fmt = QTextCharFormat()
            if level == 2:
                fmt.setFontPointSize(18)
                fmt.setFontWeight(QFont.Bold)
            elif level == 3:
                fmt.setFontPointSize(16)
                fmt.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(fmt)
            # Move cursor to end
            cursor.movePosition(QTextCursor.End)
            self.content_input.setTextCursor(cursor)
    
    def _insert_link(self):
        """Insert or edit a link"""
        cursor = self.content_input.textCursor()
        selected_text = cursor.selectedText()
        
        # Check if cursor is on an existing link
        char_format = cursor.charFormat()
        is_link = char_format.isAnchor()
        existing_url = ""
        if is_link:
            existing_url = char_format.anchorHref()
        
        # Show dialog to get URL
        url, ok = QInputDialog.getText(
            self, "Insert Link",
            "Enter URL:",
            text=existing_url if existing_url else "https://"
        )
        
        if ok and url:
            # If no text selected, use the URL as text
            if not selected_text:
                selected_text = url
            
            # Create link format - preserve current font size
            current_format = cursor.charFormat()
            fmt = QTextCharFormat()
            fmt.setAnchor(True)
            fmt.setAnchorHref(url)
            fmt.setForeground(QColor(0, 102, 204))  # Blue color for links
            fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            # Preserve font size from current text
            if current_format.fontPointSize() > 0:
                fmt.setFontPointSize(current_format.fontPointSize())
            else:
                # Use default size if not set
                fmt.setFontPointSize(11)
            
            # Insert link
            cursor.insertText(selected_text, fmt)
    
    def _update_format_buttons(self):
        """Update format buttons based on current cursor position"""
        cursor = self.content_input.textCursor()
        char_format = cursor.charFormat()
        
        # Update bold button
        self.bold_btn.setChecked(char_format.fontWeight() == QFont.Bold)
        
        # Update italic button
        self.italic_btn.setChecked(char_format.fontItalic())
        
        # Update underline button
        self.underline_btn.setChecked(char_format.underlineStyle() != QTextCharFormat.NoUnderline)
    
    def _format_content_with_prefix(self, html_content: str, publish_date: Optional[QDateTime] = None, use_custom_author: bool = False, author_name: str = "") -> str:
        """Format HTML content with date/time prefix, bold first sentence, and author signature.
        
        Format: [Bold: dd.mm.yyyy - HH:mm - first sentence.] rest of content
        Content preserves HTML formatting and is aligned to left.
        Appends blank line and author signature [FirstInitial.LastInitial]
        """
        import re
        
        # Get publication date (use current date/time if not scheduled)
        if publish_date is None or not publish_date.isValid():
            publish_date = QDateTime.currentDateTime()
        
        # Format date as dd.mm.yyyy
        date_str = publish_date.date().toString("dd.MM.yyyy")
        # Format time as HH:mm
        time_str = publish_date.time().toString("HH:mm")
        
        # Clean up the HTML content (remove QTextEdit's default HTML wrapper if present)
        # QTextEdit.toHtml() wraps content in <html><head>...</head><body>...</body></html>
        # Also remove any style tags and CSS
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            html_content = body_match.group(1).strip()
        
        # Remove style tags and their content
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove any CSS rules that might appear as text in the content
        # Pattern matches CSS rules like "p, li { white-space: pre-wrap; }"
        # Remove from anywhere in the content
        html_content = re.sub(r'p,\s*li\s*\{\s*white-space:\s*pre-wrap;\s*\}', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'[a-zA-Z0-9\s,:\{\}\-]+white-space[^<}]*[;}]?\s*', '', html_content)
        
        # Clean up any remaining style attributes that might contain unwanted CSS
        html_content = re.sub(r'style="[^"]*white-space[^"]*"', '', html_content)
        
        # Remove any standalone CSS text that might have slipped through
        # This handles cases where CSS appears as plain text between tags
        html_content = re.sub(r'>\s*[a-zA-Z0-9\s,:\{\}\-]+white-space[^<}]*[;}]?\s*<', '><', html_content)
        
        # Clean up extra whitespace that might remain (but preserve newlines between tags)
        # Only collapse multiple spaces/tabs into single space, but keep structure
        html_content = re.sub(r'[ \t]+', ' ', html_content)
        html_content = html_content.strip()
        
        # Remove ALL style attributes from HTML tags (keep only simple HTML tags)
        # This ensures WordPress uses its default styling, not inline styles
        html_content = re.sub(r'\s+style="[^"]*"', '', html_content)
        html_content = re.sub(r'\s+style=\'[^\']*\'', '', html_content)
        
        # Also remove other Qt-specific attributes that might interfere
        html_content = re.sub(r'\s+-qt-[^=]*="[^"]*"', '', html_content)
        
        # Extract first sentence from HTML (strip HTML tags for finding period)
        # Remove HTML tags temporarily to find first sentence
        text_only = re.sub(r'<[^>]+>', '', html_content).strip()
        first_period_idx = text_only.find('.')
        
        if first_period_idx > 0:
            # Extract first sentence text
            first_sentence_text = text_only[:first_period_idx + 1].strip()
            
            # Find the first sentence in the HTML (preserving its formatting)
            # We'll try to find the first sentence by matching text content
            # This is approximate - we'll prepend the prefix with the first sentence
            prefix_html = f'<strong>{date_str} - {time_str} - {first_sentence_text}</strong>'
            
            # Wrap everything in a paragraph with left alignment
            # If content already starts with <p>, we'll wrap it differently
            if html_content.strip().startswith('<p'):
                # Content already has paragraph tags
                # Insert prefix at the beginning of the first paragraph
                html_content = re.sub(r'(<p[^>]*>)', r'\1' + prefix_html + ' ', html_content, count=1)
                # Add left alignment to first paragraph if not present
                html_content = re.sub(r'(<p)([^>]*>)', r'<p style="text-align: left;"\2', html_content, count=1)
            else:
                # Wrap in paragraph with prefix
                formatted_content = f'<p style="text-align: left;">{prefix_html} {html_content}</p>'
                html_content = formatted_content
        else:
            # No period found, just prepend prefix
            prefix_html = f'<strong>{date_str} - {time_str} - </strong>'
            
            if html_content.strip().startswith('<p'):
                # Insert prefix at the beginning of the first paragraph
                html_content = re.sub(r'(<p[^>]*>)', r'\1' + prefix_html, html_content, count=1)
                # Add left alignment to first paragraph if not present
                html_content = re.sub(r'(<p)([^>]*>)', r'<p style="text-align: left;"\2', html_content, count=1)
            else:
                # Wrap in paragraph with prefix
                formatted_content = f'<p style="text-align: left;">{prefix_html}{html_content}</p>'
                html_content = formatted_content
        
        # Get author signature
        if use_custom_author and author_name.strip():
            # Extract initials from author name (format: "First Last" -> "F.L")
            name_parts = author_name.strip().split()
            if len(name_parts) >= 2:
                first_initial = name_parts[0][0].upper()
                last_initial = name_parts[-1][0].upper()
                author_signature = f"[{first_initial}.{last_initial}]"
            elif len(name_parts) == 1:
                # Only one name, use first letter twice or just first letter
                first_initial = name_parts[0][0].upper()
                author_signature = f"[{first_initial}.{first_initial}]"
            else:
                author_signature = "[A.A]"
        else:
            # Use default Redazione signature
            author_signature = "[Redazione FVG.news COED Assistant]"
        
        # Append blank line (single <br>) and author signature
        html_content += '<br>' + author_signature
        
        # Append empty row after signature
        html_content += '<br>'
        
        # Append WhatsApp channel text with link (smaller and bold)
        # Use <small> tag for smaller text and <strong> for bold
        whatsapp_text = '<small><strong>L\'informazione locale, prima di tutti e sempre con te. Scopri il nostro canale WhatsApp: <a href="https://whatsapp.com/channel/0029Vb6Cp5SBlHpcDzjHGB1J">https://whatsapp.com/channel/0029Vb6Cp5SBlHpcDzjHGB1J</a></strong></small>'
        html_content += whatsapp_text
        
        return html_content
    
    def _on_custom_author_toggled(self, checked):
        """Enable/disable custom author fields when checkbox is toggled"""
        self.use_custom_author = checked
        self.custom_author_name_input.setEnabled(checked)
        self.custom_author_password_input.setEnabled(checked)
        if not checked:
            self.custom_author_name_input.clear()
            self.custom_author_password_input.clear()
    
    def _update_word_count(self):
        """Update word and character count label (counts plain text, ignoring HTML)"""
        content = self.content_input.toPlainText()
        words = len(content.split())
        characters = len(content)
        self.word_count_label.setText(f"Words: {words} | Characters: {characters}")
    
    def _needs_miniorange_auth(self, site_url: str) -> bool:
        """Check if a site needs Miniorange authentication (Trieste)"""
        return "triesteallnews.it" in site_url.lower() or "www.triesteallnews.it" in site_url.lower()
    
    def _get_default_sites(self) -> List[Dict]:
        """Return default WordPress sites configuration (same as Image Resizer)"""
        return [
            {
                "name": "Trieste News",
                "site_url": "https://www.triesteallnews.it",  # Must use www for MiniOrange
                "username": "61kgHITprXR2",  # MiniOrange Client ID (used as Basic Auth username)
                "app_password": "GZ8706mxMfgMitqVnD3uBpf1",  # MiniOrange Client Secret (used as Basic Auth password)
                "miniorange": True,  # Mark as requiring Miniorange authentication
                "hardcoded": True,  # Mark as hardcoded - credentials cannot be changed via UI
            },
            {
                "name": "Gorizia Oggi",
                "site_url": "https://goriziaoggi.news",
                "username": "goriziaNews",  # Hardcoded username (COED Post Editor)
                "app_password": "oNhy TVJx uavO 1bvc f2Ol ts3g",  # Hardcoded Application Password (COED Post Editor)
                "hardcoded": True,  # Mark as hardcoded - credentials cannot be changed via UI
            },
            {
                "name": "Udine Oggi",
                "site_url": "https://udineoggi.news",
                "username": "udineNews",  # Hardcoded username
                "app_password": "9q7M ioUs j3ov F4WW fUqE h7F7",  # Hardcoded Application Password
                "hardcoded": True,  # Mark as hardcoded - credentials cannot be changed via UI
            },
            {
                "name": "Venezia Orientale",
                "site_url": "https://veneziaorientale.news",
                "username": "redazioneVeneto",  # Hardcoded username (COED Post Editor)
                "app_password": "5wDS wPib mOrP 04do dyYU VAcY",  # Hardcoded Application Password (COED Post Editor)
                "hardcoded": True,  # Mark as hardcoded - credentials cannot be changed via UI
            },
        ]
    
    def _load_wp_settings(self):
        """Load WordPress sites from settings (shared with Image Resizer)"""
        try:
            path = get_settings_path()
            if os.path.exists(path):
                with open(path, "r") as f:
                    cfg = json.load(f)
                    if "sites" in cfg and isinstance(cfg["sites"], list) and len(cfg["sites"]) > 0:
                        self.wp_sites = cfg["sites"]
                        # Restore hardcoded credentials for protected sites
                        default_sites = self._get_default_sites()
                        for default_site in default_sites:
                            if default_site.get("hardcoded", False):
                                # Find matching site by URL and restore hardcoded credentials
                                for i, saved_site in enumerate(self.wp_sites):
                                    if saved_site.get("site_url") == default_site.get("site_url"):
                                        # Always restore hardcoded credentials (overwrite any user changes)
                                        self.wp_sites[i]["username"] = default_site["username"]
                                        self.wp_sites[i]["app_password"] = default_site["app_password"]
                                        self.wp_sites[i]["hardcoded"] = True
                                        # Also update name to match default (in case it changed)
                                        self.wp_sites[i]["name"] = default_site["name"]
                                        # Update miniorange flag if present
                                        if "miniorange" in default_site:
                                            self.wp_sites[i]["miniorange"] = default_site["miniorange"]
                                        break
                                else:
                                    # Site not found in saved sites, add it from defaults
                                    self.wp_sites.append(default_site.copy())
                        
                        # Ensure we have all default sites (merge with defaults)
                        default_urls = {s.get("site_url"): s for s in default_sites}
                        saved_urls = {s.get("site_url"): s for s in self.wp_sites}
                        # Add any missing default sites
                        for url, default_site in default_urls.items():
                            if url not in saved_urls:
                                self.wp_sites.append(default_site.copy())
                        
                        # Maintain correct order: Trieste, Gorizia, Udine, Venezia
                        ordered_sites = []
                        default_order = [s.get("site_url") for s in self._get_default_sites()]
                        for url in default_order:
                            for site in self.wp_sites:
                                if site.get("site_url") == url:
                                    ordered_sites.append(site)
                                    break
                        # Add any extra sites not in defaults at the end
                        for site in self.wp_sites:
                            if site.get("site_url") not in default_order:
                                ordered_sites.append(site)
                        self.wp_sites = ordered_sites
                        
                        # Load last selected site indices (for multi-site publishing)
                        self.last_selected_site_indices = cfg.get("last_selected_site_indices", [])
                        # Validate indices are still valid
                        self.last_selected_site_indices = [i for i in self.last_selected_site_indices if i < len(self.wp_sites)]
                        
                        # If no saved selection, don't select any by default (user must choose)
                        if not self.last_selected_site_indices:
                            self.current_site_index = 0 if len(self.wp_sites) > 0 else -1
                        else:
                            self.current_site_index = self.last_selected_site_indices[0]
                        
                        # Save merged sites
                        self._save_wp_settings()
                    else:
                        # No sites configured, use defaults
                        self.wp_sites = self._get_default_sites()
                        self.current_site_index = -1  # No default selection
                        self.last_selected_site_indices = []
                        self._save_wp_settings()
            else:
                # Settings file doesn't exist, create with defaults
                self.wp_sites = self._get_default_sites()
                self.current_site_index = -1  # No default selection
                self.last_selected_site_indices = []
                self._save_wp_settings()
        except Exception as e:
            print(f"Error loading WP settings: {e}")
            import traceback
            traceback.print_exc()
            # On error, initialize with defaults
            self.wp_sites = self._get_default_sites()
            self.current_site_index = -1  # No default selection
            self.last_selected_site_indices = []
    
    def _update_site_checkboxes(self, layout):
        """Update site selector checkboxes"""
        # Clear existing checkboxes
        for checkbox in self.site_checkboxes:
            checkbox.setParent(None)
        self.site_checkboxes.clear()
        
        # Create checkboxes for each site
        for i, site in enumerate(self.wp_sites):
            name = site.get("name", f"Site {i+1}")
            url = site.get("site_url", "")
            display = f"{name}"
            if url:
                domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                display += f" ({domain})"
            
            checkbox = QCheckBox(display)
            # Use saved selection, or no selection by default
            default_selected = i in self.last_selected_site_indices if hasattr(self, 'last_selected_site_indices') and self.last_selected_site_indices else False
            checkbox.setChecked(default_selected)
            if default_selected and self.current_site_index < 0:
                self.current_site_index = i
            checkbox.stateChanged.connect(self._on_site_selection_changed)
            self.site_checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        if len(self.wp_sites) == 0:
            no_sites_label = QLabel("(No sites configured)")
            no_sites_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_sites_label)
    
    def _on_site_selection_changed(self):
        """Handle site checkbox selection change"""
        selected_indices = self._get_selected_site_indices()
        if len(selected_indices) > 0:
            self.current_site_index = selected_indices[0]  # Use first selected for default
            # Save last selected indices
            self.last_selected_site_indices = selected_indices
            self._save_wp_settings()
            site_names = [self.wp_sites[i].get("name", "Site") for i in selected_indices]
            if len(selected_indices) == 1:
                self.statusBar().showMessage(f"Selected site: {site_names[0]}")
            else:
                self.statusBar().showMessage(f"Selected {len(selected_indices)} sites: {', '.join(site_names)}")
        else:
            self.statusBar().showMessage("No sites selected")
    
    def _get_selected_site_indices(self) -> List[int]:
        """Get list of selected site indices"""
        selected = []
        for i, checkbox in enumerate(self.site_checkboxes):
            if checkbox.isChecked():
                selected.append(i)
        return selected
    
    def _get_sites_scroll_layout(self):
        """Get the sites scroll area layout (for updating checkboxes)"""
        # Find the sites scroll area widget
        for widget in self.findChildren(QScrollArea):
            if widget.maximumHeight() == 120:  # Identify by max height
                scroll_widget = widget.widget()
                if scroll_widget:
                    layout = scroll_widget.layout()
                    if layout:
                        return layout
        return None
    
    def _new_post(self):
        """Create a new post (clear all fields)"""
        reply = QMessageBox.question(
            self, "New Post",
            "Create a new post? Current content will be cleared.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.title_input.clear()
            self.content_input.clear()
            self.excerpt_input.clear()
            self.categories_combo.setCurrentIndex(0)  # Reset to first category
            self.tags_input.clear()
            self._remove_featured_image()
            self.status_combo.setCurrentText("draft")
            self.schedule_checkbox.setChecked(False)
            self.schedule_calendar.setSelectedDate(QDate.currentDate().addDays(1))
            self.schedule_time.setTime(QTime.currentTime())
            self.use_custom_author_checkbox.setChecked(False)
            self.custom_author_name_input.clear()
            self.custom_author_password_input.clear()
            # Reset site checkboxes - select first site by default
            for i, checkbox in enumerate(self.site_checkboxes):
                checkbox.setChecked(i == 0 if len(self.site_checkboxes) > 0 else False)
            self.current_draft_path = None
            self.statusBar().showMessage("New post created")
    
    def _save_draft(self):
        """Save current post as draft locally"""
        draft_data = {
            "title": self.title_input.text(),
            "content": self.content_input.toHtml(),
            "excerpt": self.excerpt_input.toPlainText(),
            "category": self.categories_combo.currentText(),  # Selected category from dropdown
            "tags": self.tags_input.text(),
            "featured_image_media_id": self.featured_image_media_id,
            "featured_image_path": self.featured_image_path,  # Save path for reference
            "status": self.status_combo.currentText(),
            "scheduled": self.schedule_checkbox.isChecked(),
            "schedule_datetime": self._get_schedule_datetime().toString(Qt.ISODate) if self.schedule_checkbox.isChecked() else None,
            "site_index": self.current_site_index,
            "use_custom_author": self.use_custom_author_checkbox.isChecked(),
            "custom_author_name": self.custom_author_name_input.text(),
            "custom_author_password": self.custom_author_password_input.text(),
            "selected_site_indices": self._get_selected_site_indices(),  # Save selected sites
            "saved_at": datetime.now().isoformat()
        }
        
        # Generate filename from title or use timestamp
        if draft_data["title"]:
            filename = draft_data["title"][:50].replace(" ", "_").replace("/", "_") + ".json"
            # Remove invalid filename characters
            invalid_chars = '<>:"\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, "_")
        else:
            filename = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        draft_path = os.path.join(get_drafts_path(), filename)
        
        try:
            with open(draft_path, "w", encoding="utf-8") as f:
                json.dump(draft_data, f, indent=2, ensure_ascii=False)
            self.current_draft_path = draft_path
            self.statusBar().showMessage(f"Draft saved: {filename}")
            QMessageBox.information(self, "Draft Saved", f"Draft saved successfully:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save draft:\n{str(e)}")
    
    def _load_draft(self):
        """Load a draft from file"""
        draft_path, _ = QFileDialog.getOpenFileName(
            self, "Load Draft", get_drafts_path(), "JSON Files (*.json);;All Files (*)"
        )
        
        if not draft_path:
            return
        
        try:
            with open(draft_path, "r", encoding="utf-8") as f:
                draft_data = json.load(f)
            
            self.title_input.setText(draft_data.get("title", ""))
            # Load content - support both HTML and plain text (for backward compatibility)
            content = draft_data.get("content", "")
            if content.strip().startswith('<'):
                # HTML content
                self.content_input.setHtml(content)
            else:
                # Plain text (legacy)
                self.content_input.setPlainText(content)
            self.excerpt_input.setPlainText(draft_data.get("excerpt", ""))
            # Load category (support both old "categories" and new "category" format)
            if "category" in draft_data:
                category = draft_data.get("category", "")
                index = self.categories_combo.findText(category)
                if index >= 0:
                    self.categories_combo.setCurrentIndex(index)
            elif "categories" in draft_data:
                # Legacy support for old comma-separated format
                categories = draft_data.get("categories", "")
                if categories:
                    first_cat = categories.split(",")[0].strip()
                    index = self.categories_combo.findText(first_cat)
                    if index >= 0:
                        self.categories_combo.setCurrentIndex(index)
            
            self.tags_input.setText(draft_data.get("tags", ""))
            
            # Load featured image if available
            if "featured_image_path" in draft_data and draft_data["featured_image_path"]:
                image_path = draft_data["featured_image_path"]
                if os.path.exists(image_path):
                    self._load_featured_image_preview(image_path)
                    self.featured_image_path = image_path
                    self.upload_image_btn.setEnabled(True)
                    self.remove_image_btn.setEnabled(True)
            
            if "featured_image_media_id" in draft_data:
                self.featured_image_media_id = draft_data.get("featured_image_media_id", 0)
                if self.featured_image_media_id > 0:
                    if not self.featured_image_info.text():  # Only set if not already set by image path
                        self.featured_image_info.setText(f"Media ID: {self.featured_image_media_id} (from draft)")
                    else:
                        self.featured_image_info.setText(
                            f"{self.featured_image_info.text()} | Media ID: {self.featured_image_media_id}"
                        )
                    self.upload_image_btn.setEnabled(False)  # Already uploaded
            
            self.status_combo.setCurrentText(draft_data.get("status", "draft"))
            
            scheduled = draft_data.get("scheduled", False)
            self.schedule_checkbox.setChecked(scheduled)
            if scheduled and draft_data.get("schedule_datetime"):
                schedule_dt = QDateTime.fromString(draft_data["schedule_datetime"], Qt.ISODate)
                if schedule_dt.isValid():
                    self.schedule_calendar.setSelectedDate(schedule_dt.date())
                    self.schedule_time.setTime(schedule_dt.time())
            
            # Load selected sites (support both old single site and new multi-site)
            if "selected_site_indices" in draft_data:
                selected_indices = draft_data.get("selected_site_indices", [])
                for i, checkbox in enumerate(self.site_checkboxes):
                    checkbox.setChecked(i in selected_indices)
            elif "site_index" in draft_data:
                # Legacy support for old single site selection
                site_idx = draft_data.get("site_index", 0)
                for i, checkbox in enumerate(self.site_checkboxes):
                    checkbox.setChecked(i == site_idx)
            
            # Load custom author settings if available
            if "use_custom_author" in draft_data:
                self.use_custom_author_checkbox.setChecked(draft_data.get("use_custom_author", False))
                if draft_data.get("custom_author_name"):
                    self.custom_author_name_input.setText(draft_data.get("custom_author_name", ""))
                if draft_data.get("custom_author_password"):
                    self.custom_author_password_input.setText(draft_data.get("custom_author_password", ""))
            
            self.current_draft_path = draft_path
            self.statusBar().showMessage(f"Loaded draft: {os.path.basename(draft_path)}")
            QMessageBox.information(self, "Draft Loaded", "Draft loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load draft:\n{str(e)}")
    
    def _open_settings(self):
        """Open WordPress settings (same as Image Resizer)"""
        # Import settings dialog from image_resizer_macos_wp if available
        try:
            from image_resizer_macos_wp import WPSettingsDialog
            dlg = WPSettingsDialog(self, self.wp_sites.copy(), self.current_site_index)
            if dlg.exec_() == dlg.Accepted:
                self.wp_sites = dlg.get_sites()
                self.current_site_index = dlg.get_current_index()
                # Update site checkboxes
                # Find and update site checkboxes
                sites_scroll_layout = self._get_sites_scroll_layout()
                if sites_scroll_layout:
                    self._update_site_checkboxes(sites_scroll_layout)
                # Save settings
                self._save_wp_settings()
        except ImportError:
            QMessageBox.information(
                self, "Settings",
                "WordPress settings can be configured in Image Resizer app.\n\n"
                "Settings are shared between both applications."
            )
    
    def _save_wp_settings(self):
        """Save WordPress settings"""
        try:
            path = get_settings_path()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump({
                    "sites": self.wp_sites,
                    "current_index": self.current_site_index,
                    "last_selected_site_indices": getattr(self, 'last_selected_site_indices', []),
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving WP settings: {e}")
            import traceback
            traceback.print_exc()
    
    def _publish_post(self):
        """Publish post to WordPress via REST API (supports multiple sites)"""
        # Get selected sites
        selected_site_indices = self._get_selected_site_indices()
        
        if not selected_site_indices:
            QMessageBox.warning(
                self, "No Site Selected",
                "Please select at least one WordPress site to publish to.\n\n"
                "Check one or more sites in the 'WordPress Sites' section."
            )
            return
        
        if not self.wp_sites or len(self.wp_sites) == 0:
            QMessageBox.warning(
                self, "No Sites Configured",
                "Please configure WordPress sites first.\n\n"
                "Go to Settings to add sites."
            )
            return
        
        # Validate post data
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Title Required", "Please enter a title for the post.")
            return
        
        # Get content as HTML and process it
        html_content = self.content_input.toHtml().strip()
        # Check if content is empty (QTextEdit.toHtml() returns basic HTML even for empty content)
        plain_text = self.content_input.toPlainText().strip()
        if not plain_text:
            QMessageBox.warning(self, "Content Required", "Please enter content for the post.")
            return
        
        # Get publication date (use schedule date if scheduled, otherwise current date/time)
        publish_date = None
        if self.schedule_checkbox.isChecked():
            publish_date = self._get_schedule_datetime()
        else:
            publish_date = QDateTime.currentDateTime()
        
        # Get author information for signature
        use_custom_author = self.use_custom_author_checkbox.isChecked()
        author_name = self.custom_author_name_input.text().strip() if use_custom_author else ""
        
        # Format content with prefix (date, time, bold first sentence, left-aligned)
        # Pass HTML content to preserve formatting
        formatted_content = self._format_content_with_prefix(html_content, publish_date, use_custom_author, author_name)
        
        # Prepare post data
        post_data = {
            "title": title,
            "content": formatted_content,
            "status": self.status_combo.currentText(),
        }
        
        # Add optional fields
        excerpt = self.excerpt_input.toPlainText().strip()
        if excerpt:
            post_data["excerpt"] = excerpt
        
        # Add category (single category from dropdown)
        selected_category = self.categories_combo.currentText()
        if selected_category:
            # We'll get/create category ID for each site separately
            pass  # Will be handled per-site in the loop
        
        # Add tags (will be handled per-site since tags might differ)
        tags_str = self.tags_input.text().strip()
        
        # Validate tags count (min 5, max 7)
        if tags_str:
            tag_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
            if len(tag_list) < 5:
                QMessageBox.warning(
                    self, "Not Enough Tags",
                    f"You have entered {len(tag_list)} tag(s).\n\n"
                    "Please enter at least 5 tags (comma-separated)."
                )
                return
            elif len(tag_list) > 7:
                QMessageBox.warning(
                    self, "Too Many Tags",
                    f"You have entered {len(tag_list)} tag(s).\n\n"
                    "Please enter a maximum of 7 tags (comma-separated)."
                )
                return
        
        # Featured images will be uploaded separately to each site during the loop
        # (since media IDs are site-specific)
        
        # Add schedule date if scheduled
        if self.schedule_checkbox.isChecked():
            schedule_dt = self._get_schedule_datetime()
            post_data["date"] = schedule_dt.toString(Qt.ISODate)
            post_data["status"] = "future"
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.publish_btn.setEnabled(False)
        QApplication.processEvents()
        
        # Publish to all selected sites
        results = []
        selected_category = self.categories_combo.currentText()
        
        for site_idx in selected_site_indices:
            current_site = self.wp_sites[site_idx]
            site_url = current_site.get("site_url", "").strip()
            site_name = current_site.get("name", "Site")
            
            # Determine which credentials to use for this site
            if self.use_custom_author_checkbox.isChecked():
                username = self.custom_author_name_input.text().strip()
                app_password = self.custom_author_password_input.text().strip()
                
                if not (username and app_password):
                    results.append({
                        "site": site_name,
                        "success": False,
                        "error": "Custom author credentials not provided"
                    })
                    continue
            else:
                username = current_site.get("username", "").strip()
                app_password = current_site.get("app_password", "").strip()
                
                if not (site_url and username and app_password):
                    # Provide more specific error message
                    if not app_password:
                        error_msg = f"Password not configured. Please configure the MiniOrange API password in Settings."
                    elif not username:
                        error_msg = "Username not configured. Please configure in Settings."
                    else:
                        error_msg = "Site not properly configured. Please check Settings."
                    
                    results.append({
                        "site": site_name,
                        "success": False,
                        "error": error_msg
                    })
                    continue
            
            # Create post data copy for this site
            site_post_data = post_data.copy()
            
            # Get/create category ID for this site (use Miniorange session if needed)
            if selected_category:
                category_ids = self._get_or_create_categories(site_url, username, app_password, selected_category)
                if category_ids:
                    site_post_data["categories"] = category_ids
            
            # Add tags for this site (use Miniorange session if needed)
            if tags_str:
                tag_ids = self._get_or_create_tags(site_url, username, app_password, tags_str)
                if tag_ids:
                    site_post_data["tags"] = tag_ids
            
            # Add featured image - upload separately for each site if needed
            # Featured images are site-specific, so we need to upload to each site
            if self.featured_image_path and os.path.exists(self.featured_image_path):
                # Upload featured image to this site
                if self.use_custom_author_checkbox.isChecked():
                    img_username = self.custom_author_name_input.text().strip()
                    img_password = self.custom_author_password_input.text().strip()
                else:
                    img_username = username
                    img_password = app_password
                
                if img_username and img_password:
                    # Show progress bar for image upload
                    self.progress_bar.setVisible(True)
                    self.statusBar().showMessage(f"Uploading featured image to {site_name}...")
                    QApplication.processEvents()
                    
                    # Upload featured image to this specific site
                    media_id = self._upload_featured_image_sync_for_site(site_url, img_username, img_password)
                    
                    # Hide progress bar after upload (if not publishing to more sites)
                    if site_idx == selected_site_indices[-1]:  # Last site
                        self.progress_bar.setVisible(False)
                    QApplication.processEvents()
                    
                    if media_id:
                        site_post_data["featured_media"] = media_id
                        print(f"DEBUG: Featured image uploaded to {site_name}, Media ID: {media_id}")
                    else:
                        print(f"DEBUG: Failed to upload featured image to {site_name}")
            
            # Publish to this WordPress site
            try:
                api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/posts"
                
                # Clean up Application Password (remove spaces - WordPress expects no spaces in auth)
                # This applies to both WordPress Application Passwords and MiniOrange Basic Auth
                clean_password = app_password.replace(" ", "")
                
                headers = {
                    'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',  # May help with security plugins
                    'X-ImageResizer-Client': 'WordPressPostEditor/1.0',  # Match Image Resizer header
                }
                
                self.statusBar().showMessage(f"Publishing to {site_name}...")
                QApplication.processEvents()
                
                # For Miniorange-protected sites, use Basic Auth (same as standard WordPress)
                # Miniorange API accepts Basic Auth with username and password
                # Use allow_redirects=True like Image Resizer does
                resp = requests.post(
                    api_url,
                    auth=HTTPBasicAuth(username, clean_password),
                    json=site_post_data,
                    headers=headers,
                    timeout=30,
                    allow_redirects=True  # Allow redirects in case WordPress/MiniOrange redirects
                )
                
                if resp.status_code == 201:
                    post_data_returned = resp.json()
                    post_id = post_data_returned.get("id")
                    post_link = post_data_returned.get("link", "")
                    results.append({
                        "site": site_name,
                        "success": True,
                        "post_id": post_id,
                        "link": post_link,
                        "status": post_data_returned.get("status", "unknown")
                    })
                elif resp.status_code == 401:
                    # Get more detailed error message
                    error_msg = "Authentication failed (401)"
                    try:
                        error_json = resp.json()
                        if "message" in error_json:
                            error_msg = f"Authentication failed (401): {error_json['message']}"
                        elif "code" in error_json:
                            error_msg = f"Authentication failed (401): {error_json.get('message', error_json.get('code', 'Unauthorized'))}"
                        
                        # Check for MiniOrange-specific errors
                        if "MISSING_AUTHORIZATION_HEADER" in str(error_json):
                            error_msg = (
                                "MiniOrange authentication failed (401): Authorization header not received.\n\n"
                                "Possible causes:\n"
                                "1. MiniOrange plugin may require Editor or Administrator role (not Author)\n"
                                "2. MiniOrange configuration may need to whitelist the User-Agent or headers\n"
                                "3. Check MiniOrange settings to allow REST API access for authenticated users\n"
                                "4. Verify credentials are correct in Settings"
                            )
                        # Check for permission errors (user authenticated but lacks permissions)
                        elif error_json.get("code") == "rest_cannot_create" or "permessi" in error_msg.lower() or "permission" in error_msg.lower():
                            if self._needs_miniorange_auth(site_url):
                                error_msg = (
                                    "MiniOrange: User lacks permission to create posts (401)\n\n"
                                    "The Client ID authenticates successfully, but the WordPress user it maps to doesn't have permission to create posts.\n\n"
                                    "Solution:\n"
                                    "1. Go to MiniOrange plugin settings in WordPress\n"
                                    "2. Find the Client ID: 61kgHITprXR2\n"
                                    "3. Ensure it's mapped to a WordPress user with Editor or Administrator role\n"
                                    "4. The user must have 'publish_posts' capability\n\n"
                                    "Note: MiniOrange Client IDs must be associated with WordPress users that have appropriate permissions."
                                )
                    except:
                        # If not JSON, try to get text
                        if resp.text:
                            error_msg = f"Authentication failed (401): {resp.text[:200]}"
                            if "MISSING_AUTHORIZATION_HEADER" in resp.text:
                                error_msg = (
                                    "MiniOrange authentication failed: Authorization header not received.\n\n"
                                    "The MiniOrange plugin may require:\n"
                                    "- Editor or Administrator role (not Author)\n"
                                    "- Configuration to allow REST API access\n"
                                    "- User-Agent or headers whitelisting"
                                )
                            elif "permessi" in error_msg.lower() or "permission" in error_msg.lower():
                                if self._needs_miniorange_auth(site_url):
                                    error_msg = (
                                        "MiniOrange: User lacks permission to create posts\n\n"
                                        "The Client ID authenticates, but the mapped WordPress user needs Editor or Administrator role.\n"
                                        "Configure this in MiniOrange plugin settings."
                                    )
                    
                    results.append({
                        "site": site_name,
                        "success": False,
                        "error": error_msg
                    })
                elif resp.status_code == 403:
                    results.append({
                        "site": site_name,
                        "success": False,
                        "error": "Permission denied (403)"
                    })
                else:
                    error_msg = resp.text[:200]
                    try:
                        error_json = resp.json()
                        if "message" in error_json:
                            error_msg = error_json["message"]
                    except:
                        pass
                    results.append({
                        "site": site_name,
                        "success": False,
                        "error": f"HTTP {resp.status_code}: {error_msg}"
                    })
            
            except requests.exceptions.Timeout:
                results.append({
                    "site": site_name,
                    "success": False,
                    "error": "Request timed out"
                })
            except requests.exceptions.ConnectionError:
                results.append({
                    "site": site_name,
                    "success": False,
                    "error": "Connection error"
                })
            except Exception as e:
                results.append({
                    "site": site_name,
                    "success": False,
                    "error": f"Error: {str(e)}"
                })
        
        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.publish_btn.setEnabled(True)
        
        # Display results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        if len(successful) > 0:
            success_msg = f"✅ Published to {len(successful)} site(s):\n\n"
            for r in successful:
                success_msg += f"• {r['site']}: Post ID {r['post_id']}\n"
                success_msg += f"  Link: {r['link']}\n\n"
            
            if len(failed) > 0:
                success_msg += f"\n❌ Failed on {len(failed)} site(s):\n\n"
                for r in failed:
                    success_msg += f"• {r['site']}: {r['error']}\n"
            
            QMessageBox.information(self, "Publish Results", success_msg)
            
            # Clear form if all published successfully
            if len(failed) == 0 and post_data.get("status") == "publish":
                self._new_post()
        else:
            # All failed
            error_msg = f"❌ Failed to publish to all {len(failed)} site(s):\n\n"
            for r in failed:
                error_msg += f"• {r['site']}: {r['error']}\n"
            
            QMessageBox.critical(self, "Publish Failed", error_msg)
    
    def _get_or_create_categories(self, site_url: str, username: str, app_password: str, category_name: str) -> List[int]:
        """Get a category by name (do not create). If not found, fallback to CRONACA."""
        category_ids = []
        category_name = category_name.strip()
        
        if not category_name:
            return []
        
        # For MiniOrange, don't remove spaces from password (might be different format)
        if self._needs_miniorange_auth(site_url):
            clean_password = app_password  # Keep password as-is for MiniOrange
        else:
            clean_password = app_password.replace(" ", "")  # Remove spaces for WordPress Application Passwords
        
        try:
            # Try to find existing category
            search_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/categories"
            
            headers = {
                'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
                'Accept': 'application/json',
            }
            if self._needs_miniorange_auth(site_url):
                headers['X-ImageResizer-Client'] = 'WordPressPostEditor/1.0'
            
            # Use Basic Auth for all sites (including Miniorange-protected)
            resp = requests.get(
                search_url,
                auth=HTTPBasicAuth(username, clean_password),
                params={"search": category_name, "per_page": 100},
                headers=headers,
                timeout=10
            )
            
            if resp.status_code == 200:
                categories = resp.json()
                found = False
                for cat in categories:
                    if cat.get("name", "").lower() == category_name.lower():
                        category_ids.append(cat["id"])
                        found = True
                        break
                
                # If not found, fallback to CRONACA
                if not found:
                    print(f"Category '{category_name}' not found. Falling back to 'CRONACA'.")
                    for cat in categories:
                        if cat.get("name", "").lower() == "cronaca":
                            category_ids.append(cat["id"])
                            break
                    # If CRONACA also not found, try to get it by ID 1 (default uncategorized, but we'll use it)
                    if not category_ids:
                        print(f"Warning: 'CRONACA' category not found. Category assignment may fail.")
            else:
                print(f"Error searching for category '{category_name}': HTTP {resp.status_code}")
        except Exception as e:
            print(f"Error getting category '{category_name}': {e}")
        
        return category_ids
    
    def _get_or_create_tags(self, site_url: str, username: str, app_password: str, tags_str: str) -> List[int]:
        """Get or create tags and return their IDs"""
        tag_ids = []
        # Split by comma and clean up - handle both "tag1, tag2" and "tag1,tag2" formats
        tag_names = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        if not tag_names:
            return []
        
        print(f"DEBUG: Processing {len(tag_names)} tags: {tag_names}")
        
        # For MiniOrange, don't remove spaces from password (might be different format)
        if self._needs_miniorange_auth(site_url):
            clean_password = app_password  # Keep password as-is for MiniOrange
        else:
            clean_password = app_password.replace(" ", "")  # Remove spaces for WordPress Application Passwords
        
        headers = {
            'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
            'Accept': 'application/json',
        }
        if self._needs_miniorange_auth(site_url):
            headers['X-ImageResizer-Client'] = 'WordPressPostEditor/1.0'
        
        for tag_name in tag_names:
            try:
                tag_name_clean = tag_name.strip()
                if not tag_name_clean:
                    continue
                
                # First, try to find existing tag by name (exact match)
                search_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/tags"
                
                # Use Basic Auth for all sites (including Miniorange-protected)
                resp = requests.get(
                    search_url,
                    auth=HTTPBasicAuth(username, clean_password),
                    params={"search": tag_name_clean, "per_page": 100},
                    headers=headers,
                    timeout=10
                )
                
                if resp.status_code == 200:
                    tags = resp.json()
                    found = False
                    for tag in tags:
                        # Match by name (case-insensitive) or slug
                        tag_name_match = tag.get("name", "").strip()
                        tag_slug = tag.get("slug", "").strip()
                        if (tag_name_match.lower() == tag_name_clean.lower() or 
                            tag_slug.lower() == tag_name_clean.lower().replace(" ", "-")):
                            tag_ids.append(tag["id"])
                            found = True
                            print(f"DEBUG: Found existing tag '{tag_name_clean}' with ID {tag['id']}")
                            break
                    
                    if not found:
                        # Create new tag
                        create_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/tags"
                        
                        create_headers = {
                            'Content-Type': 'application/json',
                            'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
                            'Accept': 'application/json',
                        }
                        if self._needs_miniorange_auth(site_url):
                            create_headers['X-ImageResizer-Client'] = 'WordPressPostEditor/1.0'
                        
                        # Use Basic Auth for all sites (including Miniorange-protected)
                        create_resp = requests.post(
                            create_url,
                            auth=HTTPBasicAuth(username, clean_password),
                            json={"name": tag_name_clean},
                            headers=create_headers,
                            timeout=10
                        )
                        if create_resp.status_code == 201:
                            new_tag = create_resp.json()
                            tag_id = new_tag.get("id")
                            if tag_id:
                                tag_ids.append(tag_id)
                                print(f"DEBUG: Created new tag '{tag_name_clean}' with ID {tag_id}")
                        else:
                            print(f"DEBUG: Failed to create tag '{tag_name_clean}': HTTP {create_resp.status_code}")
                            try:
                                error_data = create_resp.json()
                                print(f"DEBUG: Error details: {error_data}")
                            except:
                                print(f"DEBUG: Error response: {create_resp.text[:200]}")
                else:
                    print(f"DEBUG: Failed to search for tag '{tag_name_clean}': HTTP {resp.status_code}")
            except Exception as e:
                print(f"Error getting/creating tag '{tag_name}': {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"DEBUG: Returning {len(tag_ids)} tag IDs: {tag_ids}")
        return tag_ids
    
    def _select_featured_image(self):
        """Select a featured image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Featured Image",
            "",
            "Image files (*.jpg *.jpeg *.png);;JPEG files (*.jpg *.jpeg);;PNG files (*.png);;All files (*.*)"
        )
        
        if not file_path:
            return
        
        # Validate file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png']:
            QMessageBox.warning(
                self, "Invalid File Type",
                "Only JPEG and PNG images are allowed.\n\n"
                f"Selected file: {os.path.basename(file_path)}\n"
                f"File type: {file_ext}"
            )
            return
        
        # Validate file size (130KB limit)
        file_size_kb = os.path.getsize(file_path) / 1024
        if file_size_kb > 130:
            QMessageBox.warning(
                self, "File Too Large",
                f"The image file size is {file_size_kb:.1f} KB, which exceeds the 130 KB limit.\n\n"
                "Please select a smaller image or compress it first.\n\n"
                "Tip: Use Image Resizer to reduce the file size before selecting."
            )
            return
        
        # Load and validate image
        try:
            img = Image.open(file_path)
            img.verify()  # Verify it's a valid image
            img = Image.open(file_path)  # Reopen after verify (verify closes the file)
            
            # Check image format
            if img.format not in ['JPEG', 'PNG']:
                QMessageBox.warning(
                    self, "Invalid Image Format",
                    f"Image format '{img.format}' is not supported.\n\n"
                    "Only JPEG and PNG images are allowed."
                )
                return
            
            # Success - load the image
            self._load_featured_image_preview(file_path)
            self.featured_image_path = file_path
            self.featured_image_media_id = 0  # Reset media ID (needs to be uploaded)
            self.upload_image_btn.setEnabled(True)
            self.remove_image_btn.setEnabled(True)
            
            # Update info
            width, height = img.size
            info_text = f"{os.path.basename(file_path)} | {width}x{height} px | {file_size_kb:.1f} KB | {img.format}"
            self.featured_image_info.setText(info_text)
            self.featured_image_info.setStyleSheet("color: #27ae60; font-size: 10px;")
            
            self.statusBar().showMessage(f"Image selected: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading Image",
                f"Failed to load image:\n{str(e)}"
            )
    
    def _load_featured_image_preview(self, file_path: str):
        """Load and display image preview"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.featured_image_preview.setText("Failed to load image preview")
                return
            
            # Scale to fit preview area (max 200px height, maintain aspect ratio)
            scaled_pixmap = pixmap.scaled(
                300, 200,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.featured_image_preview.setPixmap(scaled_pixmap)
            self.featured_image_preview.setStyleSheet("border: 2px solid #27ae60; background-color: #fff;")
        except Exception as e:
            self.featured_image_preview.setText(f"Error loading preview:\n{str(e)}")
    
    def _remove_featured_image(self):
        """Remove selected featured image"""
        self.featured_image_path = None
        self.featured_image_media_id = 0
        self.featured_image_preview.clear()
        self.featured_image_preview.setText("No image selected\n\nClick 'Select Image' to choose\nJPEG or PNG (max 130KB)")
        self.featured_image_preview.setStyleSheet("border: 2px dashed #ccc; background-color: #f9f9f9;")
        self.featured_image_info.setText("")
        self.upload_image_btn.setEnabled(False)
        self.remove_image_btn.setEnabled(False)
    
    def _upload_featured_image_sync_for_site(self, site_url: str, username: str, app_password: str) -> Optional[int]:
        """Upload featured image to a specific site with given credentials"""
        if not self.featured_image_path or not os.path.exists(self.featured_image_path):
            return None
        
        try:
            # Read image file
            with open(self.featured_image_path, 'rb') as f:
                image_data = f.read()
            
            file_ext = os.path.splitext(self.featured_image_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                mime = 'image/jpeg'
            elif file_ext == '.png':
                mime = 'image/png'
            else:
                return None
            
            filename = os.path.basename(self.featured_image_path)
            image_title = filename
            if self.title_input.text().strip():
                image_title = f"{self.title_input.text().strip()} - Featured Image"
            
            api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/media"
            
            # For MiniOrange, don't remove spaces from password (might be different format)
            if self._needs_miniorange_auth(site_url):
                clean_password = app_password  # Keep password as-is for MiniOrange
            else:
                clean_password = app_password.replace(" ", "")  # Remove spaces for WordPress Application Passwords
            
            headers = {
                'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-ImageResizer-Client': 'WordPressPostEditor/1.0',
            }
            
            files = {"file": (filename, image_data, mime)}
            fields = {
                "title": image_title,
                "description": f"Featured image for: {self.title_input.text().strip() or 'Post'}"
            }
            
            # Update status during upload (allow UI to update)
            self.statusBar().showMessage(f"Uploading {filename} ({len(image_data) / 1024:.1f} KB)...")
            QApplication.processEvents()
            
            # Use Basic Auth for all sites (including Miniorange-protected)
            resp = requests.post(
                api_url,
                auth=HTTPBasicAuth(username, clean_password),
                files=files,
                data=fields,
                headers=headers,
                timeout=45,
                allow_redirects=True  # Allow redirects like Image Resizer does
            )
            
            if resp.status_code == 201:
                media_data = resp.json()
                return media_data.get("id")
            return None
        except Exception as e:
            print(f"Error uploading image to {site_url}: {e}")
            return None
    
    def _upload_featured_image_sync(self) -> Optional[int]:
        """Upload featured image synchronously and return media ID (for use during publish)"""
        # Clear previous error
        self._last_upload_error = None
        
        if not self.featured_image_path or not os.path.exists(self.featured_image_path):
            self._last_upload_error = "Image file not found"
            print(f"DEBUG: Image file not found: {self.featured_image_path}")
            return None
        
        if not self.wp_sites or self.current_site_index >= len(self.wp_sites):
            self._last_upload_error = "No WordPress site configured"
            print("DEBUG: No WordPress site configured")
            return None
        
        current_site = self.wp_sites[self.current_site_index]
        site_url = current_site.get("site_url", "").strip()
        
        # Determine which credentials to use (same logic as publish)
        if self.use_custom_author_checkbox.isChecked():
            username = self.custom_author_name_input.text().strip()
            app_password = self.custom_author_password_input.text().strip()
        else:
            username = current_site.get("username", "").strip()
            app_password = current_site.get("app_password", "").strip()
        
        if not site_url:
            self._last_upload_error = "Site URL not configured"
            print("DEBUG: Site URL not configured")
            return None
        if not username:
            self._last_upload_error = "Username not configured"
            print("DEBUG: Username not configured")
            return None
        if not app_password:
            self._last_upload_error = "Application Password not configured"
            print("DEBUG: Application Password not configured")
            return None
        
        # Use the helper function
        return self._upload_featured_image_sync_for_site(site_url, username, app_password)
    
    def _upload_featured_image(self):
        """Upload featured image to WordPress media library (with UI feedback)"""
        if not self.featured_image_path or not os.path.exists(self.featured_image_path):
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return
        
        # Validate current site
        if not self.wp_sites or self.current_site_index >= len(self.wp_sites):
            QMessageBox.warning(
                self, "No Site",
                "Please configure a WordPress site first.\n\n"
                "Go to Settings to add a site."
            )
            return
        
        current_site = self.wp_sites[self.current_site_index]
        site_url = current_site.get("site_url", "").strip()
        
        # Determine which credentials to use
        if self.use_custom_author_checkbox.isChecked():
            username = self.custom_author_name_input.text().strip()
            app_password = self.custom_author_password_input.text().strip()
            
            if not (username and app_password):
                QMessageBox.warning(
                    self, "Custom Author Required",
                    "Please enter both Author Username and Application Password\n"
                    "to upload as a custom author.\n\n"
                    "Or uncheck 'Publish as custom author' to use the system user."
                )
                return
        else:
            username = current_site.get("username", "").strip()
            app_password = current_site.get("app_password", "").strip()
            
            if not (site_url and username and app_password):
                QMessageBox.warning(
                    self, "Site Not Configured",
                    f"Site '{current_site.get('name', 'Selected site')}' is not properly configured.\n\n"
                    "Please check that Site URL, Username, and Application Password are all set."
                )
                return
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.upload_image_btn.setEnabled(False)
        self.statusBar().showMessage("Reading image file...")
        QApplication.processEvents()
        
        try:
            # Read image file
            with open(self.featured_image_path, 'rb') as f:
                image_data = f.read()
            
            # Update status
            file_size_kb = len(image_data) / 1024
            self.statusBar().showMessage(f"Preparing to upload ({file_size_kb:.1f} KB)...")
            QApplication.processEvents()
            
            # Determine file extension and MIME type
            file_ext = os.path.splitext(self.featured_image_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                ext = 'jpg'
                mime = 'image/jpeg'
            elif file_ext == '.png':
                ext = 'png'
                mime = 'image/png'
            else:
                QMessageBox.warning(self, "Invalid Format", "Only JPEG and PNG images are supported.")
                self.progress_bar.setVisible(False)
                self.upload_image_btn.setEnabled(True)
                return
            
            # Generate filename
            filename = os.path.basename(self.featured_image_path)
            if not filename.endswith(ext):
                filename = f"{os.path.splitext(filename)[0]}.{ext}"
            
            # Use post title for image title if available
            image_title = filename
            if self.title_input.text().strip():
                image_title = f"{self.title_input.text().strip()} - Featured Image"
            
            # Upload to WordPress
            api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/media"
            clean_password = app_password.replace(" ", "")
            
            headers = {
                'User-Agent': 'WordPressPostEditor/1.0 (WordPress REST API Client)',
                'Accept': 'application/json',
                'X-ImageResizer-Client': 'WordPressPostEditor/1.0',
            }
            
            files = {"file": (filename, image_data, mime)}
            fields = {
                "title": image_title,
                "description": f"Featured image for: {self.title_input.text().strip() or 'Post'}"
            }
            
            # Show uploading status
            self.statusBar().showMessage(f"Uploading {filename} to {site_url}... Please wait...")
            QApplication.processEvents()
            
            resp = requests.post(
                api_url,
                auth=HTTPBasicAuth(username, clean_password),
                files=files,
                data=fields,
                headers=headers,
                timeout=45
            )
            
            # Process response
            self.statusBar().showMessage("Processing upload response...")
            QApplication.processEvents()
            
            self.progress_bar.setVisible(False)
            
            if resp.status_code == 201:
                # Success!
                media_data = resp.json()
                media_id = media_data.get("id")
                media_url = media_data.get("source_url") or media_data.get("link", "")
                
                self.featured_image_media_id = media_id
                self.featured_image_info.setText(
                    f"✓ Uploaded to WordPress | Media ID: {media_id} | {os.path.basename(self.featured_image_path)}"
                )
                self.featured_image_info.setStyleSheet("color: #27ae60; font-size: 10px; font-weight: bold;")
                self.upload_image_btn.setEnabled(False)  # Already uploaded
                
                self.statusBar().showMessage(f"Featured image uploaded successfully! Media ID: {media_id}")
                
                QMessageBox.information(
                    self, "Upload Successful",
                    f"Featured image uploaded successfully!\n\n"
                    f"Media ID: {media_id}\n"
                    f"URL: {media_url}\n\n"
                    f"This image will be set as the featured image when you publish the post."
                )
            
            elif resp.status_code == 401:
                self.upload_image_btn.setEnabled(True)
                self.statusBar().showMessage("Upload failed: Authentication error")
                QMessageBox.critical(
                    self, "Authentication Failed",
                    "Authentication failed (401 Unauthorized).\n\n"
                    "Please check your WordPress credentials in Settings."
                )
            
            elif resp.status_code == 403:
                self.upload_image_btn.setEnabled(True)
                self.statusBar().showMessage("Upload failed: Permission denied")
                QMessageBox.critical(
                    self, "Permission Denied",
                    "Permission denied (403 Forbidden).\n\n"
                    "Possible issues:\n"
                    "- User doesn't have 'upload_files' capability\n"
                    "- REST API is blocked by security plugin\n"
                    "- Check WP Cerber settings (see guide)"
                )
            
            else:
                self.upload_image_btn.setEnabled(True)
                error_msg = resp.text[:500]
                try:
                    error_json = resp.json()
                    if "message" in error_json:
                        error_msg = error_json["message"]
                except:
                    pass
                
                self.statusBar().showMessage(f"Upload failed: HTTP {resp.status_code}")
                QMessageBox.critical(
                    self, "Upload Failed",
                    f"Failed to upload image (HTTP {resp.status_code}):\n\n{error_msg}"
                )
        
        except requests.exceptions.Timeout:
            self.progress_bar.setVisible(False)
            self.upload_image_btn.setEnabled(True)
            QMessageBox.critical(self, "Timeout", "Upload timed out. Please try again.")
        
        except requests.exceptions.ConnectionError:
            self.progress_bar.setVisible(False)
            self.upload_image_btn.setEnabled(True)
            QMessageBox.critical(
                self, "Connection Error",
                f"Could not connect to {site_url}\n\n"
                "Please check your internet connection."
            )
        
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.upload_image_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = WordPressPostEditor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

