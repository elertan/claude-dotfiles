# Data Types Overview

Type-specific handling for different data formats.

## Detected Types

The `analyze.py` script detects these semantic types:

| Type | Detection | Guide |
|------|-----------|-------|
| `email` | RFC 5322 pattern match | [Emails](emails.md) |
| `phone` | Digit/separator pattern | [Phones](phones.md) |
| `date` | Parseable date formats | [Dates](dates.md) |
| `url` | `http://` or `https://` prefix | Basic URL validation |
| `uuid` | UUID pattern | ID handling |
| `boolean` | true/false, yes/no, 1/0 | Type conversion |
| `numeric` | int/float dtypes | [Numbers](numbers.md) |
| `text` | Default for strings | [Strings](strings.md) |

## Type-Specific Operations

| Semantic Type | Recommended Operations |
|---------------|----------------------|
| email | `validate_emails` |
| phone | `normalize_phones` |
| date | `standardize_dates` |
| text | `normalize_strings` |
| numeric | `cap_outliers`, `convert_type` |

## Quick Reference

### Strings
```json
{"type": "normalize_strings", "column": "name", "ops": ["trim", "lowercase"]}
```

### Dates
```json
{"type": "standardize_dates", "column": "date", "format": "%Y-%m-%d"}
```

### Phones
```json
{"type": "normalize_phones", "column": "phone", "country": "US"}
```

### Emails
```json
{"type": "validate_emails", "column": "email"}
```

### Type Conversion
```json
{"type": "convert_type", "column": "count", "target_type": "int"}
```
