#!/usr/bin/env python3
"""
Image Resizer (macOS, PyQt) – WordPress upload version

Adds WordPress integration with:
- Multi-site support (up to 4 sites)
- Settings management (site URL, username, application password)
- Upload Current Image (sends the in-memory resized image to WP media library via REST API)

Authentication Method:
- Uses WordPress Application Passwords with REST API
- NO interactive login required - fully automated via Basic Auth
- Application Passwords are created in WordPress Dashboard → Users → Profile → Application Passwords
- This is the recommended method for programmatic access without user interaction

This file derives from the main app in image_resizer.py without changing it.
"""

import os
import json
import io
import sys
from typing import Optional, Tuple, Dict, List

import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QComboBox,
    QGroupBox, QScrollArea, QWidget, QProgressBar
)

from image_resizer import ImageResizerApp as BaseApp


def get_settings_path() -> str:
    home = os.path.expanduser("~")
    cfg_dir = os.path.join(home, ".imageresizer")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "wp_settings.json")


class WPSiteDialog(QDialog):
    """Dialog for editing a single WordPress site"""
    def __init__(self, parent=None, site_data: Optional[Dict] = None):
        super().__init__(parent)
        self.setWindowTitle("WordPress Site Configuration")
        self.setMinimumWidth(550)
        layout = QVBoxLayout(self)

        # Help text explaining Application Passwords
        help_text = QLabel(
            "💡 <b>Application Password:</b> This uses WordPress REST API authentication and does NOT require interactive login.\n\n"
            "To create an Application Password:\n"
            "1. Go to WordPress Dashboard → Users → Profile\n"
            "2. Scroll to 'Application Passwords' section\n"
            "3. Enter a name (e.g., 'Image Resizer') and click 'Add New'\n"
            "4. Copy the generated password (you'll only see it once)\n\n"
            "This password is used with your username via REST API - no browser login needed."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px; color: #2c3e50;")
        layout.addWidget(help_text)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.site_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        form.addRow("Site Name:", self.name_input)
        form.addRow("Site URL (https://example.com):", self.site_input)
        form.addRow("WordPress Username:", self.user_input)
        form.addRow("Application Password:", self.pass_input)
        layout.addLayout(form)

        btns = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        if site_data:
            self.name_input.setText(site_data.get("name", ""))
            self.site_input.setText(site_data.get("site_url", ""))
            self.user_input.setText(site_data.get("username", ""))
            self.pass_input.setText(site_data.get("app_password", ""))

    def values(self) -> Dict:
        return {
            "name": self.name_input.text().strip(),
            "site_url": self.site_input.text().strip(),
            "username": self.user_input.text().strip(),
            "app_password": self.pass_input.text().strip(),
        }


class WPSettingsDialog(QDialog):
    """Dialog for managing multiple WordPress sites"""
    def __init__(self, parent=None, sites: Optional[List[Dict]] = None, current_index: int = 0):
        super().__init__(parent)
        self.setWindowTitle("WordPress Sites Configuration")
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)

        # Instructions
        info_label = QLabel(
            "Configure up to 4 WordPress sites. Select a site from the list to edit or remove it.\n\n"
            "🔐 <b>Authentication:</b> Uses WordPress Application Passwords via REST API. "
            "This method requires NO interactive login - fully automated and secure."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)

        # Site selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Site:"))
        self.site_combo = QComboBox()
        self.site_combo.currentIndexChanged.connect(self._on_site_selected)
        selector_layout.addWidget(self.site_combo, 1)
        
        add_btn = QPushButton("+ Add Site")
        add_btn.clicked.connect(self._add_site)
        selector_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✎ Edit")
        edit_btn.clicked.connect(self._edit_site)
        selector_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("✕ Remove")
        remove_btn.clicked.connect(self._remove_site)
        selector_layout.addWidget(remove_btn)
        
        layout.addLayout(selector_layout)

        # Display area for selected site details
        details_group = QGroupBox("Site Details")
        details_layout = QVBoxLayout(details_group)
        self.details_label = QLabel("Select a site or add a new one to view/edit details.")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("padding: 10px;")
        details_layout.addWidget(self.details_label)
        layout.addWidget(details_group, 1)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()
        save_btn = QPushButton("Save & Close")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        # Initialize sites list
        self.sites = sites if sites else []
        self.current_index = current_index
        self._update_combo()

    def _update_combo(self):
        """Update the combo box with current sites"""
        self.site_combo.clear()
        for i, site in enumerate(self.sites):
            name = site.get("name", f"Site {i+1}")
            url = site.get("site_url", "")
            display = f"{name}" + (f" ({url})" if url else "")
            self.site_combo.addItem(display, i)
        
        if self.site_combo.count() > 0:
            self.site_combo.setCurrentIndex(self.current_index if self.current_index < len(self.sites) else 0)
            self._on_site_selected()
        else:
            self.details_label.setText("No sites configured. Click 'Add Site' to add your first WordPress site.")

    def _on_site_selected(self):
        """Update details display when site is selected"""
        idx = self.site_combo.currentIndex()
        if idx >= 0 and idx < len(self.sites):
            site = self.sites[idx]
            name = site.get("name", "Unnamed")
            url = site.get("site_url", "")
            username = site.get("username", "")
            has_password = bool(site.get("app_password", ""))
            is_hardcoded = site.get("hardcoded", False)
            
            details = f"<b>{name}</b><br>"
            details += f"URL: {url or '(not set)'}<br>"
            details += f"Username: {username or '(not set)'}<br>"
            details += f"Password: {'✓ Set' if has_password else '✗ Not set'}<br>"
            if is_hardcoded:
                details += f"<span style='color: orange;'><b>⚠ Hardcoded credentials (cannot be changed via UI)</b></span>"
            self.details_label.setText(details)
            self.current_index = idx

    def _add_site(self):
        """Add a new site"""
        if len(self.sites) >= 4:
            QMessageBox.warning(self, "Limit Reached", "You can configure up to 4 WordPress sites.")
            return
        
        dlg = WPSiteDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            values = dlg.values()
            if values["site_url"]:  # At least URL must be provided
                # Generate a default name if not provided
                if not values["name"]:
                    values["name"] = values["site_url"].replace("https://", "").replace("http://", "").split("/")[0]
                self.sites.append(values)
                self._update_combo()
                self.site_combo.setCurrentIndex(len(self.sites) - 1)

    def _edit_site(self):
        """Edit the currently selected site"""
        idx = self.site_combo.currentIndex()
        if idx < 0 or idx >= len(self.sites):
            QMessageBox.warning(self, "No Site Selected", "Please select a site to edit.")
            return
        
        site = self.sites[idx]
        
        # Check if site is hardcoded
        if site.get("hardcoded", False):
            QMessageBox.information(
                self, "Hardcoded Site",
                f"The site '{site.get('name', 'this site')}' uses hardcoded credentials.\n\n"
                "Username and password cannot be changed via the settings dialog.\n"
                "Contact the administrator if credentials need to be updated."
            )
            return
        
        dlg = WPSiteDialog(self, site)
        if dlg.exec_() == QDialog.Accepted:
            values = dlg.values()
            if values["site_url"]:  # URL is required
                # Update site (preserve hardcoded flag if exists)
                if not values["name"]:
                    values["name"] = values["site_url"].replace("https://", "").replace("http://", "").split("/")[0]
                # Preserve hardcoded flag
                if "hardcoded" in site:
                    values["hardcoded"] = site["hardcoded"]
                self.sites[idx] = values
                self._update_combo()
                self.site_combo.setCurrentIndex(idx)
            else:
                QMessageBox.warning(self, "Invalid", "Site URL is required.")

    def _remove_site(self):
        """Remove the currently selected site"""
        idx = self.site_combo.currentIndex()
        if idx < 0 or idx >= len(self.sites):
            QMessageBox.warning(self, "No Site Selected", "Please select a site to remove.")
            return
        
        site_name = self.sites[idx].get("name", "this site")
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove '{site_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.sites.pop(idx)
            self._update_combo()

    def get_sites(self) -> List[Dict]:
        """Return the list of sites"""
        return self.sites

    def get_current_index(self) -> int:
        """Return the currently selected index"""
        return self.site_combo.currentIndex() if self.site_combo.count() > 0 else -1


class WPImageResizerApp(BaseApp):
    def __init__(self):
        self.wp_sites: List[Dict] = []
        self.wp_current_index = 0
        self.wp_site_combo = None  # Will be set in _add_wp_menu
        self.wp_site_combo_ui = None  # Will be set in create_left_panel
        # Load settings BEFORE calling super().__init__() so they're available when create_left_panel is called
        self._load_wp_settings()
        super().__init__()

    def init_ui(self):
        super().init_ui()
        self._add_wp_menu()
        # WordPress UI elements are added in create_left_panel override
        # Make sure combo box is updated after UI is fully created
        # Use QTimer to update after UI is rendered
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self._ensure_wp_ui_updated)
    
    def _ensure_wp_ui_updated(self):
        """Ensure WordPress UI elements are updated after initialization"""
        # Force update of both combo boxes
        if hasattr(self, 'wp_sites') and len(self.wp_sites) > 0:
            if hasattr(self, 'wp_site_combo_ui') and self.wp_site_combo_ui:
                self._update_site_combo_ui()
            if hasattr(self, 'wp_site_combo') and self.wp_site_combo:
                self._update_site_combo()

    def _add_wp_menu(self):
        menubar = self.menuBar()
        wp_menu = menubar.addMenu("WordPress")

        # Site selector as a widget action in the menu
        from PyQt5.QtWidgets import QWidgetAction
        combo_widget = QWidget()
        combo_layout = QHBoxLayout(combo_widget)
        combo_layout.setContentsMargins(10, 5, 10, 5)
        combo_layout.addWidget(QLabel("Active Site:"))
        self.wp_site_combo = QComboBox()
        self.wp_site_combo.currentIndexChanged.connect(self._on_site_combo_changed)
        combo_layout.addWidget(self.wp_site_combo, 1)
        
        combo_menu_action = QWidgetAction(wp_menu)
        combo_menu_action.setDefaultWidget(combo_widget)
        wp_menu.addAction(combo_menu_action)
        wp_menu.addSeparator()
        
        self._update_site_combo()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._open_settings)
        wp_menu.addAction(settings_action)

        upload_action = QAction("Upload Current Image", self)
        upload_action.triggered.connect(self._upload_current_image)
        wp_menu.addAction(upload_action)

    def create_left_panel(self):
        """Override to add WordPress section"""
        # Call parent's create_left_panel
        panel = super().create_left_panel()
        
        # Find the layout in the panel
        layout = panel.layout()
        
        # Create WordPress section group
        wp_group = QGroupBox("📤 WordPress Upload")
        wp_layout = QVBoxLayout(wp_group)
        
        # Site selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Site:"))
        self.wp_site_combo_ui = QComboBox()
        # Populate immediately if sites are available
        if hasattr(self, 'wp_sites') and len(self.wp_sites) > 0:
            for i, site in enumerate(self.wp_sites):
                name = site.get("name", f"Site {i+1}")
                url = site.get("site_url", "")
                display = f"{name}"
                if url:
                    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                    display += f" ({domain})"
                self.wp_site_combo_ui.addItem(display, i)
            # Set current index
            if self.wp_current_index >= 0 and self.wp_current_index < len(self.wp_sites):
                self.wp_site_combo_ui.setCurrentIndex(self.wp_current_index)
        # Connect signal after initial population
        self.wp_site_combo_ui.currentIndexChanged.connect(self._on_site_combo_changed)
        selector_layout.addWidget(self.wp_site_combo_ui, 1)
        wp_layout.addLayout(selector_layout)
        
        # Upload button
        self.wp_upload_btn = QPushButton("⬆ Upload to WordPress")
        self.wp_upload_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 8px;")
        self.wp_upload_btn.clicked.connect(self._upload_current_image)
        self.wp_upload_btn.setEnabled(False)  # Enable when image is loaded
        wp_layout.addWidget(self.wp_upload_btn)
        
        # Progress bar for upload
        self.wp_progress_bar = QProgressBar()
        self.wp_progress_bar.setRange(0, 0)  # Indeterminate mode
        self.wp_progress_bar.setVisible(False)
        self.wp_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        wp_layout.addWidget(self.wp_progress_bar)
        
        # Settings button
        wp_settings_btn = QPushButton("⚙️ WordPress Settings...")
        wp_settings_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 5px;")
        wp_settings_btn.clicked.connect(self._open_settings)
        wp_layout.addWidget(wp_settings_btn)
        
        # Insert WordPress group before the action buttons (before preview/save)
        # We need to find where to insert it - insert before the last item (stretch)
        if layout:
            # Count items to find where buttons start
            count = layout.count()
            # Insert before the button layout (which should be near the end)
            # Add it before the stretch at the end
            layout.insertWidget(count - 1, wp_group)
        
        # Update the combo box with sites (settings should already be loaded in __init__)
        # Force immediate update - wp_sites should be loaded by now
        print(f"DEBUG create_left_panel: wp_sites count = {len(self.wp_sites) if hasattr(self, 'wp_sites') else 'NOT SET'}")
        print(f"DEBUG create_left_panel: wp_site_combo_ui = {self.wp_site_combo_ui}")
        
        # Call immediately - sites should be loaded in __init__ before super().__init__()
        if hasattr(self, 'wp_sites') and len(self.wp_sites) > 0:
            self._update_site_combo_ui()
        else:
            print(f"DEBUG create_left_panel: wp_sites not loaded yet, forcing reload")
            self._load_wp_settings()  # Force reload if not loaded
            self._update_site_combo_ui()
        
        # Also schedule an update after a short delay to ensure UI is fully rendered
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(200, lambda: self._update_site_combo_ui())
        QTimer.singleShot(500, lambda: self._update_site_combo_ui())  # Extra safety check
        
        return panel

    def _update_site_combo(self):
        """Update the site selector combo box in menu"""
        if not self.wp_site_combo:
            return
        
        self.wp_site_combo.clear()
        for i, site in enumerate(self.wp_sites):
            name = site.get("name", f"Site {i+1}")
            url = site.get("site_url", "")
            display = f"{name}"
            if url:
                # Show just the domain for cleaner display
                domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                display += f" ({domain})"
            self.wp_site_combo.addItem(display, i)
        
        # Set current selection
        if self.wp_current_index >= 0 and self.wp_current_index < len(self.wp_sites):
            self.wp_site_combo.setCurrentIndex(self.wp_current_index)
        elif len(self.wp_sites) > 0:
            self.wp_current_index = 0
            self.wp_site_combo.setCurrentIndex(0)
    
    def _update_site_combo_ui(self):
        """Update the site selector combo box in main UI"""
        if not hasattr(self, 'wp_site_combo_ui') or not self.wp_site_combo_ui:
            print(f"DEBUG: _update_site_combo_ui - wp_site_combo_ui not available")
            return
        
        print(f"DEBUG: _update_site_combo_ui - wp_sites count: {len(self.wp_sites) if hasattr(self, 'wp_sites') else 0}")
        
        # Temporarily block signals to avoid triggering updates during population
        self.wp_site_combo_ui.blockSignals(True)
        
        self.wp_site_combo_ui.clear()
        
        # Only populate if we have sites loaded
        if hasattr(self, 'wp_sites') and len(self.wp_sites) > 0:
            print(f"DEBUG: Populating dropdown with {len(self.wp_sites)} sites")
            for i, site in enumerate(self.wp_sites):
                name = site.get("name", f"Site {i+1}")
                url = site.get("site_url", "")
                display = f"{name}"
                if url:
                    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
                    display += f" ({domain})"
                print(f"DEBUG: Adding item {i}: {display}")
                self.wp_site_combo_ui.addItem(display, i)
            
            # Set current selection - make sure index is valid
            valid_index = max(0, min(self.wp_current_index, len(self.wp_sites) - 1))
            if valid_index >= 0 and valid_index < len(self.wp_sites):
                print(f"DEBUG: Setting current index to {valid_index}")
                self.wp_site_combo_ui.setCurrentIndex(valid_index)
                self.wp_current_index = valid_index
            elif len(self.wp_sites) > 0:
                print(f"DEBUG: Setting current index to 0 (default)")
                self.wp_current_index = 0
                self.wp_site_combo_ui.setCurrentIndex(0)
        else:
            # No sites configured yet
            print(f"DEBUG: No sites available, adding placeholder")
            self.wp_site_combo_ui.addItem("(No sites configured)", -1)
            self.wp_current_index = -1
        
        # Re-enable signals
        self.wp_site_combo_ui.blockSignals(False)
        print(f"DEBUG: Dropdown now has {self.wp_site_combo_ui.count()} items")
        
        # Enable upload button if image is loaded
        if hasattr(self, 'wp_upload_btn') and self.original_image:
            self.wp_upload_btn.setEnabled(True)

    def _on_site_combo_changed(self, index):
        """Handle site selection change"""
        # Ignore invalid indices
        if index < 0:
            return
            
        # Check if this is from the UI combo box
        sender = self.sender()
        is_ui_combo = (hasattr(self, 'wp_site_combo_ui') and sender == self.wp_site_combo_ui)
        is_menu_combo = (hasattr(self, 'wp_site_combo') and sender == self.wp_site_combo)
        
        # Get the actual data index from the combo box item data (for UI combo)
        actual_index = index
        if is_ui_combo and hasattr(self, 'wp_site_combo_ui') and self.wp_site_combo_ui:
            item_data = self.wp_site_combo_ui.itemData(index)
            if item_data is not None and isinstance(item_data, int):
                actual_index = item_data
                print(f"DEBUG _on_site_combo_changed: UI combo, index={index}, itemData={actual_index}")
        
        if actual_index >= 0 and actual_index < len(self.wp_sites):
            self.wp_current_index = actual_index
            self._save_wp_settings()
            site_name = self.wp_sites[actual_index].get("name", f"Site {actual_index+1}")
            site_url = self.wp_sites[actual_index].get("site_url", "")
            has_creds = bool(self.wp_sites[actual_index].get("username", "").strip() and 
                           self.wp_sites[actual_index].get("app_password", "").strip())
            print(f"DEBUG _on_site_combo_changed: Changed to '{site_name}' (index {actual_index}), has_creds={has_creds}")
            self.statusBar().showMessage(f"Active WordPress site: {site_name}")
            
            # Update the other combo box to stay in sync (use actual_index for UI updates)
            if is_ui_combo and hasattr(self, 'wp_site_combo') and self.wp_site_combo:
                self.wp_site_combo.blockSignals(True)
                # Find the matching item in menu combo by comparing data
                for i in range(self.wp_site_combo.count()):
                    if self.wp_site_combo.itemData(i) == actual_index:
                        self.wp_site_combo.setCurrentIndex(i)
                        break
                self.wp_site_combo.blockSignals(False)
            elif is_menu_combo and hasattr(self, 'wp_site_combo_ui') and self.wp_site_combo_ui:
                self.wp_site_combo_ui.blockSignals(True)
                # Find the matching item in UI combo by comparing data
                for i in range(self.wp_site_combo_ui.count()):
                    if self.wp_site_combo_ui.itemData(i) == actual_index:
                        self.wp_site_combo_ui.setCurrentIndex(i)
                        break
                self.wp_site_combo_ui.blockSignals(False)

    def upload_image(self):
        """Override upload_image to enable WordPress button"""
        # Call parent's upload_image method
        super().upload_image()
        
        # Enable WordPress upload button if image was loaded successfully
        if hasattr(self, 'wp_upload_btn') and self.original_image:
            self.wp_upload_btn.setEnabled(True)

    def _get_current_site(self) -> Optional[Dict]:
        """Get the currently selected site configuration"""
        # First try to get index from UI combo box if available
        if hasattr(self, 'wp_site_combo_ui') and self.wp_site_combo_ui:
            ui_index = self.wp_site_combo_ui.currentIndex()
            if ui_index >= 0:
                # Get the actual data index from the combo box item data
                item_data = self.wp_site_combo_ui.itemData(ui_index)
                if item_data is not None and isinstance(item_data, int):
                    actual_index = item_data
                else:
                    actual_index = ui_index
                
                if actual_index >= 0 and actual_index < len(self.wp_sites):
                    return self.wp_sites[actual_index]
        
        # Fallback to stored index
        if self.wp_current_index >= 0 and self.wp_current_index < len(self.wp_sites):
            return self.wp_sites[self.wp_current_index]
        return None

    def _get_default_sites(self) -> List[Dict]:
        """Return default WordPress sites configuration"""
        return [
            {
                "name": "Trieste All News",
                "site_url": "https://triesteallnews.it",
                "username": "",
                "app_password": "",
            },
            {
                "name": "Gorizia Oggi",
                "site_url": "https://goriziaoggi.news",
                "username": "goriziaNews",  # Hardcoded username
                "app_password": "E7RP LRzc mGBc aUNQ 4kd3 N2m6",  # Hardcoded Application Password
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
                "username": "",
                "app_password": "",
            },
        ]

    # Settings persistence
    def _load_wp_settings(self):
        """Load WordPress sites from settings file"""
        print(f"DEBUG: Loading WP settings...")
        try:
            path = get_settings_path()
            print(f"DEBUG: Settings path: {path}")
            if os.path.exists(path):
                with open(path, "r") as f:
                    cfg = json.load(f)
                    
                    # Try new format first (multiple sites)
                    if "sites" in cfg and isinstance(cfg["sites"], list) and len(cfg["sites"]) > 0:
                        self.wp_sites = cfg["sites"]
                        saved_index = cfg.get("current_index", 0)
                        
                        # Restore hardcoded credentials for protected sites
                        # This ensures hardcoded sites always have their credentials, even if user tries to change them
                        default_sites = self._get_default_sites()
                        for default_site in default_sites:
                            if default_site.get("hardcoded", False):
                                # Find matching site by URL
                                found = False
                                for i, saved_site in enumerate(self.wp_sites):
                                    if saved_site.get("site_url") == default_site.get("site_url"):
                                        # Always restore hardcoded credentials (overwrite any user changes)
                                        self.wp_sites[i]["username"] = default_site["username"]
                                        self.wp_sites[i]["app_password"] = default_site["app_password"]
                                        self.wp_sites[i]["hardcoded"] = True
                                        # Also ensure name matches if not set
                                        if not self.wp_sites[i].get("name"):
                                            self.wp_sites[i]["name"] = default_site["name"]
                                        found = True
                                        break
                                # If site not found in saved sites, add it from defaults
                                if not found:
                                    self.wp_sites.append(default_site.copy())
                        # Ensure we have all default sites (merge with defaults)
                        default_sites = self._get_default_sites()
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
                        
                        # Validate and fix current_index - find first site with valid credentials
                        self.wp_current_index = saved_index
                        if saved_index < 0 or saved_index >= len(self.wp_sites):
                            self.wp_current_index = 0
                        
                        # Check if selected site has valid credentials, if not, find first valid one
                        selected_site = self.wp_sites[self.wp_current_index] if self.wp_current_index < len(self.wp_sites) else None
                        if not selected_site or not (selected_site.get("username", "").strip() and selected_site.get("app_password", "").strip()):
                            # Find first site with valid credentials
                            found_valid = False
                            for i, site in enumerate(self.wp_sites):
                                if site.get("username", "").strip() and site.get("app_password", "").strip():
                                    self.wp_current_index = i
                                    found_valid = True
                                    break
                            if not found_valid:
                                # No valid site found, default to first site
                                self.wp_current_index = 0
                        
                        self._save_wp_settings()  # Save merged sites
                        print(f"DEBUG _load_wp_settings: Loaded {len(self.wp_sites)} sites, current_index = {self.wp_current_index}")
                    # Legacy format (single site) - migrate to new format
                    elif "site_url" in cfg:
                        if cfg.get("site_url"):
                            site_name = cfg["site_url"].replace("https://", "").replace("http://", "").split("/")[0]
                            self.wp_sites = [{
                                "name": site_name,
                                "site_url": cfg.get("site_url", ""),
                                "username": cfg.get("username", ""),
                                "app_password": cfg.get("app_password", ""),
                            }]
                            self.wp_current_index = 0
                            # Save in new format
                            self._save_wp_settings()
                        else:
                            # No sites configured, use defaults
                            self.wp_sites = self._get_default_sites()
                            self.wp_current_index = 0
                            self._save_wp_settings()
                    else:
                        # No sites configured, use defaults
                        self.wp_sites = self._get_default_sites()
                        self.wp_current_index = 0
                        self._save_wp_settings()
            else:
                # Settings file doesn't exist, create with defaults
                self.wp_sites = self._get_default_sites()
                self.wp_current_index = 0
                self._save_wp_settings()
        except Exception as e:
            print(f"ERROR loading WP settings: {e}")
            import traceback
            traceback.print_exc()
            # On error, initialize with defaults
            self.wp_sites = self._get_default_sites()
            self.wp_current_index = 0
            print(f"DEBUG _load_wp_settings: After error, using defaults: {len(self.wp_sites)} sites")
        
        # Ensure wp_sites is always initialized
        if not hasattr(self, 'wp_sites') or len(self.wp_sites) == 0:
            print(f"DEBUG _load_wp_settings: wp_sites was empty, initializing with defaults")
            self.wp_sites = self._get_default_sites()
            self.wp_current_index = 0
        
        print(f"DEBUG _load_wp_settings: Final wp_sites count = {len(self.wp_sites)}, current_index = {self.wp_current_index}")

    def _save_wp_settings(self):
        """Save WordPress sites to settings file"""
        try:
            path = get_settings_path()
            print(f"DEBUG _save_wp_settings: Saving to {path}")
            print(f"DEBUG _save_wp_settings: {len(self.wp_sites)} sites, current_index={self.wp_current_index}")
            for i, site in enumerate(self.wp_sites):
                has_creds = bool(site.get("username", "").strip() and site.get("app_password", "").strip())
                print(f"DEBUG _save_wp_settings: Site {i} '{site.get('name')}': has_creds={has_creds}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, "w") as f:
                json.dump(
                    {
                        "sites": self.wp_sites,
                        "current_index": self.wp_current_index,
                    },
                    f,
                    indent=2,
                )
            print(f"DEBUG _save_wp_settings: Settings saved successfully")
        except Exception as e:
            print(f"ERROR saving WP settings: {e}")
            import traceback
            traceback.print_exc()

    def _open_settings(self):
        """Open the WordPress sites configuration dialog"""
        dlg = WPSettingsDialog(self, self.wp_sites.copy(), self.wp_current_index)
        
        # Add option to reset to defaults if sites list is empty or user wants to
        if len(self.wp_sites) == 0:
            reply = QMessageBox.question(
                self, "No Sites Configured",
                "No WordPress sites are configured. Would you like to load the default sites?\n\n"
                "(Trieste All News, Gorizia Oggi, Udine Oggi, Venezia Orientale)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.wp_sites = self._get_default_sites()
                self.wp_current_index = 0
                dlg = WPSettingsDialog(self, self.wp_sites.copy(), self.wp_current_index)
        
        if dlg.exec_() == QDialog.Accepted:
            new_sites = dlg.get_sites()
            new_index = dlg.get_current_index()
            
            # Preserve hardcoded credentials for protected sites
            default_sites = self._get_default_sites()
            for default_site in default_sites:
                if default_site.get("hardcoded", False):
                    # Find matching site by URL and restore hardcoded credentials
                    for i, saved_site in enumerate(new_sites):
                        if saved_site.get("site_url") == default_site.get("site_url"):
                            # Restore hardcoded credentials (but preserve other settings like name)
                            new_sites[i]["username"] = default_site["username"]
                            new_sites[i]["app_password"] = default_site["app_password"]
                            new_sites[i]["hardcoded"] = True
                            print(f"DEBUG _open_settings: Restored hardcoded credentials for {new_sites[i].get('name')}")
                            break
            
            self.wp_sites = new_sites
            
            if new_index >= 0 and new_index < len(self.wp_sites):
                self.wp_current_index = new_index
            elif len(self.wp_sites) > 0:
                self.wp_current_index = 0
            else:
                self.wp_current_index = -1
            
            print(f"DEBUG _open_settings: Saving {len(self.wp_sites)} sites, current_index={self.wp_current_index}")
            for i, site in enumerate(self.wp_sites):
                has_creds = bool(site.get("username", "").strip() and site.get("app_password", "").strip())
                print(f"DEBUG _open_settings: Site {i} '{site.get('name')}': has_creds={has_creds}, username='{site.get('username', '')[:3] if site.get('username') else 'EMPTY'}...'")
            
            self._save_wp_settings()
            self._update_site_combo()
            self._update_site_combo_ui()  # Also update UI combo box
            
            if len(self.wp_sites) > 0:
                site_name = self.wp_sites[self.wp_current_index].get("name", "Site")
                self.statusBar().showMessage(f"WordPress sites updated. Active: {site_name}")

    # Upload logic
    def _encode_current_image(self) -> Optional[Tuple[bytes, str]]:
        if not self.resized_image and not self.original_image:
            return None
        img = self.resized_image or self.original_image
        # Figure out selected format from radio buttons (exists in base class)
        if hasattr(self, "jpg_radio") and self.jpg_radio.isChecked():
            ext = "jpg"
            buf = io.BytesIO()
            work = img
            if work.mode == "RGBA":
                from PIL import Image as PILImage
                bg = PILImage.new("RGB", work.size, (255, 255, 255))
                bg.paste(work, mask=work.split()[3])
                work = bg
            work.save(buf, format="JPEG", quality=self.quality_slider.value(), optimize=True)
            return buf.getvalue(), ext
        if hasattr(self, "png_radio") and self.png_radio.isChecked():
            ext = "png"
            buf = io.BytesIO()
            q = self.quality_slider.value()
            compress_level = 3 if q >= 80 else 6 if q >= 50 else 9
            img.save(buf, format="PNG", optimize=True, compress_level=compress_level)
            return buf.getvalue(), ext
        # Default to WebP
        ext = "webp"
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=self.quality_slider.value(), method=6)
        return buf.getvalue(), ext

    def _upload_current_image(self):
        # Get the currently selected site
        current_site = self._get_current_site()
        print(f"DEBUG _upload_current_image: current_site = {current_site}")
        if not current_site:
            reply = QMessageBox.warning(
                self, "WordPress", 
                "No WordPress site selected. Please configure and select a site in Settings.\n\n"
                "Open Settings now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._open_settings()
            return
        
        wp_site_url = current_site.get("site_url", "").strip()
        wp_username = current_site.get("username", "").strip()
        wp_app_password = current_site.get("app_password", "").strip()
        
        print(f"DEBUG _upload_current_image: Site '{current_site.get('name')}', URL={wp_site_url}, Username={wp_username[:3] if wp_username else 'EMPTY'}..., Password={'SET' if wp_app_password else 'EMPTY'}")
        
        if not (wp_site_url and wp_username and wp_app_password):
            reply = QMessageBox.warning(
                self, "WordPress", 
                f"Site '{current_site.get('name', 'Selected site')}' is not properly configured.\n\n"
                "Please check that Site URL, Username, and Application Password are all set.\n\n"
                "This site needs to be configured before uploading.\n\n"
                "Open Settings now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self._open_settings()
            return
        encoded = self._encode_current_image()
        if not encoded:
            QMessageBox.warning(self, "WordPress", "No image to upload. Please resize or load an image first.")
            return

        data_bytes, ext = encoded
        
        # Check file size - block uploads over 200KB
        file_size_kb = len(data_bytes) / 1024
        if file_size_kb > 200:
            reply = QMessageBox.warning(
                self, "File Too Large",
                f"The image file size is {file_size_kb:.1f} KB, which exceeds the 200 KB limit.\n\n"
                "Please reduce the image dimensions or quality to make it smaller than 200 KB.\n\n"
                "Would you like to proceed anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.statusBar().showMessage("Upload cancelled - file size exceeds 200 KB limit")
                return
        
        # Generate a better filename
        filename = "image_resizer_upload." + ext
        try:
            if hasattr(self, "meta_title_input") and self.meta_title_input.text().strip():
                # Use title if available, sanitize for filename
                title = self.meta_title_input.text().strip()
                # Remove invalid filename characters
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    title = title.replace(char, '_')
                # Limit length and clean up
                title = title[:50].strip()
                if title:
                    filename = f"{title}.{ext}"
            elif hasattr(self, "original_path") and self.original_path:
                # Use original filename if available
                base_name = os.path.splitext(os.path.basename(self.original_path))[0]
                filename = f"{base_name}.{ext}"
        except Exception:
            pass  # Fall back to default filename
        
        url = wp_site_url.rstrip("/") + "/wp-json/wp/v2/media"
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "application/octet-stream")

        files = {"file": (filename, data_bytes, mime)}
        fields = {}
        # Use our fields if available
        try:
            if hasattr(self, "meta_title_input"):
                t = self.meta_title_input.text().strip()
                if t:
                    fields["title"] = t
            if hasattr(self, "meta_description_input"):
                d = self.meta_description_input.text().strip()
                if d:
                    fields["description"] = d
        except Exception:
            pass
        
        # Automatically set description to site name if not already set
        site_name = current_site.get("name", "WordPress site")
        if "description" not in fields or not fields["description"]:
            fields["description"] = site_name

        # Show status message with site name
        self.statusBar().showMessage(f"Uploading to {site_name}...")
        
        # Show progress bar and disable button BEFORE the request
        self.wp_progress_bar.setVisible(True)
        self.wp_progress_bar.setRange(0, 0)  # Indeterminate mode
        self.wp_upload_btn.setEnabled(False)  # Disable button during upload
        
        # Force GUI update multiple times to ensure progress bar is visible
        QApplication.processEvents()
        QApplication.processEvents()
        QApplication.processEvents()
        
        # Also force a small delay to let GUI render
        import time
        time.sleep(0.05)  # Small delay (50ms) to let GUI update
        QApplication.processEvents()  # One more update after delay
        
        # Use WordPress REST API with Basic Auth (username + application password)
        # This method bypasses interactive login - no browser authentication needed
        # Application passwords are specifically designed for REST API programmatic access
        try:
            # Prepare headers explicitly - WP Cerber may need specific headers
            # Use a consistent User-Agent to help Cerber identify legitimate requests
            # X-ImageResizer-Client header can be whitelisted in Cerber firewall settings
            headers = {
                'User-Agent': 'ImageResizer-MacOS/1.0 (WordPress REST API Client)',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',  # May help with some security plugins
                'X-ImageResizer-Client': 'ImageResizer-MacOS/1.0',  # For Cerber firewall whitelist
                # Note: Content-Type will be set automatically by requests for multipart/form-data
            }
            
            # Clean up Application Password (remove spaces - WordPress expects no spaces in auth)
            clean_password = wp_app_password.replace(" ", "")
            
            # Use HTTPBasicAuth explicitly to ensure proper authentication
            from requests.auth import HTTPBasicAuth
            
            # Add a small delay to avoid triggering rate limiting if multiple uploads happen quickly
            # This helps prevent Cerber from thinking rapid uploads are attacks
            if hasattr(self, '_last_upload_time'):
                import time
                time_since_last = time.time() - self._last_upload_time
                if time_since_last < 2.0:  # If less than 2 seconds since last upload
                    delay = 2.0 - time_since_last
                    time.sleep(delay)  # Wait to avoid rate limiting
            
            # Make the request with explicit headers and clean password
            # For file uploads, requests library automatically sets Content-Type to multipart/form-data
            resp = requests.post(
                url, 
                auth=HTTPBasicAuth(wp_username, clean_password),
                files=files, 
                data=fields, 
                headers=headers,
                timeout=45,
                allow_redirects=True  # Allow redirects in case WordPress redirects
            )
            
            # Record upload time for rate limiting protection
            import time
            self._last_upload_time = time.time()
            if resp.status_code == 401:
                # Special handling for 401 - likely password changed
                error_msg = "Unauthorized - Authentication failed"
                try:
                    error_json = resp.json()
                    if "message" in error_json:
                        error_msg = error_json["message"]
                    elif "code" in error_json:
                        error_msg = error_json.get("message", error_msg)
                except Exception:
                    pass
                
                self.statusBar().showMessage("Upload failed - unauthorized")
                
                # Check if this is a hardcoded site
                is_hardcoded = current_site.get("hardcoded", False)
                if is_hardcoded:
                    warning_msg = (
                        f"⚠️ UNAUTHORIZED ACCESS - Password may have changed!\n\n"
                        f"Site: {site_name}\n"
                        f"Error: {error_msg}\n\n"
                        f"This site uses hardcoded credentials. The Application Password "
                        f"may have been changed on the WordPress site.\n\n"
                        f"Please contact the administrator to:\n"
                        f"1. Verify the Application Password is still active\n"
                        f"2. Check if the password was changed or revoked\n"
                        f"3. Update the Application Password in the code if needed"
                    )
                else:
                    warning_msg = (
                        f"⚠️ UNAUTHORIZED ACCESS - Check your credentials!\n\n"
                        f"Site: {site_name}\n"
                        f"Error: {error_msg}\n\n"
                        f"The Application Password may have been:\n"
                        f"- Changed on the WordPress site\n"
                        f"- Revoked or deleted\n"
                        f"- Entered incorrectly\n\n"
                        f"Please go to WordPress → Settings... and verify your credentials."
                    )
                
                # Hide progress bar
                self.wp_progress_bar.setVisible(False)
                self.wp_upload_btn.setEnabled(True)
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("WordPress Authentication Failed")
                msg.setText(warning_msg)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            elif resp.status_code == 403:
                # Special handling for 403 - WP Cerber or security plugin blocking
                error_msg = "Access Forbidden - REST API blocked"
                try:
                    error_json = resp.json()
                    if "message" in error_json:
                        error_msg = error_json["message"]
                except Exception:
                    pass
                
                # Hide progress bar
                self.wp_progress_bar.setVisible(False)
                self.wp_upload_btn.setEnabled(True)
                
                self.statusBar().showMessage("Upload failed - access forbidden")
                
                wp_403_message = (
                    f"⚠️ ACCESS FORBIDDEN (HTTP 403)\n\n"
                    f"Site: {site_name}\n"
                    f"Error: {error_msg}\n\n"
                    f"🔒 WP Cerber Security is blocking REST API access.\n\n"
                    f"📋 To fix this, you MUST configure Cerber correctly:\n\n"
                    f"1. Go to WordPress Dashboard → Cerber → Hardening\n"
                    f"2. Find 'Disable REST API' setting\n"
                    f"3. ⚠️ IMPORTANT: Enable 'Allow REST API for authenticated users'\n"
                    f"   (Italian: 'Consenti per utenti registrati' - MUST be CHECKED ✅)\n"
                    f"4. In 'Specificare gli spazi dei nomi REST API...' field, add:\n"
                    f"   wp/v2\n"
                    f"   (One per line, no trailing spaces)\n"
                    f"5. Save changes\n"
                    f"6. Clear Cerber cache: Cerber → Tools → Clear cache\n\n"
                    f"🛡️ RECOMMENDED: Whitelist ImageResizer requests in Cerber Firewall:\n"
                    f"- Go to Cerber → Hardening → Firewall Policies\n"
                    f"- Find 'Escludere le richieste con queste intestazioni HTTP...'\n"
                    f"- Add this header: X-ImageResizer-Client\n"
                    f"- This will exclude all ImageResizer requests from firewall inspection\n\n"
                    f"🛡️ Alternative: Prevent rate limiting:\n"
                    f"- Go to Cerber → Traffic Inspector\n"
                    f"- Check 'Anti-spam engine' and 'Rate limiting' settings\n"
                    f"- Consider whitelisting your IP or User-Agent: 'ImageResizer-MacOS'\n"
                    f"- Or disable rate limiting for authenticated REST API requests\n\n"
                    f"⚠️ If still blocked after these steps:\n"
                    f"- Check Cerber → Activity → Logs for blocked requests\n"
                    f"- Verify Application Password is still active in WordPress\n"
                    f"- Try temporarily disabling 'Disable REST API' to test\n\n"
                    f"Note: Authentication with Application Password requires\n"
                    f"'Allow REST API for authenticated users' to be ENABLED."
                )
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("WordPress Access Forbidden (403)")
                msg.setText(wp_403_message)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            elif resp.status_code >= 400:
                error_msg = resp.text[:300]
                try:
                    # Try to extract error message from JSON response
                    error_json = resp.json()
                    if "message" in error_json:
                        error_msg = error_json["message"]
                    elif "code" in error_json:
                        error_msg = f"{error_json.get('code', 'Unknown error')}: {error_json.get('message', error_msg)}"
                except Exception:
                    pass  # Use text response if JSON parsing fails
                # Hide progress bar
                self.wp_progress_bar.setVisible(False)
                self.wp_upload_btn.setEnabled(True)
                
                self.statusBar().showMessage("Upload failed")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("WordPress Upload Failed")
                msg.setText(f"Upload failed (HTTP {resp.status_code}):\n{error_msg}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            
            # Parse JSON response
            try:
                j = resp.json()
            except ValueError:
                # Hide progress bar
                self.wp_progress_bar.setVisible(False)
                self.wp_upload_btn.setEnabled(True)
                
                self.statusBar().showMessage("Upload failed - invalid response")
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("WordPress Upload Failed")
                msg.setText("Upload failed: Invalid response from server")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
            
            media_id = j.get("id")
            media_url = j.get("source_url") or j.get("link") or j.get("url")
            
            # Hide progress bar on success
            self.wp_progress_bar.setVisible(False)
            self.wp_upload_btn.setEnabled(True)
            
            self.statusBar().showMessage(f"Upload successful to {site_name}! Media ID: {media_id}")
            
            # Show details directly in the message instead of using "Show Details" button
            details_text = (
                f"Image uploaded successfully to {site_name}!\n\n"
                f"Site: {site_name}\n"
                f"Media ID: {media_id}\n"
                f"URL: {media_url or 'N/A'}"
            )
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("WordPress Upload Successful")
            msg.setText(details_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
        except requests.exceptions.Timeout:
            # Hide progress bar
            self.wp_progress_bar.setVisible(False)
            self.wp_upload_btn.setEnabled(True)
            
            self.statusBar().showMessage("Upload failed - timeout")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("WordPress Upload Failed")
            msg.setText("Upload failed: Request timed out. Please check your connection and try again.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except requests.exceptions.ConnectionError:
            # Hide progress bar
            self.wp_progress_bar.setVisible(False)
            self.wp_upload_btn.setEnabled(True)
            
            self.statusBar().showMessage("Upload failed - connection error")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("WordPress Upload Failed")
            msg.setText(
                f"Connection error: Could not reach {wp_site_url}\n\nPlease check:\n"
                "- Your internet connection\n"
                "- The WordPress site URL is correct\n"
                "- The site is accessible"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except requests.exceptions.RequestException as e:
            # Hide progress bar
            self.wp_progress_bar.setVisible(False)
            self.wp_upload_btn.setEnabled(True)
            
            self.statusBar().showMessage("Upload failed - network error")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("WordPress Upload Failed")
            msg.setText(f"Network error:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except Exception as e:
            # Hide progress bar
            self.wp_progress_bar.setVisible(False)
            self.wp_upload_btn.setEnabled(True)
            
            self.statusBar().showMessage("Upload failed - unexpected error")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("WordPress Upload Failed")
            msg.setText(f"Unexpected error:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


def main():
    app = QApplication(sys.argv)
    win = WPImageResizerApp()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


