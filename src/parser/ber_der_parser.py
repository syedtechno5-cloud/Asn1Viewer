"""BER/DER ASN.1 Parser - Recursive Tag-Length-Value Decoder"""
from typing import List, Tuple, Optional
from .asn1_types import ASN1Node, ASN1Tag, TagClass, Constructed


class ParseError(Exception):
    """Exception raised during parsing"""
    pass


class BERDERParser:
    """
    Recursive BER/DER Parser for ASN.1 files.
    Handles both primitive and constructed types.
    """
    
    def __init__(self, data: bytes):
        """
        Initialize parser with binary data
        
        Args:
            data: Byte array containing BER/DER encoded data
        """
        self.data = data
        self.offset = 0
    
    def parse(self) -> Optional[ASN1Node]:
        """
        Parse the entire data stream and return the root node
        
        Returns:
            Root ASN1Node or None if data is empty
        """
        if not self.data:
            return None
        
        try:
            node, _ = self._parse_tlv_from_data(self.data, 0)
            return node
        except Exception as e:
            raise ParseError(f"Failed to parse ASN.1 data: {str(e)}")
    
    def parse_all_nodes(self) -> List[ASN1Node]:
        """Parse every top-level TLV record in the file and return them as a list."""
        # base_offset=0: self.data starts at the beginning of the file
        return self._parse_children(self.data, base_offset=0)
    
    def _parse_tlv_from_data(self, data: bytes, offset: int,
                             base_offset: int = 0) -> Tuple[ASN1Node, int]:
        """
        Parse a single TLV from *data* starting at *offset*.

        Supports both definite-length (DER/BER) and indefinite-length (BER)
        encodings.  Indefinite-length values are terminated by an
        end-of-contents marker (0x00 0x00).

        *base_offset* is the absolute file position of data[0].
        All offsets stored in the returned ASN1Node are absolute file offsets.
        """
        if offset >= len(data):
            raise ParseError("Unexpected end of data")

        local_tag_start = offset

        # ── Tag ────────────────────────────────────────────────────────
        tag, offset = self._parse_tag_from_data(data, offset)

        if offset >= len(data):
            raise ParseError("Unexpected end of data after tag")

        # ── Length ─────────────────────────────────────────────────────
        local_length_start = offset
        length_byte = data[offset]
        offset += 1

        indefinite = False

        if length_byte & 0x80 == 0:
            # Short definite form (0x00–0x7F)
            length = length_byte

        elif (length_byte & 0x7F) == 0:
            # Indefinite form: length byte == 0x80
            indefinite = True

        else:
            # Long definite form: lower 7 bits = number of length bytes
            num_len_bytes = length_byte & 0x7F
            if offset + num_len_bytes > len(data):
                raise ParseError("Incomplete long-form length encoding")
            length = 0
            for _ in range(num_len_bytes):
                length = (length << 8) | data[offset]
                offset += 1

        # ── Value ──────────────────────────────────────────────────────
        local_value_offset = offset

        if indefinite:
            # BER indefinite: scan forward for the end-of-contents (0x00 0x00)
            eoc = self._find_eoc(data, offset)
            if eoc < 0:
                raise ParseError(
                    f"Cannot find end-of-contents (0x00 0x00) for indefinite-length "
                    f"TLV starting at offset 0x{base_offset + local_tag_start:X}"
                )
            length = eoc - offset
            value  = data[offset:eoc]
            offset = eoc + 2          # consume the two EOC bytes
        else:
            if offset + length > len(data):
                raise ParseError(
                    f"Insufficient data at 0x{base_offset + local_tag_start:X}: "
                    f"need {length} bytes, have {len(data) - offset}"
                )
            value  = data[offset:offset + length]
            offset += length

        # ── Absolute offsets ───────────────────────────────────────────
        abs_tag_offset    = base_offset + local_tag_start
        abs_value_offset  = base_offset + local_value_offset
        abs_length_offset = base_offset + local_length_start

        node = ASN1Node(
            tag=tag,
            length=length,
            value=value,
            offset=abs_tag_offset,
            tag_offset=abs_tag_offset,
            length_offset=abs_length_offset,
            value_offset=abs_value_offset,
        )

        # Recursively decode constructed nodes (APPLICATION included)
        if tag.constructed == Constructed.CONSTRUCTED and length > 0:
            try:
                node.children = self._parse_children(value, base_offset=abs_value_offset)
                for child in node.children:
                    child.parent = node
            except Exception:
                pass  # treat as opaque primitive if children can't be decoded

        return node, offset

    # ------------------------------------------------------------------ #
    # Indefinite-length helper                                             #
    # ------------------------------------------------------------------ #

    def _find_eoc(self, data: bytes, start: int) -> int:
        """
        Scan forward from *start* to find the end-of-contents octets (0x00 0x00)
        that close the current indefinite-length value.

        Handles nested indefinite-length encodings by tracking depth:
        each nested 0x80 length byte opens a new level and its matching
        0x00 0x00 closes it.

        Returns the offset of the first 0x00 of the matching EOC, or -1.
        """
        pos = start
        while pos < len(data) - 1:

            # End-of-contents at this depth?
            if data[pos] == 0x00 and data[pos + 1] == 0x00:
                return pos

            # Skip over a nested TLV so we don't mistake its content for EOC
            try:
                # ── skip tag ──
                tag_byte = data[pos]
                pos += 1
                if (tag_byte & 0x1F) == 0x1F:      # long-form tag
                    while pos < len(data) and (data[pos] & 0x80):
                        pos += 1
                    pos += 1                         # last tag byte (bit7=0)

                if pos >= len(data):
                    break

                # ── skip length + value ──
                len_byte = data[pos]
                pos += 1

                if len_byte == 0x80:
                    # Nested indefinite: find *its* EOC recursively
                    nested_eoc = self._find_eoc(data, pos)
                    if nested_eoc < 0:
                        return -1
                    pos = nested_eoc + 2             # skip nested EOC
                elif len_byte & 0x80:
                    num = len_byte & 0x7F
                    if pos + num > len(data):
                        return -1
                    nested_len = int.from_bytes(data[pos:pos + num], 'big')
                    pos += num + nested_len
                else:
                    pos += len_byte                  # short definite

            except (IndexError, OverflowError):
                return -1

        return -1

    def _parse_children(self, data: bytes, base_offset: int = 0) -> List[ASN1Node]:
        """
        Parse all TLV records inside *data*.

        *base_offset* is the absolute file position of data[0] so every
        child stores correct absolute offsets.
        """
        children = []
        offset = 0

        while offset < len(data):
            # Skip end-of-contents octets that may appear inside indefinite
            # values that were already stripped — harmless defensive check
            if offset + 1 < len(data) and data[offset] == 0x00 and data[offset + 1] == 0x00:
                offset += 2
                continue
            try:
                child, new_offset = self._parse_tlv_from_data(
                    data, offset, base_offset=base_offset
                )
                children.append(child)
                offset = new_offset
            except ParseError:
                break

        return children
    
    def _parse_tag_from_data(self, data: bytes, offset: int) -> Tuple[ASN1Tag, int]:
        """
        Parse ASN.1 tag from specific data starting at offset.
        Handles both single-byte and multi-byte (long-form) tags.
        Stores ALL tag bytes in raw_bytes so grammar lookup and display
        work correctly for APPLICATION/multi-byte tags like 0x5F20.
        """
        if offset >= len(data):
            raise ParseError("Unexpected end of data while parsing tag")

        tag_byte = data[offset]
        offset += 1
        raw_bytes_list = [tag_byte]

        tag_class   = (tag_byte >> 6) & 0x3
        constructed = (tag_byte >> 5) & 0x1
        tag_number  =  tag_byte & 0x1F

        # Long-form tag: tag_number == 0x1F means more bytes follow
        if tag_number == 0x1F:
            tag_number = 0
            while offset < len(data):
                byte = data[offset]
                raw_bytes_list.append(byte)
                offset += 1
                tag_number = (tag_number << 7) | (byte & 0x7F)
                if not (byte & 0x80):
                    break

        tag = ASN1Tag(
            tag_class=tag_class,
            constructed=constructed,
            tag_number=tag_number,
            raw_byte=tag_byte,
            raw_bytes=bytes(raw_bytes_list),
        )

        return tag, offset
    
    def _parse_length(self, offset: int) -> Tuple[int, int]:
        """
        Parse ASN.1 length starting at offset
        
        Handles both short form (<= 127) and long form.
        
        Args:
            offset: Current offset
        
        Returns:
            Tuple of (length, new_offset)
        """
        if offset >= len(self.data):
            raise ParseError("Unexpected end of data while parsing length")
        
        length_byte = self.data[offset]
        offset += 1
        
        if length_byte & 0x80 == 0:
            # Short form: length is in the lower 7 bits
            length = length_byte & 0x7F
        else:
            # Long form: the lower 7 bits indicate how many bytes follow
            num_bytes = length_byte & 0x7F
            
            if num_bytes == 0:
                raise ParseError("Indefinite length encoding not supported")
            
            if offset + num_bytes > len(self.data):
                raise ParseError("Incomplete length encoding")
            
            length = 0
            for _ in range(num_bytes):
                length = (length << 8) | self.data[offset]
                offset += 1
        
        return length, offset
    
    def _parse_length_from_data(self, data: bytes, offset: int) -> Tuple[int, int]:
        """
        Parse ASN.1 length from specific data starting at offset
        
        Handles both short form (<= 127) and long form.
        
        Args:
            data: The data to parse from
            offset: Current offset
        
        Returns:
            Tuple of (length, new_offset)
        """
        if offset >= len(data):
            raise ParseError("Unexpected end of data while parsing length")
        
        length_byte = data[offset]
        offset += 1
        
        if length_byte & 0x80 == 0:
            # Short form: length is in the lower 7 bits
            length = length_byte & 0x7F
        else:
            # Long form: the lower 7 bits indicate how many bytes follow
            num_bytes = length_byte & 0x7F
            
            if num_bytes == 0:
                raise ParseError("Indefinite length encoding not supported")
            
            if offset + num_bytes > len(data):
                raise ParseError("Incomplete length encoding")
            
            length = 0
            for _ in range(num_bytes):
                length = (length << 8) | data[offset]
                offset += 1
        
        return length, offset
    
    def _get_length_bytes(self, length: int) -> int:
        """
        Calculate how many bytes are needed to encode the length
        
        Args:
            length: The length value
        
        Returns:
            Number of bytes used in encoding
        """
        if length <= 127:
            return 1
        else:
            num_bytes = (length.bit_length() + 7) // 8
            return 1 + num_bytes
    
    def find_node_by_offset(self, node: ASN1Node, offset: int) -> Optional[ASN1Node]:
        """
        Find a node that spans the given offset
        
        Args:
            node: Root node to search from
            offset: Byte offset to find
        
        Returns:
            ASN1Node containing the offset or None
        """
        # Check if offset is within this node's range
        node_end = node.value_offset + node.length
        if offset < node.tag_offset or offset >= node_end:
            return None
        
        # If this node contains the offset but doesn't have children, return it
        if not node.children:
            return node
        
        # Search children
        for child in node.children:
            result = self.find_node_by_offset(child, offset)
            if result:
                return result
        
        return node
    
    def get_bytes_range(self, node: ASN1Node) -> Tuple[int, int]:
        """
        Get the byte range of a node (including tag and length)
        
        Args:
            node: The node
        
        Returns:
            Tuple of (start_offset, end_offset)
        """
        return (node.tag_offset, node.value_offset + node.length)
