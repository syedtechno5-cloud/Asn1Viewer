# Tag Extraction Guide

This guide explains how to write tag definition files for the Convert dialog and the `asn1viewcli` CLI tool.

---

## Overview

Tag extraction takes an ASN.1 binary file and a tag definition file, then outputs flat records — one row per matched record — in CSV, JSON, or XML.

The tag definition file tells the extractor:
1. **Which node** in the tree is the record container (one record per matched container)
2. **Which child nodes** inside that container are the fields to extract
3. **How to decode** the raw bytes of each field

---

## Tag definition file format

Plain text. UTF-8. One field per line.

```
# Comment lines start with #
# Blank lines are ignored

PATH,FieldName,DataType
```

| Part | Required | Description |
|------|----------|-------------|
| `PATH` | Yes | `->` separated list of tag descriptors |
| `FieldName` | Yes | Column name in the output |
| `DataType` | Yes* | How to decode the raw bytes |

*If DataType is omitted or unknown, raw uppercase hex is used.

---

## PATH syntax

### Tag descriptors

Each element of the path identifies an ASN.1 tag by its class and number.

**CLASS:Number form:**
```
CTX:0    CTX:7    APP:3    UNI:16    PRIV:1
```

**Hex byte form** (class and constructed bit derived from the byte):
```
0xA0    0x80    0xB4    0x61
```

**CLASS abbreviations:**

| Abbreviation | Full name | Tag class value |
|---|---|---|
| `CTX` or `CONTEXT` | Context-specific | 2 |
| `APP` or `APPLICATION` | Application | 1 |
| `UNI` or `UNIVERSAL` | Universal | 0 |
| `PRIV` or `PRIVATE` | Private | 3 |

### Path structure

```
RECORD_CONTAINER -> FIELD_STEP_1 -> ... -> FIELD_STEP_N
```

- The **first** element is the **record container** — every CONSTRUCTED node with this tag produces one output record
- The **remaining** elements navigate *inside* the container to the field value

**Simple (2 elements):**
```
CTX:20->CTX:0,recordType,int
```
Find each CTX:20 (constructed) → extract its CTX:0 child.

**Nested (3 elements):**
```
CTX:1->CTX:7->CTX:1,servedIMSI,imsi
```
Find each CTX:1 (constructed) → within it, find CTX:7 → within that, extract CTX:1.

**Deep nesting:**
```
CTX:0->CTX:10->CTX:0,plmnId,hex
```

---

## How the extractor handles containers

### Flat file (many top-level records)

```
[CTX:20]  ← record 1
[CTX:20]  ← record 2
[CTX:20]  ← record 3
...
```

Tag: `CTX:20->CTX:0,recordType,int`

Each CTX:20 is matched directly. One output row per CTX:20.

---

### Nested file (outer envelope + many records inside)

```
[CTX:1]  ← outer envelope
    [CTX:7]  ← CDR record 1
        [CTX:1] = IMSI
    [CTX:7]  ← CDR record 2
        [CTX:1] = IMSI
    [CTX:6]  ← CDR record (different type)
    ...
```

Tag: `CTX:1->CTX:7->CTX:1,servedIMSI,imsi`

The extractor finds CTX:1 (the envelope), then navigates CTX:7→CTX:1 across **all** CTX:7 children — producing one row per CTX:7 record (not just one row for the entire envelope).

---

### Why child records with the same tag are not duplicated

After extracting records from a matched node, the extractor **stops recursing into that node's children**. This prevents a nested CTX:7 sub-field inside a CTX:7 record from being matched as a second record. Only the first level where records are successfully extracted is used.

---

## Supported data types

### Numeric

| DataType | Description | Example input | Example output |
|----------|-------------|---------------|----------------|
| `int` | Big-endian signed integer | `0x07` | `7` |
| `uint` / `unsigned` | Big-endian unsigned integer | `0x0001F4` | `500` |

### Text

| DataType | Description |
|----------|-------------|
| `string` / `utf8` | UTF-8 string |
| `ascii` / `ia5` | ASCII / IA5 string |

### Binary

| DataType | Description | Example output |
|----------|-------------|----------------|
| `hex` / `bytes` | Raw bytes as uppercase hex | `A1B2C3` |

### Telecom

| DataType | Description | Example input | Example output |
|----------|-------------|---------------|----------------|
| `imsi` | Telephony BCD, low nibble first, 0xF=pad | `91 29 33 03 ...` | `192933...` |
| `imei` | Same as `imsi` | | |
| `tbcd` | Telephony BCD (same as imsi/imei) | | |
| `bcd` | Standard BCD, high nibble first | | |
| `msisdn` | Byte 0 = TON/NPI, rest = TBCD | `91 94 71 ...` | `+4917...` |
| `timestamp` | 6-byte BCD `YYMMDDHHMMSS` | `26 04 23 22 47 10` | `2026-04-23 22:47:10` |

### Network

| DataType | Description | Example output |
|----------|-------------|----------------|
| `ip` / `ipv4` | 4-byte IPv4 address | `192.168.1.1` |
| `ipv6` | 16-byte IPv6 address | `2001:db8::1` |

### Other

| DataType | Description |
|----------|-------------|
| `bool` / `boolean` | `true` if any byte is non-zero, else `false` |
| `oid` | ASN.1 Object Identifier (e.g. `1.2.840.113549`) |
| `length` | Number of value bytes (useful for debugging) |

---

## Complete examples

### 3GPP MSC CDR — roaming records

Structure: one outer CTX:1 envelope containing thousands of CDR records (CTX:7 = roaming, CTX:6 = MO call, CTX:1 = MT call, etc.)

```
# msc_fields.txt
# Roaming records (CTX:7) inside the CTX:1 envelope
CTX:1->CTX:7->CTX:0,recordType,int
CTX:1->CTX:7->CTX:1,servedIMSI,imsi
CTX:1->CTX:7->CTX:2,servedIMEI,imei
CTX:1->CTX:7->CTX:3,roamingNumber,msisdn
CTX:1->CTX:7->CTX:4,recordingEntity,msisdn
CTX:1->CTX:7->CTX:8,recordOpeningTime,timestamp
CTX:1->CTX:7->CTX:11,callDuration,uint
```

Run:
```powershell
asn1viewcli -d MSCPSHHW00V20260423.dat -t msc_fields.txt -f csv -o msc_records.csv
```

---

### 3GPP GPRS PGW CDR — flat file

Structure: 17,000+ CTX:20 records directly at the top level (no outer wrapper).

```
# gprs_fields.txt
CTX:20->CTX:0,recordType,int
CTX:20->CTX:1,networkInitiation,bool
CTX:20->CTX:3,servedIMSI,imsi
CTX:20->CTX:4,servedIMEI,imei
CTX:20->CTX:6,dataVolumeUplink,uint
CTX:20->CTX:7,dataVolumeDownlink,uint
CTX:20->CTX:8,recordOpeningTime,timestamp
CTX:20->CTX:12,accessPointName,string
CTX:20->CTX:20,duration,uint
```

Run:
```powershell
asn1viewcli -d gprs04_202601061246.dat -t gprs_fields.txt -f csv -o gprs_records.csv
```

---

### EMV / X.509 certificate fields

```
# emv_fields.txt
UNI:16->UNI:16->UNI:6,oid,oid
UNI:16->UNI:16->UNI:4,commonName,string
```

---

## Discovering the right tag paths

Use the **ASN.1 Viewer GUI** to explore the tree:

1. Open the binary file (`Open File`)
2. Expand nodes until you find the record container
3. Note the **tag class** and **tag number** shown in the detail panel for each node
4. Build your path:
   - First element = the container you want one row per
   - Remaining elements = the path down to the field

**Reading tag details from the tree:**
- `[CTX #1] CONSTRUCTED` → `CTX:1`
- `[CTX #7] CONSTRUCTED` → `CTX:7`
- `[CTX #1] PRIMITIVE` → field value (CTX:1 as a field step)

---

## Output formats

### CSV
```
servedIMSI,recordType,callDuration
19923330022551,7,120
19923330005150,7,45
```

### JSON
```json
[
  {"servedIMSI": "19923330022551", "recordType": "7", "callDuration": "120"},
  {"servedIMSI": "19923330005150", "recordType": "7", "callDuration": "45"}
]
```

### XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<records count="2">
  <record>
    <servedIMSI>19923330022551</servedIMSI>
    <recordType>7</recordType>
    <callDuration>120</callDuration>
  </record>
  <record>
    <servedIMSI>19923330005150</servedIMSI>
    <recordType>7</recordType>
    <callDuration>45</callDuration>
  </record>
</records>
```

---

## Tips

- **Use `hex` for unknown fields** — examine the raw bytes in the viewer first, then switch to the correct type
- **Use `length`** to quickly check whether a field is present and how large it is
- **Comment out fields** with `#` while debugging to narrow down issues
- **Missing fields** appear as empty strings in the output — they do not cause an error
- **Multiple field definitions with the same record container** are all extracted together into one record per matched container node
