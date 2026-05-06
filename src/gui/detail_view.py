"""Detail View Widget - Tabbed display of different ASN.1 representations"""
from PyQt6.QtWidgets import QTabWidget, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional, Set
from ..parser.asn1_types import ASN1Node
from ..export import Exporter


class DetailView(QTabWidget):
    """
    Tabbed view showing different representations of selected node
    Tabs: Hex, Text Hierarchy, XML, JSON
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_node: Optional[ASN1Node] = None
        self._dirty_tabs: Set[int] = set()

        # Create tabs
        self.hex_view = self._create_text_view()
        self.text_view = self._create_text_view()
        self.xml_view = self._create_text_view()
        self.json_view = self._create_text_view()

        # Add tabs
        self.addTab(self.hex_view, "Info")
        self.addTab(self.text_view, "Text Hierarchy")
        self.addTab(self.xml_view, "XML")
        self.addTab(self.json_view, "JSON")

        # Render the newly visible tab only when the user switches
        self.currentChanged.connect(self._on_tab_changed)
    
    def _create_text_view(self) -> QTextEdit:
        """Create a read-only text view"""
        view = QTextEdit()
        view.setReadOnly(True)
        
        # Use monospace font
        font = QFont("Courier", 9)
        font.setFixedPitch(True)
        view.setFont(font)
        
        return view
    
    def display_node(self, node: ASN1Node):
        """Display information about a node — only renders the active tab immediately."""
        self.current_node = node
        self._dirty_tabs = {0, 1, 2, 3}

        current_idx = self.currentIndex()
        self._render_tab(current_idx)
        self._dirty_tabs.discard(current_idx)

    def _on_tab_changed(self, index: int):
        """Render a tab the first time it becomes visible after a node selection."""
        if index in self._dirty_tabs and self.current_node is not None:
            self._render_tab(index)
            self._dirty_tabs.discard(index)

    def _render_tab(self, index: int):
        """Render a single tab by index."""
        if self.current_node is None:
            return
        if index == 0:
            self._update_hex_tab(self.current_node)
        elif index == 1:
            self._update_text_tab(self.current_node)
        elif index == 2:
            self._update_xml_tab(self.current_node)
        elif index == 3:
            self._update_json_tab(self.current_node)
    
    def _update_hex_tab(self, node: ASN1Node):
        """Update hex tab with node data"""
        content = self._build_hex_content(node)
        self.hex_view.setPlainText(content)
    
    def _update_text_tab(self, node: ASN1Node):
        """Update text hierarchy tab"""
        content = Exporter.to_text(node, include_hex=True, include_offset=True)
        self.text_view.setPlainText(content)
    
    def _update_xml_tab(self, node: ASN1Node):
        """Update XML tab"""
        try:
            content = Exporter.to_xml(node, include_hex=True, pretty_print=True)
            self.xml_view.setPlainText(content)
        except Exception as e:
            self.xml_view.setPlainText(f"Error generating XML: {str(e)}")
    
    def _update_json_tab(self, node: ASN1Node):
        """Update JSON tab"""
        try:
            content = Exporter.to_json(node, include_hex=True, pretty_print=True)
            self.json_view.setPlainText(content)
        except Exception as e:
            self.json_view.setPlainText(f"Error generating JSON: {str(e)}")
    
    def _build_hex_content(self, node: ASN1Node) -> str:
        """
        Build the Info panel content.
        Constructed nodes: offset / tag / length only (children hold the data).
        Primitive nodes:   same plus a decoded value — no formatted hex dump
                           since the top pane already shows the full file hex.
        """
        tag_class_names = ['UNIVERSAL', 'APPLICATION', 'CONTEXT', 'PRIVATE']
        tag_class = tag_class_names[node.tag.tag_class] if node.tag.tag_class < 4 else 'UNKNOWN'
        tag_hex = node.tag.get_hex_str()          # full bytes, e.g. 0x5F20 for multi-byte

        lines = [
            "Node Information",
            "=" * 50,
            f"Name      : {node.get_display_name()}",
            f"Tag       : {tag_hex}",
            f"Tag Class : {tag_class}",
            f"Type      : {'CONSTRUCTED' if node.tag.constructed else 'PRIMITIVE'}",
            f"Tag No.   : {node.tag.tag_number}",
            f"Length    : {node.length} bytes",
            f"Offset    : 0x{node.tag_offset:04X} – 0x{node.value_offset + node.length:04X}",
        ]

        if node.children:
            lines.append(f"Children  : {len(node.children)}")
        else:
            # Primitive — decode value without printing a full hex dump
            lines.append("")
            lines.append("Value")
            lines.append("-" * 50)
            lines.append(self._decode_primitive_value(node))

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Primitive value decoding                                             #
    # ------------------------------------------------------------------ #

    # Universal tag numbers whose values are text strings
    _STRING_TAGS = {0x0C, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
                    0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E}

    def _decode_primitive_value(self, node: ASN1Node) -> str:
        if not node.value:
            return "(empty)"

        tag_num   = node.tag.tag_number
        tag_class = node.tag.tag_class
        data      = node.value

        # ── UNIVERSAL ──────────────────────────────────────────────────
        if tag_class == 0:
            if tag_num == 0x01:              # BOOLEAN
                return "TRUE" if data[0] != 0 else "FALSE"

            if tag_num == 0x02:              # INTEGER
                if len(data) <= 8:
                    val = int.from_bytes(data, "big", signed=True)
                    return f"{val}  (0x{data.hex().upper()})"
                return f"0x{data.hex().upper()}  ({len(data)} bytes)"

            if tag_num == 0x05:              # NULL
                return "NULL"

            if tag_num == 0x06:              # OID
                return self._decode_oid(data)

            if tag_num == 0x03:              # BIT STRING
                unused = data[0] if data else 0
                bits   = data[1:] if data else b""
                return f"Unused bits: {unused}\n0x{bits.hex().upper()}"

            if tag_num in self._STRING_TAGS: # All text string types
                for enc in ('utf-8', 'latin-1', 'ascii'):
                    try:
                        text = data.decode(enc)
                        return (text if len(text) <= 2000
                                else text[:2000] + f"\n… ({len(text)-2000} chars truncated)")
                    except (UnicodeDecodeError, ValueError):
                        pass

        # ── APPLICATION ────────────────────────────────────────────────
        elif tag_class == 1:
            return self._decode_application_value(node, data)

        # ── CONTEXT-SPECIFIC ───────────────────────────────────────────
        elif tag_class == 2:
            return self._decode_heuristic(data, hint="Context-specific value")

        # ── PRIVATE ────────────────────────────────────────────────────
        elif tag_class == 3:
            return self._decode_heuristic(data, hint="Private value")

        # ── Fallback: inline hex, no offset column ─────────────────────
        return self._inline_hex(data)

    def _decode_application_value(self, node: ASN1Node, data: bytes) -> str:
        """
        Decode an APPLICATION-class primitive value.

        Tries heuristics in order:
          1. Printable UTF-8 / Latin-1 text
          2. Small integer (≤ 8 bytes)
          3. OID-like (starts with valid first-byte range)
          4. Inline hex with length note
        """
        tag_num = node.tag.tag_number

        # Many APPLICATION tags use implicit tagging over a UNIVERSAL type.
        # Try the most common ones by heuristic, not by fixed mapping.

        # Heuristic: printable string?
        for enc in ('utf-8', 'latin-1'):
            try:
                text = data.decode(enc)
                if all(c.isprintable() or c in '\t\r\n' for c in text):
                    note = f"  (APP #{tag_num} — decoded as {enc.upper()} text)"
                    return (text[:2000] + note
                            if len(text) <= 2000
                            else text[:2000] + f"\n… ({len(text)-2000} chars truncated)" + note)
            except (UnicodeDecodeError, ValueError):
                pass

        # Heuristic: small integer
        if 1 <= len(data) <= 8:
            signed   = int.from_bytes(data, "big", signed=True)
            unsigned = int.from_bytes(data, "big", signed=False)
            if signed == unsigned:
                return f"{unsigned}  (0x{data.hex().upper()})  (APP #{tag_num} — interpreted as unsigned integer)"
            return (f"Signed: {signed}  Unsigned: {unsigned}"
                    f"  (0x{data.hex().upper()})  (APP #{tag_num})")

        return self._inline_hex(data, prefix=f"APP #{tag_num} — ")

    def _decode_heuristic(self, data: bytes, hint: str) -> str:
        """Generic heuristic decode for CONTEXT / PRIVATE primitives."""
        for enc in ('utf-8', 'latin-1'):
            try:
                text = data.decode(enc)
                if all(c.isprintable() or c in '\t\r\n' for c in text):
                    return text[:2000] + (f"\n… ({len(text)-2000} chars truncated)"
                                          if len(text) > 2000 else "")
            except (UnicodeDecodeError, ValueError):
                pass
        if 1 <= len(data) <= 8:
            val = int.from_bytes(data, "big", signed=False)
            return f"{val}  (0x{data.hex().upper()})  ({hint})"
        return self._inline_hex(data)

    @staticmethod
    def _inline_hex(data: bytes, prefix: str = "") -> str:
        MAX = 256
        if len(data) <= MAX:
            return prefix + " ".join(f"{b:02X}" for b in data)
        preview = " ".join(f"{b:02X}" for b in data[:MAX])
        return (prefix + preview
                + f"\n… ({len(data) - MAX} more bytes — see hex viewer above)")

    def _decode_oid(self, data: bytes) -> str:
        """Decode a BER/DER OID value into dotted notation."""
        try:
            if not data:
                return "(empty OID)"
            parts = []
            first = data[0]
            parts.append(str(first // 40))
            parts.append(str(first % 40))
            val = 0
            for byte in data[1:]:
                val = (val << 7) | (byte & 0x7F)
                if not (byte & 0x80):
                    parts.append(str(val))
                    val = 0
            return ".".join(parts)
        except Exception:
            return data.hex()
    
    def export_current_tab_to_file(self, file_path: str) -> bool:
        """
        Export current tab content to file
        
        Args:
            file_path: Path to save to
        
        Returns:
            True if successful
        """
        try:
            current_view = self.currentWidget()
            if isinstance(current_view, QTextEdit):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_view.toPlainText())
                return True
        except Exception as e:
            print(f"Error exporting tab: {e}")
        return False
    
    def clear(self):
        """Clear all content"""
        self.hex_view.clear()
        self.text_view.clear()
        self.xml_view.clear()
        self.json_view.clear()
        self.current_node = None
        self._dirty_tabs.clear()
