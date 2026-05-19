"""Main entry point for ASN.1 Viewer — GUI or CLI depending on arguments.

GUI mode (no arguments):
    python main.py

CLI mode (--data and --tags required):
    python main.py --data <file> --tags <file> [--format csv|json|xml] [--output <file>]

Run  python main.py --help  for full CLI reference.
"""
import sys


def _is_cli_mode() -> bool:
    """Return True when the caller passed at least one recognised CLI flag."""
    cli_flags = {'-d', '--data', '-t', '--tags', '-f', '--format',
                 '-o', '--output', '--no-header', '-h', '--help'}
    return any(a in cli_flags for a in sys.argv[1:])


def main():
    if _is_cli_mode():
        from src.cli.runner import run_cli
        sys.exit(run_cli())
    else:
        from PyQt6.QtWidgets import QApplication
        from src.gui import ASN1ViewerMainWindow

        app = QApplication(sys.argv)
        window = ASN1ViewerMainWindow()
        window.show()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()
