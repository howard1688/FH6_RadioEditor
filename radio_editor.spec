# -*- mode: python ; coding: utf-8 -*-

PYTHON_ROOT = r'C:\Users\howar\AppData\Local\Programs\Python\Python312'

datas = [
    (rf'{PYTHON_ROOT}\tcl\tcl8.6', '_tcl_data'),
    (rf'{PYTHON_ROOT}\tcl\tk8.6', '_tk_data'),
]

binaries = [
    (rf'{PYTHON_ROOT}\DLLs\_tkinter.pyd', '.'),
    (rf'{PYTHON_ROOT}\DLLs\tcl86t.dll', '.'),
    (rf'{PYTHON_ROOT}\DLLs\tk86t.dll', '.'),
]

a = Analysis(
    ['radio_editor.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['tkinter', '_tkinter'],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[rf'{PYTHON_ROOT}\Lib\site-packages\PyInstaller\hooks\rthooks\pyi_rth__tkinter.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    [],
    exclude_binaries=True,
    name='radio_editor',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='radio_editor',
)
