# Data Normalization

Normalization standardizes data formats for consistency.

## Types of Normalization

| Type | Purpose | Examples |
|------|---------|----------|
| **String** | Consistent text format | Trim, lowercase, remove special |
| **Date** | Standard date format | Convert all to ISO 8601 |
| **Numeric** | Consistent number format | Handle locale differences |
| **Phone** | Standard phone format | Convert to E.164 |
| **Email** | Clean email addresses | Lowercase, validate |

## When to Normalize

- `whitespace_issues` in analysis → String normalization
- `mixed_case` in analysis → Case normalization
- Different date formats observed → Date standardization
- Phone numbers in various formats → Phone normalization

## String Normalization

See [Strings](../types/strings.md) for detailed guidance.

Quick reference:
```json
{
  "type": "normalize_strings",
  "column": "name",
  "ops": ["trim", "lowercase", "collapse_whitespace"]
}
```

Available ops:
- `trim`: Remove leading/trailing whitespace
- `lowercase`: Convert to lowercase
- `uppercase`: Convert to uppercase
- `titlecase`: Title Case Each Word
- `remove_special`: Remove non-alphanumeric
- `remove_digits`: Remove numbers
- `collapse_whitespace`: Multiple spaces → single space

## Date Standardization

See [Dates](../types/dates.md) for detailed guidance.

```json
{
  "type": "standardize_dates",
  "column": "created_at",
  "format": "%Y-%m-%d",
  "dayfirst": false
}
```

Target format: ISO 8601 (`YYYY-MM-DD`)

## Phone Normalization

See [Phones](../types/phones.md) for detailed guidance.

```json
{
  "type": "normalize_phones",
  "column": "phone",
  "country": "US"
}
```

Target format: E.164 (`+12025551234`)

## Email Validation

See [Emails](../types/emails.md) for detailed guidance.

```json
{
  "type": "validate_emails",
  "column": "email"
}
```

Normalizes to lowercase, validates format.

## Type Conversion

Convert column to specific data type:

```json
{
  "type": "convert_type",
  "column": "count",
  "target_type": "int"
}
```

Target types:
- `int`: Integer (nullable)
- `float`: Floating point
- `string`: Text
- `datetime`: Date/time
- `category`: Categorical (memory efficient)
- `boolean`: True/False

## Normalization Order

1. **Remove/trim whitespace** (affects all comparisons)
2. **Case normalize** (for consistency)
3. **Date/phone standardization** (format conversion)
4. **Type conversion** (final data types)

## Example: Comprehensive Normalization

```json
{
  "operations": [
    {"type": "normalize_strings", "column": "name", "ops": ["trim", "titlecase"]},
    {"type": "normalize_strings", "column": "email", "ops": ["trim", "lowercase"]},
    {"type": "validate_emails", "column": "email"},
    {"type": "standardize_dates", "column": "created_at", "format": "%Y-%m-%d"},
    {"type": "normalize_phones", "column": "phone", "country": "US"},
    {"type": "convert_type", "column": "age", "target_type": "int"}
  ]
}
```
