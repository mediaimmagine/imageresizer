# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['PIL', 'PIL.Image', 'PIL.ImageDraw', 'PyQt5.sip']
hiddenimports += collect_submodules('PyQt5.QtCore')
hiddenimports += collect_submodules('PyQt5.QtGui')
hiddenimports += collect_submodules('PyQt5.QtWidgets')


a = Analysis(
    ['image_resizer_macos_wp.py'],
    pathex=[],
    binaries=[],
    datas=[('requirements_image_resizer.txt', '.'), ('mediaimmagine_logo_white.png', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ImageResizerWP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ImageResizerWP',
)
app = BUNDLE(
    coll,
    name='ImageResizerWP.app',
    icon='app_icon.icns',
    bundle_identifier='com.imageresizer.wp',
)
