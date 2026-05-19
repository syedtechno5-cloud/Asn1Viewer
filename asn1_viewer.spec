# -*- mode: python ; coding: utf-8 -*-
import sys

# ── Shared analysis options ────────────────────────────────────────────────── #

_common = dict(
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources')],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'src.cli.runner',
        'src.parser.tag_filter',
        'src.export.convert_exporter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ── GUI ────────────────────────────────────────────────────────────────────── #

gui_a   = Analysis(['main.py'], **_common)
gui_pyz = PYZ(gui_a.pure)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    gui_a.binaries,
    gui_a.datas,
    [],
    name='ASN1Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# macOS: wrap the binary in a proper .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        gui_exe,
        name='ASN1Viewer.app',
        icon=None,
        bundle_identifier='com.syedtechnologies.asn1viewer',
        info_plist={
            'CFBundleDisplayName': 'ASN.1 Viewer',
            'CFBundleShortVersionString': '1.1.0',
            'CFBundleVersion': '1.1.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
        },
    )

# ── CLI ────────────────────────────────────────────────────────────────────── #

cli_a   = Analysis(['asn1viewcli.py'], **_common)
cli_pyz = PYZ(cli_a.pure)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    cli_a.binaries,
    cli_a.datas,
    [],
    name='asn1viewcli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
