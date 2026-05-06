# Quick Start Guide - ASN.1 Viewer

## Installation (5 minutes)

### Prerequisites
- Python 3.8 or higher from [python.org](https://www.python.org/)
- Internet connection for downloading packages

### Step 1: Install Python Dependencies

On **Windows** (Command Prompt):
```bash
pip install -r requirements.txt
```

On **macOS/Linux** (Terminal):
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python main.py
```

The ASN.1 Viewer window should open. You're ready to go!

## First Steps

### 1. Open an ASN.1 File
- Click the **"Open File"** button in the toolbar
- Select a `.der`, `.cer`, or `.asn1` file
- The file structure will appear in the left panel as a tree

### 2. Explore the Interface
- **Left Panel**: Hierarchical tree of ASN.1 tags
  - Click any tag to select it
  - Hex preview shown next to each tag
  
- **Right Upper Panel**: Hex Viewer
  - Shows raw bytes with offsets
  - Highlights bytes corresponding to selected tag
  
- **Right Lower Panel**: Detail View
  - Multiple tabs showing different representations
  - Select a node to see its details

### 3. Load a Grammar (Optional)
- Click **"Load Grammar"** button
- Click **"Create Sample Grammar"** to create a test file
- Or use the sample grammar in `resources/sample_grammar.csv`
- Tags will now show human-readable names

### 4. Search for Tags
- Type in the Search box to filter tags
- Example: `0x50` or `Application` or `50`
- Clear to see all tags again

### 5. Export Results
- Select **File → Export as Text/XML/JSON**
- Choose a location to save
- Your ASN.1 tree is now in the exported format

## Sample Files to Try

In `resources/` directory:
- `sample_grammar.csv` - Sample tag mappings (CSV format)
- `sample_grammar.json` - Sample tag mappings (JSON format)

Create your own ASN.1 file or use any existing `.der` or `.cer` file.

## Common Tasks

### Task: Find a Specific Tag
1. Click in the Search box
2. Type the tag hex code (e.g., `0x4F`)
3. Only matching tags shown
4. Click tag to see details

### Task: Export Entire File
1. Open ASN.1 file
2. Click **Export Text** button
3. Choose filename (e.g., `output.txt`)
4. File saved with hierarchical structure

### Task: Create Custom Grammar
1. Open a text editor
2. Create `my_grammar.csv`:
```
tag_id,name
0x4F,My Application ID
0x50,My Card Name
```
3. In ASN.1 Viewer, click **Load Grammar**
4. Browse to `my_grammar.csv`
5. Click Load

## Building Standalone Executable

### Windows:
```bash
build_windows.bat
```
Creates: `dist\ASN1Viewer\ASN1Viewer.exe`

### macOS/Linux:
```bash
chmod +x build.sh
./build.sh
```
Creates: `dist/ASN1Viewer/ASN1Viewer`

## Troubleshooting

**"ImportError: No module named 'PyQt6'"**
- Run: `pip install -r requirements.txt`
- Make sure you're in the project directory

**File won't open**
- Verify it's a valid BER/DER ASN.1 file
- Try a known-good file first
- Check file permissions

**Hex viewer shows nothing**
- File may have unusual encoding
- Try with a different ASN.1 file

**Grammar not loaded**
- Verify CSV/JSON file format
- Try "Create Sample Grammar" first
- Check file path is correct

## Testing

Run the test suite (optional):
```bash
python test_demo.py
```

This will:
1. Create sample ASN.1 data
2. Test the parser
3. Test grammar loading
4. Test export functionality

## Next Steps

### Learn More
- Read [README.md](README.md) for detailed documentation
- Explore `resources/` for sample grammars
- Check ASN.1 specifications for tag meanings

### Customize
- Create grammar files for your specific tags
- Extend export functionality (see README.md)
- Add support for custom ASN.1 types

### Use Cases
- Decode X.509 certificates (`.cer` files)
- Analyze EMV/ICC card data
- Inspect PKCS formats
- Reverse-engineer proprietary ASN.1 structures
- Validate ASN.1 encoding

## Support

For detailed help:
1. Check **Help → About** in application
2. Review [README.md](README.md)
3. Check `test_demo.py` for code examples

---

**You're all set!** Start by opening an ASN.1 file and exploring the tree.

Enjoy using ASN.1 Viewer! 🎉
