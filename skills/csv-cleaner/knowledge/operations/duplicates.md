# Duplicate Handling

## Detection

Run `analyze.py` and check:
- `duplicates.exact_duplicate_rows`: Count of exact duplicate rows
- `duplicates.duplicate_percentage`: Percentage of duplicates

For column-level uniqueness:
- `unique_count` and `unique_percent` per column
- Issue `potentially_unique_identifier` if 100% unique

## Types of Duplicates

| Type | Description | Detection | Handling |
|------|-------------|-----------|----------|
| **Exact** | Identical rows | `df.duplicated()` | Simple removal |
| **Key-based** | Same key, different data | Check key columns | Merge or keep latest |
| **Fuzzy** | Similar but not identical | Similarity algorithms | Advanced matching |

## Operations

### Remove Exact Duplicates
```json
{"type": "remove_duplicates", "keep": "first"}
```

Parameters:
- `columns`: Subset of columns to check (null = all columns)
- `keep`: Which duplicate to keep
  - `"first"`: Keep first occurrence
  - `"last"`: Keep last occurrence
  - `"none"`: Remove all duplicates

### Examples

#### Keep first occurrence of exact duplicates
```json
{
  "operations": [
    {"type": "remove_duplicates", "keep": "first"}
  ]
}
```

#### Deduplicate by specific key columns
```json
{
  "operations": [
    {"type": "remove_duplicates", "columns": ["email"], "keep": "last"}
  ]
}
```

#### Remove all rows that have duplicates
```json
{
  "operations": [
    {"type": "remove_duplicates", "columns": ["user_id"], "keep": "none"}
  ]
}
```

## Decision Tree

```
Are there exact duplicate rows?
├── Yes →
│   ├── Is order meaningful (timestamps)?
│   │   ├── Yes → Keep "last" (most recent)
│   │   └── No → Keep "first"
│   └── Apply remove_duplicates
└── No → Check for key-based duplicates
    ├── Define key columns (id, email, etc.)
    ├── Check duplicates on keys only
    └── Decide: merge data or keep one
```

## Fuzzy Deduplication

For similar but not identical records, consider:

1. **Normalize first**: Trim, lowercase, remove special chars
2. **Then deduplicate**: Exact matching on normalized values

```json
{
  "operations": [
    {"type": "normalize_strings", "column": "name", "ops": ["trim", "lowercase"]},
    {"type": "normalize_strings", "column": "email", "ops": ["trim", "lowercase"]},
    {"type": "remove_duplicates", "columns": ["name", "email"], "keep": "first"}
  ]
}
```

## Advanced: Fuzzy Matching Libraries

For true fuzzy matching (handling typos, variations):
- **FuzzyWuzzy**: Simple string matching
- **recordlinkage**: Comprehensive toolkit
- **Splink**: Large-scale deduplication

These require custom Python scripts beyond the basic `clean.py`.

## Edge Cases

1. **Duplicates with different data**: May need to merge columns
2. **Intentional duplicates**: Some rows may legitimately repeat
3. **Timestamps**: Consider time window for "same" event
4. **Case sensitivity**: Normalize before comparing
