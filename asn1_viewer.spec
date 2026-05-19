# -*- mode: python ; coding: utf-8 -*-

# ── Shared analysis ────────────────────────────────────────────────────────── #

common_kwargs = dict(
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

# ── GUI build ─────────────────────────────────────────────────────────────── #

gui_a = Analysis(['main.py'], **common_kwargs)
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
    console=False,               # no console window for the GUI
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# ── CLI build ─────────────────────────────────────────────────────────────── #

cli_a = Analysis(['asn1viewcli.py'], **common_kwargs)
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
    console=True,                # keep console window open for CLI output
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
