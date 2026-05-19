"""Convert Tab - tag-based field extraction and format conversion"""
from pathlib import Path
from typing import List, Dict, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QButtonGroup, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QDialog, QDialogButtonBox, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ..parser import BERDERParser
from ..parser.asn1_types import ASN1Node
from ..parser.tag_filter import TagDefinitionParser, TagExtractor
from ..export.convert_exporter import ConvertExporter


# ─── Background conversion thread ────────────────────────────────────────── #

class ConvertThread(QThread):
    finished = pyqtSignal(list, str)   # records, formatted_output
    error    = pyqtSignal(str)

    def __init__(self, data_path: str, tags_text: str, output_format: str):
        super().__init__()
        self.data_path     = data_path
        self.tags_text     = tags_text
        self.output_format = output_format   # 'csv' | 'json' | 'xml'

    def run(self):
        try:
            parser     = TagDefinitionParser()
            field_defs = parser.parse_text(self.tags_text)
            if not field_defs:
                self.error.emit("No valid tag definitions found in tag file.")
                return

            with open(self.data_path, 'rb') as f:
                data = f.read()

            ber_parser = BERDERParser(data)
            roots = ber_parser.parse_all_nodes()
            if not roots:
                self.error.emit("Failed to parse data file: no valid ASN.1 records found.")
                return

            if len(roots) == 1:
                root_node = roots[0]
            else:
                from ..parser.asn1_types import ASN1Tag as _Tag
                synth_tag = _Tag(tag_class=0, constructed=1, tag_number=0, raw_byte=0)
                root_node = ASN1Node(
                    tag=synth_tag, length=len(data), value=b'',
                    offset=0, tag_offset=0, length_offset=0, value_offset=0,
                    children=roots,
                )
                for r in roots:
                    r.parent = root_node

            extractor = TagExtractor(field_defs)
            records   = extractor.extract(root_node)

            if not records:
                self.error.emit(
                    "No matching records found.\n"
                    "Check that the tag paths in your tag file match the data file structure."
                )
                return

            fmt = self.output_format.lower()
            if fmt == 'csv':
                output = ConvertExporter.to_csv(records)
            elif fmt == 'json':
                output = ConvertExporter.to_json(records)
            elif fmt == 'xml':
                output = ConvertExporter.to_xml(records)
            else:
                output = ConvertExporter.to_csv(records)

            self.finished.emit(records, output)

        except Exception as e:
            self.error.emit(f"Conversion error: {str(e)}")


# ─── Format help dialog ───────────────────────────────────────────────────── #

FORMAT_HELP = """\
Tag Definition File Format
──────────────────────────
Each non-blank, non-comment line defines one field to extract:

    PATH , FieldName , DataType

PATH is one or more tag descriptors joined by  "->"
The FIRST descriptor identifies the record container (e.g. a CDR envelope).
Subsequent descriptors navigate to the field inside that record.

Tag descriptor forms:
    CLASS:Number    e.g.  CTX:0   APP:3   UNI:16   PRIV:1
    0xNN            e.g.  0xA0    (class and number derived from the byte)

CLASS abbreviations:
    CTX  or  CONTEXT      - Context-specific (0x80 / 0xA0)
    APP  or  APPLICATION  - Application      (0x40 / 0x60)
    UNI  or  UNIVERSAL    - Universal        (0x00 / 0x20)
    PRIV or  PRIVATE      - Private          (0xC0 / 0xE0)

Supported DataTypes:
    int / uint       - Big-endian signed / unsigned integer
    string / ascii   - UTF-8 or ASCII text
    hex / bytes      - Raw bytes as uppercase hex string
    imsi / imei      - Telephony BCD (low nibble first, 0xF = pad)
    tbcd / bcd       - Telephony BCD / Standard BCD
    msisdn           - TON/NPI byte + TBCD digits
    ip / ipv6        - IPv4 or IPv6 address
    bool             - Boolean (any non-zero byte = true)
    timestamp        - 6-byte BCD  YYMMDDHHMMSS
    oid              - ASN.1 Object Identifier
    length           - Number of value bytes (for debugging)

Example (3GPP CDR file):
    # Lines starting with # are comments
    CTX:1->CTX:7->CTX:1,servedIMSI,imsi
    CTX:1->CTX:7->CTX:0,recordType,int
    CTX:1->CTX:7->CTX:8,recordOpeningTime,timestamp

    # If each record IS the container, omit the outer envelope tag:
    CTX:7->CTX:1,servedIMSI,imsi
    CTX:7->CTX:0,recordType,int
"""


class FormatHelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag File Format Help")
        self.setMinimumSize(620, 520)

        layout = QVBoxLayout(self)
        text   = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(FORMAT_HELP)
        text.setFont(QFont("Consolas", 9))
        layout.addWidget(text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


# ─── Convert Tab widget ───────────────────────────────────────────────────── #

class ConvertTab(QWidget):
    """
    UI panel for tag-based extraction and export.
    The data file is supplied by the main window via set_data_file().
    """

    # Emitted when a tag file is successfully used (category, path)
    file_used = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data_path: Optional[str] = None
        self._records: List[Dict[str, str]] = []
        self._output_text: str = ''
        self._thread: Optional[ConvertThread] = None
        self._build_ui()

    # ─── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # ── Current data file (read-only, set by main app) ─────────────── #
        file_frame = QFrame()
        file_frame.setFrameShape(QFrame.Shape.StyledPanel)
        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(8, 6, 8, 6)
        file_layout.setSpacing(8)

        file_icon = QLabel("File:")
        file_icon.setStyleSheet("font-weight: bold;")
        file_layout.addWidget(file_icon)

        self._file_label = QLabel("No file open — open a file in the viewer first.")
        self._file_label.setStyleSheet("color: #aaa;")
        self._file_label.setWordWrap(False)
        file_layout.addWidget(self._file_label, 1)
        root.addWidget(file_frame)

        # ── Tag definition file ───────────────────────────────────────── #
        tag_group = QGroupBox("Tag Definition File")
        tag_vlayout = QVBoxLayout(tag_group)

        tag_path_row = QHBoxLayout()
        self._tag_edit = QLineEdit()
        self._tag_edit.setPlaceholderText("Path to the tag definition file…")
        self._tag_edit.setReadOnly(True)
        tag_path_row.addWidget(self._tag_edit)
        browse_tags = QPushButton("Browse…")
        browse_tags.setFixedWidth(90)
        browse_tags.clicked.connect(self._browse_tags)
        tag_path_row.addWidget(browse_tags)
        help_btn = QPushButton("? Format Help")
        help_btn.setFixedWidth(100)
        help_btn.clicked.connect(self._show_format_help)
        tag_path_row.addWidget(help_btn)
        tag_vlayout.addLayout(tag_path_row)

        self._tag_preview = QTextEdit()
        self._tag_preview.setPlaceholderText(
            "Tag definitions will appear here after loading.\n"
            "You can also paste or edit them directly."
        )
        self._tag_preview.setFont(QFont("Consolas", 9))
        self._tag_preview.setFixedHeight(130)
        tag_vlayout.addWidget(self._tag_preview)
        root.addWidget(tag_group)

        # ── Output format ─────────────────────────────────────────────── #
        fmt_group  = QGroupBox("Output Format")
        fmt_layout = QHBoxLayout(fmt_group)
        self._fmt_group = QButtonGroup(self)
        for label in ('CSV', 'JSON', 'XML'):
            rb = QRadioButton(label)
            fmt_layout.addWidget(rb)
            self._fmt_group.addButton(rb)
        self._fmt_group.buttons()[0].setChecked(True)
        fmt_layout.addStretch()
        root.addWidget(fmt_group)

        # ── Action buttons ────────────────────────────────────────────── #
        btn_row = QHBoxLayout()
        self._convert_btn = QPushButton("Convert")
        self._convert_btn.setFixedHeight(34)
        self._convert_btn.setStyleSheet(
            "QPushButton { background:#0d7db4; color:white; font-weight:bold; "
            "border-radius:4px; padding:0 18px; } "
            "QPushButton:hover { background:#0b6a9a; } "
            "QPushButton:disabled { background:#555; }"
        )
        self._convert_btn.clicked.connect(self._on_convert)
        btn_row.addWidget(self._convert_btn)

        clear_btn = QPushButton("Clear Output")
        clear_btn.setFixedHeight(34)
        clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # ── Preview ───────────────────────────────────────────────────── #
        root.addWidget(QLabel("Preview:"))
        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Consolas", 9))
        root.addWidget(self._preview)

        # ── Status + save ─────────────────────────────────────────────── #
        bottom_row = QHBoxLayout()
        self._save_btn = QPushButton("Save Output…")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        bottom_row.addWidget(self._save_btn)

        self._status_lbl = QLabel("Ready.")
        self._status_lbl.setStyleSheet("color: #aaa;")
        bottom_row.addStretch()
        bottom_row.addWidget(self._status_lbl)
        root.addLayout(bottom_row)

    # ─── Public API ───────────────────────────────────────────────────── #

    def set_data_file(self, path: str):
        """Called by the main window when a file is opened or changed."""
        self._data_path = path
        name = Path(path).name if path else ''
        self._file_label.setText(name)
        self._file_label.setStyleSheet("color: #ddd;")
        self._file_label.setToolTip(path)

    def load_tags_file(self, path: str):
        """Pre-load a tag definition file (called from History dialog)."""
        self._tag_edit.setText(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self._tag_preview.setPlainText(f.read())
        except Exception as e:
            self._tag_preview.setPlainText(f"# Error reading file: {e}")

    # kept for backward-compat calls from main_window that used the old name
    def load_data_file(self, path: str):
        self.set_data_file(path)

    # ─── File browsing ────────────────────────────────────────────────── #

    def _browse_tags(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Tag Definition File", "",
            "Text Files (*.txt *.csv *.def *.tags);;All Files (*)",
        )
        if path:
            self.load_tags_file(path)
            self.file_used.emit('tags', path)

    # ─── Helpers ──────────────────────────────────────────────────────── #

    def _selected_format(self) -> str:
        btn = self._fmt_group.checkedButton()
        return btn.text().lower() if btn else 'csv'

    def _show_format_help(self):
        FormatHelpDialog(self).exec()

    # ─── Convert ─────────────────────────────────────────────────────── #

    def _on_convert(self):
        if not self._data_path:
            QMessageBox.warning(
                self, "No File Open",
                "No data file is currently open.\n\n"
                "Please open an ASN.1 / binary file in the main viewer first, "
                "then open this dialog again."
            )
            return

        tags_text  = self._tag_preview.toPlainText().strip()
        out_format = self._selected_format()

        if not tags_text:
            QMessageBox.warning(self, "Missing Input",
                                "Please load or paste tag definitions.")
            return

        self._convert_btn.setEnabled(False)
        self._save_btn.setEnabled(False)
        self._status_lbl.setText("Converting…")
        self._preview.setPlainText("Please wait…")

        self._thread = ConvertThread(self._data_path, tags_text, out_format)
        self._thread.finished.connect(self._on_finished)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_finished(self, records: list, output: str):
        self._records     = records
        self._output_text = output
        self._preview.setPlainText(output)
        count = len(records)
        self._status_lbl.setText(
            f"Done — {count} record{'s' if count != 1 else ''} extracted."
        )
        self._save_btn.setEnabled(True)
        self._convert_btn.setEnabled(True)

        tag_path = self._tag_edit.text().strip()
        if tag_path:
            self.file_used.emit('tags', tag_path)

    def _on_error(self, msg: str):
        self._preview.setPlainText(f"Error:\n{msg}")
        self._status_lbl.setText("Conversion failed.")
        self._convert_btn.setEnabled(True)

    # ─── Clear ───────────────────────────────────────────────────────── #

    def _on_clear(self):
        self._records      = []
        self._output_text  = ''
        self._preview.clear()
        self._save_btn.setEnabled(False)
        self._status_lbl.setText("Ready.")

    # ─── Save ────────────────────────────────────────────────────────── #

    def _on_save(self):
        if not self._output_text:
            return
        fmt     = self._selected_format()
        ext_map = {'csv':  ('CSV Files (*.csv)',   'output.csv'),
                   'json': ('JSON Files (*.json)', 'output.json'),
                   'xml':  ('XML Files (*.xml)',   'output.xml')}
        flt, default = ext_map.get(fmt, ('All Files (*)', 'output.txt'))
        path, _ = QFileDialog.getSaveFileName(self, "Save Output", default, flt)
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self._output_text)
                self._status_lbl.setText(f"Saved to {Path(path).name}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", str(e))
