# Phone Number Normalization

## Detection

Run `analyze.py` and check:
- `semantic_type: phone` - Detected as phone numbers

## Common Formats

| Format | Example | Region |
|--------|---------|--------|
| E.164 | `+12025551234` | International |
| National | `(202) 555-1234` | US |
| Dots | `202.555.1234` | US |
| Dashes | `202-555-1234` | US |
| Spaces | `+44 20 7946 0958` | UK |
| No separators | `2025551234` | Various |

## Target Format: E.164

International standard format:
- Starts with `+`
- Country code
- No separators
- Example: `+12025551234` (US), `+442079460958` (UK)

## Operations

### normalize_phones
```json
{
  "type": "normalize_phones",
  "column": "phone",
  "country": "US"
}
```

Parameters:
- `country`: Default country code (ISO 3166-1 alpha-2)
  - `"US"` - United States
  - `"GB"` - United Kingdom
  - `"DE"` - Germany
  - `"NL"` - Netherlands
  - etc.

## How It Works

Uses the `phonenumbers` library (Python port of libphonenumber):

1. Parses phone number with country hint
2. Validates number is possible
3. Formats to E.164
4. Invalid numbers become `null`

## Examples

### US phone numbers
```json
{
  "operations": [
    {"type": "normalize_phones", "column": "phone", "country": "US"}
  ]
}
```

Input variations all become `+12025551234`:
- `(202) 555-1234`
- `202-555-1234`
- `202.555.1234`
- `2025551234`
- `+1-202-555-1234`

### UK phone numbers
```json
{
  "operations": [
    {"type": "normalize_phones", "column": "phone", "country": "GB"}
  ]
}
```

### Mixed international (with + prefix)
If numbers already have country code (`+1...`, `+44...`):
```json
{
  "operations": [
    {"type": "normalize_phones", "column": "phone", "country": "US"}
  ]
}
```
Numbers with `+` will use their country code; others default to specified country.

## Decision Tree

```
Is column detected as phone type?
├── Yes →
│   ├── What country are the numbers from?
│   │   ├── Known single country → Set that country
│   │   ├── Mixed with + prefix → Any country (prefix used)
│   │   └── Unknown → May need investigation
│   └── Apply normalize_phones
└── No → Skip phone normalization
```

## Handling Results

Check operation log:
- `valid`: Numbers successfully normalized
- `invalid`: Numbers that couldn't be parsed

Invalid numbers might be:
- Wrong country assumed
- Incomplete numbers
- Non-phone data in column
- Extension format (`ext.`, `x123`)

## Limitations

The normalization:
- Requires `phonenumbers` library
- Needs correct country hint for national formats
- Extensions may not be handled
- Very short numbers may fail

## Edge Cases

1. **Extensions**: `202-555-1234 ext 567` - may fail or lose extension
2. **Short codes**: `911`, `411` - may not validate
3. **Landline vs mobile**: Both normalized same way
4. **Formatted output**: Only E.164 supported via this operation

## Multiple Countries

If data contains phones from multiple countries without `+` prefix:
1. Split by country if known
2. Or require `+` prefix in source data
3. Or process in multiple passes with different country codes
