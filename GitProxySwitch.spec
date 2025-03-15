# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('./icon/', 'icon')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtNetwork",
        "unicodedata",
        "_bz2",
        "_decimal",
        "_lzma",
        "_hashlib",
        "_ctypes",
        "_queue",
        "_ssl",
        "pyexpat",
    ],
    noarchive=False,
    optimize=0,
)

# # 导入TOC以排除未使用的二进制文件以压缩体积
# from PyInstaller.building.datastruct import TOC
# excluded_dlls = {'pyside6\\opengl32sw.dll', 'pyside6\\qt6quick.dll', 'pyside6\\qt6pdf.dll', 'pyside6\\qt6qml.dll', 'pyside6\\qt6opengl.dll', 'pyside6\\qt6network.dll', 'pyside6\\qt6qmlmodels.dll', 'pyside6\\msvcp140.dll'}
# # 使用 TOC 减法操作来排除 DLL 文件
# a.binaries -= TOC([(dll, None, None) for dll in excluded_dlls])

from PyInstaller.building.datastruct import TOC
import sys
# 从 a.binaries 中获取所有 pyside6 相关的 DLL，并筛选出不包含 gui、widgets、core 的文件
excluded_dlls = {
    dll[0]
    for dll in a.binaries
    if dll[0].lower().endswith(".dll")
    and "pyside6" in dll[0].lower()
    and not any(
        x in dll[0].lower() for x in ["gui", "widgets", "core", "plugin", "abi", "svg"]
    )
}

# 使用 TOC 减法操作来排除 DLL 文件
a.binaries -= TOC(
    [(dll, path, type_) for dll, path, type_ in a.binaries if dll in excluded_dlls]
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GitProxySwitch',
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
    icon=['icon\\logo.icns'] if sys.platform == 'darwin' else ['icon\\logo.ico'],
)
