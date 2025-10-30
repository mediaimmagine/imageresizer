#!/usr/bin/env python3
"""
Image Resizer (macOS, PyQt) – WordPress upload test version

Adds a WordPress menu with:
- Settings (site URL, username, application password)
- Upload Current Image (sends the in-memory resized image to WP media library)

This file derives from the main app in image_resizer.py without changing it.
"""

import os
import json
import io
import sys
from typing import Optional, Tuple

import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox
)

from image_resizer import ImageResizerApp as BaseApp


def get_settings_path() -> str:
    home = os.path.expanduser("~")
    cfg_dir = os.path.join(home, ".imageresizer")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "wp_settings.json")


class WPSettingsDialog(QDialog):
    def __init__(self, parent=None, initial: Optional[dict] = None):
        super().__init__(parent)
        self.setWindowTitle("WordPress Settings")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.site_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        form.addRow("Site URL (https://example.com):", self.site_input)
        form.addRow("Username:", self.user_input)
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

        if initial:
            self.site_input.setText(initial.get("site_url", ""))
            self.user_input.setText(initial.get("username", ""))
            self.pass_input.setText(initial.get("app_password", ""))

    def values(self) -> Tuple[str, str, str]:
        return (
            self.site_input.text().strip(),
            self.user_input.text().strip(),
            self.pass_input.text().strip(),
        )


class WPImageResizerApp(BaseApp):
    def __init__(self):
        self.wp_site_url = ""
        self.wp_username = ""
        self.wp_app_password = ""
        super().__init__()

    def init_ui(self):
        super().init_ui()
        self._load_wp_settings()
        self._add_wp_menu()

    def _add_wp_menu(self):
        menubar = self.menuBar()
        wp_menu = menubar.addMenu("WordPress")

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._open_settings)
        wp_menu.addAction(settings_action)

        upload_action = QAction("Upload Current Image", self)
        upload_action.triggered.connect(self._upload_current_image)
        wp_menu.addAction(upload_action)

    # Settings persistence
    def _load_wp_settings(self):
        try:
            path = get_settings_path()
            if os.path.exists(path):
                with open(path, "r") as f:
                    cfg = json.load(f)
                    self.wp_site_url = cfg.get("site_url", "")
                    self.wp_username = cfg.get("username", "")
                    self.wp_app_password = cfg.get("app_password", "")
        except Exception:
            pass

    def _save_wp_settings(self):
        try:
            path = get_settings_path()
            with open(path, "w") as f:
                json.dump(
                    {
                        "site_url": self.wp_site_url,
                        "username": self.wp_username,
                        "app_password": self.wp_app_password,
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def _open_settings(self):
        dlg = WPSettingsDialog(
            self,
            initial={
                "site_url": self.wp_site_url,
                "username": self.wp_username,
                "app_password": self.wp_app_password,
            },
        )
        if dlg.exec_() == QDialog.Accepted:
            site, user, pwd = dlg.values()
            self.wp_site_url = site
            self.wp_username = user
            self.wp_app_password = pwd
            self._save_wp_settings()

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
        if not (self.wp_site_url and self.wp_username and self.wp_app_password):
            QMessageBox.warning(self, "WordPress", "Please configure WordPress settings first.")
            self._open_settings()
            return
        encoded = self._encode_current_image()
        if not encoded:
            QMessageBox.warning(self, "WordPress", "No image to upload. Please resize or load an image first.")
            return

        data_bytes, ext = encoded
        filename = "image_resizer_upload." + ext
        url = self.wp_site_url.rstrip("/") + "/wp-json/wp/v2/media"
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

        try:
            resp = requests.post(url, auth=(self.wp_username, self.wp_app_password), files=files, data=fields, timeout=45)
            if resp.status_code >= 400:
                QMessageBox.critical(self, "WordPress", f"Upload failed (HTTP {resp.status_code}):\n{resp.text[:300]}")
                return
            j = resp.json()
            media_id = j.get("id")
            media_url = j.get("source_url")
            QMessageBox.information(self, "WordPress", f"Upload successful!\nID: {media_id}\nURL: {media_url}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "WordPress", f"Network error:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "WordPress", f"Unexpected error:\n{str(e)}")


def main():
    app = QApplication(sys.argv)
    win = WPImageResizerApp()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


