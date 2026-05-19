# Quick Start — ASN.1 Viewer v1.1.0

## 1. Install

```powershell
python -m pip install -r requirements.txt
```

That's it. No other setup required to run the GUI.

---

## 2. Open the GUI

```powershell
python main.py
```

Or run the pre-built executable:
```
dist\ASN1Viewer.exe
```

---

## 3. View an ASN.1 file

1. Click **Open File** (or `Ctrl+O`)
2. Select any BER/DER binary — `.der`, `.cer`, `.dat`, `.bin`, etc.
3. The left panel shows the tag tree; click a node to highlight its bytes in the hex viewer

---

## 4. Extract specific fields (Convert dialog)

The converter lets you pull named fields out of a CDR or other structured binary and save them as CSV, JSON, or XML.

**Step 1 — Create a tag definition file** (plain text, `.txt` or `.tags`):
```
# PATH,FieldName,DataType
CTX:1->CTX:7->CTX:1,servedIMSI,imsi
CTX:1->CTX:7->CTX:0,recordType,int
CTX:1->CTX:7->CTX:8,openingTime,timestamp
```

**Step 2 — Open the Convert dialog:**
- **Tools → Convert / Extract Tags**
- The dialog automatically uses the file already open in the viewer
- If no file is open yet, open one first

**Step 3 — Load the tag file:**
- Click **Browse** next to the Tag Definition File
- Select your `.txt` or `.tags` file

**Step 4 — Convert and save:**
- Choose **CSV / JSON / XML**
- Click **Convert** — results appear in the preview
- Click **Save Output** to write the file

> Click **? Format Help** inside the dialog for a full reference of supported types and path syntax.

---

## 5. Use the CLI (no GUI needed)

Install the `asn1viewcli` command once:
```powershell
python -m pip install -e .
```

Then run it anywhere:
```powershell
asn1viewcli --data records.dat --tags fields.txt --format csv --output result.csv
```

Or use the standalone exe (no Python needed):
```powershell
dist\asn1viewcli.exe --data records.dat --tags fields.txt --format csv --output result.csv
```

See [CLI_GUIDE.md](CLI_GUIDE.md) for all options and examples.

---

## 6. Reopen recent files

**Tools → File History** lists recently used data files, grammar files, and tag files grouped by category. Double-click any entry to reopen it.

---

## 7. Add human-readable tag names (Grammar)

1. **Tools → Load Grammar** (or click **Load Grammar** in the toolbar)
2. Browse for a CSV or JSON grammar file mapping tag IDs to names
3. The tree view immediately shows the names

**CSV grammar format:**
```csv
tag_id,name
0x80,recordType
0x81,servedIMSI
0x82,servedIMEI
```

---

## Common tag definition types

| Use case | DataType |
|----------|----------|
| Integer counter | `int` |
| IMSI / IMEI | `imsi` / `imei` |
| Phone number | `msisdn` |
| Date/time | `timestamp` |
| Raw dump | `hex` |
| Text field | `string` |
| IP address | `ip` |

---

## Build standalone executables

```powershell
python -m pip install pyinstaller
python -m PyInstaller asn1_viewer.spec --noconfirm
```

Output in `dist\`:
- `ASN1Viewer.exe` — GUI
- `asn1viewcli.exe` — CLI (copy to any Windows machine, no Python needed)

---

## Need more detail?

| Guide | Contents |
|-------|----------|
| [README.md](README.md) | Full feature overview and architecture |
| [INSTALLATION.md](INSTALLATION.md) | Platform-specific install, virtual envs, PATH setup |
| [CLI_GUIDE.md](CLI_GUIDE.md) | Complete CLI reference with scripting examples |
| [TAG_EXTRACTION.md](TAG_EXTRACTION.md) | Tag definition format, path semantics, telecom examples |
