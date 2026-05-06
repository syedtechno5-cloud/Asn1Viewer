"""ASN.1 Type Definitions and Constants"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import IntEnum


class TagClass(IntEnum):
    """ASN.1 Tag Classes"""
    UNIVERSAL = 0
    APPLICATION = 1
    CONTEXT = 2
    PRIVATE = 3


class Constructed(IntEnum):
    """Primitive vs Constructed indicator"""
    PRIMITIVE = 0
    CONSTRUCTED = 1


# Universal Tags (subset of common ones)
UNIVERSAL_TAGS = {
    0x00: "END_OF_CONTENTS",
    0x01: "BOOLEAN",
    0x02: "INTEGER",
    0x03: "BIT_STRING",
    0x04: "OCTET_STRING",
    0x05: "NULL",
    0x06: "OBJECT_IDENTIFIER",
    0x07: "ObjectDescriptor",
    0x08: "EXTERNAL",
    0x09: "REAL",
    0x0A: "ENUMERATED",
    0x0B: "EMBEDDED_PDV",
    0x0C: "UTF8String",
    0x0D: "RELATIVE_OID",
    0x10: "SEQUENCE",
    0x11: "SET",
    0x12: "NumericString",
    0x13: "PrintableString",
    0x14: "TeletexString",
    0x15: "VideotexString",
    0x16: "IA5String",
    0x17: "UTCTime",
    0x18: "GeneralizedTime",
    0x19: "GraphicString",
    0x1A: "VisibleString",
    0x1B: "GeneralString",
    0x1C: "UniversalString",
    0x1D: "CharacterString",
    0x1E: "BMPString",
    0x1F: "DateString",
}


@dataclass
class ASN1Tag:
    """Represents a single ASN.1 Tag"""
    tag_class: int    # 0-3 (UNIVERSAL, APPLICATION, CONTEXT, PRIVATE)
    constructed: int  # 0 or 1
    tag_number: int   # Decoded tag number (may be multi-byte)
    raw_byte: int     # First tag byte (kept for backward compatibility)
    raw_bytes: bytes = field(default_factory=bytes)  # Full tag encoding (1+ bytes)

    def __str__(self):
        class_names = ["UNIVERSAL", "APPLICATION", "CONTEXT", "PRIVATE"]
        const_str = "CONSTRUCTED" if self.constructed else "PRIMITIVE"
        return f"[{class_names[self.tag_class]} {const_str}] #{self.tag_number}"

    def get_hex_str(self) -> str:
        """Full hex representation of all tag bytes (e.g. '0x5F20' for multi-byte tags)."""
        raw = self.raw_bytes if self.raw_bytes else bytes([self.raw_byte])
        return "0x" + raw.hex().upper()

    def get_grammar_key(self) -> str:
        """
        Normalised key used for grammar lookups.
        Matches the format stored by GrammarManager: '0xNN' or '0xNNNN'.
        """
        return self.get_hex_str()


@dataclass
class ASN1Node:
    """Represents an ASN.1 TLV (Tag-Length-Value) node in the tree"""
    tag: ASN1Tag
    length: int
    value: bytes
    offset: int  # Byte offset in the file
    tag_offset: int  # Byte offset where tag starts
    length_offset: int  # Byte offset where length starts
    value_offset: int  # Byte offset where value starts
    children: List['ASN1Node'] = None
    parent: Optional['ASN1Node'] = None
    grammar_name: Optional[str] = None  # Human-readable name from grammar
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    def is_constructed(self):
        """Check if this node contains children"""
        return self.tag.constructed == Constructed.CONSTRUCTED
    
    def get_display_name(self):
        """Get the display name (grammar name or tag info)"""
        if self.grammar_name:
            return self.grammar_name

        if self.tag.tag_class == TagClass.UNIVERSAL:
            return UNIVERSAL_TAGS.get(self.tag.tag_number, f"Tag #{self.tag.tag_number}")

        # For APPLICATION / CONTEXT / PRIVATE show short class prefix + number
        prefixes = ["UNIV", "APP", "CTX", "PRIV"]
        prefix = prefixes[self.tag.tag_class]
        return f"[{prefix} #{self.tag.tag_number}]"
    
    def get_preview(self):
        """Get a preview of the value (first 100 bytes)"""
        if len(self.value) <= 100:
            return self.value.hex()
        return self.value[:100].hex() + "..."
    
    def total_length(self):
        """Get total length including tag and length encoding"""
        # Tag length (1 or more bytes)
        tag_len = 1
        # Length encoding
        length_len = 1
        if self.length <= 127:
            pass  # Single byte for length
        else:
            # Long form: first byte is (0x80 | num_bytes), then the actual bytes
            length_len = (self.length.bit_length() + 7) // 8 + 1
        return tag_len + length_len + self.length
