# Date Standardization

## Detection

Run `analyze.py` and check:
- `semantic_type: date` - Detected as date
- Sample values show date-like patterns

## Common Formats

| Format | Example | Ambiguity |
|--------|---------|-----------|
| ISO 8601 | `2024-01-15` | None (best) |
| US | `01/15/2024` | Month first |
| European | `15/01/2024` | Day first |
| Textual | `January 15, 2024` | None |
| Unix timestamp | `1705276800` | None |
| Mixed | Various formats | Problematic |

## Target Format

**ISO 8601**: `YYYY-MM-DD` (e.g., `2024-01-15`)

Benefits:
- Unambiguous
- Sorts correctly as text
- International standard

## Operations

### standardize_dates
```json
{
  "type": "standardize_dates",
  "column": "created_at",
  "format": "%Y-%m-%d",
  "dayfirst": false
}
```

Parameters:
- `format`: Python strftime format for output
  - `%Y-%m-%d` → `2024-01-15`
  - `%Y-%m-%d %H:%M:%S` → `2024-01-15 14:30:00`
  - `%d/%m/%Y` → `15/01/2024`
- `dayfirst`: Assume day comes first in ambiguous dates (default: false)
- `yearfirst`: Assume year comes first (default: false)

## Ambiguity Resolution

For `01/02/03`:
- US format (month first): January 2, 2003
- European (day first): February 1, 2003
- Year first: 2001 February 3

Set `dayfirst: true` for European-style dates:
```json
{
  "type": "standardize_dates",
  "column": "date",
  "format": "%Y-%m-%d",
  "dayfirst": true
}
```

## Common Output Formats

| Purpose | Format | Example |
|---------|--------|---------|
| Date only | `%Y-%m-%d` | `2024-01-15` |
| Datetime | `%Y-%m-%d %H:%M:%S` | `2024-01-15 14:30:00` |
| With timezone | `%Y-%m-%dT%H:%M:%S%z` | `2024-01-15T14:30:00+0000` |
| US display | `%m/%d/%Y` | `01/15/2024` |
| European | `%d/%m/%Y` | `15/01/2024` |
| Long form | `%B %d, %Y` | `January 15, 2024` |

## Decision Tree

```
Is column detected as date type?
├── Yes → Check sample values
│   ├── All same format? → Simple conversion
│   └── Mixed formats? → Parser will attempt all
│       ├── Mostly US style? → dayfirst: false
│       └── Mostly European? → dayfirst: true
└── No → Check if should be date
    ├── Looks like timestamp? → Convert
    └── Not a date → Skip
```

## Examples

### Standard ISO conversion
```json
{
  "operations": [
    {"type": "standardize_dates", "column": "date", "format": "%Y-%m-%d"}
  ]
}
```

### European dates (day first)
```json
{
  "operations": [
    {
      "type": "standardize_dates",
      "column": "order_date",
      "format": "%Y-%m-%d",
      "dayfirst": true
    }
  ]
}
```

### Include time
```json
{
  "operations": [
    {
      "type": "standardize_dates",
      "column": "timestamp",
      "format": "%Y-%m-%d %H:%M:%S"
    }
  ]
}
```

## Handling Failures

Check the operation log for:
- `converted`: Number successfully parsed
- `failed`: Number that couldn't be parsed

Failed parses become `null`. Consider:
1. Investigating failed values
2. Trying different `dayfirst`/`yearfirst` settings
3. Custom preprocessing for unusual formats

## Edge Cases

1. **Two-digit years**: `01/15/24` - assumes 2024 vs 1924
2. **Timezone handling**: Parser may not preserve timezone
3. **Invalid dates**: `02/31/2024` - will fail
4. **Relative dates**: `"yesterday"` - not supported
