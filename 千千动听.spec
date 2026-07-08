# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.'), ('icons.py', '.'), ('ui.py', '.'), ('core.py', '.'), ('config.py', '.'), ('updater.py', '.'), ('version.py', '.'), ('config', 'config')],
    hiddenimports=['PyQt5', 'PyQt5.QtMultimedia', 'PyQt5.QtNetwork', 'updater', 'version'],
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
    a.binaries,
    a.datas,
    [],
    name='千千动听',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
