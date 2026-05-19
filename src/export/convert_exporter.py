"""Convert Exporter - export extracted tag records to CSV, JSON, or XML"""
import csv
import json
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Dict, List


def _xml_indent(elem, level: int = 0):
    """Add pretty-print indentation to an ElementTree element (Python 3.8 compatible)."""
    pad = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = pad
        for child in elem:
            _xml_indent(child, level + 1)
        # Last child's tail closes back to parent indent
        if not child.tail or not child.tail.strip():
            child.tail = pad
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = pad


class ConvertExporter:
    """Export a list of flat record dicts to CSV, JSON, or XML."""

    @staticmethod
    def to_csv(records: List[Dict[str, str]], header: bool = True) -> str:
        if not records:
            return ''
        output = StringIO()
        fieldnames: List[str] = []
        for rec in records:
            for k in rec:
                if k not in fieldnames:
                    fieldnames.append(k)
        writer = csv.DictWriter(
            output, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n'
        )
        if header:
            writer.writeheader()
        writer.writerows(records)
        return output.getvalue()

    @staticmethod
    def to_json(records: List[Dict[str, str]]) -> str:
        return json.dumps(records, indent=2, ensure_ascii=False)

    @staticmethod
    def to_xml(records: List[Dict[str, str]],
               root_tag: str = 'records',
               record_tag: str = 'record') -> str:
        root = ET.Element(root_tag)
        root.set('count', str(len(records)))
        for rec in records:
            elem = ET.SubElement(root, record_tag)
            for key, val in rec.items():
                child = ET.SubElement(elem, _safe_xml_tag(key))
                child.text = str(val) if val is not None else ''
        _xml_indent(root)
        raw = ET.tostring(root, encoding='unicode')
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + raw


def _safe_xml_tag(name: str) -> str:
    """Convert a field name to a valid XML element name."""
    safe = ''.join(c if (c.isalnum() or c in ('_', '-', '.')) else '_' for c in name)
    if safe and not (safe[0].isalpha() or safe[0] == '_'):
        safe = '_' + safe
    return safe or 'field'
