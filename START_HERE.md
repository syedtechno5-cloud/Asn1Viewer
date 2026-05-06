# 🚀 START HERE - ASN.1 Viewer

**Welcome to ASN.1 Viewer!** A professional-grade, cross-platform application for decoding and analyzing BER/DER encoded ASN.1 files.

## ⚡ Quick Start (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python main.py
```

✅ Done! The ASN.1 Viewer window is now open.

## 📖 Choose Your Path

### 👤 I'm a User - I want to use the application
**→ Read: [QUICKSTART.md](QUICKSTART.md)** (5 min read)
- Open and view ASN.1 files
- Load grammar files
- Export data
- Search and filter

### 🔧 I'm a Developer - I want to install or extend
**→ Read: [INSTALLATION.md](INSTALLATION.md)** (10 min read)
- Installation options
- Virtual environment setup
- Building executables
- Troubleshooting

### 👨‍💻 I'm a Developer - I want to modify the code
**→ Read: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** (15 min read)
- Architecture overview
- How to extend features
- Code organization
- Development workflow

### 📚 I want comprehensive documentation
**→ Read: [README.md](README.md)** (30 min read)
- Complete feature list
- All capabilities
- Architecture details
- Advanced usage

### 🗺️ I want to understand the project structure
**→ Read: [PROJECT_INDEX.md](PROJECT_INDEX.md)** (15 min read)
- File organization
- Module descriptions
- Data flow
- Component details

## ✨ What Can I Do?

### ✅ Parse ASN.1 Files
- Open BER/DER encoded files (.der, .cer, .asn1, etc.)
- View hierarchical structure
- See byte-level details

### ✅ Add Grammar Support
- Load CSV or JSON grammar files
- Map tag hex IDs to human-readable names
- Use sample grammars included

### ✅ Search & Filter
- Find specific tags quickly
- Filter by name or hex ID
- Navigate large files easily

### ✅ Export Data
- Export to formatted text
- Generate valid XML
- Create JSON representations
- Preserve structure and hierarchy

### ✅ Inspect Data
- View hex dumps with offsets
- See ASCII representation
- Highlight byte ranges
- Display tag metadata

## 📁 What's Included?

```
✅ Complete Application
   - Full BER/DER parser
   - Professional GUI
   - Grammar support
   - Export engine

✅ Documentation
   - User guides
   - Installation guide
   - Developer guide
   - Code examples

✅ Resources
   - Sample grammars
   - Build scripts
   - Test suite

✅ Build Tools
   - PyInstaller config
   - Windows/Unix scripts
   - Package setup
```

## 🎯 Get Started Now

### Option 1: Quick Test (No Installation)
```bash
python test_demo.py
```
This runs the test suite and shows how the parser works.

### Option 2: Run the Application
```bash
pip install -r requirements.txt
python main.py
```
Opens the ASN.1 Viewer GUI.

### Option 3: Build Standalone Executable
```bash
# Windows
build_windows.bat

# macOS/Linux
chmod +x build.sh
./build.sh
```
Creates and executable you can distribute.

## 📚 Documentation Map

| Document | Purpose | Time | For |
|----------|---------|------|-----|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 min | 5 min | Users |
| [INSTALLATION.md](INSTALLATION.md) | Install & setup | 10 min | Installers |
| [README.md](README.md) | Complete reference | 30 min | Everyone |
| [PROJECT_INDEX.md](PROJECT_INDEX.md) | Project structure | 15 min | Developers |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | What's included | 5 min | Decision makers |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | Extend & modify | 20 min | Developers |
| [FILE_MANIFEST.md](FILE_MANIFEST.md) | File listing | 10 min | Reference |

## 🆘 Having Issues?

### I can't install Python
- Download from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH"
- See [INSTALLATION.md](INSTALLATION.md) for details

### Dependencies won't install
- Check internet connection
- Run: `pip install --upgrade pip`
- Then: `pip install -r requirements.txt`
- See "Troubleshooting" in [INSTALLATION.md](INSTALLATION.md)

### Application won't open
- Verify installation: `python test_demo.py`
- Check dependencies: `pip list | grep PyQt6`
- See [README.md](README.md) troubleshooting section

### I don't understand how to use it
- Start with [QUICKSTART.md](QUICKSTART.md)
- Follow the step-by-step guide
- Look at examples in [README.md](README.md)

## 💡 Tips & Tricks

### Tip 1: Use Sample Grammar
```bash
# In the app: Load Grammar → Create Sample Grammar
# Generates ready-to-use grammar file
```

### Tip 2: Search Filters
```
0x4F        → Find tag 0x4F
Application → Find tags named "Application"
50          → Find tag by decimal number
```

### Tip 3: Keyboard Shortcuts
- `Ctrl+O` - Open file
- `Ctrl+Q` - Quit
- `Ctrl+F` - Search
- `Ctrl+E` - Export

### Tip 4: Large Files
- Program warns if file > 10MB
- Parsing happens in background
- UI stays responsive

## 🎓 Learn More

### ASN.1 Resources
- [ITU-T X.680 Specification](https://www.itu.int/rec/T-REC-X.680/)
- [X.690 BER/DER Encoding](https://www.itu.int/rec/T-REC-X.690/)

### Python Resources
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Python Guide](https://docs.python.org/3/)

### Specific Topics
- Certificates (.cer files) →See README - X.509
- EMV/Payment Cards → See README - EMV Tags
- Custom ASN.1 Types → See DEVELOPER_GUIDE

## 🚀 Next Steps

1. **Right Now**
   - [ ] Read QUICKSTART.md (5 min)
   - [ ] Run `python test_demo.py`
   - [ ] Check Python installed: `python --version`

2. **In 10 Minutes**
   - [ ] Install dependencies: `pip install -r requirements.txt`
   - [ ] Run app: `python main.py`
   - [ ] Open a sample ASN.1 file

3. **Later**
   - [ ] Read full [README.md](README.md)
   - [ ] Load sample grammar
   - [ ] Try different export formats
   - [ ] Build standalone executable

4. **When Ready**
   - [ ] Create custom grammar files
   - [ ] Integrate with other tools
   - [ ] Extend with custom features

## ✅ Verification

### Check Installation
```bash
python -c "import PyQt6; print('✓ PyQt6 OK')"
python -c "from src.parser import BERDERParser; print('✓ Parser OK')"
```

### Run Tests
```bash
python test_demo.py
```

Expected: All tests pass with ✓ symbols

### Launch Application
```bash
python main.py
```

Expected: Window opens with empty tree view

## 📞 Support

**For Common Issues**: See [INSTALLATION.md](INSTALLATION.md) - Troubleshooting

**For Detailed Help**: See [README.md](README.md) - Troubleshooting

**For Dev Questions**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

**For File Details**: See [FILE_MANIFEST.md](FILE_MANIFEST.md)

## 🎉 You're Ready!

### Summary
- ✅ Application ready to use
- ✅ Comprehensive documentation available
- ✅ Sample files included
- ✅ Build scripts provided
- ✅ Test suite included

### Next: Choose your path from "📖 Choose Your Path" section above

---

## Quick Reference

```bash
# Install
pip install -r requirements.txt

# Run
python main.py

# Test
python test_demo.py

# Build (Windows)
build_windows.bat

# Build (macOS/Linux)
./build.sh

# Install as package
pip install -e .

# Run from anywhere (after package install)
asn1-viewer
```

---

**Questions?** Start with [QUICKSTART.md](QUICKSTART.md)

**Want details?** Read [README.md](README.md)

**Ready to code?** See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

**Enjoy! 🎉**

---

**ASN.1 Viewer v1.0.0** | Python 3.8+ | Cross-Platform
