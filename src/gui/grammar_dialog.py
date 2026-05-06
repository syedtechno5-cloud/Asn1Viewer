"""Grammar Dialog - Load and manage grammar files"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFileDialog, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from ..grammar import GrammarManager


class GrammarDialog(QDialog):
    """
    Dialog for loading and managing ASN.1 grammar files
    """
    
    # Signal emitted when grammar is loaded
    grammar_loaded = pyqtSignal(GrammarManager)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grammar_manager = GrammarManager()
        
        self.setWindowTitle("Load Grammar")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self._create_ui()
    
    def _create_ui(self):
        """Create dialog UI"""
        layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Grammar File:"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Format selector
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItem("Auto-detect", "auto")
        self.format_combo.addItem("CSV", "csv")
        self.format_combo.addItem("JSON", "json")
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Preview
        layout.addWidget(QLabel("Preview:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        layout.addWidget(self.preview_text)
        
        # Statistics
        self.stats_label = QLabel("No grammar loaded")
        layout.addWidget(self.stats_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_sample_btn = QPushButton("Create Sample Grammar")
        create_sample_btn.clicked.connect(self._on_create_sample)
        btn_layout.addWidget(create_sample_btn)
        
        btn_layout.addStretch()
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._on_load)
        btn_layout.addWidget(load_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _on_browse(self):
        """Handle browse button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Grammar File",
            "",
            "Grammar Files (*.csv *.json);;CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
            self._update_preview(file_path)
    
    def _update_preview(self, file_path: str):
        """Update preview of grammar file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)
            self.preview_text.setPlainText(content)
        except Exception as e:
            self.preview_text.setPlainText(f"Error reading file: {e}")
    
    def _on_load(self):
        """Handle load button click"""
        file_path = self.file_path_edit.text()
        if not file_path:
            self.stats_label.setText("Error: No file selected")
            return
        
        format_type = self.format_combo.currentData()
        
        try:
            if format_type == 'csv':
                success = self.grammar_manager.load_csv(file_path)
            elif format_type == 'json':
                success = self.grammar_manager.load_json(file_path)
            else:  # auto-detect
                success = self.grammar_manager.load_file(file_path)
            
            if success:
                num_mappings = len(self.grammar_manager.get_all_mappings())
                self.stats_label.setText(f"Loaded: {num_mappings} tag mappings")
                self.grammar_loaded.emit(self.grammar_manager)
                self.accept()
            else:
                self.stats_label.setText("Error: Failed to load grammar file")
        except Exception as e:
            self.stats_label.setText(f"Error: {str(e)}")
    
    def _on_create_sample(self):
        """Handle create sample button click"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Sample Grammar",
            "sample_grammar.csv",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            format_type = 'json' if file_path.endswith('.json') else 'csv'
            try:
                self.grammar_manager.create_sample_grammar(file_path, format_type)
                self.file_path_edit.setText(file_path)
                self._update_preview(file_path)
                self.stats_label.setText("Sample grammar created")
            except Exception as e:
                self.stats_label.setText(f"Error creating sample: {e}")
    
    def get_grammar_manager(self) -> GrammarManager:
        """Get the loaded grammar manager"""
        return self.grammar_manager
