"""Main entry point for ASN.1 Viewer"""
import sys
from PyQt6.QtWidgets import QApplication
from src.gui import ASN1ViewerMainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = ASN1ViewerMainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
