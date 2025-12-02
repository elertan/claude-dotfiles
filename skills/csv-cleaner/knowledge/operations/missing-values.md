# Missing Value Handling

## Detection

Run `analyze.py` and check for each column:
- `null_count`: Number of missing values
- `null_percent`: Percentage missing
- `issues`: Contains `has_missing_values` or `high_missing_rate`

## Understanding Missingness Types

| Type | Definition | How to Identify | Best Approach |
|------|------------|-----------------|---------------|
| **MCAR** | Missing Completely At Random | Random pattern, no correlation with other columns | Any method works |
| **MAR** | Missing At Random | Depends on observed values | Impute using related columns |
| **MNAR** | Missing Not At Random | Depends on the missing value itself | Requires domain knowledge |

## Decision Tree

```
Is >50% of column missing?
├── Yes → Drop column: {"type": "drop_column", "column": "col"}
└── No → Is it an ID/unique identifier?
    ├── Yes → Drop rows: {"type": "drop_missing", "columns": ["col"]}
    └── No → Is it <5% missing?
        ├── Yes → Drop rows OR simple imputation
        └── No → Is it categorical?
            ├── Yes → Mode OR "Unknown" category
            └── No → Check distribution
                ├── Symmetric → Mean imputation
                └── Skewed → Median imputation
```

## Operations

### Fill Missing Values
```json
{"type": "fill_missing", "column": "age", "strategy": "median"}
```

Strategies:
| Strategy | When to Use | Example |
|----------|-------------|---------|
| `mean` | Numeric, symmetric distribution | Salaries with normal distribution |
| `median` | Numeric, skewed distribution | Income, prices |
| `mode` | Categorical data | Categories, status codes |
| `constant` | Known default value | `{"strategy": "constant", "value": "Unknown"}` |
| `forward` | Time series, carry forward | Stock prices, sensors |
| `backward` | Time series, carry backward | Pre-fill from known future |

### Drop Missing
```json
{"type": "drop_missing", "columns": ["required_field"], "how": "any"}
```

Parameters:
- `columns`: List of columns to check (or null for all)
- `how`: `"any"` (drop if any null) or `"all"` (drop only if all null)

## Edge Cases

1. **Never impute IDs** - Drop rows with missing IDs
2. **Consider creating flag column** - Track which values were imputed:
   - Add `is_imputed_<col>` column before imputation
3. **High missing rate (>30%)** - Consider if column is useful
4. **Missing as information** - Sometimes NULL means something (e.g., "no phone")

## Examples

### Numeric column with skewed distribution
```json
{
  "operations": [
    {"type": "fill_missing", "column": "income", "strategy": "median"}
  ]
}
```

### Categorical with mode
```json
{
  "operations": [
    {"type": "fill_missing", "column": "status", "strategy": "mode"}
  ]
}
```

### Required field - drop rows
```json
{
  "operations": [
    {"type": "drop_missing", "columns": ["email", "user_id"], "how": "any"}
  ]
}
```

### Multiple columns with different strategies
```json
{
  "operations": [
    {"type": "fill_missing", "column": "age", "strategy": "median"},
    {"type": "fill_missing", "column": "gender", "strategy": "constant", "value": "Unknown"},
    {"type": "drop_missing", "columns": ["id"], "how": "any"}
  ]
}
```
