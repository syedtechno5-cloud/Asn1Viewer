# Installation Guide — ASN.1 Viewer v1.1.0

## Prerequisites

- **Python 3.8 or higher** — download from [python.org](https://www.python.org/)
- **pip** — included with Python 3.8+

Verify:
```powershell
python --version      # Python 3.8+
python -m pip --version
```

---

## Option A — Run from source (GUI)

```powershell
cd "path\to\Asn1Viewer"
python -m pip install -r requirements.txt
python main.py
```

---

## Option B — Run from source (GUI + CLI command)

Installing the package in editable mode registers the `asn1viewcli` command on your PATH:

```powershell
cd "path\to\Asn1Viewer"
python -m pip install -r requirements.txt
python -m pip install -e .
```

After this you can run:
```powershell
python main.py          # GUI
asn1viewcli --help      # CLI
```

### Add Python Scripts to PATH (Windows, if needed)

If `asn1viewcli` is not found after install, find your Scripts directory:
```powershell
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

Add that path to your user PATH:
```powershell
# Example — replace with your actual Scripts path
$scripts = "C:\Users\YourName\AppData\Local\Python\pythoncore-3.14-64\Scripts"
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$scripts", "User")
```

Open a new terminal and verify:
```powershell
asn1viewcli --version
```

---

## Option C — Standalone executables (no Python needed)

Build once, distribute anywhere:

```powershell
python -m pip install pyinstaller
python -m PyInstaller asn1_viewer.spec --noconfirm
```

Output in `dist\`:

| File | Size | Purpose |
|------|------|---------|
| `ASN1Viewer.exe` | ~37 MB | GUI — double-click to open |
| `asn1viewcli.exe` | ~37 MB | CLI — copy to any Windows machine |

The executables are fully self-contained (Python + Qt bundled). Copy them to any machine — no installation required.

---

## Option D — Virtual environment (recommended for development)

```powershell
cd "path\to\Asn1Viewer"
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
python -m pip install -r requirements.txt
python -m pip install -e .
python main.py
```

---

## Dependencies

`requirements.txt`:
```
PyQt6==6.7.0
PyQt6-Qt6==6.7.0
PyQt6-sip>=13.6
```

The CLI (`asn1viewcli`) has **no additional dependencies** beyond the above — it does not import Qt at runtime.

---

## Verify installation

```powershell
# GUI opens without errors
python main.py

# CLI responds
asn1viewcli --help

# Parser imports correctly
python -c "from src.parser import BERDERParser; print('Parser OK')"
python -c "from src.parser.tag_filter import TagExtractor; print('Extractor OK')"
```

---

## macOS / Linux

Replace `python` with `python3` and `python -m pip` with `pip3` if needed:

```bash
cd /path/to/Asn1Viewer
pip3 install -r requirements.txt
pip3 install -e .
python3 main.py
asn1viewcli --help
```

**Linux display dependencies (Ubuntu/Debian):**
```bash
sudo apt-get install libxkbcommon0 libxcb-cursor0
```

---

## Uninstall

```powershell
# Remove the asn1viewcli command
python -m pip uninstall asn1-viewer

# Remove build artifacts
Remove-Item -Recurse dist, build, "*.egg-info"
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: PyQt6` | `python -m pip install -r requirements.txt` |
| `asn1viewcli: command not found` | Add Python Scripts directory to PATH (see Option B above) |
| `No module named PyInstaller` | `python -m pip install pyinstaller` |
| `BackendUnavailable` during `pip install -e .` | Ensure `setup.py` exists and `pyproject.toml` is absent |
| GUI won't open on Linux | Install `libxkbcommon0`; verify `echo $DISPLAY` is set |

---

## Next steps

- [QUICKSTART.md](QUICKSTART.md) — first steps with the GUI and CLI
- [CLI_GUIDE.md](CLI_GUIDE.md) — complete CLI reference
- [TAG_EXTRACTION.md](TAG_EXTRACTION.md) — tag definition file format
