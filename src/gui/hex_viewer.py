"""Hex Viewer Widget - Display and highlight binary data"""
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from typing import Optional, Tuple


class HexViewer(QTextEdit):
    """
    Hex viewer with efficient byte-range highlighting.

    Highlighting uses setExtraSelections() — Qt's dedicated overlay API —
    so it never touches the document model and costs exactly 2 block lookups
    regardless of how large the highlighted range is.
    """

    bytes_selected = pyqtSignal(int, int)

    MAX_RENDER_BYTES = 512 * 1024  # render at most 512 KB in the text widget

    # Line layout: "XXXXXXXX  HH HH … HH  AAAA…\n"
    # Offset column: 8 chars, then 2 spaces → hex starts at column 10.
    _HEX_COL = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: bytes = b''
        self.bytes_per_line = 16
        self.highlighted_start = -1
        self.highlighted_end = -1

        font = QFont("Courier", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    # ------------------------------------------------------------------ #
    # Data loading                                                         #
    # ------------------------------------------------------------------ #

    def set_data(self, data: bytes):
        """Load binary data; renders only the first MAX_RENDER_BYTES."""
        self.data = data
        self.highlighted_start = -1
        self.highlighted_end = -1
        self.setExtraSelections([])
        self._render_hex()

    def _render_hex(self):
        render_data = self.data[:self.MAX_RENDER_BYTES]
        truncated = len(self.data) > self.MAX_RENDER_BYTES

        lines = []
        bpl = self.bytes_per_line
        for i in range(0, len(render_data), bpl):
            chunk = render_data[i:i + bpl]
            hex_str = " ".join(f"{b:02X}" for b in chunk)
            hex_str = f"{hex_str:<{bpl * 3 - 1}}"
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{i:08X}  {hex_str}  {ascii_str}")

        if truncated:
            remaining = len(self.data) - self.MAX_RENDER_BYTES
            lines.append(f"\n... {remaining:,} more bytes not shown (file too large to display in full)")

        self.setPlainText("\n".join(lines))

    # ------------------------------------------------------------------ #
    # Highlighting                                                         #
    # ------------------------------------------------------------------ #

    # Highlight colours for the three TLV regions
    _COLOR_TAG    = QColor(173, 216, 230)   # light blue
    _COLOR_LENGTH = QColor(144, 238, 144)   # light green
    _COLOR_VALUE  = QColor(255, 178,  80)   # orange

    def highlight_tlv(self,
                      tag_start: int,
                      length_start: int,
                      value_start: int, value_end: int) -> None:
        """
        Highlight the tag, length, and value byte regions with distinct colours.

        Each region is a separate ExtraSelection so Qt overlays them without
        touching the document model.  Only 2 findBlockByLineNumber() calls per
        region → O(1) regardless of how many bytes the node spans.
        """
        selections = []
        first_char = -1

        for start, end, color in (
            (tag_start,    length_start, self._COLOR_TAG),
            (length_start, value_start,  self._COLOR_LENGTH),
            (value_start,  value_end,    self._COLOR_VALUE),
        ):
            sel = self._make_selection(start, end, color)
            if sel is not None:
                if first_char < 0:
                    first_char = sel.cursor.selectionStart()
                selections.append(sel)

        self.setExtraSelections(selections)

        # Scroll so the tag byte is visible
        if first_char >= 0:
            nav = QTextCursor(self.document())
            nav.setPosition(first_char)
            self.setTextCursor(nav)
            self.ensureCursorVisible()

        self.highlighted_start = tag_start
        self.highlighted_end   = value_end

    def _make_selection(self, start_offset: int, end_offset: int,
                        color: QColor) -> "QTextEdit.ExtraSelection | None":
        """
        Build one ExtraSelection for the hex-column bytes in [start_offset, end_offset).
        Returns None when the range is empty or outside the rendered area.
        """
        if start_offset < 0 or end_offset <= start_offset or not self.data:
            return None

        doc = self.document()
        bpl = self.bytes_per_line
        col = self._HEX_COL

        start_line = start_offset // bpl
        start_pos  = start_offset % bpl
        last_byte  = min(end_offset, self.MAX_RENDER_BYTES) - 1
        if last_byte < start_offset:
            return None
        end_line = last_byte // bpl
        end_pos  = last_byte % bpl

        start_block = doc.findBlockByLineNumber(start_line)
        if not start_block.isValid():
            return None
        end_block = doc.findBlockByLineNumber(end_line)
        if not end_block.isValid():
            end_block = start_block

        char_start = start_block.position() + col + start_pos * 3
        char_end   = end_block.position()   + col + end_pos   * 3 + 3

        fmt = QTextCharFormat()
        fmt.setBackground(color)
        fmt.setForeground(QColor(0, 0, 0))

        cursor = QTextCursor(doc)
        cursor.setPosition(char_start)
        cursor.setPosition(char_end, QTextCursor.MoveMode.KeepAnchor)

        sel = QTextEdit.ExtraSelection()
        sel.cursor = cursor
        sel.format  = fmt
        return sel

    def clear_highlight(self):
        self.setExtraSelections([])
        self.highlighted_start = -1
        self.highlighted_end = -1

    # ------------------------------------------------------------------ #
    # Misc                                                                 #
    # ------------------------------------------------------------------ #

    def get_selected_bytes(self) -> Optional[Tuple[int, int]]:
        if self.highlighted_start >= 0 and self.highlighted_end >= 0:
            return (self.highlighted_start, self.highlighted_end)
        return None

    def export_as_text(self) -> str:
        return self.toPlainText()
