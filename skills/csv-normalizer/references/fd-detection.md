# Functional Dependency Detection

## Overview

Detecting functional dependencies (FDs) from data is essential for normalization. This skill uses a hybrid approach:
1. **Automatic detection** from data patterns
2. **Interactive confirmation** for semantic/uncertain dependencies

## Automatic Detection Algorithm

### Core Principle

For columns X and Y, X → Y holds if: grouping by X, all Y values within each group are identical.

```python
# Pseudocode
def check_fd(df, x_cols, y_col):
    groups = df.groupby(x_cols)[y_col].nunique()
    violations = (groups > 1).sum()
    confidence = 1 - (violations / len(groups))
    return confidence
```

### Confidence Scoring

| Confidence | Interpretation | Action |
|------------|----------------|--------|
| 1.0 | Perfect FD, no violations | Auto-accept |
| 0.95-0.99 | Likely FD, few violations (data errors?) | Flag for review |
| 0.80-0.95 | Possible FD | Ask user |
| < 0.80 | Unlikely FD | Skip |

### Detection Steps

1. **Single-column determinants**: Check each column pair (A → B)
2. **Composite determinants**: For columns with high uniqueness, check pairs (A,B → C)
3. **Key inference**: Find minimal column sets that determine all others

## When to Ask the User

### Semantic Dependencies

Data patterns alone can't detect:
- **Business rules**: `employee_type → salary_grade`
- **Domain constraints**: `country → currency`
- **Temporal dependencies**: `order_date → fiscal_quarter`

### Ambiguous Patterns

Ask user when:
1. **Near-perfect FD (95-99% confidence)**: Could be data errors or valid exceptions
2. **Multiple candidate keys**: User must choose primary key
3. **Composite key ambiguity**: Is {A,B} the key, or just A with B as attribute?

### Example Questions

```
Q: Column 'zip_code' determines 'city' in 98% of rows.
   Is this a valid functional dependency?
   (2% violations could be data errors or multi-city zip codes)

Q: Both 'email' and 'user_id' are unique.
   Which should be the primary key?

Q: Does 'department_id' determine 'manager_id'?
   (Each department has one manager)
```

## Handling Large Datasets

For datasets > 100K rows:

1. **Sample-based detection**: Use random sample (10K rows)
2. **Verify on full data**: Confirm detected FDs
3. **Approximate FDs**: Report confidence with violation counts

## Output Format

```json
{
  "functional_dependencies": [
    {
      "determinant": ["employee_id"],
      "dependent": ["employee_name", "hire_date"],
      "confidence": 1.0,
      "violations": 0,
      "status": "confirmed"
    },
    {
      "determinant": ["zip_code"],
      "dependent": ["city"],
      "confidence": 0.98,
      "violations": 15,
      "status": "needs_review",
      "question": "zip_code → city has 15 violations. Valid FD or data errors?"
    }
  ],
  "candidate_keys": [
    {
      "columns": ["employee_id"],
      "is_minimal": true
    }
  ],
  "current_normal_form": "1NF",
  "violations": {
    "2NF": ["employee_id partially determines dept_name via dept_id"],
    "3NF": ["dept_id → dept_name is transitive"]
  }
}
```

## Special Cases

### Null Values
- Nulls break FD detection (null ≠ null in SQL)
- Strategy: Exclude null rows from FD checks, report null percentage

### Unique Columns
- Column with all unique values → trivial FD to everything
- Mark as candidate key, not as regular FD

### Constant Columns
- Single value in column → no useful FDs
- Flag for potential removal (unless semantically meaningful)
