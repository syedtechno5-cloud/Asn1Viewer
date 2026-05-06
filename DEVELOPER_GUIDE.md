# Developer's Guide - ASN.1 Viewer

Guide for developers who want to extend, modify, or contribute to the ASN.1 Viewer project.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              PyQt6 GUI Layer                        │
│  (main_window.py, tree_view.py, hex_viewer.py, etc) │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│          Business Logic Layer                       │
│  (exporter.py, grammar_manager.py)                  │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│           Parser Core Layer                         │
│  (ber_der_parser.py, asn1_types.py)                 │
└─────────────────────────────────────────────────────┘
```

## 📝 Code Organization

### Parser Module (`src/parser/`)

**ber_der_parser.py** - Recursive BER/DER parser

Key classes:
- `BERDERParser`: Main parser class
  - `parse()`: Entry point
  - `parse_all_nodes()`: Parse multiple top-level nodes
  - `_parse_tlv()`: Parse single TLV triplet
  - `_parse_tag()`: Extract tag byte(s)
  - `_parse_length()`: Extract length byte(s)
  - `_parse_children()`: Recursively parse children

Extending:
- Add support for indefinite length: Modify `_parse_length()`
- Custom tag processing: Override `_parse_tlv()`
- New encoding support: Extend `BERDERParser` class

**asn1_types.py** - Data structures

Key classes:
- `ASN1Tag`: Represents a tag
  - Fields: `tag_class`, `constructed`, `tag_number`, `raw_byte`
  - Methods: `__str__()`, `get_hex_str()`

- `ASN1Node`: Represents a TLV node
  - Fields: `tag`, `length`, `value`, `offset*`, `children`, `parent`, `grammar_name`
  - Methods: `is_constructed()`, `get_display_name()`, `get_preview()`, `total_length()`

Extending:
- Add custom fields to `ASN1Node` for specialized applications
- Create subclasses for specific ASN.1 types
- Add serialization methods for custom formats

### Grammar Module (`src/grammar/`)

**grammar_manager.py** - Grammar file handling

Key class:
- `GrammarManager`: Manages tag ID → name mappings
  - `load_csv()`: Load from CSV
  - `load_json()`: Load from JSON
  - `load_file()`: Auto-detect format
  - `get_name()`: Lookup by tag ID
  - `create_sample_grammar()`: Generate template

Extending:
- Add YAML format: Implement `load_yaml()`
- Add database support: Create `load_from_db()`
- Add remote sources: Implement `load_from_url()`
- Custom normalization: Modify `_normalize_and_add()`

### GUI Modules (`src/gui/`)

**main_window.py** - Application controller

Key class:
- `ASN1ViewerMainWindow`: Main window
  - `_load_file()`: File loading pipeline
  - `_on_node_selected()`: Handle tree selection
  - `_apply_grammar()`: Apply grammar to tree

Extending:
- Add file drag-and-drop: Override `dragEnterEvent()`, `dropEvent()`
- Add recent files menu: Track in config file
- Add preferences dialog: Create `SettingsDialog` class

**tree_view.py** - Hierarchical tree display

Key class:
- `ASN1TreeWidget`: Custom tree widget
  - `load_asn1_tree()`: Display tree
  - `filter_nodes()`: Search/filter
  - `select_node_by_offset()`: Sync with hex viewer

Extending:
- Add drag-and-drop: Implement `dragMoveEvent()`
- Add copy-to-clipboard: Override context menu
- Add color coding: Modify `_add_node_recursive()`
- Add sorting: Extend `load_asn1_tree()`

**hex_viewer.py** - Hex display widget

Key class:
- `HexViewer`: Custom hex viewer
  - `set_data()`: Show binary data
  - `highlight_offset()`: Highlight bytes
  - `_render_hex()`: Create hex display

Extending:
- Add editing capabilities: Override `keyPressEvent()`
- Add colors for different byte types: Modify `_render_hex()`
- Add byte grouping: Adjust `bytes_per_line` dynamically
- Add search in hex: Create `find_bytes()` method

**detail_view.py** - Tabbed detail panel

Key class:
- `DetailView`: Tabbed view widget
  - `display_node()`: Show node details
  - Tabs: Hex, Text, XML, JSON

Extending:
- Add new tab: Create `_create_*_view()` and `_update_*_tab()`
- Add custom representations: Create new export methods
- Add interactive tabs: Override `currentChanged()`
- Add search within tab: Add find toolbar

**grammar_dialog.py** - Grammar loader dialog

Key class:
- `GrammarDialog`: Modal dialog for loading grammar

Extending:
- Add grammar editor: Create inline edit fields
- Add validation UI: Show invalid entries before loading
- Add remote grammar loading: Add URL input
- Add grammar merge: Allow loading multiple grammars

### Export Module (`src/export/`)

**exporter.py** - Export engine

Key class:
- `Exporter`: Static export methods
  - `to_text()`: Text export
  - `to_xml()`: XML export
  - `to_json()`: JSON export
  - `search_and_export()`: Find and export node

Extending:
- Add CSV export: Create `to_csv()` method
- Add YAML export: Create `to_yaml()` method
- Add binary export: Create `to_binary()` method
- Add diff export: Compare two trees

## 🔨 Common Development Tasks

### Task 1: Add New Export Format

1. Create export method in `exporter.py`:
```python
@staticmethod
def to_yaml(node: ASN1Node, pretty_print: bool = True) -> str:
    """Export ASN.1 tree to YAML format"""
    # Implementation here
    pass
```

2. Add tab to `detail_view.py`:
```python
self.yaml_view = self._create_text_view()
self.addTab(self.yaml_view, "YAML")
```

3. Update tab content:
```python
def _update_yaml_tab(self, node: ASN1Node):
    content = Exporter.to_yaml(node, pretty_print=True)
    self.yaml_view.setPlainText(content)
```

4. Add to `display_node()`:
```python
self._update_yaml_tab(node)
```

5. Add menu item in `main_window.py`:
```python
export_yaml_action = QAction("Export as &YAML...", self)
export_yaml_action.triggered.connect(self._on_export_yaml)
file_menu.addAction(export_yaml_action)

def _on_export_yaml(self):
    if not self.root_node:
        return
    file_path, _ = QFileDialog.getSaveFileName(...)
    if file_path:
        content = Exporter.to_yaml(self.root_node)
        with open(file_path, 'w') as f:
            f.write(content)
```

### Task 2: Add Grammar Format Support

1. Add loader to `grammar_manager.py`:
```python
def load_yaml(self, file_path: str) -> bool:
    """Load grammar from YAML file"""
    try:
        import yaml
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        for tag_id, name in data.items():
            self._normalize_and_add(tag_id, str(name))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

2. Update auto-detect in `load_file()`:
```python
elif path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
    return self.load_yaml(file_path)
```

3. Update dialog in `grammar_dialog.py`:
```python
self.format_combo.addItem("YAML", "yaml")
```

### Task 3: Customize Tree Appearance

Modify `tree_view.py` `_add_node_recursive()`:

```python
# Change font for different tag types
if node.tag.tag_class == TagClass.APPLICATION:
    font.setItalic(True)
if node.tag.tag_class == TagClass.CONTEXT:
    font.setUnderline(True)

# Add icons
if node.tag.constructed:
    item.setIcon(0, QIcon("resources/icons/folder.png"))
else:
    item.setIcon(0, QIcon("resources/icons/file.png"))

# Add colors
if node.length > 1000:
    item.setForeground(0, QBrush(QColor("red")))
```

### Task 4: Add Search Highlighting

Modify `hex_viewer.py`:

```python
def highlight_search(self, search_bytes: bytes):
    """Find and highlight search bytes"""
    positions = []
    data = self.data
    search_hex = search_bytes.hex()
    
    # Find all occurrences
    pos = 0
    while True:
        pos = data.find(search_bytes, pos)
        if pos == -1:
            break
        positions.append((pos, pos + len(search_bytes)))
        pos += 1
    
    # Highlight all positions
    for start, end in positions:
        self.highlight_offset(start, end)
```

### Task 5: Add Preferences Dialog

Create new file `src/gui/preferences_dialog.py`:

```python
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QSpinBox

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        
        layout = QVBoxLayout()
        
        self.auto_expand = QCheckBox("Auto-expand tree")
        self.bytes_per_line = QSpinBox()
        self.bytes_per_line.setValue(16)
        
        layout.addWidget(self.auto_expand)
        layout.addWidget(self.bytes_per_line)
        
        self.setLayout(layout)
```

## 🧪 Testing Your Changes

### Unit Testing

Create test files in `tests/` directory:

```python
# tests/test_parser.py
import unittest
from src.parser import BERDERParser

class TestParser(unittest.TestCase):
    def test_parse_sequence(self):
        data = bytes([0x30, 0x03, 0x02, 0x01, 0x2A])
        parser = BERDERParser(data)
        node = parser.parse()
        self.assertIsNotNone(node)
        self.assertEqual(len(node.children), 1)
```

Run tests:
```bash
python -m unittest discover -s tests
```

### Integration Testing

Test with real ASN.1 files:
```python
# tests/test_integration.py
from src.parser import BERDERParser
from src.grammar import GrammarManager
from src.export import Exporter

def test_full_workflow():
    # Load file
    with open("test_file.der", "rb") as f:
        data = f.read()
    
    # Parse
    parser = BERDERParser(data)
    root = parser.parse()
    
    # Apply grammar
    grammar = GrammarManager()
    grammar.load_csv("test_grammar.csv")
    
    # Export
    text = Exporter.to_text(root)
    assert text is not None
    print("✓ Workflow test passed!")
```

### Performance Testing

```python
# tests/test_performance.py
import time
from src.parser import BERDERParser

def test_parse_large_file():
    with open("large_file.der", "rb") as f:
        data = f.read()
    
    start = time.time()
    parser = BERDERParser(data)
    root = parser.parse()
    elapsed = time.time() - start
    
    print(f"Parsed {len(data)} bytes in {elapsed:.2f}s")
    assert elapsed < 10, "Parsing too slow!"
```

## 📊 Code Metrics

### Current State
- **Total Lines**: 3500+
- **Functions**: 80+
- **Classes**: 15+
- **Test Coverage**: Basic

### Quality Goals
- Maintain < 25 lines per function average
- Keep classes focused (single responsibility)
- Aim for 80%+ test coverage
- All public methods documented

## 🐛 Debugging Tips

### Enable Verbose Logging

Add to `main.py`:
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Debug Parser

Add to `ber_der_parser.py`:
```python
def _parse_tag(self, offset: int):
    # ... existing code ...
    print(f"DEBUG: Parsing tag at offset {offset}: 0x{tag_byte:02X}")
    return tag, offset
```

### Debug GUI Events

Add to `main_window.py`:
```python
def _on_node_selected(self, node: ASN1Node):
    print(f"DEBUG: Node selected: {node.get_display_name()}")
    # ... rest of method
```

### Use PyCharm Debugger

1. Set breakpoints
2. Run > Debug
3. Use debugger console

## 📚 Best Practices

1. **Type Hints**: Always use type hints
   ```python
   def parse(self) -> Optional[ASN1Node]:
   ```

2. **Docstrings**: Document all public methods
   ```python
   def load_csv(self, file_path: str) -> bool:
       """Load grammar from CSV file
       
       Args:
           file_path: Path to CSV file
       
       Returns:
           True if successful, False otherwise
       """
   ```

3. **Error Handling**: Always handle exceptions
   ```python
   try:
       # Code here
   except Exception as e:
       print(f"Error: {e}")
       return False
   ```

4. **Memory Management**: Clean up large objects
   ```python
   del large_data  # Help garbage collector
   ```

5. **Performance**: Use generators for large datasets
   ```python
   def parse_all_nodes(self):
       while offset < len(self.data):
           yield parse_tlv(offset)
   ```

## 🔗 Dependencies & Versions

Currently using:
- PyQt6 6.7.0 - GUI framework
- Python 3.8+ - Language

Future considerations:
- PyYAML - For YAML support
- SQLAlchemy - For database backend
- networkx - For tree visualization

## 📖 Additional Resources

- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)
- [ASN.1 Specification](https://www.itu.int/rec/T-REC-X.680/en)
- [BER/DER Encoding](https://www.itu.int/rec/T-REC-X.690/en)

## 🎯 Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/my-feature`
2. **Make Changes**: Modify files, follow best practices
3. **Test Locally**: Run `python test_demo.py`
4. **Run Test Suite**: `python -m unittest discover`
5. **Commit Changes**: `git commit -m "Add my feature"`
6. **Push & Create PR**: Submit for review

## 🚀 Contributing

1. Fork repository
2. Create feature branch
3. Make improvements
4. Add tests
5. Ensure all tests pass
6. Submit pull request

---

**Happy developing!** 🎉

Questions? Check existing code patterns and documentation.
