"""
Test and Demo Script for ASN.1 Viewer
Tests parsing, grammar loading, and export functionality
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.parser import BERDERParser
from src.grammar import GrammarManager
from src.export import Exporter


def create_test_asn1_data():
    """Create sample BER/DER encoded data for testing"""
    # SEQUENCE { INTEGER 42, OCTET STRING "Hello" }
    # SEQUENCE tag (0x30)
    # Length 12
    # INTEGER tag (0x02)
    # Length 1
    # Value 42 (0x2A)
    # OCTET STRING tag (0x04)
    # Length 5  
    # Value "Hello"
    
    data = bytes([
        0x30, 0x0A,           # SEQUENCE, length 10
        0x02, 0x01, 0x2A,     # INTEGER, length 1, value 42
        0x04, 0x05,           # OCTET STRING, length 5
    ]) + b"Hello"
    
    return data


def test_parser():
    """Test ASN.1 parser"""
    print("=" * 60)
    print("TEST 1: ASN.1 Parser")
    print("=" * 60)
    
    # Create test data
    data = create_test_asn1_data()
    print(f"Test data (hex): {data.hex()}")
    print(f"Test data length: {len(data)} bytes")
    print()
    
    # Parse
    parser = BERDERParser(data)
    root = parser.parse()
    
    if root:
        print(f"✓ Parse successful!")
        print(f"  Root tag: {root.get_display_name()}")
        print(f"  Root length: {root.length}")
        print(f"  Children: {len(root.children)}")
        for i, child in enumerate(root.children):
            print(f"    [{i}] {child.get_display_name()} - Length: {child.length}")
        print()
        return root
    else:
        print("✗ Parse failed!")
        return None


def test_grammar(root_node):
    """Test grammar loading and application"""
    print("=" * 60)
    print("TEST 2: Grammar Manager")
    print("=" * 60)
    
    # Create sample grammar
    grammar_path = Path("test_grammar.csv")
    
    # Write sample grammar
    with open(grammar_path, 'w') as f:
        f.write("tag_id,name\n")
        f.write("0x30,SEQUENCE\n")
        f.write("0x02,INTEGER\n")
        f.write("0x04,OCTET-STRING\n")
    
    print(f"Created sample grammar: {grammar_path}")
    print()
    
    # Load grammar
    grammar = GrammarManager()
    success = grammar.load_csv(str(grammar_path))
    
    if success:
        print("✓ Grammar loaded!")
        mappings = grammar.get_all_mappings()
        print(f"  Mappings: {len(mappings)}")
        for tag_id, name in mappings.items():
            print(f"    {tag_id}: {name}")
        print()
        
        # Apply to root node
        def apply_grammar(node):
            tag_hex = f"0x{node.tag.raw_byte:02X}"
            name = grammar.get_name_by_hex_string(tag_hex)
            if name:
                node.grammar_name = name
            for child in node.children:
                apply_grammar(child)
        
        apply_grammar(root_node)
        print("✓ Grammar applied to tree")
        print()
    else:
        print("✗ Grammar loading failed!")
    
    # Clean up
    grammar_path.unlink()
    return grammar


def test_export(root_node):
    """Test export functionality"""
    print("=" * 60)
    print("TEST 3: Export Functionality")
    print("=" * 60)
    print()
    
    # Text export
    print("Text Export:")
    print("-" * 40)
    text = Exporter.to_text(root_node, include_hex=True, include_offset=True)
    print(text)
    print()
    
    # XML export
    print("XML Export:")
    print("-" * 40)
    xml = Exporter.to_xml(root_node, include_hex=True, pretty_print=True)
    print(xml[:500])  # First 500 chars
    print()
    
    # JSON export
    print("JSON Export:")
    print("-" * 40)
    json_str = Exporter.to_json(root_node, include_hex=True, pretty_print=True)
    print(json_str[:500])  # First 500 chars
    print()
    
    print("✓ All exports completed successfully!")
    print()


def main():
    """Run all tests"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "ASN.1 Viewer - Test Suite" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Test 1: Parser
    root_node = test_parser()
    if not root_node:
        print("Cannot continue without successful parse")
        return
    
    # Test 2: Grammar
    test_grammar(root_node)
    
    # Test 3: Export
    test_export(root_node)
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print()
    print("To run the GUI application:")
    print("  python main.py")
    print()


if __name__ == "__main__":
    main()
