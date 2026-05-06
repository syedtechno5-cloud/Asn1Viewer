"""Export Engine - Export ASN.1 trees to various formats"""
from typing import Optional
from io import StringIO
from ..parser.asn1_types import ASN1Node, TagClass


class Exporter:
    """Export ASN.1 trees to different formats"""
    
    @staticmethod
    def to_text(node: ASN1Node, include_hex: bool = True, include_offset: bool = True) -> str:
        """
        Export ASN.1 tree to hierarchical text format
        
        Args:
            node: Root ASN1Node
            include_hex: Include hex preview of values
            include_offset: Include byte offsets
        
        Returns:
            Formatted text string
        """
        output = StringIO()
        Exporter._write_text_recursive(node, output, 0, include_hex, include_offset)
        return output.getvalue()
    
    @staticmethod
    def _write_text_recursive(node: ASN1Node, output: StringIO, depth: int, 
                               include_hex: bool, include_offset: bool, last_child: bool = True):
        """
        Recursively write node to text format
        
        Args:
            node: Current node
            output: Output StringIO
            depth: Current nesting depth
            include_hex: Include hex preview
            include_offset: Include offsets
            last_child: Is this the last child (for tree lines)
        """
        indent = "  " * depth
        prefix = "└── " if last_child else "├── "
        
        # Build node info line
        info = node.get_display_name()
        info += f" ({node.tag})"
        info += f" | Length: {node.length}"
        
        if include_offset:
            info += f" | @0x{node.tag_offset:04X}"
        
        if include_hex and node.length <= 100:
            info += f" | Value: {node.get_preview()}"
        elif include_hex and node.length > 100:
            info += f" | Value: [Binary data {node.length} bytes]"
        
        output.write(indent + prefix + info + "\n")
        
        # Write children
        if node.children:
            for i, child in enumerate(node.children):
                is_last = i == len(node.children) - 1
                child_indent = "  " * depth
                if last_child:
                    new_depth = depth + 1
                else:
                    new_depth = depth + 1
                
                Exporter._write_text_recursive(child, output, new_depth, 
                                               include_hex, include_offset, is_last)
    
    @staticmethod
    def to_xml(node: ASN1Node, include_hex: bool = True, pretty_print: bool = True) -> str:
        """
        Export ASN.1 tree to XML format
        
        Args:
            node: Root ASN1Node
            include_hex: Include hex values as text content
            pretty_print: Add indentation and newlines
        
        Returns:
            XML string
        """
        output = StringIO()
        
        if pretty_print:
            output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        else:
            output.write('<?xml version="1.0" encoding="UTF-8"?>')
        
        Exporter._write_xml_recursive(node, output, 0, include_hex, pretty_print)
        return output.getvalue()
    
    @staticmethod
    def _write_xml_recursive(node: ASN1Node, output: StringIO, depth: int,
                             include_hex: bool, pretty_print: bool):
        """
        Recursively write node to XML format
        
        Args:
            node: Current node
            output: Output StringIO
            depth: Current nesting depth
            include_hex: Include hex values
            pretty_print: Add formatting
        """
        indent = "  " * depth if pretty_print else ""
        newline = "\n" if pretty_print else ""
        
        # Create safe XML element name from display name
        tag_name = Exporter._make_xml_safe(node.get_display_name())
        
        # Build attributes
        attributes = []
        attributes.append(f'tag="0x{node.tag.raw_byte:02X}"')
        attributes.append(f'class="{Exporter._get_tag_class_name(node.tag.tag_class)}"')
        attributes.append(f'constructed="{bool(node.tag.constructed)}"')
        attributes.append(f'length="{node.length}"')
        attributes.append(f'offset="0x{node.tag_offset:04X}"')
        
        attr_str = " ".join(attributes)
        
        if node.children:
            # Write opening tag
            output.write(f'{indent}<{tag_name} {attr_str}>{newline}')
            
            # Write children
            for child in node.children:
                Exporter._write_xml_recursive(child, output, depth + 1, 
                                              include_hex, pretty_print)
            
            # Write closing tag
            output.write(f'{indent}</{tag_name}>{newline}')
        else:
            # Leaf node - include value as content or text
            if include_hex and node.length > 0:
                if node.length <= 100:
                    # Try to decode as ASCII if possible
                    try:
                        text_val = node.value.decode('ascii', errors='ignore')
                        if text_val and text_val.isprintable():
                            output.write(f'{indent}<{tag_name} {attr_str}>{text_val}</{tag_name}>{newline}')
                        else:
                            hex_val = node.value.hex()
                            output.write(f'{indent}<{tag_name} {attr_str} hex="{hex_val}" />{newline}')
                    except:
                        hex_val = node.value.hex()
                        output.write(f'{indent}<{tag_name} {attr_str} hex="{hex_val}" />{newline}')
                else:
                    output.write(f'{indent}<{tag_name} {attr_str} size="{node.length}" />{newline}')
            else:
                output.write(f'{indent}<{tag_name} {attr_str} />{newline}')
    
    @staticmethod
    def to_json(node: ASN1Node, include_hex: bool = True, pretty_print: bool = True) -> str:
        """
        Export ASN.1 tree to JSON format
        
        Args:
            node: Root ASN1Node
            include_hex: Include hex values
            pretty_print: Add indentation
        
        Returns:
            JSON string
        """
        import json
        
        def node_to_dict(n: ASN1Node) -> dict:
            d = {
                'name': n.get_display_name(),
                'tag': f'0x{n.tag.raw_byte:02X}',
                'tagClass': Exporter._get_tag_class_name(n.tag.tag_class),
                'constructed': bool(n.tag.constructed),
                'length': n.length,
                'offset': f'0x{n.tag_offset:04X}',
            }
            
            if include_hex and n.length > 0:
                if n.length <= 100:
                    d['value'] = n.value.hex()
                else:
                    d['value'] = f"[Binary data: {n.length} bytes]"
            
            if n.children:
                d['children'] = [node_to_dict(child) for child in n.children]
            
            return d
        
        data = node_to_dict(node)
        
        if pretty_print:
            return json.dumps(data, indent=2)
        else:
            return json.dumps(data)
    
    @staticmethod
    def _make_xml_safe(text: str) -> str:
        """
        Convert text to XML-safe element name
        
        Args:
            text: Original text
        
        Returns:
            XML-safe name
        """
        # Replace spaces and special chars
        safe = text.replace(' ', '_').replace('[', '').replace(']', '')
        safe = safe.replace('(', '').replace(')', '').replace('#', 'tag_')
        # Remove any remaining special characters
        safe = ''.join(c if c.isalnum() or c == '_' else '' for c in safe)
        # Ensure it starts with a letter or underscore
        if safe and not safe[0].isalpha() and safe[0] != '_':
            safe = '_' + safe
        return safe or 'element'
    
    @staticmethod
    def _get_tag_class_name(tag_class: int) -> str:
        """
        Get name of tag class
        
        Args:
            tag_class: Tag class value (0-3)
        
        Returns:
            Class name
        """
        names = ['UNIVERSAL', 'APPLICATION', 'CONTEXT', 'PRIVATE']
        return names[tag_class] if tag_class < len(names) else 'UNKNOWN'
    
    @staticmethod
    def search_and_export(node: ASN1Node, search_term: str) -> Optional[ASN1Node]:
        """
        Search for a node matching the term and return it
        
        Searches by display name, tag hex, or tag number
        
        Args:
            node: Root node to search from
            search_term: Search term (case-insensitive)
        
        Returns:
            Matching node or None
        """
        search_lower = search_term.lower()
        
        # Check current node
        if (search_lower in node.get_display_name().lower() or
            search_lower in f"0x{node.tag.raw_byte:02X}".lower() or
            search_lower in str(node.tag.raw_byte)):
            return node
        
        # Search children
        if node.children:
            for child in node.children:
                result = Exporter.search_and_export(child, search_term)
                if result:
                    return result
        
        return None
