# CSV Handling

Overview of CSV file processing.

## Topics

- [Edge Cases](edge-cases.md) - Common CSV problems and solutions

## CSV Basics

CSV (Comma-Separated Values) is a simple text format where:
- Each line is a record
- Fields are separated by delimiter (usually comma)
- Fields may be quoted to handle special characters

## Auto-Detection

The `analyze.py` script automatically detects:
- **Encoding**: UTF-8, Latin-1, Windows-1252, etc.
- **Delimiter**: Comma, semicolon, tab, pipe
- **Quote character**: Usually double-quote

## Common Delimiters

| Delimiter | Common Use | Example |
|-----------|------------|---------|
| `,` (comma) | Standard CSV | `a,b,c` |
| `;` (semicolon) | European CSV | `a;b;c` |
| `\t` (tab) | TSV files | `a	b	c` |
| `|` (pipe) | Data exports | `a|b|c` |

## Output Format

The `clean.py` script always outputs:
- UTF-8 encoding
- Comma delimiter
- Standard quoting (as needed)
- Unix line endings (LF)

This ensures consistent, portable output.
