# Numeric Data Handling

## Detection

Run `analyze.py` and check:
- `dtype`: `int64`, `float64` indicate numeric
- `semantic_type: numeric`
- `stats`: Contains min, max, mean, median, std

## Common Issues

| Issue | Example | Solution |
|-------|---------|----------|
| String numbers | `"123"` as text | `convert_type` to int/float |
| Locale formatting | `"1.234,56"` (German) | Custom parsing |
| Currency symbols | `"$1,234.56"` | Remove symbols first |
| Percentage signs | `"45%"` | Remove and divide by 100 |
| Outliers | Extreme values | `cap_outliers` |
| Mixed formats | Some with decimals, some without | `convert_type` |

## Operations

### Type Conversion
```json
{
  "type": "convert_type",
  "column": "count",
  "target_type": "int"
}
```

Target types:
- `int`: Integer (nullable, handles NaN)
- `float`: Floating point

### Cap Outliers
```json
{
  "type": "cap_outliers",
  "column": "salary",
  "method": "iqr",
  "multiplier": 1.5
}
```

See [Outliers](../operations/outliers.md) for details.

## Locale-Specific Parsing

Different locales use different number formats:

| Locale | Format | Meaning |
|--------|--------|---------|
| US/UK | 1,234.56 | One thousand... |
| Germany | 1.234,56 | One thousand... |
| India | 1,23,456 | One lakh... |

For locale-aware parsing, preprocess with custom Python:

```python
# German format to standard
df['amount'] = df['amount'].str.replace('.', '', regex=False)
df['amount'] = df['amount'].str.replace(',', '.', regex=False)
df['amount'] = pd.to_numeric(df['amount'])
```

## Currency Handling

To clean currency values:

1. Remove currency symbols: `$`, `€`, `£`, etc.
2. Remove thousand separators
3. Handle negative formats: `(100)` → `-100`
4. Convert to numeric

```python
# Example preprocessing
df['price'] = df['price'].str.replace(r'[$€£,]', '', regex=True)
df['price'] = pd.to_numeric(df['price'])
```

## Percentage Handling

Values like `"45%"`:

1. Remove `%` symbol
2. Divide by 100 (if needed as decimal)
3. Convert to float

## Decision Tree

```
Is column supposed to be numeric?
├── Already numeric dtype?
│   ├── Yes → Check for outliers
│   └── No → Need type conversion
│       ├── Clean string format first (remove $, %, etc.)
│       └── Apply convert_type
└── Check stats for issues
    ├── Has outliers? → cap_outliers
    ├── All integers? → convert_type to int
    └── Has decimals? → keep as float
```

## Examples

### Convert string to integer
```json
{
  "operations": [
    {"type": "convert_type", "column": "quantity", "target_type": "int"}
  ]
}
```

### Convert and cap outliers
```json
{
  "operations": [
    {"type": "convert_type", "column": "price", "target_type": "float"},
    {"type": "cap_outliers", "column": "price", "method": "iqr"}
  ]
}
```

## Validation Checks

After conversion, verify:
- No unexpected NaN values (conversion failures)
- Range is reasonable (min/max)
- Mean and median look correct
