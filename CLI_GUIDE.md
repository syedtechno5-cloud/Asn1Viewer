# CLI Guide — `asn1viewcli`

`asn1viewcli` extracts tagged fields from ASN.1 binary files and outputs flat records as CSV, JSON, or XML. It runs entirely headless — no display, no Qt, suitable for scripts, batch jobs, and server-side automation.

---

## Installation

**Registered command (requires Python):**
```powershell
python -m pip install -e .         # run once from the project directory
asn1viewcli --help
```

**Standalone executable (no Python needed):**
```powershell
python -m pip install pyinstaller
python -m PyInstaller asn1_viewer.spec --noconfirm
# dist\asn1viewcli.exe is ready to copy anywhere
```

---

## Syntax

```
asn1viewcli -d <data_file> -t <tags_file> [-f FORMAT] [-o <output_file>] [--no-header]
```

### Required arguments

| Flag | Long form | Description |
|------|-----------|-------------|
| `-d` | `--data`  | Path to the ASN.1 / binary data file |
| `-t` | `--tags`  | Path to the tag definition file |

### Optional arguments

| Flag | Long form | Default | Description |
|------|-----------|---------|-------------|
| `-f` | `--format` | `csv` | Output format: `csv` \| `json` \| `xml` |
| `-o` | `--output` | stdout | Output file path |
|      | `--no-header` | — | CSV only: suppress the header row |
| `-h` | `--help`  | — | Show help and exit |

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Argument or file error (file not found, bad path) |
| `2` | Parse or extraction error (invalid ASN.1, no matching records) |

Use exit codes in scripts to detect failures:

**PowerShell:**
```powershell
asn1viewcli -d file.dat -t tags.txt -f csv -o out.csv
if ($LASTEXITCODE -ne 0) { Write-Error "Extraction failed"; exit 1 }
```

**Bash:**
```bash
asn1viewcli -d file.dat -t tags.txt -f csv -o out.csv || { echo "Failed"; exit 1; }
```

---

## Output behaviour

- **Status messages** are written to **stderr** — they do not pollute the output
- **Extracted data** goes to **stdout** (or the file specified with `-o`)
- This allows clean piping:

```powershell
# Pipe CSV to another tool
asn1viewcli -d file.dat -t tags.txt -f csv | Import-Csv

# Pipe JSON into jq (Linux/macOS)
asn1viewcli -d file.dat -t tags.txt -f json | jq '.[] | .servedIMSI'
```

---

## Examples

### Basic CSV export to file
```powershell
asn1viewcli --data MSCPSHHW00V20260423.dat --tags msc_fields.txt --format csv --output records.csv
```

### JSON output to stdout
```powershell
asn1viewcli -d file.dat -t tags.txt -f json
```

### XML export
```powershell
asn1viewcli -d file.dat -t tags.txt -f xml -o output.xml
```

### CSV without header row
```powershell
asn1viewcli -d file.dat -t tags.txt --no-header -o output.csv
```

### Standalone exe (no Python on target machine)
```powershell
.\dist\asn1viewcli.exe -d file.dat -t tags.txt -f csv -o result.csv
```

### Batch processing multiple files
```powershell
Get-ChildItem *.dat | ForEach-Object {
    $out = $_.BaseName + ".csv"
    asn1viewcli -d $_.FullName -t tags.txt -f csv -o $out
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: $out"
    } else {
        Write-Warning "FAILED: $($_.Name)"
    }
}
```

### Scheduled task / cron job
```powershell
# Windows Task Scheduler action:
asn1viewcli.exe -d "C:\CDR\daily.dat" -t "C:\CDR\fields.txt" -f csv -o "C:\CDR\out\daily.csv"
```

```bash
# Linux cron (every hour)
0 * * * * /opt/asn1viewer/asn1viewcli -d /data/cdr.dat -t /etc/cdr_fields.txt -f csv -o /out/cdr_$(date +\%Y\%m\%d\%H).csv
```

---

## Tag definition file

The `-t` / `--tags` argument points to a plain text file defining which fields to extract. Each non-blank, non-comment line specifies one field:

```
PATH,FieldName,DataType
```

**Example (`msc_fields.txt`):**
```
# 3GPP MSC CDR — roaming records (CTX:7)
CTX:1->CTX:7->CTX:1,servedIMSI,imsi
CTX:1->CTX:7->CTX:0,recordType,int
CTX:1->CTX:7->CTX:8,recordOpeningTime,timestamp
CTX:1->CTX:7->CTX:3,calledNumber,msisdn
CTX:1->CTX:7->CTX:11,callDuration,uint
```

**Example (`gprs_fields.txt`):**
```
# GPRS PGW CDR — each CTX:20 is a top-level record
CTX:20->CTX:0,recordType,int
CTX:20->CTX:3,servedIMSI,imsi
CTX:20->CTX:4,servedIMEI,imei
CTX:20->CTX:6,dataVolumeUplink,uint
CTX:20->CTX:7,dataVolumeDownlink,uint
```

See [TAG_EXTRACTION.md](TAG_EXTRACTION.md) for the complete format reference.

---

## Stderr output format

The tool writes progress lines to stderr so you can monitor long-running extractions:

```
Reading tag definitions from: msc_fields.txt
  5 field definition(s) loaded.
Parsing data file: MSCPSHHW00V20260423.dat
  1 top-level node(s) parsed.
  8021 record(s) extracted.
Output written to: records.csv  (284,150 bytes)
```

Redirect stderr to suppress it:
```powershell
asn1viewcli -d file.dat -t tags.txt -o out.csv 2>$null
```

---

## CSV output notes

- Header row matches the `FieldName` values from the tag file, in definition order
- Fields not found in a record are output as empty strings (no column is skipped)
- Line endings are `\n` — opens correctly in Excel, Notepad, and Python `csv` module
- Omit the header with `--no-header` when appending to an existing file

---

## Compared to the GUI Convert dialog

| Feature | GUI Convert dialog | `asn1viewcli` |
|---------|-------------------|---------------|
| File selection | Uses file open in viewer | Command-line argument |
| Interactive preview | Yes | No |
| Automation / scripting | No | Yes |
| Batch processing | No | Yes (loop in shell) |
| Requires display | Yes | No |
| Exit codes | No | Yes |
| Pipe to other tools | No | Yes |

Both use identical extraction logic — the same tag definitions and data types work in both.
