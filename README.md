# ASN.1 Viewer - Complete BER/DER ASN.1 File Decoder

A modern, cross-platform application for viewing, analyzing, and exporting ASN.1 (Abstract Syntax Notation One) files encoded in BER (Basic Encoding Rules) or DER (Distinguished Encoding Rules) format.

## Features

### Core Functionality
- **BER/DER Parser**: Recursive parser that correctly decodes ASN.1 TLV (Tag-Length-Value) structures
- **Hierarchical Tree View**: Display nested ASN.1 structure with proper indentation and nesting
- **Synchronized Hex Viewer**: View raw hex data with byte-level precision
- **Byte Highlighting**: Clicking tree nodes highlights corresponding bytes in hex viewer

### Grammar Support
- **Grammar Files**: Load CSV or JSON files mapping tag IDs to human-readable names
- **Live Grammar Application**: Grammar names appear in tree view for easier interpretation
- **Sample Grammars**: Includes sample grammar files with common ASN.1 and EMV tags

### Export Capabilities
- **Text Export**: Hierarchical text representation with all details
- **XML Export**: Generate valid XML from ASN.1 structure
- **JSON Export**: Complete JSON representation of tree

### User Interface
- **Modern Design**: Clean, professional interface similar to file explorers
- **Search/Filter**: Find specific tags or names in the tree
- **Responsive Layout**: Efficient handling of large files with thread-based parsing
- **Visual Indicators**: Constructed tags shown in bold, leaf nodes clearly distinguished

### Advanced Features
- **Context Menu**: Right-click options for copy, export, search
- **Quick Preview**: Hex preview in tree view for quick data inspection
- **Tabbed Detail View**: Multiple representations (Hex, Text, XML, JSON) of selected node
- **Large File Support**: Warning for files >10MB with optimized parsing

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt6

### From Source

1. Clone or extract the project:
```bash
cd ASN1Viewer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

### Building Standalone Executable

#### Windows (.exe)
```bash
pip install pyinstaller
pyinstaller asn1_viewer.spec
```

The executable will be in the `dist/ASN1Viewer` directory.

#### macOS
```bash
pip install pyinstaller
pyinstaller asn1_viewer.spec
cd dist
hdiutil create -volname ASN1Viewer -srcfolder ASN1Viewer -ov -format UDZO ASN1Viewer.dmg
```

#### Linux
```bash
pip install pyinstaller
pyinstaller asn1_viewer.spec
# Binary in dist/ASN1Viewer/ASN1Viewer
```

## Usage

### Opening an ASN.1 File
1. Click **Open File** button or use **File → Open**
2. Select a `.der`, `.cer`, `.asn1`, or other ASN.1 file
3. The parser will load and display the file structure

### Understanding the Interface

**Left Pane - Tree View:**
- Shows hierarchical structure of ASN.1 tags
- **Bold items** = Constructed tags (contain other tags)
- Regular items = Primitive tags (contain data)
- Click a tag to select it

**Right Upper Pane - Hex Viewer:**
- Shows raw hex data from the file
- **Highlighted bytes** = Selected tree node
- Displays byte offsets on left, hex values in middle, ASCII on right

**Right Lower Pane - Detail View:**
- **Hex Tab**: Detailed hex dump of selected node with metadata
- **Text Hierarchy Tab**: Hierarchical text representation
- **XML Tab**: XML representation of the node and children
- **JSON Tab**: JSON representation

### Loading a Grammar File

Grammar files map tag hex values to human-readable names.

1. Click **Load Grammar** button
2. Choose **Browse** to select a grammar file, or
3. Click **Create Sample Grammar** to generate a template
4. Click **Load** to apply the grammar

#### Grammar File Formats

**CSV Format:**
```csv
tag_id,name
0x4F,Application Identifier
0x50,Card Holder Name
0x5A,Application PAN
```

**JSON Format:**
```json
{
  "0x4F": "Application Identifier",
  "0x50": "Card Holder Name",
  "0x5A": "Application PAN"
}
```

Tag IDs can be specified as:
- Hex with prefix: `0x4F`, `0x50`
- Hex without prefix: `4F`, `50`
- Decimal: `79`, `80`

### Searching Tags

1. Type in the **Search** field (e.g., `Application`, `0x4F`, `79`)
2. Tree view filters to show only matching tags
3. Clear the search to show all tags again

### Exporting Data

#### Export as Text
1. Select **File → Export as Text** or click **Export Text** button
2. Choose location and filename
3. Saves hierarchical text representation with all metadata

#### Export as XML
1. Select **File → Export as XML** or click **Export XML** button
2. Choose location and filename
3. Generates valid XML with full tree structure
4. Each node becomes an element with metadata as attributes

#### Export as JSON
1. Select **File → Export as JSON**
2. Choose location and filename
3. Generates JSON with complete tree representation

### Using Context Menu
Right-click on a tree node to see options:
- Copy tag information
- Export this subtree
- Search for similar tags

## Architecture

### Project Structure
```
Asn1Viewer/
├── src/
│   ├── parser/              # ASN.1 parsing engine
│   │   ├── ber_der_parser.py   # Main BER/DER decoder
│   │   └── asn1_types.py       # ASN.1 type definitions
│   ├── grammar/             # Grammar file handling
│   │   └── grammar_manager.py  # Grammar loader and mapper
│   ├── gui/                 # PyQt6 GUI components
│   │   ├── main_window.py      # Main application window
│   │   ├── tree_view.py        # Hierarchical tree widget
│   │   ├── hex_viewer.py       # Hex display widget
│   │   ├── detail_view.py      # Tabbed detail view
│   │   └── grammar_dialog.py   # Grammar load dialog
│   ├── export/              # Export functionality
│   │   └── exporter.py         # Export to Text/XML/JSON
│   └── utils/               # Utility functions
│       └── __init__.py         # Helper functions
├── resources/               # Sample files
│   ├── sample_grammar.csv   # Sample CSV grammar
│   └── sample_grammar.json  # Sample JSON grammar
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── asn1_viewer.spec        # PyInstaller configuration
└── README.md               # This file
```

### Key Components

#### BER/DER Parser (`parser/ber_der_parser.py`)
- Recursive TLV parser
- Handles both short and long form length encoding
- Supports single and multi-byte tag encoding
- Proper error handling and validation

#### ASN.1 Types (`parser/asn1_types.py`)
- `ASN1Tag`: Represents a single ASN.1 tag with class, constructed flag, and number
- `ASN1Node`: Represents complete TLV node with children, parent references, and grammar support
- Tag class constants and universal tag mappings

#### Grammar Manager (`grammar/grammar_manager.py`)
- Loads CSV and JSON format grammar files
- Normalizes tag ID formats (hex, decimal)
- Provides lookup methods for tag names

#### Exporter (`export/exporter.py`)
- Exports to text with hierarchical indentation
- Generates valid XML with attributes and proper structure
- Creates JSON representation
- Recursive tree traversal

#### GUI Components
- **MainWindow**: Application window, file handling, threading
- **TreeWidget**: Hierarchical tree display with filtering
- **HexViewer**: Hex display with byte highlighting
- **DetailView**: Tabbed view with multiple representations
- **GrammarDialog**: Grammar file selection and loading

## File Format Support

### Supported Extensions
- `.der` - Distinguished Encoding Rules (most common)
- `.cer` - Certificate files (DER encoded)
- `.asn1` / `.asn` - Generic ASN.1 files
- `.dn` / `.ans` - Other ASN.1 variants

### File Size Handling
- **< 1 MB**: Instant parsing
- **1-10 MB**: Fast parsing with progress indicator
- **> 10 MB**: User warning, proceeding with threaded parser

Large files are parsed on a background thread to prevent UI freezing.

## Common Tag Examples

### Universal Tags
| Hex | Decimal | Name |
|-----|---------|------|
| 0x02 | 2 | INTEGER |
| 0x04 | 4 | OCTET STRING |
| 0x06 | 6 | OBJECT IDENTIFIER |
| 0x10 | 16 | SEQUENCE |
| 0x11 | 17 | SET |

### EMV/ICC Tags (Examples)
| Hex | Name |
|-----|------|
| 0x4F | Application Identifier |
| 0x50 | Cardholder Name |
| 0x5A | Application PAN |
| 0x9F02 | Amount |
| 0x9F26 | Cryptogram |

## Troubleshooting

### File Won't Open
- Verify it's a valid BER/DER encoded file
- Check that the application has read permissions
- Try with a known-good sample file first

### Tree View Seems Empty
- File might not have valid ASN.1 structure
- Try increasing UI responsiveness with search filter
- Check hex viewer to see raw data

### Grammar Names Not Showing
1. Verify grammar file is loaded (status bar should show count)
2. Ensure tag IDs in grammar file match file's tags
3. Try creating sample grammar and loading it

### Performance Issues with Large Files
- Files > 100MB may show parsing slowdown
- Use search filter to focus on specific tags
- Export specific subtree instead of entire file

## Development Notes

### Extending the Application

#### Add New Export Format
1. Add method to `Exporter` class in `export/__init__.py`
2. Add tab to `DetailView` in `gui/detail_view.py`
3. Add menu option to `MainWindow` in `gui/main_window.py`

#### Add New Grammar Format
1. Add loader method to `GrammarManager` in `grammar/__init__.py`
2. Update file dialog filters in `GrammarDialog` in `gui/grammar_dialog.py`

#### Customize Tag Display
1. Modify `ASN1Node.get_display_name()` in `parser/asn1_types.py`
2. Update tree rendering in `ASN1TreeWidget._add_node_recursive()` in `gui/tree_view.py`

### Performance Optimization Tips
- Use threading for files > 1MB (already implemented)
- Implement lazy loading for very large trees (future enhancement)
- Cache parsed results for repeated access
- Use streaming XML export for very large files

## Security Considerations

- Only load grammar files from trusted sources
- Hex viewer doesn't interpret embedded code
- No network access or external resource loading
- File permissions respected (read-only for loaded files)

## License

© 2024 Syed Technologies. All rights reserved.

## Support

For issues, feature requests, or questions:
1. Check this README for solutions
2. Review sample files in `resources/` directory
3. Check application status bar for error messages
4. Refer to ASN.1 specification (X.680) for tag definitions

## Future Enhancements

- [ ] Template/Schema matching against loaded ASN.1 schemas
- [ ] Lazy loading for very large files (100MB+)
- [ ] Edit and re-encode functionality
- [ ] Batch file processing
- [ ] Comparison between two files
- [ ] Custom visualization for specific ASN.1 types
- [ ] Plugin system for domain-specific grammars
- [ ] Dark mode UI theme
- [ ] Keyboard navigation improvements
- [ ] Multi-file tab support

## Technical Details

### Supported ASN.1 Features
- ✓ Primitive tags
- ✓ Constructed tags
- ✓ Short form length (0-127)
- ✓ Long form length (128+)
- ✓ Single-byte tags
- ✓ Multi-byte tags
- ✓ Universal, Application, Context, and Private tag classes

### Not Supported (Yet)
- Indefinite length encoding
- Constructed encodings of primitive types
- Schema validation
- Custom type definitions

---

**Version**: 1.0.0  
**Last Updated**: May 2024  
**Platform**: Windows, macOS, Linux  
**Python**: 3.8+  
**GUI Framework**: PyQt6
