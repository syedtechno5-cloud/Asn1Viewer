# Installation Guide - ASN.1 Viewer

Complete installation instructions for all platforms and scenarios.

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager (included with Python)
- **Internet**: For downloading dependencies
- **RAM**: 500MB minimum, 1GB recommended
- **Disk Space**: 200MB for installation + dependencies

## ✅ Verify Python Installation

### Windows (Command Prompt)
```bash
python --version
pip --version
```

### macOS/Linux (Terminal)
```bash
python3 --version
pip3 --version
```

**Required output**: Python 3.8+ and pip 20.0+

### Install Python

If Python isn't installed:
1. Visit https://www.python.org/
2. Download Python 3.11 or newer
3. Run installer, **check "Add Python to PATH"**
4. Restart terminal/command prompt

## 🚀 Installation Methods

### Method 1: Quick Start (Recommended)

**Windows (Command Prompt):**
```bash
cd D:\Projects\IT Projects\Syed Technologies\Asn1Viewer
pip install -r requirements.txt
python main.py
```

**macOS/Linux (Terminal):**
```bash
cd ~/Projects/Asn1Viewer
pip3 install -r requirements.txt
python3 main.py
```

### Method 2: Virtual Environment (Recommended for Development)

**Windows:**
```bash
cd D:\Projects\IT Projects\Syed Technologies\Asn1Viewer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**macOS/Linux:**
```bash
cd ~/Projects/Asn1Viewer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### Method 3: Package Installation

**All Platforms:**
```bash
cd /path/to/Asn1Viewer
pip install -e .
asn1-viewer
```

This makes ASN1 Viewer available system-wide.

### Method 4: Standalone Executable

**Windows:**
```bash
cd D:\Projects\IT Projects\Syed Technologies\Asn1Viewer
build_windows.bat
```

Executable: `dist\ASN1Viewer\ASN1Viewer.exe`

**macOS:**
```bash
cd ~/Projects/Asn1Viewer
chmod +x build.sh
./build.sh
```

Executable: `dist/ASN1Viewer/ASN1Viewer`

**Linux:**
```bash
cd ~/Projects/Asn1Viewer
chmod +x build.sh
./build.sh
```

Executable: `dist/ASN1Viewer/ASN1Viewer`

## 🐛Troubleshooting Installation

### Issue: "Python not found"
**Solution:**
- Python not in PATH
- Run installer again, check "Add Python to PATH"
- Use `python -V` to verify
- Restart command prompt/terminal

### Issue: "ModuleNotFoundError: PyQt6"
**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Permission denied" (macOS/Linux)
**Solution:**
```bash
chmod +x build.sh
chmod +x main.py
sudo pip install -r requirements.txt  # If needed
```

### Issue: "Build failed"
**Solution:**
```bash
pip install --upgrade pyinstaller
pip install pyinstaller
pyinstaller asn1_viewer.spec --onefile
```

### Issue: "Virtual environment not activating"
**Windows:**
```bash
venv\Scripts\activate.bat  # Use .bat, not .ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Issue: "Port already in use" (if running webserver)
**Solution:** Use different port or check for existing processes

### Issue: GUI window won't open
**Windows:**
- Check Display Settings → Scaling
- Try: `python -m PyQt6.qsci`

**macOS:**
- Check XQuartz installation
- May need: `pip install PyQt6-Qt6`

**Linux:**
- Ensure display server available: `echo $DISPLAY`
- Install: `sudo apt-get install libxkbcommon0`

## 📦 Dependencies

The `requirements.txt` file contains:
```
PyQt6==6.7.0
PyQt6-Qt6==6.7.0
PyQt6-sip==13.8.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

Or individually:
```bash
pip install PyQt6==6.7.0
pip install PyQt6-Qt6==6.7.0
pip install PyQt6-sip==13.8.0
```

## ✨ Verification

After installation, verify everything works:

### Test 1: Import modules
```bash
python -c "import PyQt6; print('PyQt6 OK')"
python -c "from src.parser import BERDERParser; print('Parser OK')"
```

### Test 2: Run test suite
```bash
python test_demo.py
```

Expected output:
```
============================================================
ASN.1 Viewer - Test Suite
============================================================

======== TEST 1: ASN.1 Parser ========
✓ Parse successful!
  Root tag: [UNIVERSAL CONSTRUCTED] #16
  ...

======== TEST 2: Grammar Manager ========
✓ Grammar loaded!
  Mappings: 3
  ...

======== TEST 3: Export Functionality ========
✓ All exports completed successfully!
...
```

### Test 3: Run application
```bash
python main.py
```

The ASN.1 Viewer window should open with:
- Toolbar with Open, Load Grammar, Search buttons
- Empty tree view (left)
- Empty hex viewer (right)
- Empty detail tabs (bottom right)

## 🎯 Platform-Specific Notes

### Windows

**Requirements:**
- Windows 7 SP1 or later
- Visual C++ Runtime (may be needed)

**Installation:**
```bash
pip install -r requirements.txt
python main.py
```

**Known Issues:**
- High DPI scaling may affect display
- Windows Defender may slow first run
- Antivirus may block executable building

**Solution:**
- Disable temporary High DPI scaling test
- Add to Defender exclusions
- Whitelist pyinstaller

### macOS

**Requirements:**
- macOS 10.12 or later
- May need: `xcode-select --install`

**Installation:**
```bash
pip3 install -r requirements.txt
python3 main.py
```

**Build DMG:**
```bash
./build.sh
hdiutil create -volname ASN1Viewer -srcfolder dist/ASN1Viewer -ov -format UDZO ASN1Viewer.dmg
```

### Linux

**Requirements:**
- Ubuntu 18.04+ or equivalent
- X11 or Wayland display

**Installation:**
```bash
sudo apt-get install python3 python3-pip
pip3 install -r requirements.txt
python3 main.py
```

**Common issues:**
- Missing libraries: `sudo apt-get install libxkbcommon0`
- Display issues: Check X server with `echo $DISPLAY`

## 🔄 Updating

### Update dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Update application
```bash
cd /path/to/Asn1Viewer
git pull  # If using git
pip install -e . --upgrade
```

## 🗑️ Uninstallation

### Remove virtual environment
```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

### Remove installed package
```bash
pip uninstall asn1-viewer
```

### Remove executables
```bash
# Windows
rmdir /s dist build *.egg-info

# macOS/Linux
rm -rf dist build *.egg-info
```

## 🆘 Support

### Check installation
```bash
pip list | grep -i pyqt
python -c "import sys; print(sys.version)"
```

### Detailed diagnostic
```bash
python -c "
import sys
import PyQt6
from src.parser import BERDERParser
print('Python:', sys.version)
print('PyQt6:', PyQt6.__version__)
print('All imports successful!')
"
```

### Report issues with:
- Python version: `python --version`
- PyQt6 version: `pip show PyQt6`
- OS and version: `System Information`
- Output of `pip list`
- Full error message

## 📚 Next Steps

1. **Quick Start**: See `QUICKSTART.md`
2. **Full Guide**: See `README.md`
3. **Code Structure**: See `PROJECT_INDEX.md`
4. **Test Suite**: Run `python test_demo.py`
5. **Open Application**: Run `python main.py`

## ⚙️ Advanced Configuration

### Custom Python Path
```bash
/usr/bin/python3 main.py  # Use specific Python
```

### Debug Mode (for development)
```bash
python -u main.py  # Unbuffered output
```

### With Profiling
```bash
python -m cProfile -s cumtime main.py
```

### Memory Usage
```bash
python -m memory_profiler main.py  # Requires: pip install memory-profiler
```

## 🎓 Learning Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [ASN.1 Standard (X.680)](https://www.itu.int/rec/T-REC-X.680/en)

## ✅ Checklist

After installation, verify:
- [ ] Python 3.8+ installed
- [ ] pip working (`pip --version`)
- [ ] dependencies installed (`pip list | grep PyQt6`)
- [ ] Application starts (`python main.py`)
- [ ] Test suite passes (`python test_demo.py`)
- [ ] Sample grammar loads
- [ ] Can open test files
- [ ] Export functions work

---

**Installation complete!** 🎉

Proceed to `QUICKSTART.md` for first steps.
