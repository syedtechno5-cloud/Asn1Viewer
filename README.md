# ASN.1 Viewer — BER/DER ASN.1 File Decoder

A modern desktop application and command-line tool for viewing, analyzing, and extracting data from ASN.1 binary files encoded in BER or DER format. Built for telecom, EMV, and PKI use cases.

**Version 1.1.0** | Python 3.8+ | PyQt6 | Windows · macOS · Linux

---

## What's New in v1.1.0

- **Tag-Based Extraction** — define field mappings in a simple text file and export any subset of an ASN.1 file to CSV, JSON, or XML
- **Convert Dialog** — GUI tool for extraction; auto-loads the file currently open in the viewer
- **File History** — recently used data, grammar, and tag files remembered across sessions
- **CLI Tool (`asn1viewcli`)** — headless extraction for scripting and automation; no GUI required
- **Standalone executables** — both `ASN1Viewer.exe` (GUI) and `asn1viewcli.exe` (CLI) built from a single PyInstaller spec

---

## Features

### Core Viewer
- **BER/DER Parser** — recursive TLV decoder; handles short/long form lengths, multi-byte tags, indefinite length
- **Hierarchical Tree View** — nested ASN.1 structure with tag class, number, length, and hex preview
- **Synchronized Hex Viewer** — raw bytes with tag/length/value highlighting when a tree node is selected
- **Detail View** — Hex, Text, XML, and JSON representations of the selected node

### Grammar Support
- Load CSV or JSON files to map tag hex values to human-readable names
- Grammar applies live to the tree view

### Full-File Export
- **Text** — indented tree with full metadata
- **XML** — well-formed XML of the entire structure
- **JSON** — complete tree as JSON

### Tag-Based Extraction (v1.1.0)
- Define which fields to extract using a simple tag definition file
- Outputs flat records — one row per matched record — as **CSV**, **JSON**, or **XML**
- Handles deeply nested structures and container tags automatically
- Supports telecom data types: IMSI, IMEI, MSISDN, TBCD, timestamp, OID, IPv4/IPv6

### CLI Tool — `asn1viewcli` (v1.1.0)
- Runs headless; no Qt or display required
- Suitable for batch jobs, scripts, and server-side processing
- Prints status to stderr, output to stdout or a file
- Returns standard exit codes for scripting

### File History (v1.1.0)
- Remembers recently used data files, grammar files, and tag definition files
- Accessible from **Tools → File History**
- Click any entry to reopen it

---

## Quick Start

### Run the GUI
```powershell
python -m pip install -r requirements.txt
python main.py
```

### Extract tags from the command line
```powershell
python -m pip install -e .          # registers the asn1viewcli command
asn1viewcli --data file.dat --tags tags.txt --format csv --output result.csv
```

### Build standalone executables
```powershell
python -m pip install pyinstaller
python -m PyInstaller asn1_viewer.spec --noconfirm
# dist\ASN1Viewer.exe   — GUI
# dist\asn1viewcli.exe  — CLI (no Python needed on target machine)
```

---

## Installation

See [INSTALLATION.md](INSTALLATION.md) for full platform-specific instructions.

**Minimum steps:**
```powershell
cd "path\to\Asn1Viewer"
python -m pip install -r requirements.txt
python main.py                      # open GUI
```

---

## GUI Usage

### Open a file
1. Click **Open File** or **File → Open File**
2. Select any BER/DER binary file (`.der`, `.cer`, `.dat`, `.asn1`, and others)

### Extract fields with the Convert dialog
1. Open the data file in the viewer first
2. **Tools → Convert / Extract Tags**
3. Browse for a tag definition file (see format below), or paste definitions directly
4. Choose CSV / JSON / XML and click **Convert**
5. Preview the result, then **Save Output**

> The dialog always uses the file currently open in the viewer — no separate file picker needed.

### File History
- **Tools → File History** shows recently used files grouped by category
- Double-click or select and click **Open Selected** to reopen any file

---

## CLI Usage

```
asn1viewcli -d <data_file> -t <tags_file> [-f csv|json|xml] [-o <output_file>] [--no-header]
```

| Flag | Long form | Description |
|------|-----------|-------------|
| `-d` | `--data`   | ASN.1 / binary data file **(required)** |
| `-t` | `--tags`   | Tag definition file **(required)** |
| `-f` | `--format` | Output format: `csv` \| `json` \| `xml`  (default: `csv`) |
| `-o` | `--output` | Output file path (default: stdout) |
|      | `--no-header` | Suppress CSV header row |

**Examples:**
```powershell
# Save to file
asn1viewcli -d records.dat -t fields.txt -f csv -o output.csv

# JSON to stdout
asn1viewcli -d records.dat -t fields.txt -f json

# XML with no header, exit code for scripting
asn1viewcli -d records.dat -t fields.txt -f xml -o output.xml
if ($LASTEXITCODE -ne 0) { Write-Error "Extraction failed" }
```

**Exit codes:** `0` success · `1` file/argument error · `2` parse/extraction error

See [CLI_GUIDE.md](CLI_GUIDE.md) for full reference.

---

## Tag Definition File Format

Each line defines one field to extract:

```
PATH,FieldName,DataType
```

`PATH` is one or more tag descriptors joined by `->`. The **first** descriptor is the record container; the rest navigate to the field inside it.

**Tag descriptor forms:**

| Form | Example | Meaning |
|------|---------|---------|
| `CLASS:Number` | `CTX:0` | Context tag 0 |
| Hex byte | `0xA0` | Class and number from raw byte |

**CLASS abbreviations:** `CTX` / `CONTEXT` · `APP` / `APPLICATION` · `UNI` / `UNIVERSAL` · `PRIV` / `PRIVATE`

**Supported data types:**

| Type | Description |
|------|-------------|
| `int` / `uint` | Signed / unsigned big-endian integer |
| `string` / `ascii` | UTF-8 or ASCII text |
| `hex` / `bytes` | Raw bytes as uppercase hex |
| `imsi` / `imei` | Telephony BCD (low nibble first) |
| `tbcd` / `bcd` | Telephony BCD / standard BCD |
| `msisdn` | TON/NPI byte + TBCD digits |
| `ip` / `ipv6` | IPv4 or IPv6 address string |
| `bool` | Boolean (any non-zero byte = true) |
| `timestamp` | 6-byte BCD `YYMMDDHHMMSS` |
| `oid` | ASN.1 Object Identifier |
| `length` | Value byte count (debug) |

**Example — 3GPP MSC CDR file:**
```
# CTX:1 is the outer envelope; CTX:7 records inside it each contain these fields
CTX:1->CTX:7->CTX:1,servedIMSI,imsi
CTX:1->CTX:7->CTX:0,recordType,int
CTX:1->CTX:7->CTX:8,recordOpeningTime,timestamp
CTX:1->CTX:7->CTX:3,calledNumber,msisdn
```

**Example — flat record file (each CTX:20 is a top-level record):**
```
CTX:20->CTX:0,recordType,int
CTX:20->CTX:3,servedIMSI,imsi
CTX:20->CTX:4,servedIMEI,imei
```

See [TAG_EXTRACTION.md](TAG_EXTRACTION.md) for the full guide including path semantics and telecom examples.

---

## Project Structure

```
Asn1Viewer/
├── main.py                     # Entry point — GUI or CLI routing
├── asn1viewcli.py              # CLI entry point (used by PyInstaller)
├── setup.py                    # Package definition; registers asn1viewcli command
├── asn1_viewer.spec            # PyInstaller spec — builds GUI + CLI executables
├── requirements.txt            # Runtime dependencies
│
├── src/
│   ├── parser/
│   │   ├── ber_der_parser.py   # Recursive BER/DER TLV decoder
│   │   ├── asn1_types.py       # ASN1Node / ASN1Tag dataclasses; TagClass enum
│   │   └── tag_filter.py       # TagDefinitionParser, ValueDecoder, TagExtractor
│   │
│   ├── grammar/
│   │   └── grammar_manager.py  # CSV/JSON tag-name mapping loader
│   │
│   ├── export/
│   │   ├── __init__.py         # Exporter — full-tree Text/XML/JSON
│   │   └── convert_exporter.py # ConvertExporter — flat records CSV/JSON/XML
│   │
│   ├── gui/
│   │   ├── main_window.py      # Main window; Tools menu; Convert & History dialogs
│   │   ├── convert_tab.py      # Convert dialog UI + ConvertThread
│   │   ├── history_tab.py      # History dialog UI
│   │   ├── tree_view.py        # ASN1TreeWidget
│   │   ├── hex_viewer.py       # HexViewer with TLV highlighting
│   │   ├── detail_view.py      # Tabbed detail panel
│   │   └── grammar_dialog.py   # Grammar load dialog
│   │
│   ├── cli/
│   │   └── runner.py           # Headless CLI runner (no Qt)
│   │
│   └── utils/
│       ├── history_manager.py  # JSON-persisted file history (~/.asn1viewer/)
│       └── __init__.py
│
├── resources/
│   ├── sample_grammar.csv
│   └── sample_grammar.json
│
└── docs/
    ├── README.md               # This file
    ├── QUICKSTART.md
    ├── INSTALLATION.md
    ├── CLI_GUIDE.md            # Full CLI reference
    └── TAG_EXTRACTION.md       # Tag definition file format & examples
```

---

## Building Executables

### Local build

**Windows:**
```powershell
build_windows.bat
```

**macOS / Linux:**
```bash
chmod +x build.sh && ./build.sh
```

Both scripts install dependencies, run PyInstaller, and produce a platform zip/tar.gz ready to upload.

**Manual:**
```powershell
python -m pip install pyinstaller
python -m PyInstaller asn1_viewer.spec --noconfirm
```

Output in `dist\`:

| Platform | GUI | CLI |
|----------|-----|-----|
| Windows | `ASN1Viewer.exe` | `asn1viewcli.exe` |
| macOS | `ASN1Viewer.app` (bundle) | `asn1viewcli` |
| Linux | `ASN1Viewer` | `asn1viewcli` |

All outputs are fully self-contained — no Python required on the target machine.

### GitHub Release (automated — all three platforms at once)

Push a version tag and GitHub Actions builds everything and creates the release automatically:

```bash
git tag v1.1.0
git push origin v1.1.0
```

GitHub Actions runs on Windows, macOS, and Linux in parallel and attaches these assets to the release:

| Asset | Platform |
|-------|----------|
| `ASN1Viewer-Windows-x64.zip` | Windows — `ASN1Viewer.exe` + `asn1viewcli.exe` |
| `ASN1Viewer-macOS-x64.zip` | macOS — `ASN1Viewer.app` + `asn1viewcli` |
| `ASN1Viewer-Linux-x64.tar.gz` | Linux — `ASN1Viewer` + `asn1viewcli` |

Workflow files: [`.github/workflows/release.yml`](.github/workflows/release.yml) (release) · [`.github/workflows/build.yml`](.github/workflows/build.yml) (CI on every push)

---

## Supported File Types

Any file containing BER or DER encoded ASN.1 data. Common extensions:

`.der` · `.cer` · `.asn1` · `.asn` · `.dat` · `.bin` · `.dn` · `.ans`

Files > 10 MB trigger a confirmation dialog; parsing runs on a background thread.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: PyQt6` | `python -m pip install -r requirements.txt` |
| `asn1viewcli` not found | Add Python Scripts dir to PATH, or use `python -m pip install -e .` |
| No records extracted | Verify tag paths with the viewer — check class/number against the tree |
| Extra blank lines in CSV | Use the Save button in the GUI (fixed in v1.1.0) |
| Only 1 record extracted | Ensure the record container tag is correct (v1.1.0 handles branching automatically) |

---

## Architecture Notes

### Tag Extraction Algorithm
`TagExtractor.extract()` uses an iterative DFS. When a node matches the record key:
- `_build_records()` calls `_navigate_all()` which branches over **all** children matching each path step — this handles CDR files where an outer container holds thousands of records of the same type
- If records are found at a level, children are **not** pushed further — preventing nested nodes with the same tag from being double-counted
- If no records are found at a level (outer wrapper), children are explored

### CLI vs GUI
`main.py` routes based on presence of CLI flags (`--data`, `--tags`, etc.). The CLI path imports only `src.cli.runner` — no Qt is imported, making it suitable for headless server environments.

---

## License

© 2025 Syed Technologies. All rights reserved.

---

**Version**: 1.1.0 | **Updated**: May 2026 | **Python**: 3.8+ | **GUI**: PyQt6
