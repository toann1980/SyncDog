# main.spec
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
block_cipher = None


# Collect all data files and submodules for PySide6
pyside6_datas = collect_data_files('PySide6')
hiddenimports = collect_submodules('PySide6')

svg_files = [
    ('UI/sync_mirror.svg', 'UI'),
    ('UI/sync_off.svg', 'UI'),
    ('UI/sync_atob.svg', 'UI'),
    ('UI/sync_btoa.svg', 'UI'),
    ('UI/syncdog-icon_64.ico', 'UI')
]


datas = pyside6_datas + svg_files

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SyncDog',
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
    icon='UI/syncdog-icon_64.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SyncDog',
)
app = BUNDLE(
    coll,
    name='SyncDog',
    icon=None,
    bundle_identifier=None,
    onefile=True
)