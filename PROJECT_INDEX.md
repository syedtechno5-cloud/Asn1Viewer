# ASN.1 Viewer - Project Structure & Index

## 📁 Directory Overview

```
Asn1Viewer/
├── 📄 README.md                  # Complete documentation
├── 📄 QUICKSTART.md              # Quick start guide (5 min setup)
├── 📄 main.py                    # Application entry point
├── 📄 setup.py                   # Package setup for installation
├── 📄 requirements.txt           # Python dependencies
├── 📄 test_demo.py              # Test suite and examples
├── 📄 asn1_viewer.spec          # PyInstaller configuration
├── 🔨 build_windows.bat          # Build script for Windows
├── 🔨 build.sh                   # Build script for macOS/Linux
│
├── 📂 src/                       # Main application source
│   ├── __init__.py
│   │
│   ├── 📂 parser/                # BER/DER ASN.1 parsing engine
│   │   ├── ber_der_parser.py     # Main parser - recursive TLV decoder
│   │   └── asn1_types.py         # Data structures (ASN1Node, ASN1Tag)
│   │
│   ├── 📂 grammar/               # Grammar file handling
│   │   ├── grammar_manager.py    # Load and manage tag mappings
│   │   └── __init__.py
│   │
│   ├── 📂 gui/                   # User interface (PyQt6)
│   │   ├── main_window.py        # Main application window
│   │   ├── tree_view.py          # Hierarchical tree widget
│   │   ├── hex_viewer.py         # Hex display widget
│   │   ├── detail_view.py        # Tabbed detail panel
│   │   ├── grammar_dialog.py     # Grammar loader dialog
│   │   └── __init__.py
│   │
│   ├── 📂 export/                # Export functionality
│   │   ├── exporter.py           # Export to Text/XML/JSON
│   │   └── __init__.py
│   │
│   └── 📂 utils/                 # Utility functions
│       ├── __init__.py           # Helper utilities
│       └── helpers.py            # (additional helpers)
│
└── 📂 resources/                 # Sample files & data
    ├── sample_grammar.csv        # Sample grammar (CSV format)
    └── sample_grammar.json       # Sample grammar (JSON format)
```

## 🎯 Key Modules Explained

### Parser Module (`src/parser/`)
**Purpose**: Decode binary BER/DER encoded ASN.1 files

**Files**:
- `ber_der_parser.py` (350+ lines)
  - Recursive BER/DER parser
  - Handles TLV (Tag-Length-Value) structure
  - Supports multi-byte tags and long-form length
  - Error handling and validation
  
- `asn1_types.py` (150+ lines)
  - `ASN1Tag`: Represents individual ASN.1 tags
  - `ASN1Node`: Complete node with children/parent references
  - Tag class definitions and universal tag mappings

**Key Methods**:
- `parse()`: Parse entire file, return root node
- `find_node_by_offset()`: Find node at specific byte offset
- `_parse_tlv()`: Parse single Tag-Length-Value triplet

### Grammar Module (`src/grammar/`)
**Purpose**: Map tag hex IDs to human-readable names

**Files**:
- `grammar_manager.py` (200+ lines)
  - Load CSV format grammars
  - Load JSON format grammars
  - Auto-detect format
  - Normalize tag ID formats (hex, decimal)

**Key Methods**:
- `load_csv()`: Load from CSV file
- `load_json()`: Load from JSON file
- `get_name()`: Lookup tag name by hex ID
- `create_sample_grammar()`: Generate sample grammar file

### GUI Module (`src/gui/`)
**Purpose**: PyQt6-based user interface

**Files**:
- `main_window.py` (500+ lines)
  - Main application window
  - File loading and parsing (threaded)
  - Menu bar and toolbar
  - Signals and slots for inter-component communication
  
- `tree_view.py` (300+ lines)
  - Hierarchical tree widget
  - Node filtering/search
  - Click-to-select functionality
  - Custom context menu
  
- `hex_viewer.py` (200+ lines)
  - Hex display with formatting
  - Byte offset highlighting
  - ASCII preview column
  - Syntax highlighting support
  
- `detail_view.py` (300+ lines)
  - Tabbed widget (Hex, Text, XML, JSON)
  - Different representations of selected node
  - Export each tab to file
  
- `grammar_dialog.py` (180+ lines)
  - Grammar file selection dialog
  - Preview of grammar content
  - Sample grammar generation

### Export Module (`src/export/`)
**Purpose**: Export ASN.1 trees to various formats

**Files**:
- `exporter.py` (350+ lines)
  - Export to hierarchical text
  - Export to XML (valid XML output)
  - Export to JSON
  - Search nodes by criteria

**Key Methods**:
- `to_text()`: Text representation
- `to_xml()`: XML representation
- `to_json()`: JSON representation
- `search_and_export()`: Find and export specific node

### Utils Module (`src/utils/`)
**Purpose**: Helper and utility functions

**Files**:
- `__init__.py` (100+ lines)
  - Hex formatting utilities
  - File size detection
  - Filename sanitization
  - Large file detection

## 🚀 Getting Started

### Option 1: Quick Start (Recommended)
```bash
pip install -r requirements.txt
python main.py
```
See `QUICKSTART.md` for detailed instructions.

### Option 2: Build Standalone Executable
```bash
# Windows
build_windows.bat

# macOS/Linux
chmod +x build.sh
./build.sh
```

### Option 3: Install as Package
```bash
pip install -e .
# Can now run from anywhere
asn1-viewer
```

## 📊 File Statistics

| Component | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| Parser | 2 | 500+ | BER/DER decoding |
| Grammar | 1 | 200+ | Tag name mapping |
| GUI | 5 | 1300+ | User interface |
| Export | 1 | 350+ | Export functionality |
| Utils | 2 | 100+ | Helpers |
| **Total** | **11** | **2500+** | Complete app |

## 🔄 Data Flow

```
ASN.1 File (*.der, *.cer)
        |
        v
  BERDERParser
        |
        v
  ASN1Node Tree
        |
        +----> TreeWidget (display)
        |
        +----> HexViewer (highlight)
        |
        +----> DetailView (tabs)
        |
        v
  Exporter (Text/XML/JSON)
        |
        v
  Output File
```

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────┐
│  ASN.1 Viewer                                       │
├─────────────────────────────────────────────────────┤
│ [Open] [Load Grammar] [Search: ________] [Export...]│
├────────────────────┬─────────────────────────────────┤
│   Tree View        │   Hex Viewer                    │
│                    │                                 │
│ SEQUENCE           │ 0000  30 0C 02 01 2A 04 05      │
│  ├─INTEGER         │ 0010  48 65 6C 6C 6F           │
│  └─OCTET STRING    │                                 │
│                    ├─────────────────────────────────┤
│                    │   Detail View (Tabs)            │
│                    │ [Hex][Text][XML][JSON]         │
│                    │                                 │
│                    │ <Node details shown here>      │
└────────────────────┴─────────────────────────────────┘
```

## 💾 Sample Grammar Formats

### CSV Format
```csv
tag_id,name
0x4F,Application Identifier
0x50,Card Holder Name
0x5A,Application PAN
```

### JSON Format
```json
{
  "0x4F": "Application Identifier",
  "0x50": "Card Holder Name",
  "0x5A": "Application PAN"
}
```

## 🧪 Testing

Run the test suite:
```bash
python test_demo.py
```

This tests:
1. ✅ BER/DER parser with sample data
2. ✅ Grammar loading and application
3. ✅ Export functionality (Text/XML/JSON)

## 📝 File Formats

### Supported Input
- `.der` - Distinguished Encoding Rules (most common)
- `.cer` - Certificate files
- `.asn1` / `.asn` - Generic ASN.1 files
- `.dn` / `.ans` - Other variants

### Supported Export
- `.txt` - Hierarchical text format
- `.xml` - Valid XML format
- `.json` - JSON format

### Grammar Files
- `.csv` - CSV format
- `.json` - JSON format

## 🔧 Extending the Application

### Add New Export Format
1. Add method to `Exporter` class
2. Add tab to `DetailView`
3. Add menu item to main window

### Add New Grammar Format
1. Add loader to `GrammarManager`
2. Update dialog file filters
3. Handle in auto-detect

### Customize Display
1. Modify `ASN1Node.get_display_name()`
2. Adjust tree rendering in `TreeWidget`
3. Update hex labels in `HexViewer`

## 🐛 Debugging

### Enable Verbose Output
Modify `main_window.py` in `_on_parse_error()` to see detailed error messages.

### Check Parser Issues
Run `test_demo.py` to verify parser works correctly.

### Grammar Problems
- Verify format (CSV vs JSON)
- Check tag ID formats
- Load sample grammar to verify it works

## ⚙️ System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.8+
- **Memory**: 500MB minimum
- **Disk**: 100MB (including dependencies)
- **Screen**: 1000x700+ recommended

## 📚 Documentation

- `README.md` - Complete reference documentation
- `QUICKSTART.md` - 5-minute setup guide
- Code comments - Inline documentation
- Type hints - Function signatures

## 🎓 Learning Resources

- ASN.1 Specification: X.680 standard
- BER/DER Encoding: X.690 standard
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- EMV Specifications: For tag meanings in payment cards

---

**Version**: 1.0.0  
**Language**: Python 3.8+  
**GUI Framework**: PyQt6  
**License**: © 2024 Syed Technologies

For complete documentation, see `README.md`
