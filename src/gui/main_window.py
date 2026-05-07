"""Main Application Window"""
import math
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QSplitter,
    QLineEdit, QPushButton, QLabel, QApplication,
    QDialog, QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QEvent
from PyQt6.QtGui import (
    QKeySequence, QAction, QShortcut,
    QPainter, QPen, QFont, QColor, QIcon, QPixmap,
)

from .tree_view import ASN1TreeWidget
from .hex_viewer import HexViewer
from .detail_view import DetailView
from .grammar_dialog import GrammarDialog
from ..parser import BERDERParser
from ..parser.asn1_types import ASN1Node, ASN1Tag
from ..grammar import GrammarManager
from ..export import Exporter
from ..utils import is_large_file


# ═══════════════════════════════════════════════════════════════════════ #
#  Loading overlay                                                        #
# ═══════════════════════════════════════════════════════════════════════ #

class LoadingOverlay(QWidget):
    """
    Animated semi-transparent spinner that covers the central widget
    whenever the application is doing heavy work.

    Usage:
        overlay.start("Parsing file…")   # show + begin animation
        overlay.stop()                    # hide
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setVisible(False)

        self._message = ""
        self._angle   = 0

        self._timer = QTimer(self)
        self._timer.setInterval(16)          # ~60 fps
        self._timer.timeout.connect(self._tick)

        # Keep our size in sync with the parent widget
        parent.installEventFilter(self)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def start(self, message: str = "Please wait…"):
        self._message = message
        self._angle   = 0
        self._fit()
        self.raise_()
        self.setVisible(True)
        self._timer.start()
        # Process one round of events so the overlay paints before the
        # caller blocks the main thread with synchronous work.
        QApplication.processEvents()

    def stop(self):
        self._timer.stop()
        self.setVisible(False)

    # ------------------------------------------------------------------ #
    # Internals                                                            #
    # ------------------------------------------------------------------ #

    def _tick(self):
        self._angle = (self._angle + 5) % 360
        self.update()

    def _fit(self):
        if self.parent():
            self.setGeometry(self.parent().rect())

    def eventFilter(self, obj, ev):
        if obj is self.parent() and ev.type() == QEvent.Type.Resize:
            self._fit()
        return super().eventFilter(obj, ev)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dim background
        p.fillRect(self.rect(), QColor(20, 20, 20, 160))

        cx = self.width()  // 2
        cy = self.height() // 2
        outer, inner = 32, 16

        # Spinner: 12 radiating line segments
        for i in range(12):
            alpha = int(40 + 215 * i / 11)
            pen = QPen(QColor(255, 255, 255, alpha))
            pen.setWidth(3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)

            rad = math.radians(self._angle + i * 30)
            x1 = int(cx + inner * math.sin(rad))
            y1 = int(cy - inner * math.cos(rad))
            x2 = int(cx + outer * math.sin(rad))
            y2 = int(cy - outer * math.cos(rad))
            p.drawLine(x1, y1, x2, y2)

        # Message below the spinner
        if self._message:
            p.setPen(QColor(230, 230, 230))
            font = QFont()
            font.setPointSize(10)
            p.setFont(font)
            msg_rect = self.rect().adjusted(0, cy + outer + 14, 0, 0)
            p.drawText(
                msg_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                self._message,
            )

        p.end()


# ═══════════════════════════════════════════════════════════════════════ #
#  Background parse thread                                                #
# ═══════════════════════════════════════════════════════════════════════ #

class ParseThread(QThread):
    finished = pyqtSignal(ASN1Node)
    error    = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read()

            parser = BERDERParser(data)
            roots  = parser.parse_all_nodes()

            if not roots:
                self.error.emit("Failed to parse file: no valid ASN.1 records found")
                return

            if len(roots) == 1:
                root_node = roots[0]
            else:
                synthetic_tag = ASN1Tag(
                    tag_class=0, constructed=1, tag_number=0, raw_byte=0
                )
                root_node = ASN1Node(
                    tag=synthetic_tag,
                    length=len(data),
                    value=b'',
                    offset=0,
                    tag_offset=0,
                    length_offset=0,
                    value_offset=0,
                    children=roots,
                )
                root_node.grammar_name = f"File ({len(roots)} records)"
                for r in roots:
                    r.parent = root_node

            self.finished.emit(root_node)

        except Exception as e:
            self.error.emit(f"Parse error: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════ #
#  Main window                                                            #
# ═══════════════════════════════════════════════════════════════════════ #

class ASN1ViewerMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ASN.1 Viewer")
        self.setWindowIcon(self._create_icon())
        self.setMinimumSize(1200, 700)

        self.current_file: Optional[str] = None
        self.root_node:    Optional[ASN1Node] = None
        self.grammar_manager = GrammarManager()
        self.parse_thread:   Optional[ParseThread] = None

        self._create_ui()
        self._create_menus()
        self._create_shortcuts()

        self.statusBar().showMessage("Ready. Open an ASN.1 file to begin.")

    # ------------------------------------------------------------------ #
    # UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.open_btn = QPushButton("Open File")
        self.open_btn.clicked.connect(self._on_open_file)
        toolbar_layout.addWidget(self.open_btn)

        self.grammar_btn = QPushButton("Load Grammar")
        self.grammar_btn.clicked.connect(self._on_load_grammar)
        toolbar_layout.addWidget(self.grammar_btn)

        toolbar_layout.addSpacing(20)

        toolbar_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setMaximumWidth(200)
        self.search_input.setPlaceholderText("Search tags/names...")
        self.search_input.textChanged.connect(self._on_search_debounced)
        toolbar_layout.addWidget(self.search_input)

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._search_pending = ""

        toolbar_layout.addSpacing(20)

        self.export_text_btn = QPushButton("Export Text")
        self.export_text_btn.clicked.connect(self._on_export_text)
        self.export_text_btn.setEnabled(False)
        toolbar_layout.addWidget(self.export_text_btn)

        self.export_xml_btn = QPushButton("Export XML")
        self.export_xml_btn.clicked.connect(self._on_export_xml)
        self.export_xml_btn.setEnabled(False)
        toolbar_layout.addWidget(self.export_xml_btn)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree_widget = ASN1TreeWidget()
        self.tree_widget.node_selected.connect(self._on_node_selected)
        splitter.addWidget(self.tree_widget)

        right_splitter = QSplitter(Qt.Orientation.Vertical)

        self.hex_viewer = HexViewer()
        right_splitter.insertWidget(0, self.hex_viewer)

        self.detail_view = DetailView()
        right_splitter.addWidget(self.detail_view)

        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 1)

        splitter.addWidget(right_splitter)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # Loading overlay — must be created LAST so it sits on top
        self._loading = LoadingOverlay(central_widget)

    def _create_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open File...", self)
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        for label, slot, _ in (
            ("Export as &Text...",  self._on_export_text, None),
            ("Export as &XML...",   self._on_export_xml,  None),
            ("Export as &JSON...",  self._on_export_json, None),
        ):
            act = QAction(label, self)
            act.triggered.connect(slot)
            file_menu.addAction(act)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("&Tools")
        grammar_action = QAction("Load &Grammar...", self)
        grammar_action.triggered.connect(self._on_load_grammar)
        tools_menu.addAction(grammar_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_shortcuts(self):
        QShortcut(QKeySequence.StandardKey.Open, self, self._on_open_file)
        QShortcut(QKeySequence.StandardKey.Quit, self, self.close)
        QShortcut(QKeySequence.StandardKey.Find, self, self.search_input.setFocus)

    def _logo_pixmap(self, size: int = 0) -> QPixmap:
        """Load the Syed Technologies logo; works in dev and PyInstaller exe."""
        if hasattr(sys, '_MEIPASS'):
            path = Path(sys._MEIPASS) / 'resources' / 'syed-tech-logo-transparent.png'
        else:
            path = Path(__file__).parent.parent.parent / 'resources' / 'syed-tech-logo-transparent.png'
        px = QPixmap(str(path))
        if size > 0 and not px.isNull():
            px = px.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        return px

    def _create_icon(self):
        px = self._logo_pixmap(56)
        canvas = QPixmap(64, 64)
        canvas.fill(QColor(0, 0, 0))
        if not px.isNull():
            p = QPainter(canvas)
            p.drawPixmap((64 - px.width()) // 2, (64 - px.height()) // 2, px)
            p.end()
        return QIcon(canvas)

    # ------------------------------------------------------------------ #
    # File loading                                                         #
    # ------------------------------------------------------------------ #

    def _on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open ASN.1 File", "",
            "ASN.1 Files (*.der *.cer *.asn1 *.asn *.dn *.ans);;All Files (*)",
        )
        if file_path:
            self._load_file(file_path)

    def _load_file(self, file_path: str):
        try:
            if is_large_file(file_path):
                reply = QMessageBox.warning(
                    self, "Large File",
                    "This file is quite large (>10 MB). Parsing may take a while.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            self.current_file = file_path
            self._loading.start(f"Parsing {Path(file_path).name}…")
            self.statusBar().showMessage(f"Parsing: {Path(file_path).name}…")

            self.parse_thread = ParseThread(file_path)
            self.parse_thread.finished.connect(self._on_parse_finished)
            self.parse_thread.error.connect(self._on_parse_error)
            self.parse_thread.start()

        except Exception as e:
            self._loading.stop()
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def _on_parse_finished(self, root_node: ASN1Node):
        self.root_node = root_node

        if self.grammar_manager.has_grammar():
            self._loading.start("Applying grammar…")
            self._apply_grammar(root_node)

        self._loading.start("Building tree…")
        self.tree_widget.load_asn1_tree(root_node)

        self._loading.start("Loading hex view…")
        if self.current_file:
            with open(self.current_file, 'rb') as f:
                data = f.read()
            self.hex_viewer.set_data(data)

        self._loading.stop()

        self.export_text_btn.setEnabled(True)
        self.export_xml_btn.setEnabled(True)

        file_name = Path(self.current_file).name if self.current_file else "File"
        self.statusBar().showMessage(f"Loaded: {file_name}")

    def _on_parse_error(self, error_msg: str):
        self._loading.stop()
        QMessageBox.critical(self, "Parse Error", error_msg)
        self.statusBar().showMessage("Parse failed")

    # ------------------------------------------------------------------ #
    # Grammar                                                              #
    # ------------------------------------------------------------------ #

    def _apply_grammar(self, node: ASN1Node):
        # Try full tag bytes first (handles multi-byte APPLICATION tags like 0x5F20)
        name = self.grammar_manager.get_name_by_hex_string(node.tag.get_grammar_key())
        # Fall back to single first byte in case grammar only lists the first byte
        if not name:
            name = self.grammar_manager.get_name_by_hex_string(
                f"0x{node.tag.raw_byte:02X}"
            )
        if name:
            node.grammar_name = name
        for child in node.children:
            self._apply_grammar(child)

    def _on_load_grammar(self):
        dialog = GrammarDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.grammar_manager = dialog.get_grammar_manager()

            if self.root_node:
                self._loading.start("Applying grammar…")
                self._apply_grammar(self.root_node)

                self._loading.start("Rebuilding tree…")
                self.tree_widget.load_asn1_tree(self.root_node)
                self._loading.stop()

            self.statusBar().showMessage(
                f"Loaded grammar: {len(self.grammar_manager.get_all_mappings())} mappings"
            )

    # ------------------------------------------------------------------ #
    # Node selection                                                       #
    # ------------------------------------------------------------------ #

    def _on_node_selected(self, node: ASN1Node):
        self.detail_view.display_node(node)

        self.hex_viewer.highlight_tlv(
            tag_start=node.tag_offset,
            length_start=node.length_offset,
            value_start=node.value_offset,
            value_end=node.value_offset + node.length,
        )

        self.statusBar().showMessage(
            f"Selected: {node.get_display_name()} | "
            f"Tag: 0x{node.tag_offset:04X}  "
            f"Length: 0x{node.length_offset:04X}  "
            f"Value: 0x{node.value_offset:04X}  "
            f"({node.length} bytes)"
        )

    # ------------------------------------------------------------------ #
    # Search                                                               #
    # ------------------------------------------------------------------ #

    def _on_search_debounced(self, search_term: str):
        self._search_pending = search_term
        self._search_timer.start(300)

    def _do_search(self):
        search_term = self._search_pending
        if search_term:
            self._loading.start("Filtering…")
            self.tree_widget.filter_nodes(search_term)
            self._loading.stop()
        else:
            if self.root_node:
                self._loading.start("Restoring tree…")
                self.tree_widget.load_asn1_tree(self.root_node)
                self._loading.stop()

    # ------------------------------------------------------------------ #
    # Export                                                               #
    # ------------------------------------------------------------------ #

    def _on_export_text(self):
        self._export("Export as Text", "asn1_export.txt",
                     "Text Files (*.txt);;All Files (*)", Exporter.to_text)

    def _on_export_xml(self):
        self._export("Export as XML", "asn1_export.xml",
                     "XML Files (*.xml);;All Files (*)", Exporter.to_xml)

    def _on_export_json(self):
        self._export("Export as JSON", "asn1_export.json",
                     "JSON Files (*.json);;All Files (*)", Exporter.to_json)

    def _export(self, title: str, default_name: str, file_filter: str, exporter_fn):
        if not self.root_node:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, title, default_name, file_filter)
        if file_path:
            try:
                self._loading.start("Exporting…")
                content = exporter_fn(self.root_node)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._loading.stop()
                self.statusBar().showMessage(f"Exported to {Path(file_path).name}")
            except Exception as e:
                self._loading.stop()
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    # ------------------------------------------------------------------ #
    # About                                                                #
    # ------------------------------------------------------------------ #

    def _on_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("About ASN.1 Viewer")
        dlg.setFixedWidth(360)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 16)

        # Logo
        logo_label = QLabel()
        px = self._logo_pixmap(100)
        if not px.isNull():
            logo_label.setPixmap(px)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background-color: black; padding: 8px; border-radius: 6px;")
        layout.addWidget(logo_label)

        # Text
        text = QLabel(
            "<div style='text-align:center;'>"
            "<b>ASN.1 Viewer v1.0.0</b><br><br>"
            "A cross-platform BER/DER ASN.1 file decoder with GUI.<br><br>"
            "• Hierarchical tree view of ASN.1 structure<br>"
            "• Synchronized hex viewer with TLV highlighting<br>"
            "• Grammar file support for human-readable tag names<br>"
            "• Multiple export formats (Text, XML, JSON)<br>"
            "• Search and filter capabilities<br><br>"
            "© 2025 Syed Technologies<br>"
            "<a href='http://www.syed-technologies.com'>www.syed-technologies.com</a>"
            "</div>"
        )
        text.setOpenExternalLinks(True)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        # OK button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)

        dlg.exec()
