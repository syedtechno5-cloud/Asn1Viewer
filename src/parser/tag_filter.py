"""Tag Filter - Parse tag definition files and extract/decode matching ASN.1 values"""
import socket
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .asn1_types import ASN1Node, TagClass


# ─── Tag class name → integer mapping ─────────────────────────────────────── #

_CLASS_MAP: Dict[str, int] = {
    'UNI': TagClass.UNIVERSAL,
    'UNIVERSAL': TagClass.UNIVERSAL,
    'APP': TagClass.APPLICATION,
    'APPLICATION': TagClass.APPLICATION,
    'CTX': TagClass.CONTEXT,
    'CONTEXT': TagClass.CONTEXT,
    'PRIV': TagClass.PRIVATE,
    'PRIVATE': TagClass.PRIVATE,
}

# ─── Data structures ──────────────────────────────────────────────────────── #

TagPathElement = Tuple[int, int]   # (tag_class, tag_number)


@dataclass
class TagFieldDef:
    record_key: TagPathElement           # Top-level path element (the record container)
    field_path: List[TagPathElement]     # Path *within* the record to reach the value
    field_name: str
    data_type: str


# ─── Tag definition file parser ───────────────────────────────────────────── #

class TagDefinitionParser:
    """
    Parses tag definition files.

    Supported line format:
        PATH,FieldName,DataType

    PATH is one or more tag descriptors joined by "->".
    Each tag descriptor is either:
        CLASS:Number   e.g.  CTX:0  APP:3  UNI:2
        0xNN           e.g.  0xA0   (class and number derived from the byte)

    The first element of PATH identifies the *record container*; the
    remaining elements navigate to the specific *field* inside that record.

    Example:
        CTX:0->CTX:0,recordType,int
        CTX:0->CTX:1,servedIMSI,imsi
        CTX:0->CTX:2,servedIMEI,imei
        CTX:0->CTX:4->CTX:0,nestedField,string

    Lines beginning with '#' and blank lines are ignored.
    """

    def parse_file(self, file_path: str) -> List[TagFieldDef]:
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.parse_text(f.read())

    def parse_text(self, text: str) -> List[TagFieldDef]:
        fields = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            fdef = self._parse_line(line)
            if fdef:
                fields.append(fdef)
        return fields

    def _parse_line(self, line: str) -> Optional[TagFieldDef]:
        parts = line.split(',', 2)
        if len(parts) < 3:
            return None
        path_str  = parts[0].strip()
        field_name = parts[1].strip()
        data_type  = parts[2].strip().lower()

        full_path = self._parse_path(path_str)
        if not full_path:
            return None

        return TagFieldDef(
            record_key=full_path[0],
            field_path=full_path[1:],
            field_name=field_name,
            data_type=data_type,
        )

    def _parse_path(self, path_str: str) -> Optional[List[TagPathElement]]:
        elements = []
        for part in path_str.split('->'):
            part = part.strip()
            elem = self._parse_tag_element(part)
            if elem is None:
                return None
            elements.append(elem)
        return elements if elements else None

    def _parse_tag_element(self, s: str) -> Optional[TagPathElement]:
        # Hex byte form: 0xA0
        if s.upper().startswith('0X'):
            try:
                byte_val = int(s, 16)
                tag_class  = (byte_val >> 6) & 0x03
                tag_number =  byte_val & 0x1F
                return (tag_class, tag_number)
            except ValueError:
                return None

        # CLASS:Number form: CTX:0
        if ':' not in s:
            return None
        cls_str, num_str = s.split(':', 1)
        cls_str = cls_str.strip().upper()
        num_str = num_str.strip()
        if cls_str not in _CLASS_MAP:
            return None
        try:
            num = int(num_str)
        except ValueError:
            return None
        return (_CLASS_MAP[cls_str], num)


# ─── Value decoder ────────────────────────────────────────────────────────── #

class ValueDecoder:
    """Decode raw ASN.1 value bytes into a human-readable string."""

    @staticmethod
    def decode(value: bytes, data_type: str) -> str:
        if value is None:
            return ''
        dt = data_type.lower().strip()
        try:
            return ValueDecoder._dispatch(value, dt)
        except Exception:
            return value.hex().upper()

    @staticmethod
    def _dispatch(value: bytes, dt: str) -> str:
        if not value:
            return ''

        if dt in ('int', 'integer'):
            return str(int.from_bytes(value, 'big', signed=True))

        if dt in ('uint', 'unsigned', 'unsigned_int'):
            return str(int.from_bytes(value, 'big', signed=False))

        if dt in ('string', 'str', 'utf8', 'utf-8'):
            return value.decode('utf-8', errors='replace')

        if dt in ('ascii', 'ia5', 'ia5string'):
            return value.decode('ascii', errors='replace')

        if dt == 'hex':
            return value.hex().upper()

        if dt == 'bytes':
            return value.hex().upper()

        if dt in ('imsi',):
            return ValueDecoder._tbcd(value)

        if dt in ('imei',):
            return ValueDecoder._tbcd(value)

        if dt in ('tbcd', 'telephony', 'telephony_bcd'):
            return ValueDecoder._tbcd(value)

        if dt in ('bcd',):
            return ValueDecoder._bcd(value)

        if dt == 'msisdn':
            return ValueDecoder._msisdn(value)

        if dt in ('ip', 'ipv4'):
            if len(value) >= 4:
                return '.'.join(str(b) for b in value[:4])
            return value.hex().upper()

        if dt == 'ipv6':
            if len(value) >= 16:
                return socket.inet_ntop(socket.AF_INET6, value[:16])
            return value.hex().upper()

        if dt in ('bool', 'boolean'):
            return 'true' if any(value) else 'false'

        if dt in ('timestamp', 'time', 'datetime'):
            return ValueDecoder._timestamp(value)

        if dt == 'oid':
            return ValueDecoder._oid(value)

        if dt == 'length':
            return str(len(value))

        # Unknown type → raw hex
        return value.hex().upper()

    @staticmethod
    def _tbcd(data: bytes) -> str:
        """Telephony BCD: low nibble first, 0xF = padding (skip)."""
        digits = []
        for b in data:
            low  = b & 0x0F
            high = (b >> 4) & 0x0F
            if low  != 0x0F:
                digits.append(str(low))
            if high != 0x0F:
                digits.append(str(high))
        return ''.join(digits)

    @staticmethod
    def _bcd(data: bytes) -> str:
        """Standard BCD: high nibble first, 0xF = padding (skip)."""
        digits = []
        for b in data:
            high = (b >> 4) & 0x0F
            low  = b & 0x0F
            if high != 0x0F:
                digits.append(str(high))
            if low  != 0x0F:
                digits.append(str(low))
        return ''.join(digits)

    @staticmethod
    def _msisdn(data: bytes) -> str:
        """MSISDN: byte 0 = TON/NPI, rest = TBCD digits."""
        if len(data) < 2:
            return data.hex().upper()
        ton_npi = data[0]
        digits  = ValueDecoder._tbcd(data[1:])
        ton     = (ton_npi >> 4) & 0x07
        return ('+' + digits) if ton == 1 else digits

    @staticmethod
    def _timestamp(data: bytes) -> str:
        """6-byte BCD timestamp YYMMDDHHMMSS (telecom CDR format)."""
        if len(data) < 6:
            return data.hex().upper()
        d = []
        for b in data[:6]:
            d.append((b >> 4) & 0x0F)
            d.append(b & 0x0F)
        year   = d[0] * 10 + d[1]
        month  = d[2] * 10 + d[3]
        day    = d[4] * 10 + d[5]
        hour   = d[6] * 10 + d[7]
        minute = d[8] * 10 + d[9]
        second = d[10] * 10 + d[11]
        year_full = 2000 + year if year < 50 else 1900 + year
        return f"{year_full:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

    @staticmethod
    def _oid(data: bytes) -> str:
        """Decode ASN.1 Object Identifier bytes."""
        if not data:
            return ''
        components = [str(data[0] // 40), str(data[0] % 40)]
        val = 0
        for b in data[1:]:
            val = (val << 7) | (b & 0x7F)
            if not (b & 0x80):
                components.append(str(val))
                val = 0
        return '.'.join(components)


# ─── Tag extractor ────────────────────────────────────────────────────────── #

class TagExtractor:
    """
    Walk an ASN1Node tree and extract records defined by a list of TagFieldDefs.

    All field definitions that share the same record_key form one record type.
    Each time a node matching that record_key is found, all defined fields are
    extracted and decoded into a flat dict.
    """

    def __init__(self, field_defs: List[TagFieldDef]):
        self.field_defs = field_defs
        # Group fields by their record_key
        self._groups: Dict[TagPathElement, List[TagFieldDef]] = {}
        for fd in field_defs:
            self._groups.setdefault(fd.record_key, []).append(fd)

    @property
    def field_names(self) -> List[str]:
        """Ordered list of all field names across all record types."""
        seen = []
        for fd in self.field_defs:
            if fd.field_name not in seen:
                seen.append(fd.field_name)
        return seen

    def extract(self, root: ASN1Node) -> List[Dict[str, str]]:
        """Return a list of record dicts extracted from the whole tree."""
        records: List[Dict[str, str]] = []
        # Iterative DFS — always pushes children so nested records of the same
        # tag type are found even inside an outer wrapper of identical class+number.
        stack = [root]
        while stack:
            node = stack.pop()
            children = list(node.children or [])
            key = (node.tag.tag_class, node.tag.tag_number)
            if key in self._groups and node.tag.constructed:
                new_recs = self._build_records(node, self._groups[key])
                if new_recs:
                    records.extend(new_recs)
                    # Records found at this level — stop here.
                    # Do NOT push children so that nested nodes sharing the
                    # same tag are not processed a second time.
                else:
                    # No records at this level — this node is an outer wrapper;
                    # recurse into its children to find the actual records.
                    stack.extend(reversed(children))
            else:
                stack.extend(reversed(children))
        return records

    def _build_records(self, record_node: ASN1Node,
                       fields: List[TagFieldDef]) -> List[Dict[str, str]]:
        """
        Extract one or more records from record_node.

        For each field the path is followed with branching: if an intermediate
        path step matches N children, N leaf nodes are collected.  This handles
        the common CDR pattern where the record_key node is an outer container
        that holds many sub-records of the same navigable type (e.g. CTX:1 outer
        wrapper → 8 000 CTX:7 records each containing a CTX:1 IMSI field).

        Row count = max number of leaves reached by any single field.
        Rows where every value came from a CONSTRUCTED node are discarded (they
        indicate we matched a container, not an individual record).
        """
        # Collect all leaf nodes for each field
        field_leaves: Dict[str, List[ASN1Node]] = {}
        for fd in fields:
            field_leaves[fd.field_name] = self._navigate_all(record_node, fd.field_path)

        max_rows = max((len(v) for v in field_leaves.values()), default=0)
        if max_rows == 0:
            return []

        results: List[Dict[str, str]] = []
        for i in range(max_rows):
            rec: Dict[str, str] = {}
            found_primitive = False
            for fd in fields:
                leaves = field_leaves[fd.field_name]
                if i < len(leaves):
                    n = leaves[i]
                    rec[fd.field_name] = ValueDecoder.decode(n.value, fd.data_type)
                    if not n.tag.constructed:
                        found_primitive = True
                else:
                    rec[fd.field_name] = ''
            if found_primitive:
                results.append(rec)
        return results

    def _navigate_all(self, node: ASN1Node,
                      path: List[TagPathElement]) -> List[ASN1Node]:
        """
        Return ALL nodes reachable by following path from node.
        Branches whenever multiple children share the same tag at a given step.
        """
        if not path:
            return [node]
        cls, num = path[0]
        results: List[ASN1Node] = []
        for child in (node.children or []):
            if child.tag.tag_class == cls and child.tag.tag_number == num:
                results.extend(self._navigate_all(child, path[1:]))
        return results
