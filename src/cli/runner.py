"""
asn1viewcli — headless ASN.1 tag extraction, no Qt required.

Usage
-----
asn1viewcli --data <file> --tags <file> --format csv|json|xml --output <file>

Arguments
---------
  -d / --data     Path to the ASN.1 / binary data file  (required)
  -t / --tags     Path to the tag definition file        (required)
  -f / --format   Output format: csv | json | xml        (default: csv)
  -o / --output   Output file path. Omit to print to stdout.
  --no-header     (CSV only) suppress the column header row

Exit codes
----------
  0  success
  1  argument / file error
  2  parse / extraction error
"""
import sys
import argparse
from pathlib import Path


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='asn1viewcli',
        description='Extract tagged fields from an ASN.1 binary file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument('-d', '--data',   required=True,
                   metavar='FILE', help='ASN.1 / binary data file')
    p.add_argument('-t', '--tags',   required=True,
                   metavar='FILE', help='Tag definition file')
    p.add_argument('-f', '--format', default='csv',
                   choices=['csv', 'json', 'xml'],
                   metavar='FORMAT', help='Output format: csv | json | xml  (default: csv)')
    p.add_argument('-o', '--output', default=None,
                   metavar='FILE', help='Output file (default: stdout)')
    p.add_argument('--no-header', action='store_true',
                   help='CSV only: suppress the header row')
    return p


def run_cli(argv=None) -> int:
    """
    Parse argv, run the conversion, and return an exit code.
    Prints status messages to stderr so stdout stays clean for piping.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    data_path = Path(args.data)
    tags_path = Path(args.tags)

    # ── Validate inputs ───────────────────────────────────────────────── #
    if not data_path.exists():
        print(f'ERROR: data file not found: {data_path}', file=sys.stderr)
        return 1
    if not tags_path.exists():
        print(f'ERROR: tag file not found: {tags_path}', file=sys.stderr)
        return 1

    fmt = args.format.lower()

    # ── Parse tag definitions ─────────────────────────────────────────── #
    print(f'Reading tag definitions from: {tags_path}', file=sys.stderr)
    from ..parser.tag_filter import TagDefinitionParser, TagExtractor
    tag_parser = TagDefinitionParser()
    try:
        field_defs = tag_parser.parse_file(str(tags_path))
    except Exception as e:
        print(f'ERROR reading tag file: {e}', file=sys.stderr)
        return 1

    if not field_defs:
        print('ERROR: no valid tag definitions found in tag file.', file=sys.stderr)
        return 1
    print(f'  {len(field_defs)} field definition(s) loaded.', file=sys.stderr)

    # ── Parse the data file ───────────────────────────────────────────── #
    print(f'Parsing data file: {data_path}', file=sys.stderr)
    from ..parser import BERDERParser
    from ..parser.asn1_types import ASN1Node, ASN1Tag
    try:
        with open(data_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f'ERROR reading data file: {e}', file=sys.stderr)
        return 1

    try:
        ber_parser = BERDERParser(data)
        roots = ber_parser.parse_all_nodes()
    except Exception as e:
        print(f'ERROR parsing data file: {e}', file=sys.stderr)
        return 2

    if not roots:
        print('ERROR: no valid ASN.1 records found in data file.', file=sys.stderr)
        return 2

    if len(roots) == 1:
        root_node = roots[0]
    else:
        synth_tag = ASN1Tag(tag_class=0, constructed=1, tag_number=0, raw_byte=0)
        root_node = ASN1Node(
            tag=synth_tag, length=len(data), value=b'',
            offset=0, tag_offset=0, length_offset=0, value_offset=0,
            children=roots,
        )
        for r in roots:
            r.parent = root_node

    print(f'  {len(roots)} top-level node(s) parsed.', file=sys.stderr)

    # ── Extract records ───────────────────────────────────────────────── #
    extractor = TagExtractor(field_defs)
    try:
        records = extractor.extract(root_node)
    except Exception as e:
        print(f'ERROR during extraction: {e}', file=sys.stderr)
        return 2

    if not records:
        print('ERROR: no matching records found. Check tag paths match the data file.',
              file=sys.stderr)
        return 2

    print(f'  {len(records)} record(s) extracted.', file=sys.stderr)

    # ── Format output ─────────────────────────────────────────────────── #
    from ..export.convert_exporter import ConvertExporter
    try:
        if fmt == 'csv':
            output = ConvertExporter.to_csv(records, header=not args.no_header)
        elif fmt == 'json':
            output = ConvertExporter.to_json(records)
        elif fmt == 'xml':
            output = ConvertExporter.to_xml(records)
        else:
            output = ConvertExporter.to_csv(records)
    except Exception as e:
        print(f'ERROR formatting output: {e}', file=sys.stderr)
        return 2

    # ── Write output ──────────────────────────────────────────────────── #
    if args.output:
        out_path = Path(args.output)
        try:
            out_path.write_text(output, encoding='utf-8')
            print(f'Output written to: {out_path}  ({out_path.stat().st_size:,} bytes)',
                  file=sys.stderr)
        except Exception as e:
            print(f'ERROR writing output file: {e}', file=sys.stderr)
            return 1
    else:
        sys.stdout.write(output)

    return 0


def main():
    """Entry point registered by pyproject.toml and PyInstaller."""
    sys.exit(run_cli())
