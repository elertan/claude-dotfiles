# CSV Edge Cases

Common problems when parsing CSV files and how to handle them.

## Encoding Issues

### Problem: Mojibake (garbled text)
Cause: Wrong encoding assumed
Example: `Ã©` instead of `é`

**Solution**: The `analyze.py` auto-detects encoding using `chardet`.
- Check `encoding` field in analysis output
- If wrong, may need manual override

### Problem: BOM (Byte Order Mark)
Cause: UTF-8 BOM at file start (`\xEF\xBB\xBF`)
Example: First column name has hidden characters

**Solution**: pandas handles this with `encoding='utf-8-sig'`

### Common Encodings

| Encoding | Usage |
|----------|-------|
| UTF-8 | Modern, international |
| Latin-1 (ISO-8859-1) | Western European |
| Windows-1252 | Windows legacy |
| ASCII | Basic English only |

## Quoting Issues

### Problem: Unescaped quotes
Cause: Quote inside field not escaped
Example: `He said "hello"` breaks parsing

**Standard escape**: Double the quote
- Correct: `"He said ""hello"""`
- Incorrect: `"He said "hello""`

### Problem: Inconsistent quoting
Cause: Some fields quoted, some not
Example: `value1,"value 2",value3`

**Solution**: pandas handles mixed quoting

## Delimiter Issues

### Problem: Wrong delimiter detected
Cause: Delimiter character appears in data

**Solution**:
- Check `delimiter` in analysis output
- Fields with delimiter should be quoted
- May need manual specification

### Problem: Inconsistent column counts
Cause: Extra/missing delimiters
Example: `a,b,c` then `a,b,c,d`

**Detection**: Will cause parsing warnings
**Solution**: Investigate source data

## Newline Issues

### Problem: Newlines inside fields
Cause: Multi-line text in cell
Example: Address with line breaks

**Correct format**: Quote the field
```
"123 Main St
Apt 4
City, ST 12345"
```

### Problem: Mixed line endings
Cause: Different OS origins (CRLF vs LF)

**Solution**: pandas handles automatically

## Common Problems

| Issue | Symptom | Solution |
|-------|---------|----------|
| Wrong encoding | Garbled characters | Check/specify encoding |
| BOM present | Weird first column | Use `utf-8-sig` |
| Bad quotes | Parse errors | Check source quoting |
| Wrong delimiter | Wrong columns | Specify delimiter |
| Inconsistent columns | Warnings/errors | Fix source |
| Newlines in data | Missing rows | Ensure proper quoting |

## Best Practices for Output

The `clean.py` produces clean CSVs:
- UTF-8 encoding (universal)
- Comma delimiter (standard)
- Quote fields containing commas/newlines
- Unix line endings (LF)
- No BOM

## Handling Large Files

For files too large for memory:

1. **Check size**: `memory_usage_mb` in analysis
2. **Use chunking**: Process in parts
3. **Optimize dtypes**: Reduce memory

See [Handling Large Datasets](../operations/normalization.md) for techniques.

## Troubleshooting

### Can't open file
- Check file path
- Check permissions
- Try different encoding

### Wrong number of columns
- Check delimiter
- Look for unquoted delimiters in data
- Check for missing closing quotes

### Special characters wrong
- Try different encoding
- Check for double-encoding
- Verify source file encoding

### Parse errors
- Check for malformed rows
- Look for unescaped quotes
- Verify consistent structure
