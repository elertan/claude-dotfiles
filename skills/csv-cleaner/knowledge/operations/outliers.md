# Outlier Detection & Handling

## Detection

Run `analyze.py` and check for numeric columns:
- `stats.min` and `stats.max`: Extreme values
- `stats.mean` vs `stats.median`: Large difference indicates skew/outliers
- `potential_outliers`: Count of IQR-based outliers
- Issue `has_outliers` if outliers detected

## Detection Methods

| Method | Formula | Best For |
|--------|---------|----------|
| **IQR** | < Q1 - 1.5×IQR or > Q3 + 1.5×IQR | General purpose, robust |
| **Z-score** | \|z\| > 3 (3 std from mean) | Normal distributions |
| **Percentile** | < 1st or > 99th percentile | Known bounds |
| **Domain** | Business rules | Known valid ranges |

## Handling Strategies

| Strategy | When to Use | Operation |
|----------|-------------|-----------|
| **Cap (Winsorize)** | Reduce influence, keep data | `cap_outliers` |
| **Remove** | Invalid data, errors | Filter rows |
| **Flag** | Keep but mark | Add column |
| **Transform** | Reduce impact | Log transform |
| **Keep** | Valid extreme values | No action |

## Operations

### Cap Outliers (Winsorization)
```json
{"type": "cap_outliers", "column": "income", "method": "iqr", "multiplier": 1.5}
```

Parameters:
- `method`: Detection method
  - `"iqr"`: Interquartile range (default)
  - `"zscore"`: Standard deviations
  - `"percentile"`: Fixed percentiles
- `multiplier`: How many IQR/std (default: 1.5 for IQR, 3 for zscore)
- `lower_percentile` / `upper_percentile`: For percentile method (e.g., 1 and 99)

### Examples

#### Cap using IQR method
```json
{
  "operations": [
    {"type": "cap_outliers", "column": "salary", "method": "iqr", "multiplier": 1.5}
  ]
}
```

#### Cap using Z-score (3 std)
```json
{
  "operations": [
    {"type": "cap_outliers", "column": "score", "method": "zscore", "multiplier": 3}
  ]
}
```

#### Cap at specific percentiles
```json
{
  "operations": [
    {
      "type": "cap_outliers",
      "column": "response_time",
      "method": "percentile",
      "lower_percentile": 1,
      "upper_percentile": 99
    }
  ]
}
```

## Decision Tree

```
Is the column numeric?
├── No → Skip outlier detection
└── Yes → Check stats
    ├── Mean ≈ Median? → Likely no outliers or symmetric
    └── Mean >> Median or Mean << Median? → Outliers present
        ├── Are outliers valid data? (domain knowledge)
        │   ├── Yes → Keep or just flag
        │   └── No →
        │       ├── Error values → Remove rows
        │       └── Extreme but valid → Cap/Winsorize
        └── Apply appropriate operation
```

## When NOT to Remove Outliers

1. **Domain expects extremes**: Income, wealth, viral content
2. **Small sample size**: May lose important data
3. **Outlier IS the signal**: Fraud detection, anomaly detection
4. **Measurement is accurate**: Just unusual, not wrong

## Best Practices

1. **Investigate first**: Understand why outliers exist
2. **Domain knowledge**: Consult business rules
3. **Document decisions**: Record what was done and why
4. **Check distributions**: Before and after cleaning

## Example: Multiple Columns

```json
{
  "operations": [
    {"type": "cap_outliers", "column": "age", "method": "iqr", "multiplier": 1.5},
    {"type": "cap_outliers", "column": "income", "method": "percentile", "lower_percentile": 1, "upper_percentile": 99},
    {"type": "cap_outliers", "column": "score", "method": "zscore", "multiplier": 3}
  ]
}
```
