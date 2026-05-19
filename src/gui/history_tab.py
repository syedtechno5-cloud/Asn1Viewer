"""History Tab - browse and reuse recently opened files"""
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ..utils.history_manager import HistoryManager


# Category metadata: (category key, display label, button label)
_CATEGORIES = [
    ('data',    'Data Files',        'Open in Viewer'),
    ('grammar', 'Grammar Files',     'Load Grammar'),
    ('tags',    'Tag/Convert Files', 'Open in Convert'),
]


class HistoryTab(QWidget):
    """
    Displays recently used files grouped by category.
    Emits signals so the main window can route file opens to the right handler.
    """

    # Emitted when the user wants to open a file from history
    open_data_file    = pyqtSignal(str)
    open_grammar_file = pyqtSignal(str)
    open_tags_file    = pyqtSignal(str)

    def __init__(self, history: HistoryManager, parent=None):
        super().__init__(parent)
        self._history = history
        self._build_ui()
        self.refresh()

    # ─── UI construction ──────────────────────────────────────────────── #

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        header = QLabel("Recently Used Files")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        header.setFont(font)
        root.addWidget(header)

        # ── Tree ─────────────────────────────────────────────────────── #
        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(['File Name', 'Full Path', 'Last Accessed'])
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        root.addWidget(self._tree)

        # ── Action buttons ────────────────────────────────────────────── #
        btn_row = QHBoxLayout()

        self._use_btn = QPushButton("Open Selected")
        self._use_btn.setEnabled(False)
        self._use_btn.setFixedHeight(32)
        self._use_btn.setStyleSheet(
            "QPushButton { background:#0d7db4; color:white; font-weight:bold; "
            "border-radius:4px; padding:0 14px; } "
            "QPushButton:hover { background:#0b6a9a; } "
            "QPushButton:disabled { background:#555; }"
        )
        self._use_btn.clicked.connect(self._on_use_selected)
        btn_row.addWidget(self._use_btn)

        self._remove_btn = QPushButton("Remove Entry")
        self._remove_btn.setEnabled(False)
        self._remove_btn.setFixedHeight(32)
        self._remove_btn.clicked.connect(self._on_remove_selected)
        btn_row.addWidget(self._remove_btn)

        btn_row.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedHeight(32)
        refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(refresh_btn)

        clear_cat_btn = QPushButton("Clear Category")
        clear_cat_btn.setFixedHeight(32)
        clear_cat_btn.clicked.connect(self._on_clear_category)
        btn_row.addWidget(clear_cat_btn)

        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.setFixedHeight(32)
        clear_all_btn.setStyleSheet(
            "QPushButton { color: #e05050; } "
            "QPushButton:hover { color: #ff6060; }"
        )
        clear_all_btn.clicked.connect(self._on_clear_all)
        btn_row.addWidget(clear_all_btn)

        root.addLayout(btn_row)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #aaa;")
        root.addWidget(self._status_lbl)

    # ─── Populate tree ────────────────────────────────────────────────── #

    def refresh(self):
        self._tree.clear()
        self._use_btn.setEnabled(False)
        self._remove_btn.setEnabled(False)

        total = 0
        for cat_key, cat_label, action_label in _CATEGORIES:
            entries = self._history.get(cat_key)
            cat_item = QTreeWidgetItem([cat_label, '', f'{len(entries)} file(s)'])
            cat_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            cat_item.setData(0, Qt.ItemDataRole.UserRole, ('category', cat_key))
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            self._tree.addTopLevelItem(cat_item)

            for entry in entries:
                path   = entry.get('path', '')
                name   = entry.get('name', Path(path).name)
                ts     = entry.get('accessed', '')
                exists = Path(path).exists()

                child = QTreeWidgetItem([name, path, ts])
                child.setData(0, Qt.ItemDataRole.UserRole,
                              ('file', cat_key, path, action_label))
                child.setToolTip(1, path)

                if not exists:
                    for col in range(3):
                        child.setForeground(col, QColor('#888'))
                    child.setToolTip(0, 'File not found')

                cat_item.addChild(child)
                total += 1

            cat_item.setExpanded(True)

        self._status_lbl.setText(f"{total} file(s) in history.")

    # ─── Selection handling ───────────────────────────────────────────── #

    def _on_selection_changed(self):
        item = self._tree.currentItem()
        is_file = item and item.data(0, Qt.ItemDataRole.UserRole) and \
                  item.data(0, Qt.ItemDataRole.UserRole)[0] == 'file'
        self._use_btn.setEnabled(bool(is_file))
        self._remove_btn.setEnabled(bool(is_file))
        if is_file:
            _, cat_key, path, action_label = item.data(0, Qt.ItemDataRole.UserRole)
            self._use_btn.setText(action_label)

    def _on_double_click(self, item: QTreeWidgetItem, _col: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == 'file':
            self._open_entry(data[1], data[2])

    def _on_use_selected(self):
        item = self._tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == 'file':
            self._open_entry(data[1], data[2])

    def _open_entry(self, category: str, path: str):
        if not Path(path).exists():
            QMessageBox.warning(
                self, "File Not Found",
                f"The file no longer exists:\n{path}\n\nIt will be removed from history.",
            )
            self._history.remove(category, path)
            self.refresh()
            return

        if category == 'data':
            self.open_data_file.emit(path)
        elif category == 'grammar':
            self.open_grammar_file.emit(path)
        elif category == 'tags':
            self.open_tags_file.emit(path)

    # ─── Remove / Clear ───────────────────────────────────────────────── #

    def _on_remove_selected(self):
        item = self._tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == 'file':
            _, cat_key, path, _ = data
            self._history.remove(cat_key, path)
            self.refresh()

    def _on_clear_category(self):
        item = self._tree.currentItem()
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        # Work out which category this item belongs to
        if data[0] == 'category':
            cat_key   = data[1]
            cat_label = next((l for k, l, _ in _CATEGORIES if k == cat_key), cat_key)
        elif data[0] == 'file':
            cat_key   = data[1]
            cat_label = next((l for k, l, _ in _CATEGORIES if k == cat_key), cat_key)
        else:
            return

        reply = QMessageBox.question(
            self, "Clear Category",
            f"Clear all history entries for '{cat_label}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear(cat_key)
            self.refresh()

    def _on_clear_all(self):
        reply = QMessageBox.question(
            self, "Clear All History",
            "Clear the entire file history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._history.clear()
            self.refresh()
